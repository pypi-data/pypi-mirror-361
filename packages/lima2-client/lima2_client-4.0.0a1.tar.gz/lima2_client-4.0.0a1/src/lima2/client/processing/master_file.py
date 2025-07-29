# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT licence. See LICENSE for more info.

"""Master file generation utilities."""

import asyncio
import logging
import os
import time
import traceback
from dataclasses import dataclass
from uuid import UUID

import h5py
import numpy as np
import numpy.typing as npt

from lima2.client.processing.frame import (
    FrameChannel,
    FrameType,
    SavingParams,
)
from lima2.client.tango.processing import FrameInfo
from lima2.client.topology import (
    DynamicDispatch,
    LookupTable,
    RoundRobin,
    SingleReceiver,
    Topology,
)

logger = logging.getLogger(__name__)


@dataclass
class MasterFileDescription:
    """Contains all parameters required to build a master file."""

    num_frames: int
    master_file_path: str
    base_path: str
    filename_prefix: str
    frame_info: FrameInfo
    params: SavingParams


def log_exception(func):
    """Log any exceptions from func and reraise."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(traceback.format_exc())
            raise e

    return wrapper


def configure(
    num_frames: int, channels: dict[str, FrameChannel]
) -> dict[str, MasterFileDescription]:
    """Build a set of MasterFileDescriptions from a set of FrameChannels."""

    mfd: dict[str, MasterFileDescription] = {}
    """Master file descriptions"""

    for name, (source, info, params) in channels.items():
        # Skip non-dense frame sources
        if source.frame_type != FrameType.DENSE:
            logger.info(
                f"Master file not generated for '{name}': not a DENSE frame type"
            )
            continue
        # Skip non-persistent sources
        if params is None:
            logger.info(
                f"Master file not generated for '{name}': no associated saving channel"
            )
            continue
        # Skip source if channel is disabled
        if not params["enabled"]:
            logger.info(
                f"Master file not generated for '{name}': saving disabled in this run"
            )
            continue

        base_path = params["base_path"]
        filename_prefix = params["filename_prefix"]
        file_exists_policy = params["file_exists_policy"]

        master_file_path = f"{base_path}/{filename_prefix}_master.h5"

        if os.path.exists(master_file_path) and file_exists_policy != "overwrite":
            raise RuntimeError(
                f"Master file (channel={source.saving_channel}) exists at {master_file_path} "
                f"but {file_exists_policy=}. Cannot enable master file generation."
            )

        logger.info(
            f"Master file will be generated for source '{name}' at {master_file_path}"
        )

        mfd[name] = MasterFileDescription(
            num_frames=num_frames,
            master_file_path=master_file_path,
            base_path=base_path,
            frame_info=info,
            filename_prefix=filename_prefix,
            params=params,
        )

    return mfd


class MasterFileGenerator:
    def __init__(self, uuid: UUID, topology: Topology):
        self.acq_id = uuid
        self.topology = topology
        self.layout_task: asyncio.Future | None = None
        self.cancel_flag = asyncio.Event()

        self.mfd: dict[str, MasterFileDescription] = {}
        """Master file descriptions"""

    def prepare(
        self,
        num_frames: int,
        frame_channels: dict[str, FrameChannel],
    ):
        self.mfd = configure(num_frames=num_frames, channels=frame_channels)

    def start(self) -> None:
        if self.layout_task is not None:
            raise RuntimeError(
                f"Master file generation for acquisition '{self.acq_id}'"
                "already started"
            )

        loop = asyncio.get_running_loop()
        self.layout_task = loop.run_in_executor(None, self.write_master_files)

    def abort(self) -> None:
        if self.layout_task is not None and not self.layout_task.done():
            logger.info("Aborting master file layout building task")
            self.cancel_flag.set()

    @log_exception
    def write_master_files(self) -> None:
        """For each saved frame channel, write the virtual dataset to the master file."""
        for description in self.mfd.values():
            layout = build_layout(
                num_frames=description.num_frames,
                topology=self.topology,
                frame_info=description.frame_info,
                params=description.params,
                cancel_flag=self.cancel_flag,
            )

            with h5py.File(description.master_file_path, "w") as master_file:
                write_virtual_dataset(
                    file=master_file,
                    nx_entry_name=description.params["nx_entry_name"],
                    nx_instrument_name=description.params["nx_instrument_name"],
                    nx_detector_name=description.params["nx_detector_name"],
                    layout=layout,
                )

                # Wait for the first file to be readable to copy the metadata
                first_file_path = (
                    f"{description.base_path}/{description.filename_prefix}_0_00000.h5"
                )
                retry_count = 0
                while True:
                    if retry_count > 60:
                        raise RuntimeError(
                            f"Unable to copy master file metadata from '{first_file_path}'"
                        )
                    try:
                        first_file = h5py.File(first_file_path, "r")
                        break
                    except FileNotFoundError:
                        logger.debug("First file not created yet. Waiting...")
                        time.sleep(0.5)
                    except OSError:
                        logger.debug("First file is still locked. Waiting...")
                        time.sleep(0.5)
                    retry_count += 1

                write_metadata(master_file=master_file, from_file=first_file)
                logger.info(f"Master file written at {description.master_file_path}")


def build_layout(
    num_frames: int,
    topology: Topology,
    frame_info: FrameInfo,
    params: SavingParams,
    cancel_flag: asyncio.Event,
) -> h5py.VirtualLayout:
    match topology:
        case SingleReceiver():
            layout = build_layout_single(
                num_frames=num_frames,
                info=frame_info,
                params=params,
            )
        case RoundRobin(num_receivers=num_receivers, ordering=_):
            logger.warning(
                "Assuming sequential ordering of receivers "
                "in round robin master file generation"
            )
            layout = build_layout_round_robin(
                num_frames=num_frames,
                info=frame_info,
                params=params,
                num_receivers=num_receivers,
            )
        case DynamicDispatch(num_receivers=num_receivers):
            if topology.lut is None:
                raise RuntimeError(
                    "Lookup table not initialized. "
                    "Cannot build master file for dynamic dispatch."
                )
            layout = build_layout_dynamic(
                num_frames=num_frames,
                info=frame_info,
                params=params,
                lut=topology.lut,
                polling_interval_s=0.1,
                num_receivers=num_receivers,
                cancel_flag=cancel_flag,
            )
        case _:
            raise NotImplementedError

    return layout


def build_layout_single(
    num_frames: int, info: FrameInfo, params: SavingParams
) -> h5py.VirtualLayout:
    """Compute the virtual layout for a single receiver acquisition."""
    return build_layout_round_robin(
        num_frames=num_frames,
        info=info,
        params=params,
        num_receivers=1,
    )


def build_layout_round_robin(
    num_frames: int,
    info: FrameInfo,
    params: SavingParams,
    num_receivers: int,
) -> h5py.VirtualLayout:
    """Compute the virtual layout for a strict round robin acquisition."""

    base_path = params["base_path"]
    filename_prefix = params["filename_prefix"]
    nx_entry_name = params["nx_entry_name"]
    nx_instrument_name = params["nx_instrument_name"]
    nx_detector_name = params["nx_detector_name"]
    nb_frames_per_file = params["nb_frames_per_file"]

    logger.info(f"Generating virtual dataset for files at {base_path}")

    logger.debug(
        f"Creating virtual layout with shape={(num_frames, info.height, info.width)}, "
        f"dtype={info.pixel_type}"
    )
    layout = h5py.VirtualLayout(
        shape=(num_frames, info.height, info.width),
        dtype=info.pixel_type,
    )

    # Frames are dispatched to each receiver in turn.
    # If num_frames is not a multiple of num_receivers, some receivers
    # will get one more frame than the rest.
    nframes_in_rcv = [num_frames // num_receivers] * num_receivers
    for i in range(num_frames % num_receivers):
        nframes_in_rcv[i % num_receivers] += 1

    # From the number of frames dispatched to each receiver,
    # we can calculate the number of files created by each one.
    nfiles_of_rcv = [
        (nframes + nb_frames_per_file - 1) // nb_frames_per_file
        for nframes in nframes_in_rcv
    ]

    for file_idx in range(max(nfiles_of_rcv)):
        for rank, nframes in enumerate(nframes_in_rcv):
            if file_idx >= nfiles_of_rcv[rank]:
                # This receiver saved fewer files because it got fewer frames
                continue

            filepath = f"{base_path}/{filename_prefix}_{rank}_{file_idx:05d}.h5"

            # Actual number of frames in this file
            nframes_in_file = min(
                nframes - file_idx * nb_frames_per_file,
                nb_frames_per_file,
            )

            # Assign the virtual source to the virtual layout using the obtained frame indices
            vsource = h5py.VirtualSource(
                filepath,
                f"{nx_entry_name}/{nx_instrument_name}/{nx_detector_name}/data",
                shape=(nframes_in_file, info.height, info.width),
            )

            offset_rank = rank % num_receivers
            start_idx = offset_rank + file_idx * nb_frames_per_file * num_receivers
            end_idx = start_idx + nframes_in_file * num_receivers
            logger.debug(
                f"Setting vds slice {start_idx}:{end_idx}:{num_receivers} to file {filepath}"
            )
            layout[start_idx:end_idx:num_receivers] = vsource

    return layout


def build_layout_dynamic(
    num_frames: int,
    info: FrameInfo,
    params: SavingParams,
    lut: LookupTable,
    polling_interval_s: float,
    num_receivers: int,
    cancel_flag: asyncio.Event,
) -> h5py.VirtualLayout:
    """Compute the virtual layout in a dynamic dispatch acquisition.

    This procedure uses the provided lookup table to determine where each frame
    is saved. It expects the lookup table to be updated by an external task until
    all frames have been associated with a receiver.
    """

    base_path = params["base_path"]
    filename_prefix = params["filename_prefix"]
    nx_entry_name = params["nx_entry_name"]
    nx_instrument_name = params["nx_instrument_name"]
    nx_detector_name = params["nx_detector_name"]

    logger.info(f"Generating virtual dataset for files at {base_path}")

    logger.debug(
        f"Creating virtual layout with shape={(num_frames, info.height, info.width)}, "
        f"dtype={info.pixel_type}"
    )
    layout = h5py.VirtualLayout(
        shape=(num_frames, info.height, info.width),
        dtype=info.pixel_type,
    )

    file_size = params["nb_frames_per_file"]
    """Number of frames per file"""
    file_index = [0] * num_receivers
    """For each receiver, the next file to consider"""
    num_frames_mapped = [0] * num_receivers
    """Number of frames mapped for each receiver"""

    def map_virtual_source(
        layout: h5py.VirtualLayout,
        indices: npt.NDArray,
        rank: int,
        file_idx: int,
    ):

        filepath = f"{base_path}/{filename_prefix}_{rank}_{file_idx:05d}.h5"
        vsource = h5py.VirtualSource(
            filepath,
            f"{nx_entry_name}/{nx_instrument_name}/{nx_detector_name}/data",
            shape=(indices.size, info.height, info.width),
        )

        logger.debug(f"Mapping {indices=} ({indices.size} frames) to {filepath}")

        # Map !
        layout[indices] = vsource

    receiver_done = [False] * num_receivers

    while not cancel_flag.is_set():
        loop_start = time.perf_counter()

        lut_complete = bool(np.all(lut.valid))

        for i in range(num_receivers):
            if receiver_done[i]:
                continue

            mappable_frames = lut.frame_idx[
                np.logical_and(lut.valid, lut.receiver == i)
            ]

            indices, done = find_frame_indices(
                frame_idx=mappable_frames,
                start_idx=num_frames_mapped[i],
                file_size=file_size,
                allow_partial=lut_complete,
            )

            if indices is not None:
                map_virtual_source(
                    layout=layout,
                    indices=indices,
                    rank=i,
                    file_idx=file_index[i],
                )
                file_index[i] += 1
                num_frames_mapped[i] += indices.size

            if lut_complete and done:
                receiver_done[i] = True

        delta = time.perf_counter() - loop_start
        logger.debug(f"loop time: {delta * 1000:.1f}ms")

        if all(receiver_done):
            break

        if delta > polling_interval_s:
            logger.warning(f"Master file VDS loop took {delta * 1000:.1f}ms")
        delay_s = max(0.0, polling_interval_s - delta)
        logger.debug(f"sleeping for {delay_s * 1000:.1f}ms")
        time.sleep(delay_s)

    return layout


def find_frame_indices(
    frame_idx: npt.NDArray[np.int64],
    start_idx: int,
    file_size: int,
    allow_partial: bool,
) -> tuple[npt.NDArray[np.int64] | None, bool]:
    """
    Find indices of frames stored in the next file.

    - If we have more frames than file_size, return the first
      file_size entries.
    - Else, if we know the table is complete (there are no frame indices
      missing), return the remaining indices.
    - Otherwise, return None to signal that we cannot yet map all frames
      in a file.
    """

    mappable = frame_idx[start_idx:]
    done = False

    if mappable.size >= file_size:
        # Enough frames to fill a file: map `file_size` frames
        indices = mappable[:file_size]

    elif allow_partial:
        # Last file for this receiver:
        # Take all the remaining frames and map them, then mark as done
        logger.debug(f"remaining frames: {mappable.size}")

        if mappable.size > 0:
            # Map the entire remainder
            indices = mappable
        else:
            indices = None

        done = True
    else:
        # Insufficient frames have been processed to map a whole file:
        # Wait for more frames to be processed
        indices = None

    return indices, done


def write_virtual_dataset(
    file: h5py.File,
    nx_entry_name: str,
    nx_instrument_name: str,
    nx_detector_name: str,
    layout: h5py.VirtualLayout,
):
    """Commit a virtual dataset to a master file."""

    data_path = f"{nx_entry_name}/{nx_instrument_name}/{nx_detector_name}/data"
    measurement_path = f"{nx_entry_name}/measurement/data"
    plot_path = f"{nx_entry_name}/{nx_instrument_name}/{nx_detector_name}/plot/data"

    # Create VDS
    dataset = file.create_virtual_dataset(data_path, layout=layout)
    dataset.attrs["interpretation"] = "image"

    # Create links
    file[measurement_path] = file[data_path]
    file[plot_path] = file[data_path]

    logger.debug(f"Virtual dataset written at {file.filename}")


def write_metadata(master_file: h5py.File, from_file: h5py.File) -> None:
    """Add metadata copied from the first file to a master file."""
    print(master_file)
    print(from_file)
    logger.debug(
        f"{master_file.filename}: inheriting metadata from {from_file.filename}"
    )
    copy_metadata(src=from_file, dst=master_file)


def copy_group(src_node: h5py.Group, dst_node: h5py.Group) -> None:
    """Recursively copy items of a group, skipping frame datasets."""

    for attr_key, attr_value in src_node.attrs.items():
        logger.debug(f"{dst_node.name}: copying attribute {attr_key} ({attr_value})")
        dst_node.attrs[attr_key] = attr_value

    for key, value in src_node.items():
        if key == "data" and isinstance(value, h5py.Dataset):
            # Skip frame datasets
            logger.debug(f"Skipping {value.name}")
            continue
        elif isinstance(value, h5py.Group):
            # Conservative group copy
            if key in dst_node:
                grp = dst_node[key]
            else:
                logger.debug(f"Creating group {value.name}")
                grp = dst_node.create_group(name=key)
            copy_group(src_node=value, dst_node=grp)
        else:
            # Plain copy
            logger.debug(f"Copying object {key} into {dst_node.name}")
            src_node.copy(value, dst_node)


def copy_metadata(src: h5py.File, dst: h5py.File) -> None:
    """Copy everything but frame data from one hdf5 file to another."""
    copy_group(src_node=src, dst_node=dst)
