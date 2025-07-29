# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT licence. See LICENSE for more info.

"""Conductor client /acquisition requests."""


from typing import Any, cast
from uuid import UUID

from lima2.client.progress_counter import ProgressCounter, SingleCounter
from lima2.client.state import RunState
from lima2.conductor.client.session import ConductorSession


def prepare(
    session: ConductorSession,
    control: dict[str, Any],
    receiver: dict[str, Any],
    processing: dict[str, Any],
) -> UUID:
    """Prepare for a new acquisition given control, receiver and processing params."""
    json = session.post(
        "/acquisition/prepare",
        json={
            "control": control,
            "receiver": receiver,
            "processing": processing,
        },
    ).json()
    return UUID(json["uuid"])


def start(session: ConductorSession) -> RunState:
    """Start the currently prepared acquisition."""
    return RunState(session.post("/acquisition/start").json())


def stop(session: ConductorSession) -> RunState:
    """Stop the currently running acquisition."""
    return RunState(session.post("/acquisition/stop").json())


def trigger(session: ConductorSession) -> RunState:
    """Trigger the detector in the currently running acquisition.

    Only useful in software-triggered acquisitions.
    """
    return RunState(session.post("/acquisition/trigger").json())


def reset(session: ConductorSession) -> RunState:
    """Call reset() on the Lima2 devices to attempt recovery from a FAULT state."""
    return RunState(session.post("/acquisition/reset").json())


def state(session: ConductorSession) -> RunState:
    """Get the acquisition system's current RunState."""
    return RunState(session.get("/acquisition/state").json())


def default_params(session: ConductorSession) -> dict[str, Any]:
    """Get default acquisition parameters."""
    return cast(dict[str, Any], session.get("/acquisition/default_params").json())


def params_schema(session: ConductorSession) -> dict[str, Any]:
    """Get the schema for acquisition parameters."""
    return cast(dict[str, Any], session.get("/acquisition/params_schema").json())


def nb_frames_acquired(session: ConductorSession) -> SingleCounter:
    """Get the number of frames acquired in the current acquisition."""
    json_dict = session.get("/acquisition/nb_frames_acquired").json()
    return SingleCounter.fromdict(json_dict)


def nb_frames_xferred(session: ConductorSession) -> ProgressCounter:
    """Get the number of frames transferred in the current acquisition."""
    json_dict = session.get("/acquisition/nb_frames_xferred").json()
    return ProgressCounter.fromdict(json_dict)


def errors(session: ConductorSession) -> list[str]:
    """Get all error messages for the current acquisition.

    Can be used in case of failure during the acquisition to report
    the causes.
    """
    return cast(list[str], session.get("/acquisition/errors").json())
