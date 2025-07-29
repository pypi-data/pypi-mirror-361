# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT license. See LICENSE for more info.

"""Legacy pipeline subclass."""

import logging

from lima2.client.processing.frame import (
    FrameSource,
    FrameType,
)
from lima2.client.processing.pipeline import Pipeline
from lima2.client.processing.reduced_data import ReducedDataSource

# Create a logger
logger = logging.getLogger(__name__)


class Legacy(Pipeline):
    TANGO_CLASS = "LimaProcessingLegacy"

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
            saving_channel="saving",
            progress_counter_name="nb_frames_processed",
        ),
    }
    """Available frame sources."""

    REDUCED_DATA_SOURCES: dict[str, ReducedDataSource] = {}
    """Available static reduced data sources."""
