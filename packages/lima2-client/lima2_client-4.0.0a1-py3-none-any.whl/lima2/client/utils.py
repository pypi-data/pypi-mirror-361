# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT license. See LICENSE for more info.

"""Utility functions"""

from typing import Any, Callable, TypeVar

import jsonschema
import numpy as np
import numpy.typing as npt
from jsonschema import validators
from jsonschema.protocols import Validator


DecoratedFunc = TypeVar("DecoratedFunc", bound=Callable[..., Any])


def find_first_gap(array: npt.NDArray[np.int32]) -> int:
    """Find the index of the first element after a gap in a sorted array."""
    gap_idx = np.where(np.diff(array) > 1)[0]

    return gap_idx[0] + 1 if gap_idx.size > 0 else array.size


ValidationError = jsonschema.ValidationError
"""Type alias for `jsonschema.ValidationError`."""


def validate(instance: dict[str, Any], schema: dict[str, Any]) -> None:
    """Lima2 param validation.

    Raises a ValidationError if `instance` fails the schema validation.

    Since JSON schema draft 6, a value is considered an "integer" if its
    fractional part is zero [1]. This means for example that 2.0 is considered
    an integer. Since we don't want floats to pass the validation where ints are
    expected, this function overrides this flexibility with a stricter type check.

    [1] https://json-schema.org/draft-06/json-schema-release-notes
    """

    def is_strict_int(_: Validator, value: Any) -> bool:
        return type(value) is int

    base_validator: type[Validator] = validators.validator_for(schema)
    strict_checker = base_validator.TYPE_CHECKER.redefine("integer", is_strict_int)
    strict_validator = validators.extend(base_validator, type_checker=strict_checker)

    jsonschema.validate(instance, schema, cls=strict_validator)


pixel_type_to_np_dtype = {
    "gray8s": np.int8,
    "gray8": np.uint8,
    "gray16s": np.int16,
    "gray16": np.uint16,
    "gray32s": np.int32,
    "gray32": np.uint32,
    "gray32f": np.float32,
    "gray64f": np.float64,
}
"""Mapping from pixel_enum to numpy type."""


def frame_info_to_shape_dtype(frame_info: dict[str, Any]) -> dict[str, Any]:
    return dict(
        shape=(
            frame_info["nb_channels"],
            frame_info["dimensions"]["y"],
            frame_info["dimensions"]["x"],
        ),
        dtype=pixel_type_to_np_dtype[frame_info["pixel_type"]],
    )
