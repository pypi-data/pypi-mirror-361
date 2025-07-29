# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT licence. See LICENSE for more info.

"""Reduced data input/output mechanisms."""

import asyncio
import functools
import logging
import time
import traceback
from collections import namedtuple
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any, AsyncIterator, cast

import numpy as np
import numpy.typing as npt

from lima2.client.devencoded import structured_array
from lima2.client.tango.processing import TangoProcessing

logger = logging.getLogger(__name__)

Roi = namedtuple("Roi", ())
Profile = namedtuple("Profile", ("length"))


@dataclass
class ScalarDataSource:
    """A data source with zero-dimensional values.

    E.g. fill factor (count = 1), roi statistics (count = number of rois).
    """

    getter_name: str
    src_dtype: np.dtype
    """Numpy dtype of the source stream (decoded after pop)."""
    exposed_cols: list[str]
    """Columns of the source (keys in src_dtype) exposed in outgoing ReducedDataChannels."""
    count: int
    """Number of elements in each frame. Each element will become one ReducedDataChannel."""
    inject_receiver: bool = False
    """If True, the index of the receiver will be concatenated with the reduced data."""

    def length(self) -> int:
        return self.count

    def shapes(self) -> list[tuple[int, ...]]:
        return [(1,)] * self.count

    def stream_dtype(self) -> np.dtype:
        """Effective dtype of the outgoing data, given source dtype and exposed columns."""
        return np.dtype([(col, self.src_dtype[col]) for col in self.exposed_cols])


@dataclass
class VectorDataSource:
    """A data source whose values are 1D vectors with a fixed length.

    E.g. roi profiles.
    """

    getter_name: str
    src_dtype: np.dtype
    """Numpy dtype of the source stream (decoded after pop)."""
    exposed_cols: list[str]
    """Columns of the source (keys in src_dtype) exposed in outgoing ReducedDataChannels."""
    sizes: list[int]
    inject_receiver: bool = False
    """If True, the index of the receiver will be concatenated with the reduced data."""

    def length(self) -> int:
        return sum(self.sizes)

    def shapes(self) -> list[tuple[int, ...]]:
        return [(size,) for size in self.sizes]

    def stream_dtype(self) -> np.dtype:
        """Effective dtype of the outgoing data, given source dtype and exposed columns."""
        return np.dtype([(col, self.src_dtype[col]) for col in self.exposed_cols])


ReducedDataSource = ScalarDataSource | VectorDataSource


@dataclass
class ReducedDataInfo:
    """Describes an outgoing reduced data channel."""

    shape: tuple[int, ...]
    dtype: np.dtype

    def asdict(self) -> dict[str, Any]:
        return {
            "shape": self.shape,
            "dtype": np.dtype(self.dtype).descr,
        }

    @staticmethod
    def fromdict(d) -> "ReducedDataInfo":
        return ReducedDataInfo(
            shape=d["shape"],
            dtype=np.dtype([tuple(i) for i in d["dtype"]]),
        )


ROI_STATS_DTYPE = np.dtype(
    [
        ("frame_idx", np.int32),
        ("recv_idx", np.int32),
        ("min", np.float32),
        ("max", np.float32),
        ("avg", np.float32),
        ("std", np.float32),
        ("sum", np.float64),
    ]
)

ROI_PROFILES_DTYPE = np.dtype(
    [
        ("frame_idx", np.int32),
        ("recv_idx", np.int32),
        ("min", np.float32),
        ("max", np.float32),
        ("avg", np.float32),
        ("std", np.float32),
        ("sum", np.float64),
    ]
)


def parse_roi_params(
    roi_params: dict[str, Any] | None, profile_params: dict[str, Any] | None
) -> tuple[list[Roi], list[Profile]]:
    """Interpret roi stats and roi profile params to build Roi/Profile lists."""

    rois: list[Roi] = []
    profiles: list[Profile] = []

    if roi_params and roi_params["enabled"]:
        for _ in roi_params["rect_rois"] + roi_params["arc_rois"]:
            rois.append(Roi())

    if profile_params and profile_params["enabled"]:
        for roi, direction in zip(profile_params["rois"], profile_params["directions"]):
            if direction == "vertical":
                profiles.append(Profile(length=roi["dimensions"]["y"]))
            elif direction == "horizontal":
                profiles.append(Profile(length=roi["dimensions"]["x"]))
            else:
                raise RuntimeError(
                    f"Invalid profile direction '{direction}'."
                )  # pragma: no cover

    logger.debug(f"{rois=}")
    logger.debug(f"{profiles=}")

    return rois, profiles


def log_exception(func):
    """Log any exceptions from func and reraise."""

    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(traceback.format_exc())
            raise e

    return wrapper


async def fetch(
    devices: list[TangoProcessing], getter_name: str
) -> list[tuple[str, bytes]]:
    """Pop reduced data from all devices, raise on any error."""

    results = await asyncio.gather(
        *[dev.pop_reduced_data(getter_name) for dev in devices],
        return_exceptions=True,  # Collect exceptions in results
    )

    errors = [result for result in results if isinstance(result, Exception)]

    if len(errors) > 0:
        logger.error(errors)
        raise RuntimeError(
            "Reduced data fetch failed:\n- "
            + "\n- ".join([str(error) for error in errors])
        )
    return cast(list[tuple[str, bytes]], results)


def decode(
    raw: list[tuple[str, bytes]],
    dtype: np.dtype,
    length: int,
    return_receiver: bool,
) -> npt.NDArray | tuple[npt.NDArray, npt.NDArray[np.int32]]:
    """Decode devencoded data into numpy arrays, concatenate across receivers.

    If return_receiver is True, additionally return the receiver array,
    which encodes the index of the receiving device for each row.
    """

    with ThreadPoolExecutor(max_workers=len(raw)) as executor:
        result = list(
            executor.map(functools.partial(structured_array.decode, dtype=dtype), raw)
        )

    if return_receiver:
        receiver = []
        for rcv_idx, array in enumerate(result):
            receiver.append(
                np.full(fill_value=rcv_idx, shape=array.shape, dtype=np.int32)
            )
        return np.concatenate(result).reshape((-1, length)), np.concatenate(receiver)
    else:
        return np.concatenate(result).reshape((-1, length))  # type: ignore


def reorder(
    data: npt.NDArray, source: ReducedDataSource
) -> tuple[npt.NDArray, list[npt.NDArray]]:
    """Order data in sequential frame ordering.

    Returns unique frame_indices present in the new data, and a list
    of arrays of ordered data.

    TODO(mdu) Rename this method. We are not reordering here, simply splitting
    the data source into its components and figuring out what corresponding
    frame indices are present this time around.
    """

    frame_indices, idx = np.unique(data["frame_idx"], return_index=True)

    data = data.reshape((frame_indices.size, -1))

    result: list[npt.NDArray] = []
    offset = 0
    for shape in source.shapes():
        tgt = data[:, offset : offset + sum(shape)]
        result.append(tgt)
        offset += sum(shape)

    # np.argsort(idx) is used to restore the original ordering
    # of frame indices, so that rows aren't swapped in the output
    return frame_indices[np.argsort(idx)], result


@dataclass
class ReducedDataChannel:
    """Outgoing reduced data channel.

    One reduced data source can correspond to multiple
    reduced data channels. For example, the roi statistics
    source is exposed as multiple channels: one for each roi.
    """

    data: npt.NDArray
    valid: npt.NDArray[np.bool_]
    """Indicates whether a data row is ready for consumption by the serving task."""


@dataclass
class ReceiverAwareReducedDataChannel(ReducedDataChannel):
    """A reduced data channel which includes indices of the receiving device for each row."""

    receiver: npt.NDArray[np.int32]


class ReducedDataFetcher:
    """Encapsulates the reduced data fetch-decode-reorder mechanisms.

    One ReducedDataFetcher is created by the Pipeline instance at prepare-time,
    at which point all reduced data sources are identified.

    When the acquisition is started, the ReducedDataFetcher starts its fetching
    tasks, which periodically pop data from the devices. The data is then stored
    in the `channels` dictionary, in sequential order.

    When a client requests a stream of reduced data, a serving task is started,
    and an async generator is returned.

    The serving task populates an asyncio.Queue with ordered data until the data
    for all frames is there. The async generator pops from this queue as soon
    as data for a frame is available.
    """

    def __init__(self, devices: list[TangoProcessing]):
        self.devices = devices

        self.fetching_tasks: set[asyncio.Task] = set()
        self.serving_tasks: set[asyncio.Task] = set()

        self.sources: dict[str, ReducedDataSource] = {}
        self.channels: dict[str, list[ReducedDataChannel]] = {}
        self.new_data_event: dict[str, list[list[asyncio.Event]]] = {}

        self.cancelled = asyncio.Event()
        """
        Signals that the fetching was cancelled, so callers of get_stream() should
        not expect to receive the entirety of the data.
        """

        self.num_frames_expected = 0

    def prepare(
        self,
        num_frames: int,
        roi_stats_params: dict[str, Any] | None,
        profile_params: dict[str, Any] | None,
        static_sources: dict[str, ReducedDataSource],
    ) -> None:
        """Allocate numpy arrays for all reduced data sources.

        Must be called at prepare time.

        Combine static reduced data sources (e.g. xpcs fill_factor) with
        dynamically created rois to allocate all reduced data arrays.

        Roi stats and profiles are a special case: they correspond to a single
        server-side source (popRoiStatistics) but can provide multiple reduced
        data streams (roi_stats_0, roi_stats_1, ..., roi_profile_0, roi_profile_1, ...)
        """

        self.num_frames_expected = num_frames
        self.sources = static_sources.copy()

        # NOTE(mdu) we could avoid having to parse roi/profile params by adding
        # a server-side mechanism for querying the active reduced data streams
        rois, profiles = parse_roi_params(
            roi_params=roi_stats_params, profile_params=profile_params
        )

        if len(rois) > 0:
            self.sources["roi_stats"] = ScalarDataSource(
                getter_name="popRoiStatistics",
                src_dtype=ROI_STATS_DTYPE,
                exposed_cols=["avg", "std", "min", "max", "sum"],
                count=len(rois),
            )

        if len(profiles) > 0:
            self.sources["roi_profile"] = VectorDataSource(
                getter_name="popRoiProfiles",
                src_dtype=ROI_PROFILES_DTYPE,
                exposed_cols=["avg", "std", "min", "max", "sum"],
                sizes=[profile.length for profile in profiles],
            )

        logger.debug("Allocating reduced data buffers")

        if num_frames <= 0:
            # TODO(mdu) infinite acquisition mechanism
            raise NotImplementedError("Infinite acquisition cannot be handled yet")

        start = time.perf_counter()
        for name, source in self.sources.items():
            self.channels[name] = []
            self.new_data_event[name] = []

            for i, shape in enumerate(source.shapes()):
                logger.debug(f"Allocate {(num_frames, *shape)} for {name}[{i}]")

                channel_dtype: list[tuple[str, np.dtype]] = [
                    (key, source.src_dtype[key]) for key in source.exposed_cols
                ]

                if source.inject_receiver:
                    self.channels[name].append(
                        ReceiverAwareReducedDataChannel(
                            data=np.empty(
                                shape=(num_frames, *shape), dtype=channel_dtype
                            ),
                            valid=np.zeros(shape=(num_frames,), dtype=bool),
                            receiver=np.full(
                                fill_value=-1, shape=(num_frames,), dtype=np.int32
                            ),
                        )
                    )
                else:
                    self.channels[name].append(
                        ReducedDataChannel(
                            data=np.empty(
                                shape=(num_frames, *shape), dtype=channel_dtype
                            ),
                            valid=np.zeros(shape=(num_frames,), dtype=bool),
                        )
                    )

                self.new_data_event[name].append([])

                logger.debug(
                    f"Allocated {self.channels[name][-1].data.nbytes / 1024} kiB "
                    f" for {name}[{i}]"
                )

        logger.debug(f"Allocated in {(time.perf_counter() - start) * 1e3:.1f}ms")
        logger.info(f"Ready to fetch reduced data for {list(self.channels.keys())}")

    @log_exception
    async def fetching_loop(
        self, name: str, source: ReducedDataSource, fetch_interval_s: float
    ):
        """Fetch, decode and reorder data from a reduced data source."""

        logger.info(f"Fetching task started for '{name}'")
        num_frames_fetched = 0

        while True:
            start_time = time.perf_counter()

            raw = await fetch(devices=self.devices, getter_name=source.getter_name)

            # Run CPU-bound decode() in executor (thread) to release the GIL while numpy
            # operates on the data.
            if source.inject_receiver:
                (
                    unordered_data,
                    receiver,
                ) = await asyncio.get_running_loop().run_in_executor(
                    None,
                    functools.partial(
                        decode,
                        raw=raw,
                        dtype=source.src_dtype,
                        length=source.length(),
                        return_receiver=True,
                    ),
                )
            else:
                unordered_data = await asyncio.get_running_loop().run_in_executor(
                    None,
                    functools.partial(
                        decode,
                        raw=raw,
                        dtype=source.src_dtype,
                        length=source.length(),
                        return_receiver=False,
                    ),
                )

            if unordered_data.size == 0:
                await asyncio.sleep(
                    max(0.0, fetch_interval_s - (time.perf_counter() - start_time))
                )
                continue

            assert unordered_data.dtype.fields is not None, "must be a structured array"
            if "frame_idx" not in unordered_data.dtype.fields:
                raise RuntimeError(
                    f"No column 'frame_idx' in data fetched for '{name}'.\n"
                    "Cannot reorder."
                )

            # Run CPU-bound reorder() in executor (thread) to release the GIL while numpy
            # operates on the data.
            frame_indices, data = await asyncio.get_running_loop().run_in_executor(
                None, functools.partial(reorder, data=unordered_data, source=source)
            )

            num_frames_fetched += frame_indices.size

            for i in range(len(data)):
                channel = self.channels[name][i]
                channel.data[frame_indices] = data[i][source.exposed_cols]
                channel.valid[frame_indices] = True
                if type(channel) is ReceiverAwareReducedDataChannel:
                    channel.receiver[frame_indices] = receiver

                # Signal new data to consumers
                for event in self.new_data_event[name][i]:
                    event.set()

            # Break condition
            if num_frames_fetched >= self.num_frames_expected:
                break

            end_time = time.perf_counter()

            loop_time = end_time - start_time
            logger.debug(f"{name} fetching iteration time: {loop_time * 1e3:.1f}ms")

            if end_time - start_time > fetch_interval_s:
                # Iteration took longer than interval -> go straight to the next iteration
                logger.warning(
                    f"Fetch-decode-reorder cycle for {name} took {loop_time * 1e3:.1f}ms"
                )
            else:
                # Iteration took less than interval -> wait
                await asyncio.sleep(fetch_interval_s - loop_time)

        logger.info(f"Fetching task done for '{name}'")

    def start(self, fetch_interval_s: float) -> None:
        """Start the reduced data fetching and reordering task."""
        if len(self.fetching_tasks) > 0:
            raise RuntimeError("Fetching tasks already started")

        for name, source in self.sources.items():
            task = asyncio.create_task(
                self.fetching_loop(
                    name=name, source=source, fetch_interval_s=fetch_interval_s
                ),
                name=f"{name}_fetching_task",
            )
            self.fetching_tasks.add(task)
            # See https://docs.python.org/3/library/asyncio-task.html#asyncio.create_task
            task.add_done_callback(self.fetching_tasks.discard)

    def abort(self) -> None:
        """Stop all fetching and serving tasks."""

        # Signal to get_stream() serving tasks to stop before all data is fetched.
        self.cancelled.set()

        for task in self.fetching_tasks | self.serving_tasks:
            logger.info(f"Aborting {task.get_name()}")
            task.cancel()

    def channel_info(self) -> dict[str, list[ReducedDataInfo]]:
        return {
            key: [
                ReducedDataInfo(shape=item.data.shape[1:], dtype=item.data.dtype)
                for item in channel_list
            ]
            for key, channel_list in self.channels.items()
        }

    async def get_stream(self, name: str, chan_index: int) -> AsyncIterator[bytes]:
        """Get a stream of reduced data as an async generator.

        Multiple clients may request the same reduced data stream, therefore
        this returns a new, independent generator every time it is called.

        To do this, it launches a task to fill a Queue and generates the
        reduced data rows by popping from this queue and yielding the rows one
        by one.
        """
        if name not in self.channels:
            raise RuntimeError(
                f"No reduced data stream named '{name}'. Have {self.channels}"
            )

        new_data = asyncio.Event()
        # Register the event so that the fetching_task can signal new data
        self.new_data_event[name][chan_index].append(new_data)

        queue: asyncio.Queue[bytes | None] = asyncio.Queue()

        @log_exception
        async def fill_queue() -> None:
            try:
                cur_row = 0
                channel = self.channels[name][chan_index]
                while True:
                    for valid, row in zip(
                        channel.valid[cur_row:], channel.data[cur_row:]
                    ):
                        if valid:
                            cur_row += 1
                            await queue.put(row.tobytes())
                        else:
                            break

                    if cur_row >= self.num_frames_expected or self.cancelled.is_set():
                        await queue.put(None)
                        break

                    await new_data.wait()
                    new_data.clear()

            except asyncio.CancelledError:
                logger.debug(f"{name} serving task cancelled")
                await queue.put(None)

        serving_task = asyncio.create_task(fill_queue(), name=f"{name}_serving_task")
        serving_task.add_done_callback(self.serving_tasks.discard)
        self.serving_tasks.add(serving_task)

        while True:
            row = await queue.get()
            if row is None:
                break
            else:
                yield row

        logger.debug(f"get_stream({name}) done")
