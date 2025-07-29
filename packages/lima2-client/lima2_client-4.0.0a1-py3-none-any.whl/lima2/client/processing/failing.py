# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT license. See LICENSE for more info.

"""Failing pipeline subclass."""

import logging

from lima2.client.processing.frame import FrameSource
from lima2.client.processing.pipeline import Pipeline
from lima2.client.processing.reduced_data import ReducedDataSource
from lima2.client.utils import frame_info_to_shape_dtype

logger = logging.getLogger(__name__)


class Failing(Pipeline):
    TANGO_CLASS = "LimaProcessingFailing"

    FRAME_SOURCES: dict[str, FrameSource] = {}
    """Available frame sources."""

    REDUCED_DATA_SOURCES: dict[str, ReducedDataSource] = {}
    """Available reduced data sources."""

    @property
    def channels(self):
        """Return the channel descriptions"""
        return {
            "frame": frame_info_to_shape_dtype(
                {
                    "nb_channels": 1,
                    "dimensions": {"x": 0, "y": 0},
                    "pixel_type": "gray8",
                }
            ),
        }
