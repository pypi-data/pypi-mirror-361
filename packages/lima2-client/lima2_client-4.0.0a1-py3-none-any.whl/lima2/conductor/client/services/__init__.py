# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT licence. See LICENSE for more info.

"""Conductor client-side service API.

This submodule is a thin wrapper around requests to the conductor server.
Its only purpose is to expose endpoints of the conductor server as python
functions with slightly richer parameter and return types.

It is used in the higher-level object-oriented API defined in the
lima2.conductor.client module.

Anywhere communication with the conductor is performed, this submodule's
functions should be used instead of straight HTTP requests.

Example usage:
```
from lima2.conductor.client import session
from lima2.conductor.client.services import acquisition, detector, pipeline

s = session.init(hostname="localhost", port=58712)
print(s.connection_state())

acq_params = acquisition.default_params(s)
proc_params = pipeline.default_params(s, "LimaProcessingLegacy")

acquisition.prepare(s, acq_params["control"], acq_params["receiver"], proc_params)
acquisition.start(s)
print(pipeline.progress_counters(s))
```
"""
