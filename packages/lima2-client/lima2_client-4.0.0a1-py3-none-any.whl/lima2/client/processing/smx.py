# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT license. See LICENSE for more info.

"""SMX pipeline subclass."""

import logging

import numpy as np

from lima2.client.processing.frame import (
    FrameSource,
    FrameType,
)
from lima2.client.processing.pipeline import Pipeline
from lima2.client.processing.reduced_data import ScalarDataSource

logger = logging.getLogger(__name__)


PEAK_COUNTER_DTYPE = np.dtype(
    [
        ("frame_idx", "i4"),
        ("recv_idx", "i4"),
        ("nb_peaks", "i4"),
    ]
)


class Smx(Pipeline):
    TANGO_CLASS = "LimaProcessingSmx"

    FRAME_SOURCES = {
        "frame": FrameSource(
            getter_name="getFrame",
            frame_type=FrameType.DENSE,
            saving_channel="saving_dense",
            progress_counter_name="nb_frames_input",
        ),
        "sparse_frame": FrameSource(
            getter_name="getSparseFrame",
            frame_type=FrameType.SMX_SPARSE,
            saving_channel="saving_sparse",
            progress_counter_name="nb_frames_sparse",
        ),
        "acc_corrected": FrameSource(
            getter_name="getAccCorrected",
            frame_type=FrameType.DENSE,
            saving_channel="saving_accumulation_corrected",
            progress_counter_name=None,
        ),
        "acc_peaks": FrameSource(
            getter_name="getAccPeaks",
            frame_type=FrameType.DENSE,
            saving_channel="saving_accumulation_peak",
            progress_counter_name=None,
        ),
    }
    """Available frame sources."""

    REDUCED_DATA_SOURCES = {
        "peak_counter": ScalarDataSource(
            getter_name="popPeakCounters",
            src_dtype=PEAK_COUNTER_DTYPE,
            exposed_cols=["nb_peaks"],
            count=1,
        )
    }
    """Available reduced data sources."""
