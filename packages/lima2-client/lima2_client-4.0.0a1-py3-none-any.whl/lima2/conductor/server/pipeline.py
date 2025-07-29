# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT licence. See LICENSE for more info.

"""Conductor server /pipeline endpoints"""

import logging

import jsonschema_default
import numpy as np
from starlette.requests import Request
from starlette.responses import JSONResponse, StreamingResponse
from starlette.routing import Route

from lima2.client import processing
from lima2.client.acquisition_system import AcquisitionSystem
from lima2.client.topology import FrameLookupError

logger = logging.getLogger(__name__)


async def home(request: Request) -> JSONResponse:
    """
    summary: List of pipeline UUIDs.
    responses:
      200:
        description: OK.
    """
    lima2: AcquisitionSystem = request.state.lima2
    pipelines = await lima2.list_pipelines()

    return JSONResponse([str(uuid) for uuid in pipelines])


async def pipeline_classes(request: Request) -> JSONResponse:
    """
    summary: Lists all pipeline class names.
    responses:
      200:
        description: OK.
    """
    return JSONResponse(list(processing.pipeline_classes.keys()))


async def pipeline_class(request: Request) -> JSONResponse:
    """
    summary: Get the description for a specific pipeline class.
    parameters:
      - in: path
        name: name
        schema:
          type: string
        required: true
        description: name of a processing class
    responses:
      200:
        description: OK.
    """
    class_name = str(request.path_params["name"])

    if class_name not in processing.pipeline_classes:
        raise RuntimeError(f"Invalid pipeline class '{class_name}'")

    pipeline_class = processing.pipeline_classes[class_name]

    lima2: AcquisitionSystem = request.state.lima2
    schema = lima2.receivers[0].fetch_proc_schema(proc_class=class_name)
    defaults = jsonschema_default.create_from(schema)

    return JSONResponse(
        {
            "tango_class": pipeline_class.TANGO_CLASS,
            "frame_sources": list(pipeline_class.FRAME_SOURCES.keys()),
            "reduced_data_sources": list(pipeline_class.REDUCED_DATA_SOURCES.keys()),
            "params_schema": schema,
            "default_params": defaults,
        }
    )


async def pipeline_params_schema(request: Request) -> JSONResponse:
    """
    summary: Get the params schema for a specific pipeline class.
    parameters:
      - in: path
        name: name
        schema:
          type: string
        required: true
        description: name of a processing class
    responses:
      200:
        description: OK.
    """
    class_name = str(request.path_params["name"])

    if class_name not in processing.pipeline_classes:
        raise RuntimeError(f"Invalid pipeline class '{class_name}'")

    lima2: AcquisitionSystem = request.state.lima2
    schema = lima2.receivers[0].fetch_proc_schema(proc_class=class_name)

    return JSONResponse(schema)


async def clear_previous_pipelines(request: Request) -> JSONResponse:
    """
    summary: Erase all pipelines except the current one.
    responses:
      202:
        description: OK.
    """
    lima2: AcquisitionSystem = request.state.lima2
    cleared = await lima2.clear_previous_pipelines()

    return JSONResponse({"cleared": cleared}, status_code=202)


async def pipeline_by_uuid(request: Request) -> JSONResponse:
    """
    summary: Pipeline attributes given its uuid.
    parameters:
      - in: path
        name: uuid
        schema:
          type: string
        required: true
        description: UUID of a pipeline, or "current"
    responses:
      200:
        description: OK.
    """
    lima2: AcquisitionSystem = request.state.lima2
    pipeline = await lima2.get_pipeline(uuid=request.path_params["uuid"])

    return JSONResponse(
        {
            "uuid": str(pipeline.uuid),
            "type": pipeline.TANGO_CLASS,
            "is_finished": pipeline.is_finished(),
            "progress_counters": {
                name: counter.asdict()
                for name, counter in (await pipeline.progress_counters()).items()
            },
            "reduced_data": {
                key: [item.asdict() for item in channel_list]
                for key, channel_list in pipeline.reduced_data_channels().items()
            },
        }
    )


async def pipeline_progress_counters(request: Request) -> JSONResponse:
    """
    summary: Lists all progress counters of a pipeline.
    parameters:
      - in: path
        name: uuid
        schema:
          type: string
        required: true
        description: UUID of a pipeline, or "current"
    responses:
      200:
        description: OK.
    """
    lima2: AcquisitionSystem = request.state.lima2
    pipeline = await lima2.get_pipeline(uuid=request.path_params["uuid"])
    counters = await pipeline.progress_counters()

    return JSONResponse({name: counter.asdict() for name, counter in counters.items()})


async def pipeline_reduced_data_channels(request: Request) -> JSONResponse:
    """
    summary: Lists all available reduced data streams (e.g. roi stats).
    parameters:
      - in: path
        name: uuid
        schema:
          type: string
        required: true
        description: UUID of a pipeline, or "current"
    responses:
      200:
        description: OK.
    """
    lima2: AcquisitionSystem = request.state.lima2
    pipeline = await lima2.get_pipeline(uuid=request.path_params["uuid"])

    return JSONResponse(
        {
            key: [item.asdict() for item in channel_list]
            for key, channel_list in pipeline.reduced_data_channels().items()
        }
    )


async def pipeline_reduced_data_stream(request: Request) -> StreamingResponse:
    """
    summary: Get a specific reduced data stream (e.g. roi stats).
    parameters:
      - in: path
        name: uuid
        schema:
          type: string
        required: true
        description: UUID of a pipeline, or "current"
      - in: path
        name: name
        schema:
          type: string
        required: true
        description: name of the data stream
      - in: path
        name: index
        schema:
          type: integer
        required: true
        description: channel index (e.g. if 3 rois are
                     defined, can be 0, 1 or 2)
    responses:
      200:
        description: OK.
    """
    uuid = request.path_params["uuid"]
    name = str(request.path_params["name"])
    index = int(request.path_params["index"])

    lima2: AcquisitionSystem = request.state.lima2
    pipeline = await lima2.get_pipeline(uuid=uuid)

    stream = pipeline.get_reduced_data(name=name, chan_index=index)

    return StreamingResponse(content=stream, media_type="application/octet-stream")


async def pipeline_frame_channels(request: Request) -> JSONResponse:
    """
    summary: List available frame channels.
    parameters:
      - in: path
        name: uuid
        schema:
          type: string
        required: true
        description: UUID of a pipeline, or "current"
    responses:
      200:
        description: OK.
    """
    uuid = request.path_params["uuid"]

    lima2: AcquisitionSystem = request.state.lima2
    pipeline = await lima2.get_pipeline(uuid=uuid)

    return JSONResponse(
        {
            key: {
                "num_channels": value.num_channels,
                "width": value.width,
                "height": value.height,
                "pixel_type": np.dtype(value.pixel_type).name,
            }
            for key, value in pipeline.frame_infos.items()
        }
    )


async def pipeline_num_available(request: Request) -> JSONResponse:
    """
    summary: Find the number of available contiguous frames for a given source.
    parameters:
      - in: path
        name: uuid
        schema:
          type: string
        required: true
        description: UUID of a pipeline, or "current"
      - in: path
        name: source
        schema:
          type: string
        required: true
        description: frame source name
    responses:
      200:
        description: OK.
      404:
        description: No such frame source.
    """
    uuid = request.path_params["uuid"]
    source = str(request.path_params["source"])

    lima2: AcquisitionSystem = request.state.lima2
    pipeline = await lima2.get_pipeline(uuid)

    return JSONResponse(await pipeline.num_available(source=source))


async def pipeline_frame_lookup(request: Request) -> JSONResponse:
    """
    summary: Find the receiver to ask for a specific frame.
    parameters:
      - in: path
        name: uuid
        schema:
          type: string
        required: true
        description: UUID of a pipeline, or "current"
      - in: path
        name: frame_idx
        schema:
          type: integer
        required: true
        description: frame index
    responses:
      200:
        description: OK.
      404:
        description: Frame not found.
    """
    uuid = request.path_params["uuid"]
    frame_idx = int(request.path_params["frame_idx"])

    lima2: AcquisitionSystem = request.state.lima2
    pipeline = await lima2.get_pipeline(uuid)

    try:
        if frame_idx == -1:
            rcv_url = await pipeline.lookup_last()
        else:
            rcv_url = pipeline.lookup(frame_idx)
    except FrameLookupError as e:
        logger.warning(f"Lookup failed for frame {frame_idx}")
        return JSONResponse(
            {"message": "Frame not found.", "error": repr(e)}, status_code=404
        )

    return JSONResponse(
        {
            "frame_idx": int(frame_idx),
            "receiver_url": rcv_url,
        }
    )


async def pipeline_get_errors(request: Request) -> JSONResponse:
    """
    summary: Get processing error message, if any.
    parameters:
      - in: path
        name: uuid
        schema:
          type: string
        required: true
        description: UUID of a pipeline, or "current"
    responses:
      200:
        description: OK.
    """
    uuid = request.path_params["uuid"]

    lima2: AcquisitionSystem = request.state.lima2
    pipeline = await lima2.get_pipeline(uuid)

    return JSONResponse(pipeline.errors)


routes = [
    Route("/", home, methods=["GET"]),
    Route("/class", pipeline_classes, methods=["GET"]),
    Route("/class/{name:str}", pipeline_class, methods=["GET"]),
    Route("/class/{name:str}/schema", pipeline_params_schema, methods=["GET"]),
    Route("/clear", clear_previous_pipelines, methods=["POST"]),
    Route("/{uuid}", pipeline_by_uuid, methods=["GET"]),
    Route("/{uuid}/errors", pipeline_get_errors, methods=["GET"]),
    Route("/{uuid}/progress_counters", pipeline_progress_counters, methods=["GET"]),
    Route("/{uuid}/reduced_data", pipeline_reduced_data_channels, methods=["GET"]),
    Route(
        "/{uuid}/reduced_data/{name:str}/{index:int}",
        pipeline_reduced_data_stream,
        methods=["GET"],
    ),
    Route("/{uuid}/frames", pipeline_frame_channels, methods=["GET"]),
    Route(
        "/{uuid}/{source:str}/num_available", pipeline_num_available, methods=["GET"]
    ),
    Route("/{uuid}/lookup/{frame_idx}", pipeline_frame_lookup, methods=["GET"]),
]
