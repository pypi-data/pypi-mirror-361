# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT licence. See LICENSE for more info.

"""Lima2 pipeline base class.

An instance of Pipeline represents one processing pipeline, possibly distributed across multiple
Lima2 receivers. The processing is assumed to be the same across all receivers.

It has knowledge of the topology, and therefore can fetch a frame given a global
frame index, and provide aggregated progress counters during/after an acquisition.
"""

import logging
import traceback
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, AsyncIterator, Awaitable, cast
from uuid import UUID

import numpy as np

from lima2.client import progress_counter
from lima2.client.processing.frame import FrameChannel, FrameSource, SavingParams
from lima2.client.processing.master_file import MasterFileGenerator
from lima2.client.processing.reduced_data import (
    ReceiverAwareReducedDataChannel,
    ReducedDataFetcher,
    ReducedDataInfo,
    ReducedDataSource,
    ScalarDataSource,
)
from lima2.client.progress_counter import ProgressCounter, SingleCounter
from lima2.client.tango.processing import (
    FrameInfo,
    ProcessingErrorEvent,
    TangoProcessing,
)
from lima2.client.topology import (
    DynamicDispatch,
    FrameLookupError,
    LookupTable,
    RoundRobin,
    SingleReceiver,
    Topology,
)

logger = logging.getLogger(__name__)


FRAME_IDX_DTYPE = np.dtype(
    [
        ("recv_idx", np.int32),
        ("frame_idx", np.int32),
    ]
)


@dataclass
class PipelineErrorEvent:
    """Structure passed to the registered callback upon error in the pipeline."""

    uuid: UUID
    device_name: str
    error_msg: str


class Pipeline:
    """A base class for all processing pipelines.

    Implements logic common to all processing pipelines.
    """

    FRAME_SOURCES: dict[str, FrameSource]
    """Map of available frame source names to a corresponding FrameSource descriptor.

    Definition in child classes is enforced by __init_subclass__().
    """

    REDUCED_DATA_SOURCES: dict[str, ReducedDataSource]
    """Map of available reduced data names to a corresponding ReducedDataSource descriptor.

    Definition in child classes is enforced by __init_subclass__().
    """

    TANGO_CLASS: str
    """Class name as defined on server side.

    Definition in child classes is enforced by __init_subclass__().
    """

    @classmethod
    def __init_subclass__(cls) -> None:
        """Initialize a pipeline subclass."""
        if not hasattr(cls, "TANGO_CLASS"):
            raise ValueError(
                f"Pipeline subclass {cls} must define a TANGO_CLASS class member"
            )

        if not hasattr(cls, "FRAME_SOURCES"):
            raise ValueError(
                f"Pipeline subclass {cls} must define a FRAME_SOURCES class member"
            )

        if not hasattr(cls, "REDUCED_DATA_SOURCES"):
            raise ValueError(
                f"Pipeline subclass {cls} must define a REDUCED_DATA_SOURCES class member"
            )

    def __init__(
        self,
        uuid: UUID,
        devices: list[TangoProcessing],
        topology: Topology,
        on_finished: Callable[[list[str]], Awaitable[None]],
        on_error: Callable[[PipelineErrorEvent], Awaitable[None]],
    ):
        """Construct a Pipeline object.

        Args:
            uuid: Unique identifer of the acquisition
            devices: Variable length processing device instances
            topology: Receiver topology
            on_finished: Async callback called when all devices are done processing
            on_error: Async callback called when an error event is received from
                one of the processing devices.
        """

        self.uuid = uuid
        self.devices: list[TangoProcessing] = devices
        self.topology = topology

        self.on_finished_callback = on_finished
        self.on_error_callback = on_error

        self.errors: list[str] = []
        """Holds processing error messages that occurred during the run, if any."""

        self.finished_devices: set[str] = set()
        """Set of names of processing devices which are done processing.

        Used to call the on_finished_callback when all devices are finished.
        """

        self.frame_infos: dict[str, FrameInfo] = {}
        """Dynamic frame info (shape, pixel type). Populated in connect()."""

        self.reduced_data_fetcher = ReducedDataFetcher(devices=self.devices)

        self.master_file_generator = MasterFileGenerator(uuid=uuid, topology=topology)

    async def connect(self) -> None:
        """Ping the devices, then subscribe to error/finished events.

        Should be called just after instantiating the Pipeline instance.
        """

        async def on_finished(device_name: str) -> None:
            """Adds a processing device to the finished_devices set.

            When the set is complete, call the on_finished callback registered to
            this pipeline instance (see constructor).
            """
            logger.info(f"Processing device {device_name} is done")
            self.finished_devices.add(device_name)

            if self.is_finished():
                try:
                    await self.on_finished_callback(self.errors)
                except Exception:
                    logger.error(
                        f"Exception raised in pipeline {self.uuid} "
                        "on_finished callback:\n"
                        f"{traceback.format_exc()}"
                    )

        async def on_processing_error(evt: ProcessingErrorEvent) -> None:
            """Reports a processing error to the registered callback.

            Also cancels the reduced data fetching task.
            """
            logger.warning(
                f"Error from processing device {evt.device_name}. "
                f"Reason: '{evt.error_msg}'"
            )
            self.errors.append(f"{evt.device_name}: {evt.error_msg}")

            pipeline_err_evt = PipelineErrorEvent(
                uuid=self.uuid, error_msg=evt.error_msg, device_name=evt.device_name
            )

            try:
                self.abort()
                await self.on_error_callback(pipeline_err_evt)
            except Exception:
                logger.error(
                    f"Exception raised in pipeline {self.uuid} "
                    "on_error callback:\n"
                    f"{traceback.format_exc()}"
                )

        for device in self.devices:
            ping_us = await device.ping()
            logger.debug(f"Ping {device.name}: {ping_us}µs")
            await device.on_finished(on_finished)
            await device.on_error(on_processing_error)

        for name in self.FRAME_SOURCES.keys():
            # TODO(mdu) We should come up with a better mechanism for getting
            # the frame info for a specific frame source.
            if name == "input_frame":
                self.frame_infos[name] = await self.devices[0].input_frame_info()
            else:
                self.frame_infos[name] = await self.devices[0].processed_frame_info()

    def prepare(self, num_frames: int, proc_params: dict[str, Any]) -> None:
        """Prepare the reduced-data fetcher."""

        sources = self.REDUCED_DATA_SOURCES.copy()

        if type(self.topology) is DynamicDispatch or proc_params.get(
            "frame_idx_enabled"
        ):
            # Enable frame_idx fetching
            frame_idx_source: ReducedDataSource = ScalarDataSource(
                getter_name="popFrameIdx",
                src_dtype=FRAME_IDX_DTYPE,
                exposed_cols=["frame_idx"],
                count=1,
                inject_receiver=True,
            )
            sources["frame_idx"] = frame_idx_source

        self.reduced_data_fetcher.prepare(
            num_frames=num_frames,
            roi_stats_params=proc_params.get("statistics"),
            profile_params=proc_params.get("profiles"),
            static_sources=sources,
        )

        if type(self.topology) is DynamicDispatch:
            if "frame_idx" not in self.reduced_data_fetcher.channels:
                raise RuntimeError(
                    "Dynamic frame dispatch but the frame_idx stream is absent"
                )

            logger.warning(
                "Dynamic dispatch: frame_idx fetching enabled to build lookup table"
            )
            channel = cast(
                ReceiverAwareReducedDataChannel,
                self.reduced_data_fetcher.channels["frame_idx"][0],
            )
            self.topology.set_lut(
                LookupTable(
                    frame_idx=channel.data,
                    receiver=channel.receiver,
                    valid=channel.valid,
                )
            )

        frame_channels: dict[str, FrameChannel] = {
            name: (
                source,
                self.frame_infos[name],
                cast(SavingParams, proc_params[source.saving_channel])
                if source.saving_channel is not None
                else None,
            )
            for name, source in self.FRAME_SOURCES.items()
        }

        self.master_file_generator.prepare(
            num_frames=num_frames, frame_channels=frame_channels
        )

    def start(self) -> None:
        """Start the reduced data fetching and master file generation tasks."""
        self.reduced_data_fetcher.start(fetch_interval_s=0.1)

        self.master_file_generator.start()

    def abort(self) -> None:
        """Abort reduced data fetching."""
        self.reduced_data_fetcher.abort()

        self.master_file_generator.abort()

    def reduced_data_channels(self) -> dict[str, list[ReducedDataInfo]]:
        """Get the description of available reduced data streams."""
        return self.reduced_data_fetcher.channel_info()

    def is_finished(self) -> bool:
        return self.finished_devices == set([dev.name for dev in self.devices])

    async def progress_counters(self) -> dict[str, ProgressCounter]:
        """Get the list of aggregated progress counters"""
        pcs_by_rcv = [await dev.progress_counters() for dev in self.devices]

        # Set of unique progress counter names
        pc_keys = set()
        for rcv_pcs in pcs_by_rcv:
            for k in rcv_pcs.keys():
                pc_keys.add(k)

        # Sanity check: all receivers have the same progress counters (assume homogeneous)
        # Perhaps not true in all future topologies
        for rcv in pcs_by_rcv:
            for key in pc_keys:
                assert key in rcv.keys()

        aggregated_pcs: dict[str, ProgressCounter] = {}
        for pc_key in pc_keys:
            single_counters = []
            for dev, pcs in zip(self.devices, pcs_by_rcv):
                single_counters.append(
                    SingleCounter(name=pc_key, value=pcs[pc_key], source=dev.name)
                )

            aggregated_pcs[pc_key] = progress_counter.aggregate(
                single_counters=single_counters
            )

        return aggregated_pcs

    async def lookup_last(self) -> str:
        """Returns the url of the receiver who has processed the latest frame."""
        match self.topology:
            case SingleReceiver():
                return self.devices[0].name
            case RoundRobin():
                # From the number of frames acquired, determine the
                # receiver of the last frame

                # In strict round robin, the last frame is the one with the highest frame
                # index. To find it, use progress counters from individual receivers.

                nb_frames_processed = (await self.progress_counters())[
                    "nb_frames_processed"
                ]

                values = [counter.value for counter in nb_frames_processed.counters]

                if all([value <= 0 for value in values]):
                    raise FrameLookupError(
                        "Cannot lookup last frame: no frames processed yet"
                    )
                else:
                    # Take the receiver with most frames processed and ask it for the
                    # latest one
                    # Reverse the list so that rightmost receivers are favored.
                    values.reverse()
                    rcv_idx = len(values) - values.index(max(values)) - 1
                    return self.devices[rcv_idx].name
            case DynamicDispatch():
                # Use lookup table to determine last frame acquired
                rcv_idx = self.topology.lookup_last()
                return self.devices[rcv_idx].name
            case _:
                raise NotImplementedError

    def lookup(self, frame_idx: int) -> str:
        """Returns the url of the receiver that processed a given frame."""
        return self.devices[self.topology.lookup(frame_idx=frame_idx)].name

    async def num_available(self, source: str) -> int:

        if source not in self.FRAME_SOURCES:
            raise ValueError(
                f"Cannot get the number of available '{source}': invalid source. "
                f"Try {list(self.FRAME_SOURCES.keys())}"
            )

        counter_name = self.FRAME_SOURCES[source].progress_counter_name
        if counter_name is None:
            raise ValueError(
                f"Cannot get the number of available '{source}': no associated progress counter"
            )

        counter = (await self.progress_counters())[counter_name]

        return self.topology.num_contiguous(counter)

    async def get_reduced_data(
        self, name: str, chan_index: int
    ) -> AsyncIterator[bytes]:
        """Get a reduced data stream as an async iterator."""
        async for row in self.reduced_data_fetcher.get_stream(
            name=name, chan_index=chan_index
        ):
            yield row
