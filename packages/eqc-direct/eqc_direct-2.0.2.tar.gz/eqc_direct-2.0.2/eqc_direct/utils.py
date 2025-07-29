"""
Utilities for running server sim and client
"""
from dataclasses import dataclass
from typing import List, Tuple, TypedDict

import numpy as np

# levels for precision calc
PREC_MIN_RECOMMENDED_LEVELS = 200
PREC_MAX_LEVELS = 10000


class SystemInfo(TypedDict):
    """Python binding to SystemInfo->VersionOutput proto spec."""

    server_version: str
    fpga_version: str
    device_type: str
    device_id: str


@dataclass
class SysStatus:
    """
    Status codes for system paired with their descriptions.
    """

    IDLE = {"status_code": 0, "status_desc": "IDLE"}
    JOB_RUNNING = {"status_code": 1, "status_desc": "JOB_RUNNING"}
    CALIBRATION = {"status_code": 2, "status_desc": "CALIBRATION"}
    HEALTH_CHECK = {"status_code": 3, "status_desc": "HEALTH_CHECK"}
    HARDWARE_FAILURE = {"status_code": [4, 5], "status_desc": "HARDWARE_FAILURE"}


@dataclass
class LockCheckStatus:
    """
    Statuses codes for checking lock status paired with their descriptions
    """

    AVAILABLE = {"status_code": 0, "status_desc": "Lock available"}
    USER_LOCKED = {
        "status_code": 1,
        "status_desc": "lock_id matches current server lock_id",
    }
    UNAVAILABLE = {
        "status_code": 2,
        "status_desc": "Execution lock is in use by another user",
    }


@dataclass
class LockManageStatus:
    """
    Statuses and descriptions for acquiring and releasing lock
    """

    SUCCESS = {"status_code": 0, "status_desc": "Success"}
    MISMATCH = {
        "status_code": 1,
        "status_desc": "lock_id does not match current device lock_id",
    }
    BUSY = {
        "status_code": 2,
        "status_desc": "Lock currently in use unable to perform operation",
    }


@dataclass
class JobCodes:
    """
    Job codes for errors paired with their descriptions
    """

    NORMAL = {"err_code": 0, "err_desc": "Success"}
    INDEX_OUT_OF_RANGE = {
        "err_code": 1,
        "err_desc": (
            "Index in submitted data is out of range for specified "
            "number of variables"
        ),
    }
    COEF_INDEX_MISMATCH = {
        "err_code": 2,
        "err_desc": (
            "Polynomial indices do not match required length for "
            "specified coefficient length"
        ),
    }
    DEVICE_BUSY = {
        "err_code": 3,
        "err_desc": "Device currently processing other request",
    }
    LOCK_MISMATCH = {
        "err_code": 4,
        "err_desc": "lock_id doesn't match current device lock",
    }
    HARDWARE_FAILURE = {
        "err_code": 5,
        "err_desc": "Device failed during execution",
    }
    INVALID_SUM_CONSTRAINT = {
        "err_code": 6,
        "err_desc": (
            "Sum constraint must be greater than or equal to 1 and "
            "less than or equal to 10000"
        ),
    }
    INVALID_RELAXATION_SCHEDULE = {
        "err_code": 7,
        "err_desc": "Parameter relaxation_schedule must be in set {1,2,3,4}",
    }
    USER_INTERRUPT = {
        "err_code": 8,
        "err_desc": "User sent stop signal before result was returned",
    }
    EXCEEDS_MAX_SIZE = {
        "err_code": 9,
        "err_desc": "Exceeds max problem size for device",
    }
    DECREASING_INDEX = {
        "err_code": 10,
        "err_desc": (
            "One of specified polynomial indices is not specified in "
            "non-decreasing order"
        ),
    }
    INVALID_PRECISION = {
        "err_code": 11,
        "err_desc": "The input precision exceeds maximum allowed precision for device",
    }
    NUM_SAMPLES_POSITIVE = {
        "err_code": 12,
        "err_desc": "Input num_samples must be positive.",
    }
    PRECISION_CONSTRAINT_MISMATCH = {
        "err_code": 13,
        "err_desc": "Sum constraint must be divisible by solution_precision",
    }
    PRECISION_NONNEGATIVE = {
        "err_code": 14,
        "err_desc": "Input solution precision cannot be negative",
    }
    DEGREE_POSITIVE = {
        "err_code": 15,
        "err_desc": "Input degree must be greater than 0",
    }
    NUM_VARIABLES_POSITIVE = {
        "err_code": 16,
        "err_desc": "Input num_variables must be greater than 0",
    }
    NUM_LEVELS_NUM_VARS_MISMATCH = {
        "err_code": 17,
        "err_desc": "Length of `num_levels` input must be equal to num_variables",
    }
    NUM_LEVELS_GT_ONE = {
        "err_code": 18,
        "err_desc": "All elements of input `num_levels` must be greater than 1",
    }
    TOTAL_INTEGER_LEVELS = {
        "err_code": 19,
        "err_desc": "Total number of integer levels from input variables exceeds limit",
    }
    INVALID_MEAN_PHOTON_NUMBER = {
        "err_code": 20,
        "err_desc": "Mean photon number if specified must be in range [0.0000667, 0.0066666]",
    }
    INVALID_QUANTUM_FLUCTUATION_COEFFICIENT = {
        "err_code": 21,
        "err_desc": "Quantum fluctuation coefficient if specified must be in range [1, 100]",
    }


def message_to_dict(grpc_message) -> dict:
    """Convert a gRPC message to a dictionary."""
    result = {}
    for descriptor in grpc_message.DESCRIPTOR.fields:
        field = getattr(grpc_message, descriptor.name)

        if descriptor.type == descriptor.TYPE_MESSAGE:
            # Handle repeated message fields with nested repeated fields
            if descriptor.label == descriptor.LABEL_REPEATED:
                if descriptor.message_type and any(
                    subfield.label == subfield.LABEL_REPEATED
                    for subfield in descriptor.message_type.fields
                ):
                    # If the message contains repeated fields, extract only the lists
                    result[descriptor.name] = (
                        [list(item.values) for item in field] if field else []
                    )
                else:
                    # Standard repeated message field
                    result[descriptor.name] = (
                        [message_to_dict(item) for item in field] if field else []
                    )
            else:
                # Singular message field
                result[descriptor.name] = message_to_dict(field) if field else {}
        else:
            # Handle repeated primitive fields
            if descriptor.label == descriptor.LABEL_REPEATED:
                result[descriptor.name] = list(field) if field else []
            else:
                result[descriptor.name] = field
    return result


def convert_hamiltonian_to_poly_format(
    linear_terms: np.ndarray,
    quadratic_terms: np.ndarray,
) -> Tuple[List[List[int]], List[float]]:
    """
    Converts linear terms and quadratic terms of Hamiltonian to polynomial
    index formatting for Dirac device

    :param linear_terms: the linear terms for the Hamiltonian 1D length n array
    :param quadratic_terms: the quadratic coefficients of the Hamiltonian (n by n)
    :return: a tuple with the following members:

        - **poly_indices**: List[List[int]] - polynomial indices in non-decreasing sparse format
        - **poly_coefficients**: List[float] - polynomial coefficients in sparse format

    .. Sparse matrices are much slower with this implementation convert to dense first
    """
    assert len(linear_terms.shape) == 1, "`linear_terms` input must be 1D"
    try:
        m, n = quadratic_terms.shape  # pylint: disable=C0103
        assert m == n, "`quadratic_terms` must be a square matrix"
    except ValueError as exc:
        raise ValueError("`quadratic_terms` must be 2D") from exc

    assert len(linear_terms) == m, (
        "`linear_terms` must match dimension row and "
        "column dimension of `quadratic_terms`"
    )
    poly_coefficients = []
    poly_indices = []
    # multiplying by 2 here is faster than doing it at each entry in the upper
    # triangular portion
    quadratic_terms = quadratic_terms * 2
    diag_idx = np.diag_indices(m)
    quadratic_terms[diag_idx] /= 2
    for i in range(m):
        # add nonzero linear terms to lists
        if linear_terms[i] != 0:
            poly_indices.append([0, i + 1])
            poly_coefficients.append(linear_terms[i])
        for j in range(m):
            # add quad terms to lists
            if quadratic_terms[i, j] and i <= j:
                poly_coefficients.append(quadratic_terms[i, j])
                poly_indices.append([i + 1, j + 1])
    return poly_indices, poly_coefficients


def get_decimal_places(float_num: float) -> int:
    """
    Helper function which gets the number of decimal places for a float,
    excluding trailing zeros.

    :param float_num: float input for which decimal places will be found
    :return: a non-negative integer representing the number of decimal places
    """
    try:
        # Split the number into integer and fractional parts
        _, fractional_part = str(float_num).split(".")
        # Strip trailing zeros from the fractional part
        fractional_part = fractional_part.rstrip("0")
        decimal_places = len(fractional_part)
    except ValueError:
        # No fractional part means 0 decimal places
        decimal_places = 0
    return decimal_places
