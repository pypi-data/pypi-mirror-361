# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT licence. See LICENSE for more info.

"""Conductor client session."""

from enum import Enum, auto
from typing import Any, cast

import requests

from lima2.client.state import State
from lima2.conductor.client.exceptions import (
    BadRequest,
    ConductorConnectionError,
    ConductorError,
)


class ConnectionState(Enum):
    ONLINE = auto()
    CONDUCTOR_OFFLINE = auto()
    DEVICES_OFFLINE = auto()


class ConductorSession:
    def __init__(self, url: str) -> None:
        self.session = requests.Session()
        self.base_url = url

    def get(self, endpoint: str, *args, **kwargs) -> requests.Response:
        try:
            res = self.session.get(f"{self.base_url}{endpoint}", *args, **kwargs)
        except requests.ConnectionError as e:
            raise ConductorConnectionError(
                f"Conductor server at {self.base_url} is unreachable"
            ) from e

        if res.status_code == 200:
            return res
        elif res.status_code == 500:
            raise ConductorError(f"Conductor returned 500: '{res.json()['error']}'")
        else:
            raise BadRequest(
                method=res.request.method,
                url=res.request.url,
                status=res.status_code,
                text=res.text,
            )

    def post(self, endpoint: str, *args, **kwargs) -> requests.Response:
        try:
            res = self.session.post(f"{self.base_url}{endpoint}", *args, **kwargs)
        except requests.ConnectionError as e:
            raise ConductorConnectionError(
                f"Conductor server at {self.base_url} is unreachable"
            ) from e

        if res.status_code == 202:
            return res
        elif res.status_code == 500:
            raise ConductorError(res.json()["error"])
        else:
            raise BadRequest(
                method=res.request.method,
                url=res.request.url,
                status=res.status_code,
                text=res.text,
            )

    def system_state(self) -> dict[str, Any]:
        return cast(dict[str, Any], self.get("/state").json())

    def conductor_state(self) -> State:
        return State[self.system_state()["state"]]

    def connection_state(self) -> ConnectionState:
        try:
            cu_state = self.conductor_state()
        except ConductorConnectionError:
            return ConnectionState.CONDUCTOR_OFFLINE

        if cu_state == State.DISCONNECTED:
            return ConnectionState.DEVICES_OFFLINE

        return ConnectionState.ONLINE


def init(hostname: str, port: int = 58712) -> ConductorSession:
    return ConductorSession(url=f"http://{hostname}:{port}")
