# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT licence. See LICENSE for more info.

"""Conductor server command-line interface, available as `lima2-conductor`"""

import os
from enum import Enum
from pathlib import Path

import typer
import uvicorn

from lima2.conductor.server import webapp

cli = typer.Typer()


class LogLevel(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@cli.command()
def start(
    tango_host: str,
    topology: str,
    control_url: str,
    receiver_urls: list[str],
    port: int = webapp.DEFAULT_PORT,
    log_level: LogLevel = LogLevel.INFO,
    env_file: Path = Path(".env"),
) -> None:
    """Start the conductor"""
    print(f"Starting Conductor server on port {port}...")

    os.environ["TANGO_HOST"] = tango_host
    os.environ["LIMA2_TOPOLOGY"] = topology
    os.environ["LIMA2_CONTROL_URL"] = control_url
    os.environ["LIMA2_RECEIVER_URLS"] = ",".join(receiver_urls)
    os.environ["LOG_LEVEL"] = log_level

    uvicorn.run(
        app="lima2.conductor.server.main:app",
        host="0.0.0.0",
        port=port,
        env_file=env_file,
    )


@cli.command()
def dev(
    tango_host: str,
    topology: str,
    control_url: str,
    receiver_urls: list[str],
    port: int = webapp.DEFAULT_PORT,
    log_level: LogLevel = LogLevel.DEBUG,
    env_file: Path = Path(".env"),
) -> None:
    """Start the conductor in dev mode (auto-reload)"""
    print(f"Starting Conductor server with auto-reload on port {port}...")

    os.environ["TANGO_HOST"] = tango_host
    os.environ["LIMA2_TOPOLOGY"] = topology
    os.environ["LIMA2_CONTROL_URL"] = control_url
    os.environ["LIMA2_RECEIVER_URLS"] = ",".join(receiver_urls)
    os.environ["LOG_LEVEL"] = log_level
    # See https://docs.python.org/3/library/asyncio-dev.html
    os.environ["PYTHONASYNCIODEBUG"] = "1"

    uvicorn.run(
        app="lima2.conductor.server.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        env_file=env_file,
    )


if __name__ == "__main__":
    cli()
