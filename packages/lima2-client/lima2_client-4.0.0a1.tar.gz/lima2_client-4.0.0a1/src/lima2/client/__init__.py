# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT licence. See LICENSE for more info.

"""Lima2 client package.

Contains the stateful client for the lima2 acquisition system, with
tango as the communication protocol.
"""

from lima2.client.acquisition_system import AcquisitionSystem

__all__ = ["AcquisitionSystem"]
