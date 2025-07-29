# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT licence. See LICENSE for more info.

"""Conductor client exceptions."""


from dataclasses import dataclass


@dataclass
class BadRequest(RuntimeError):
    """Signals a mismatch between client-side and server-side code."""

    method: str | None
    url: str | None
    status: int | None
    text: str | None

    def __str__(self) -> str:
        if self.method is not None:
            method = self.method.upper()
        return f"{method} {self.url} -> {self.status} ({self.text})"


class ConductorError(RuntimeError):
    """A server-side error, usually signals an invalid command or params."""


class ConductorConnectionError(RuntimeError):
    """Raised by all client functions when the conductor can't be reached."""
