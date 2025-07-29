# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT licence. See LICENSE for more info.

"""Conductor client /pipelines requests."""

import logging
from typing import Any, Iterator, cast
from uuid import UUID

import numpy as np
import numpy.typing as npt
import tango as tg

from lima2.client import processing
from lima2.client.devencoded.dense_frame import Frame
from lima2.client.devencoded.smx_sparse_frame import SmxSparseFrame
from lima2.client.devencoded.sparse_frame import SparseFrame
from lima2.client.processing.frame import decoder_by_type
from lima2.client.processing.reduced_data import ReducedDataInfo
from lima2.client.progress_counter import ProgressCounter
from lima2.client.tango.processing import FrameInfo
from lima2.conductor.client.exceptions import BadRequest
from lima2.conductor.client.session import ConductorSession

logger = logging.getLogger(__name__)


def classes(
    session: ConductorSession,
) -> list[str]:
    return cast(list[str], session.get("/pipeline/class").json())


def default_params(session: ConductorSession, processing_name: str) -> dict[str, Any]:
    json = session.get(f"/pipeline/class/{processing_name}").json()
    return cast(dict[str, Any], json["default_params"])


def params_schema(session: ConductorSession, processing_name: str) -> dict[str, Any]:
    """Returns the JSON schema for a given pipeline's params."""
    json = session.get(f"/pipeline/class/{processing_name}/schema").json()
    return cast(dict[str, Any], json)


def uuids(
    session: ConductorSession,
) -> list[UUID]:
    return [UUID(uuid_str) for uuid_str in session.get("/pipeline/").json()]


def current_pipeline(
    session: ConductorSession,
) -> UUID:
    res = session.get("/pipeline/current")
    return UUID(res.json()["uuid"])


def pipeline(session: ConductorSession, uuid: UUID | str) -> dict[str, Any]:
    return cast(dict[str, Any], session.get(f"/pipeline/{str(uuid)}").json())


def errors(session: ConductorSession, uuid: str = "current") -> list[str]:
    """Get processing error messages, if any."""
    return cast(list[str], session.get(f"/pipeline/{uuid}/errors").json())


def progress_counters(
    session: ConductorSession, uuid: str = "current"
) -> dict[str, ProgressCounter]:
    """Get current progress counters for a given pipeline."""
    json = session.get(f"/pipeline/{uuid}/progress_counters").json()
    return {key: ProgressCounter.fromdict(value) for key, value in json.items()}


def clear_previous_pipelines(session: ConductorSession) -> list[str]:
    res = session.post("/pipeline/clear")
    return cast(list[str], res.json()["cleared"])


def reduced_data_channels(
    session: ConductorSession, uuid: str = "current"
) -> dict[str, list[ReducedDataInfo]]:
    json = session.get(f"/pipeline/{uuid}/reduced_data").json()
    return {
        key: [ReducedDataInfo.fromdict(item) for item in channel_list]
        for key, channel_list in json.items()
    }


def frame_channels(
    session: ConductorSession, uuid: str = "current"
) -> dict[str, FrameInfo]:
    json = session.get(f"/pipeline/{uuid}/frames").json()
    return {
        key: FrameInfo(
            num_channels=value["num_channels"],
            width=value["width"],
            height=value["height"],
            pixel_type=np.dtype(value["pixel_type"]),
        )
        for key, value in json.items()
    }


def reduced_data(
    session: ConductorSession, name: str, chan_index: int, uuid: str = "current"
) -> Iterator[npt.NDArray]:
    dtype = reduced_data_channels(session=session, uuid=uuid)[name][chan_index].dtype

    res = session.get(f"/pipeline/{uuid}/reduced_data/{name}/{chan_index}", stream=True)
    for i, chunk in enumerate(res.iter_content(chunk_size=None)):
        if i % 100 == 0:
            logger.debug(f"Decoding {name} for frame {i}")
        yield np.frombuffer(chunk, dtype=dtype)


def num_available(
    session: ConductorSession, source_name: str, uuid: str = "current"
) -> int:
    """Get the number of frames of a given source."""
    return cast(
        int, session.get(f"/pipeline/{uuid}/{source_name}/num_available").json()
    )


def lookup(
    session: ConductorSession, frame_idx: int, uuid: str = "current"
) -> tuple[int, str]:
    try:
        json = session.get(f"/pipeline/{uuid}/lookup/{frame_idx}").json()
    except BadRequest as e:
        raise LookupError(f"Failed to lookup frame {frame_idx}: {e}")

    return (json["frame_idx"], json["receiver_url"])


def get_frame(
    session: ConductorSession, frame_idx: int, source: str, uuid: str = "current"
) -> Frame | SparseFrame | SmxSparseFrame:
    fidx, rcv_url = lookup(session=session, frame_idx=frame_idx, uuid=uuid)

    pipeline_type = pipeline(session=session, uuid=uuid)["type"]
    pipeline_class = processing.pipeline_classes[pipeline_type]

    try:
        frame_source = pipeline_class.FRAME_SOURCES[source]
    except KeyError:
        raise ValueError(
            f"Invalid source name {source}. "
            f"Available ones are: {list(pipeline_class.FRAME_SOURCES.keys())}"
        )

    device = tg.DeviceProxy(rcv_url)

    getter = getattr(device, frame_source.getter_name)

    try:
        raw_data: tuple[str, bytes] = getter(frame_idx)
    except tg.DevFailed as e:
        logger.error(
            f"Failed to get {source} {frame_idx} (resolved to {fidx} on {device.dev_name()})"
        )
        raise RuntimeError(f"Unable to get frame {fidx} from {device.dev_name()}:\n{e}")

    decoder = decoder_by_type[frame_source.frame_type]

    frame = decoder(raw_data)

    return frame
