# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT licence. See LICENSE for more info.

"""Lima2 frame helpers."""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable, TypedDict

from lima2.client.devencoded import dense_frame, smx_sparse_frame, sparse_frame
from lima2.client.devencoded.dense_frame import EncodedFrame, Frame
from lima2.client.devencoded.smx_sparse_frame import SmxSparseFrame
from lima2.client.devencoded.sparse_frame import SparseFrame
from lima2.client.tango.processing import FrameInfo


class FrameType(Enum):
    DENSE = auto()
    SPARSE = auto()
    SMX_SPARSE = auto()


decoder_by_type: dict[
    FrameType,
    Callable[
        [EncodedFrame],
        Frame | SparseFrame | SmxSparseFrame,
    ],
] = {
    FrameType.DENSE: dense_frame.decode,
    FrameType.SPARSE: sparse_frame.decode,
    FrameType.SMX_SPARSE: smx_sparse_frame.decode,
}
"""Mapping from frame type to associated decode function"""


@dataclass
class FrameSource:
    """Specifies the name of a getter and a frame type for a given frame source.

    From these two attributes, it is possible to fetch a frame from a processing tango
    device and then decode it.
    """

    getter_name: str
    """Name of the getter method to call on the tango device to fetch the data"""

    frame_type: FrameType
    """Frame type"""

    saving_channel: str | None
    """Name of the associated saving_params object in the proc_params struct.

    Can be None for sources without persistency.
    """

    progress_counter_name: str | None
    """Name of corresponding reading field in the progress_counters.

    Can be None for a frame source without an associated counter.
    """


class SavingParams(TypedDict):
    """Analogue of lima::io::h5::saving_params."""

    base_path: str
    filename_format: str
    filename_prefix: str
    filename_rank: int
    filename_suffix: str
    start_number: int
    file_exists_policy: str
    nb_frames_per_file: int
    nb_frames_per_chunk: int
    compression: str
    nx_entry_name: str
    nx_instrument_name: str
    nx_detector_name: str
    nb_dimensions: str
    include_frame_idx: bool
    enabled: bool


FrameChannel = tuple[FrameSource, FrameInfo, SavingParams | None]
"""
Represents the set of informations required to write a master file
for a particlar frame type.
"""
