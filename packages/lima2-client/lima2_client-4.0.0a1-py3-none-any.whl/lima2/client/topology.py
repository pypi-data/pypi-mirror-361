# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT license. See LICENSE for more info.

"""Classes and functions to handle receiver topologies (single, round-robin, etc)."""

import copy
import logging
from abc import ABC, abstractmethod
from typing import Any

import numpy as np
import numpy.typing as npt
from typing_extensions import override

from lima2.client import processing
from lima2.client.progress_counter import ProgressCounter

logger = logging.getLogger(__name__)


class FrameLookupError(RuntimeError):
    """Unable to find the requested frame: likely not acquired yet."""


class Topology(ABC):
    """Receiver topology interface."""

    @abstractmethod
    def lookup(self, frame_idx: int) -> int:
        """Look up a frame by global index.

        Args:
            frame_idx: absolute frame index
        """
        raise NotImplementedError

    @abstractmethod
    def num_contiguous(self, counter: ProgressCounter) -> int:
        """Determine the number of contiguous frames given a progress counter."""
        raise NotImplementedError


class SingleReceiver(Topology):
    """Single receiver topology."""

    @override
    def lookup(self, frame_idx: int) -> int:
        return 0

    @override
    def num_contiguous(self, counter: ProgressCounter) -> int:
        return counter.sum


class RoundRobin(Topology):
    """Multiple-receiver topology where the receiver ordering is fixed throughout the acquisition.

    This class represents a static, strict round robin where the ordering is fixed at prepare-time.
    """

    def __init__(self, num_receivers: int, ordering: list[int]):
        self.num_receivers = num_receivers
        """Number of receivers"""

        self.ordering = ordering
        """Ordering of receivers: list of indices specifying who gets a given frame.

        E.g. for two receivers, ordering = [1, 0] means:
        - receiver 1 gets the first frame
        - receiver 0 gets the second frame
        - receiver 1 gets the third frame
        and so on.
        `ordering[i % num_receivers]` yields the index of the receiver which acquired frame i.
        """

    @override
    def lookup(self, frame_idx: int) -> int:
        return self.ordering[frame_idx % self.num_receivers]

    @override
    def num_contiguous(self, counter: ProgressCounter) -> int:
        # Use the single counters to determine which receiver is most behind
        values = [ctr.value for ctr in counter.counters]
        min_value = min(values)

        return min_value * len(values) + values.index(min_value)


class LookupTable:
    """A lookup table based on a structured numpy array."""

    def __init__(
        self,
        frame_idx: npt.NDArray[np.int64],
        receiver: npt.NDArray[np.int32],
        valid: npt.NDArray[np.bool_],
    ):
        """Build from a numpy array.

        Args:
            frame_idx (ndarray[int64]): global (absolute) frame indices
            receiver (ndarray[int32]): corresponding receiver index for each frame
            valid (ndarray[bool]): whether rows in the above arrays are valid yet

        """
        self.frame_idx = frame_idx
        self.receiver = receiver
        self.valid = valid

    def whereis(self, frame_idx: int) -> int:
        """Determine the receiver that received a given frame."""
        rcv_idx = self.receiver[
            np.logical_and(self.valid, (self.frame_idx == frame_idx))
        ]
        if rcv_idx.size == 0:
            raise FrameLookupError(f"Requested frame {frame_idx} has not been acquired")
        elif rcv_idx.size > 1:
            logger.warning(
                f"Requested frame {frame_idx} is available from more than one device..."
            )
        return int(rcv_idx[0])

    def whereis_last(self) -> int:
        """Returns a the receiver index for the latest frame acquired."""
        valid_fidx = self.frame_idx[self.valid]
        if valid_fidx.size == 0:
            raise FrameLookupError(
                "Cannot find last frame: lookup table has no entries yet"
            )
        else:
            latest_frame_idx = valid_fidx.max()
            return self.whereis(latest_frame_idx)

    def has(self, frame_idx: int) -> bool:
        rcv_idx = self.receiver[np.logical_and(self.valid, self.frame_idx == frame_idx)]
        return bool(rcv_idx.size > 0)


class DynamicDispatch(Topology):
    """A multi-receiver topology where the frame dispatching is unpredictable.

    For instance, when the detector has an internal mechanism for load-balancing across receivers,
    there is no simple way to map a frame index to a receiver. In such cases, a lookup table
    generated at runtime is used to determine where any given frame is located.
    """

    def __init__(self, num_receivers: int):
        self.num_receivers = num_receivers
        self.lut: LookupTable | None = None

    def set_lut(self, lut: LookupTable) -> None:
        self.lut = lut

    def lookup_last(self) -> int:
        """Find the index of the latest frame using the dynamic lut"""
        if self.lut is None:
            # Can only happen if pipeline did not call set_lut()
            raise RuntimeError("Cannot do a dynamic frame lookup without a lut")

        return self.lut.whereis_last()

    @override
    def lookup(self, frame_idx: int) -> int:
        """Find a frame using the dynamic lut."""

        if self.lut is None:
            # Can only happen if pipeline did not call set_lut()
            raise RuntimeError("Cannot do a dynamic frame lookup without a lut")

        rcv_idx = self.lut.whereis(frame_idx=frame_idx)

        return rcv_idx

    @override
    def num_contiguous(self, counter: ProgressCounter) -> int:
        raise NotImplementedError


def distribute_acq(
    ctl_params: dict[str, Any],
    acq_params: dict[str, Any],
    proc_params: dict[str, Any],
    num_receivers: int,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    """Reinterpret params for a distributed acquisition assuming homoegeneous processing.

    Given the number of receivers, return the appropriate set of acquisition and processing params
    for each receiver.

    Does not modify the input dictionaries.

    Returns:
        Tuple (ctl_params, list[acq_params], list[proc_params]) adjusted for
        homogeneous acquisition.

    Example:
        ```
        ctl, acq, proc = topology.distribute_acq(ctl, acq, proc, 16)
        detector.prepare_acq(ctl, acq, proc)
        ```
    """

    # Clone params
    ctl = copy.deepcopy(ctl_params)
    acq = [copy.deepcopy(acq_params) for _ in range(num_receivers)]
    proc = [copy.deepcopy(proc_params) for _ in range(num_receivers)]

    for i in range(num_receivers):
        # Assign unique filename rank per receiver
        processing_class = processing.pipeline_classes[proc_params["class_name"]]
        for source in processing_class.FRAME_SOURCES.values():
            if source.saving_channel is not None:
                proc[i][source.saving_channel]["filename_rank"] = i

        # Idem for detector RAW saving params
        if "saving" in acq[i]:
            acq[i]["saving"]["filename_rank"] = i

    return ctl, acq, proc
