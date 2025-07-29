"""Conductor client /detector requests."""

from typing import Any, cast

from lima2.conductor.client.session import ConductorSession


def info(session: ConductorSession) -> dict[str, Any]:
    """Retrieve the detector info dictionary."""
    return cast(dict[str, Any], session.get("/detector/info").json())


def status(session: ConductorSession) -> dict[str, Any]:
    """Retrieve the detector status dictionary."""
    return cast(dict[str, Any], session.get("/detector/status").json())


def capabilities(session: ConductorSession) -> dict[str, Any]:
    """Retrieve the detector capabilities dictionary."""
    return cast(dict[str, Any], session.get("/detector/capabilities").json())
