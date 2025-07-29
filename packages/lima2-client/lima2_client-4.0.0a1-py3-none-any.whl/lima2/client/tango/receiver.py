# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT licence. See LICENSE for more info.

"""Lima2 receiver tango device.

Specializes the ReceiverDevice protocol for lima2 tango receiver device.

Allows us to add typechecking to all attributes and remote procedure calls.
"""

import asyncio
import json
import logging
import traceback
from typing import Any, Awaitable, Callable, cast
from uuid import UUID

import tango as tg

from lima2.client.progress_counter import SingleCounter
from lima2.client.tango.utils import (
    DeviceError,
    DeviceState,
    TangoDevice,
    handle_tango_errors,
)

logger = logging.getLogger(__name__)


class TangoReceiver(TangoDevice):
    """Wrapper around the raw receiver DeviceProxy.

    Provides type-annotated methods and attributes.
    """

    def __init__(self, url: str):
        self.device = tg.DeviceProxy(url, green_mode=tg.GreenMode.Asyncio)
        self.device.set_timeout_millis(10000)

        self.prev_state = DeviceState.IDLE
        """Last device state value polled in poll_state()."""

        self.state_change_callback: Callable[
            [DeviceState], Awaitable[None]
        ] | None = None
        """Callback registered in on_state_change()."""

        self.state_polling_task = asyncio.create_task(
            self.poll_state(), name=f"{self.name} acq_state polling task"
        )
        """Start polling acq_state."""

    @property
    def name(self) -> str:
        return cast(str, self.device.dev_name())

    @handle_tango_errors
    async def ping(self) -> int:
        return cast(int, await self.device.ping())

    @handle_tango_errors
    async def prepare(
        self, uuid: UUID, acq_params: dict[str, Any], proc_params: dict[str, Any]
    ) -> None:
        logger.debug(f"Passing prepare params to RECEIVER ({self.name})")

        # NOTE(mdu) Workaround for a pytango 10.0.2 bug: calling write_attribute
        # on a device which is offline will not raise a DevFailed exception.
        # To make sure we can catch an error and print a useful message, ping
        # devices before setting the params
        await self.ping()

        await self.device.write_attribute("acq_params", json.dumps(acq_params))
        await self.device.write_attribute("proc_params", json.dumps(proc_params))
        logger.debug(f"Executing prepare on RECEIVER ({self.name})")
        await self.device.Prepare(str(uuid))

    @handle_tango_errors
    async def start(self) -> None:
        await self.device.Start()

    @handle_tango_errors
    async def stop(self) -> None:
        await self.device.Stop()

    @handle_tango_errors
    async def reset(self) -> None:
        await self.device.Reset()

    @handle_tango_errors
    async def acq_state(self) -> DeviceState:
        return DeviceState(await self.device.acq_state)

    @handle_tango_errors
    async def nb_frames_xferred(self) -> SingleCounter:
        return SingleCounter(
            name="nb_frames_xferred",
            value=await self.device.nb_frames_xferred,
            source=self.name,
        )

    @handle_tango_errors
    async def list_pipelines(self) -> list[str]:
        return cast(list[str], await self.device.pipelines)

    @handle_tango_errors
    async def erase_pipeline(self, uuid: str) -> None:
        await self.device.erasePipeline(uuid)

    @handle_tango_errors
    async def last_error(self) -> str:
        return cast(str, await self.device.last_error)

    def fetch_params_schema(self) -> dict[str, Any]:
        """Retrieve 'acq_params' schema for this device from the tango database."""
        tango_db = tg.Database()

        dev_class = tango_db.get_device_info(self.name).class_name

        prop = tango_db.get_class_attribute_property(dev_class, "acq_params")
        # Each attribute property is a StdStringVector with a single value
        try:
            return cast(dict[str, Any], json.loads(prop["acq_params"]["schema"][0]))
        except KeyError as e:
            raise RuntimeError(
                f"Schema for 'acq_params' not found on {dev_class} in tango db"
            ) from e

    def fetch_proc_schema(self, proc_class: str) -> dict[str, Any]:
        """Retrieve 'proc_params' schema for this device from the tango database."""
        tango_db = tg.Database()

        prop = tango_db.get_class_attribute_property(proc_class, "proc_params")
        # Each attribute property is a StdStringVector with a single value
        try:
            schema_json = prop["proc_params"]["schema"][0]
            return cast(dict[str, Any], json.loads(schema_json))
        except KeyError as e:
            raise RuntimeError(
                f"Schema for 'proc_params' not found for processing class '{proc_class}'"
            ) from e

    def on_state_change(
        self, callback: Callable[[DeviceState], Awaitable[None]]
    ) -> None:
        """Register a callback to changes in DeviceState.

        The callback should be an async function which takes the new DeviceState
        value as parameter.
        """
        logger.debug(f"Registering on_state_change callback on {self.name}")
        self.state_change_callback = callback

    async def poll_state(self, interval_s: float = 0.05) -> None:
        """Poll the device's acq_state periodically to notify of changes/disconnects.

        This loop calls the registered state_change_callback on every acq_state change.
        """
        while True:
            await asyncio.sleep(interval_s)

            try:
                new_state = await self.acq_state()
            except DeviceError:
                if self.prev_state is not DeviceState.OFFLINE:
                    self.prev_state = DeviceState.OFFLINE
                    logger.warning(f"Device {self.name} is offline...")
                continue

            if new_state != self.prev_state:
                logger.debug(f"{self.name}: {self.prev_state} -> {new_state}")
                if self.state_change_callback is None:
                    logger.info(
                        f"State change on {self.name} but no callback is registered."
                    )
                else:
                    try:
                        await self.state_change_callback(new_state)
                    except Exception:
                        logger.error(
                            f"Exception raised in receiver {self.name} "
                            f"on_state_change callback:\n"
                            f"{traceback.format_exc()}"
                        )

                self.prev_state = new_state
