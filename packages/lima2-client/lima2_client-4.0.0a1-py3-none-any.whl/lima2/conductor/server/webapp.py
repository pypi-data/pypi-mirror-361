# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT licence. See LICENSE for more info.

"""Conductor server entrypoint.

This module defines the create_app function, used by uvicorn to instantiate
our Starlette app.

Here we also define endpoints located at the root (/).
"""

import contextlib
import logging
from typing import AsyncIterator, TypedDict

from starlette.applications import Starlette
from starlette.config import environ
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Mount, Route
from starlette.schemas import SchemaGenerator

from lima2.client.acquisition_system import AcquisitionSystem
from lima2.conductor.server import acquisition, detector, pipeline

logger = logging.getLogger(__name__)

DEFAULT_PORT = 58712
"""Webservice default port"""


ConductorState = TypedDict("ConductorState", {"lima2": AcquisitionSystem})


@contextlib.asynccontextmanager
async def lifespan(app: Starlette) -> AsyncIterator[ConductorState]:
    """Lifespan generator.

    Makes contextual objects (state, ...) accessible in handlers as `request.state.*`.
    """

    # Can run concurrent tasks here
    # async def side_task():
    #     while True:
    #         logger.info("side_task!")
    #         await asyncio.sleep(0.5)
    #
    # asyncio.create_task(side_task())

    lima2: AcquisitionSystem = app.state.lima2

    yield {
        "lima2": lima2,
    }

    logger.info("Bye bye")


async def homepage(request: Request) -> JSONResponse:
    """
    summary: Says hi :)
    responses:
      200:
        description: OK
    """

    lima2: AcquisitionSystem = request.state.lima2
    state = await lima2.state()

    devices = [lima2.control, *lima2.receivers]
    dev_states = await lima2.device_states()

    return JSONResponse(
        {"hello": "lima2 :)", "state": state.name}
        | {"devices": {dev.name: state.name for dev, state in zip(devices, dev_states)}}
    )


schemas = SchemaGenerator(
    {"openapi": "3.0.0", "info": {"title": "Conductor API", "version": "0.1"}}
)


async def openapi_schema(request: Request) -> Response:
    return schemas.OpenAPIResponse(request=request)


async def system_state(request: Request) -> JSONResponse:
    """
    summary: Returns the system state.
    responses:
      200:
        description: OK
    """
    lima2: AcquisitionSystem = request.state.lima2
    state = await lima2.state()
    dev_states = await lima2.device_states()
    devices = [lima2.control, *lima2.receivers]
    return JSONResponse(
        {"state": state.name}
        | {"runstate": lima2.runstate.name}
        | {"devices": {dev.name: state.name for dev, state in zip(devices, dev_states)}}
    )


async def exception_handler(request: Request, exception: Exception) -> JSONResponse:
    """Handler for generic exceptions that occur in handler logic.

    If debug=True in the Starlette constructor, this handler is replaced to print out the
    full trace on the client side.
    """
    return JSONResponse(
        status_code=500,
        content={"error": repr(exception)},
    )


def create_app(
    lima2: AcquisitionSystem,
) -> Starlette:
    """Build the web app.

    Returns the webapp instance, with Lima2 context assigned to app's state.
    """

    debug = True if environ.get("DEBUG") == "TRUE" else False
    if debug:
        logger.info("Creating webapp in debug mode")

    app = Starlette(
        routes=[
            Route("/", homepage, methods=["GET"]),
            Route(
                "/schema",
                endpoint=openapi_schema,
                include_in_schema=False,
                methods=["GET"],
            ),
            # Mount("/benchmark", routes=benchmark.routes),
            Mount("/acquisition", routes=acquisition.routes),
            Route("/state", system_state, methods=["GET"]),
            Mount("/detector", routes=detector.routes),
            Mount("/pipeline", routes=pipeline.routes),
        ],
        debug=debug,
        lifespan=lifespan,
        exception_handlers={500: exception_handler},
    )

    # Pass the AcquisitionSystem instance to the shared app state
    # This is necessary for handlers to be able to use the object.
    app.state.lima2 = lima2

    return app
