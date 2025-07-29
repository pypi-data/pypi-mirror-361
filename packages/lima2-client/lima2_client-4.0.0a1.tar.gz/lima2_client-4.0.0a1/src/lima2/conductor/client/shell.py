#!/usr/bin/env python
#
# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT license. See LICENSE for more info.


"""Lima2 client interactive shell

Given a Conductor running, launch an ipython interactive shell
and suggest some example control/acquisition/processing parameters.
"""

import rich
import typer

app = typer.Typer()


@app.command()
def main(
    conductor_hostname: str = "localhost",
    conductor_port: int = 58712,
) -> None:
    """Start the conductor"""

    from lima2.conductor.client import session
    from lima2.conductor.client.services import acquisition, detector, pipeline

    s = session.init(hostname=conductor_hostname, port=conductor_port)

    if s.connection_state() == session.ConnectionState.CONDUCTOR_OFFLINE:
        raise ValueError(
            f"Conductor at {conductor_hostname}:{conductor_port} seems offline.\n"
            "Run locally with 'lima2-conductor start [TANGO_HOST] [single|round_robin|dynamic] [LIMA2_CONTROL_URL] [LIMA2_RECEIVER1_URL ...]"
        )

    else:
        print("Connected to conductor.\nState: ")
        rich.print(s.system_state())

        params = acquisition.default_params(session=s)

        acq = params["receiver"]

        proc = pipeline.default_params(
            session=s, processing_name="LimaProcessingLegacy"
        )

        acq["acq"]["nb_frames"] = 120
        acq["acq"]["expo_time"] = 10000  # 10ms

        acq["det"]["nb_prefetch_frames"] = 16

        proc["saving"]["enabled"] = False
        proc["saving"]["file_exists_policy"] = "overwrite"

        def run_acquisition(
            nb_frames: int,
            expo_time: float,
            latency_time: float = 0.0,
            trigger_mode: str = "internal",
        ):
            acq["acq"]["trigger_mode"] = trigger_mode
            acq["acq"]["nb_frames"] = nb_frames
            acq["acq"]["expo_time"] = int(expo_time * 1e6)
            acq["acq"]["latency_time"] = int(latency_time * 1e6)

            acquisition.prepare(session=s, control=acq, receiver=acq, processing=proc)
            acquisition.start(session=s)

        user_namespace = {
            "acquisition": acquisition,
            "detector": detector,
            "pipeline": pipeline,
            "s": s,
            "ctl": acq,
            "acq": acq,
            "proc": proc,
            "run_acquisition": run_acquisition,
        }

        from IPython import start_ipython
        from traitlets.config import Config
        from termcolor import colored

        config = Config()

        def bold(x):
            return colored(x, attrs=["bold"])

        # Show defined symbols on ipython banner
        config.TerminalInteractiveShell.banner2 = (
            "\n"
            + colored(
                "=========================\n"
                "| Lima2 Conductor Shell |\n"
                "=========================\n\n",
                "blue",
                attrs=["bold"],
            )
            + f"Defined symbols: {[key for key in user_namespace]}\n"
            "\n"
            + bold("Run an acquisition:\n")
            + "  acquisition.prepare(s, ctl, acq, proc)\n"
            "  acquisition.start(s)\n"
            "or use the helper:\n"
            "  run_acquisition(nb_frames=120, expo_time=0.01, latency_time=1e-4, "
            'trigger_mode="internal")'
            "\n"
            "\n" + bold("Query the state:\n") + "  acquisition.state(s)\n"
            "\n"
            + bold("Find reduced data channels:\n")
            + "  pipeline.reduced_data_channels(s)\n"
            "\n"
            + bold("Fetch reduced data:\n")
            + ' for row in pipeline.reduced_data(s, "frame_idx", 0):\n'
            "      print(row)\n"
            "\n" + bold("Find frame channels:\n") + "  pipeline.frame_channels(s)\n"
            "\n" + bold("Fetch a frame:\n") + '  pipeline.get_frame(s, -1, "frame")\n'
            "\n"
        )

        # Enable autoreload
        config.InteractiveShellApp.extensions = ["autoreload"]
        config.InteractiveShellApp.exec_lines = [r"%autoreload all"]
        config.TerminalInteractiveShell.highlighting_style = "monokai"

        start_ipython(user_ns=user_namespace, config=config)


if __name__ == "__main__":
    app()
