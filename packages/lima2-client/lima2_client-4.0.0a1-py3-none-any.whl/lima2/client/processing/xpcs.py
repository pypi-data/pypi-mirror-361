# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT license. See LICENSE for more info.

"""XPCS pipeline subclass."""

import logging

import numpy as np

from lima2.client.processing.frame import (
    FrameSource,
    FrameType,
)
from lima2.client.processing.pipeline import Pipeline
from lima2.client.processing.reduced_data import ScalarDataSource

# Create a logger
logger = logging.getLogger(__name__)

FILL_FACTOR_DTYPE = np.dtype(
    [
        ("frame_idx", "i4"),
        ("recv_idx", "i4"),
        ("fill_factor", "i4"),
    ]
)


class Xpcs(Pipeline):
    TANGO_CLASS = "LimaProcessingXpcs"

    FRAME_SOURCES = {
        "input_frame": FrameSource(
            getter_name="getInputFrame",
            frame_type=FrameType.DENSE,
            saving_channel=None,
            progress_counter_name="nb_frames_input",
        ),
        "frame": FrameSource(
            getter_name="getFrame",
            frame_type=FrameType.DENSE,
            saving_channel="saving_dense",
            progress_counter_name="nb_frames_processed",
        ),
        "sparse_frame": FrameSource(
            getter_name="getSparseFrame",
            frame_type=FrameType.SPARSE,
            saving_channel="saving_sparse",
            progress_counter_name="nb_frames_sparse",
        ),
    }
    """Available frame sources."""

    REDUCED_DATA_SOURCES = {
        "fill_factor": ScalarDataSource(
            getter_name="popFillFactors",
            src_dtype=FILL_FACTOR_DTYPE,
            exposed_cols=["fill_factor"],
            count=1,
        )
    }
    """Available reduced data sources."""
