# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT licence. See LICENSE for more info.

"""Conductor client processing subpackage.

Contains functionality related to processing pipelines, reduced data handling
and master file generation.

Contains a specific class for each supported processing pipeline.
This file defines a dictionary of all supported pipelines by tango class name.

```
legacy_class = processing.pipeline_classes["LimaProcessingLegacy"]
legacy_pipeline = legacy_class(...)
```
"""

from typing import Awaitable, Callable
from uuid import UUID

from lima2.client.processing.failing import Failing
from lima2.client.processing.legacy import Legacy
from lima2.client.processing.pipeline import Pipeline, PipelineErrorEvent
from lima2.client.processing.smx import Smx
from lima2.client.processing.xpcs import Xpcs
from lima2.client.tango import processing
from lima2.client.tango.processing import TangoProcessing
from lima2.client.topology import Topology

# Dictionary of all pipelines supported by the client
pipeline_classes: dict[str, type[Pipeline]] = {
    "LimaProcessingLegacy": Legacy,
    "LimaProcessingSmx": Smx,
    "LimaProcessingXpcs": Xpcs,
    "LimaProcessingFailing": Failing,
}


def from_uuid(
    uuid: UUID,
    topology: Topology,
    on_finished: Callable[[list[str]], Awaitable[None]],
    on_error: Callable[[PipelineErrorEvent], Awaitable[None]],
) -> Pipeline:
    """Instantiate a Pipeline subclass from the acquisition uuid."""

    devices: list[TangoProcessing] = processing.from_uuid(uuid=uuid)

    class_names = [device.class_name for device in devices]

    if len(set(class_names)) > 1:
        raise NotImplementedError(
            f"Processing {class_names=}, but heterogeneous processing is not supported."
        )

    pipeline_class = pipeline_classes[class_names[0]]  # NOTE Homogeneous processing
    return pipeline_class(
        uuid=uuid,
        devices=devices,
        topology=topology,
        on_finished=on_finished,
        on_error=on_error,
    )
