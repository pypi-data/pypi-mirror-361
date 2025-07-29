"""
:class:`.EqcClient` contains all gRPC calls to solve problems and monitor system
"""
import json
import logging
import time
from typing import List, Optional, TypedDict, Union
import warnings

import grpc
from grpc._channel import _InactiveRpcError
import numpy as np
import numpy.typing as np_typing

import eqc_direct
from eqc_direct import eqc_pb2, eqc_pb2_grpc
from eqc_direct.utils import SysStatus, SystemInfo, get_decimal_places, message_to_dict

DIRAC_FLOAT_BITS = 32


class InactiveRpcError(Exception):
    """Custom exception wrapper around grpc._channel._InactiveRpcError."""


class SumConstrainedResult(TypedDict):
    """
    Sum-constrained results object. Will not contain energy or solution if err_code is
    not 0. Contains nonempty distilled entries when solution_precision is not 0 or None.

    :param err_code: the error code for a given job. Full list of :code:`err_code`
        values can be found :class:`eqc_direct.utils.JobCodes`
    :param err_desc: the error description for a given job submission. Full list of
        :code:`err_desc` values can be found  in :class:`eqc_direct.utils.JobCodes`
    :param preprocessing_time: data validation and time to re-format input data for
        running on the device in seconds
    :param runtime: sampling time in seconds for each solve on Dirac hardware
    :param energy: list of energies for best solution found (float32 precision) for
        each sample from Dirac hardware
    :param solution: a list of vectors representing the lowest energy solution
        (float32 precision) for each sample from Dirac hardware
    :param postprocessing_time: runtime for auxilary computations that occur
        besides sampling during each sample routine from Dirac hardware including
        intermediate energy calculations, objective function adjustments, and
        distillation of solutions
    :param distilled_energy: list of energies for distilled solution for input polynomial
        (float32 precision) for each sample from Dirac hardware
    :param distilled_solution: a vector representing the solution after
        the distillation procedure is applied to the original solution
        derived from the hardware. (float32 precision)
    :param calibration_time: calibration time is unrelated to execution of the
        individual sampling for the optimization. This time is from system level
        interruptions from calibrations that happen at regular intervals to maintain
        system performance.

    .. note::
      * solutions are length `num_variables` vectors of non-negative float that sum to
        `sum_constraint`
      * distilled solutions, when present, are length `num_variables` vectors of
        non-negative float with precision `solution_precision` that sum to
        `sum_constraint`
    """

    err_code: int
    err_desc: str
    num_samples: int
    num_variables: int
    preprocessing_time: float
    runtime: List[float]
    postprocessing_time: List[float]
    energy: List[float]
    solution: List[List[float]]
    distilled_energy: List[float]
    distilled_solution: List[List[float]]
    calibration_time: float


class IntegerResult(TypedDict):
    """
    Integer solver results object. Will not contain energy or solution if err_code is not
    0.

    :param err_code: the error code for a given job. Full list of :code:`err_code`
        values can be found :class:`eqc_direct.utils.JobCodes`
    :param err_desc: the error description for a given job submission. Full list of
        :code:`err_desc` values can be found  in :class:`eqc_direct.utils.JobCodes`
    :param preprocessing_time: data validation and time to re-format input data for
        running on the device in seconds
    :param runtime: sampling time in seconds for each solve on Dirac hardware
    :param postprocessing_time: runtime for auxilary computations that occur
        besides sampling during each sample routine from Dirac hardware including
        intermediate energy calculations and objective function adjustments
    :param energy: list of energies of best solution found for each sample from Dirac hardware
    :param solution: list of vectors representing the lowest energy solution found by the device
        for each sample from Dirac hardware
    :param calibration_time: calibration time is unrelated to execution of the individual
        sampling for the optimization but it will occassionally interrupt execution to
        run calibration to maintain the system in order to provide transparency for total
        where time was spent solving a specific problem this value is provided


    .. note::
      * solutions are length `num_variables` vectors of non-negative bounded above
        inclusively by `num_levels`-1.
    """

    err_code: int
    err_desc: str
    num_samples: int
    num_variables: int
    preprocessing_time: List[float]
    runtime: List[float]
    postprocessing_time: List[float]
    energy: List[float]
    solution: List[List[float]]


class EqcClient:
    """
    Client interface to communicate with EQC device.

    :param ip_address: The IP address of the EQC device
    :param port: The port over which the gRPC server is communicating on the EQC device

    .. note::

       :code:`lock_id` is used by a variety of class functions.
       It is set to an empty string by default since default for device server
       :code:`lock_id` is also an empty string. This allows for single user
       processing without having to acquire a device lock.

    .. .. admonition::
       All GRPC calls follow a specific pattern:
       1. Fill in data to be sent in message stub
       2. Send data using stub service method
       3. Parse response
    """

    def __init__(
        self,
        ip_address: str = "",
        port: str = "",
        cert_file: Optional[str] = None,
    ):
        if not ip_address:
            ip_address = eqc_direct.DEVICE_IP_ADDRESS_DEFAULT

        self._ip_address = ip_address

        if not port:
            port = eqc_direct.DEVICE_PORT_DEFAULT

        self._port = port

        max_data_size = 512 * 1024 * 1024
        options = [
            ("grpc.max_send_message_length", max_data_size),
            ("grpc.max_receive_message_length", max_data_size),
            (
                "grpc.service_config",
                json.dumps(
                    {
                        "methodConfig": [
                            {
                                "name": [{"service": "eqc.EqcService"}],
                                "retryPolicy": {
                                    "maxAttempts": 5,
                                    "initialBackoff": "0.2s",
                                    "maxBackoff": "10s",
                                    "backoffMultiplier": 2.5,
                                    "retryableStatusCodes": ["UNAVAILABLE"],
                                },
                            }
                        ]
                    }
                ),
            ),
        ]

        if cert_file:
            # read in certs
            with open(cert_file, "rb") as f:
                ca_cert = f.read()

            channel_credentials = grpc.ssl_channel_credentials(ca_cert)
            self.channel = grpc.secure_channel(
                self.ip_add_port, channel_credentials, options=options
            )
        else:
            self.channel = grpc.insecure_channel(self.ip_add_port, options=options)

        self.eqc_stub = eqc_pb2_grpc.EqcServiceStub(self.channel)

    @property
    def ip_address(self) -> str:
        """Return configured IP address."""
        return self._ip_address

    @property
    def port(self) -> str:
        """Return configured IP port."""
        return self._port

    @property
    def ip_add_port(self) -> str:
        """Return configured IP address + port, concatenated with a colon."""
        return self.ip_address + ":" + self.port

    def submit_integer_job(
        self,
        poly_coefficients: Union[List[float], np_typing.NDArray[np.float32]],
        poly_indices: Union[List[List[int]], np_typing.NDArray[np.uint32]],
        num_levels: Union[int, List[int], np_typing.NDArray[np.uint16]],
        num_variables: Optional[int] = None,
        num_samples: int = 1,
        lock_id: str = "",
        relaxation_schedule: int = 1,
        mean_photon_number: Optional[float] = None,
        quantum_fluctuation_coefficient: Optional[int] = None,
    ) -> dict:
        """
        Submits a polynomial to be minimized by Dirac, with solutions restricted to integers
        between 0 and :math:`L - 1`, where :math:`L` is the value in :code:`num_levels` for each
        variable.

        :param poly_coefficients:
            Coefficient values for the polynomial to be minimized.
            Inputs should be precision float32 or less, as higher precision will be truncated.
        :param poly_indices:
            Index sets corresponding to the variables for each coefficient in the polynomial.
        :param num_levels:
            Specifies the number of discrete values (levels) each variable can take.
            A value of 2 means a variable can be {0, 1}, and in general, if :math:`L_i` is
            specified for variable :math:`i`, then its domain is :math:`\{0, 1, ..., L_i - 1\}`.

            .. math::
                \\sum_{i=1}^{n} L_i \\leq 954

        :param num_variables:
            Optional, specifies the number of variables in the polynomial. Must be greater than or
            equal to the maximum index appearing in :code:`poly_indices`.
        :param num_samples:
            The number of samples (independent solutions) to generate from the device.
        :param lock_id:
            A UUID to coordinate multi-user access to the device.
        :param relaxation_schedule:
            An integer from the set {1, 2, 3, 4} indicating the type of analog relaxation schedule.
            Higher values reduce the variability in analog spin values, increasing the probability
            of reaching lower-energy solutions.
        :param mean_photon_number:
            Optional, overrides the default photon number associated with the selected
            :code:`relaxation_schedule`. This sets the average number of photons present in a
            given quantum state.
        :param quantum_fluctuation_coefficient:
            Optional, overrides the default value from :code:`relaxation_schedule`. Specifies the
            number of photons (:math:`N`) in each feedback loop, which determines
            the shot noise. Accepts integer values in the range [0, 100].
            Shot noise scales inversely with the square root of the photon number:

        .. math::
            \\delta x \\propto \\frac{1}{\\sqrt{N}}

        :return:
            A dictionary from :class:`eqc_direct.utils.JobCodes` with the following keys:

            - **err_code** (`int`): Error code for the job submission.
            - **err_desc** (`str`): Description corresponding to the error code.
        """
        poly_coefficients = np.array(poly_coefficients)
        poly_coefficients_dtype = poly_coefficients.dtype

        if not (
            np.issubdtype(poly_coefficients_dtype, np.floating)
            and np.finfo(poly_coefficients_dtype).bits <= DIRAC_FLOAT_BITS
        ):
            warn_dtype_msg = (
                "Max precision for `poly_coefficients` representation in EQC device is "
                f"float32, but input dtype was {poly_coefficients_dtype.name}. Input "
                "polynomial coefficients will be rounded."
            )
            logging.warning(warn_dtype_msg)
            warnings.warn(warn_dtype_msg, Warning)

        poly_indices = np.array(poly_indices)

        try:
            _, poly_degree = poly_indices.shape
        except ValueError as err:
            err_msg = "`poly_indices` array must be two dimensional"
            logging.error(err_msg, exc_info=True)
            raise ValueError(err_msg) from err

        if num_variables is None:
            num_variables = np.max(poly_indices)

        if mean_photon_number is None:
            mean_photon_number = 0

        if quantum_fluctuation_coefficient is None:
            quantum_fluctuation_coefficient = 0

        # Scalar num_levels indicates to use same num_levels for each variable.
        # This "passes through" if num_levels as an array.
        num_levels = np.broadcast_to(num_levels, (num_variables,))

        if not (np.issubdtype(num_levels.dtype, np.integer)):
            raise ValueError("`num_levels` must be type int")

        logging.info("Submitting integer job to device...")
        job_input = eqc_pb2.IntInput(
            num_variables=num_variables,
            degree=poly_degree,
            poly_indices=poly_indices.flatten(order="c").tolist(),  # rowwise for matrix
            coef_values=poly_coefficients.tolist(),
            num_levels=num_levels.tolist(),
            mean_photon_number=mean_photon_number,
            quantum_fluctuation_coefficient=quantum_fluctuation_coefficient,
            relaxation_schedule=relaxation_schedule,
            num_samples=num_samples,
            lock_id=lock_id,
        )
        logging.info("Submitting integer job to device...done")

        try:
            job_results = self.eqc_stub.SolveInt(job_input)
        except _InactiveRpcError as exc:
            # Make error easier to read/detect by consumers.
            raise InactiveRpcError(
                "EQC submit_job failed due to grpc._channel._InactiveRpcError."
            ) from exc

        return message_to_dict(job_results)

    def fetch_integer_result(self, lock_id: str = "") -> IntegerResult:
        """
        Fetches results for last integer solve on Dirac device.

        :param lock_id: a valid :code:`lock_id` that matches current device
            :code:`lock_id`
        :return: an :class:`.IntegerResult` object
        """
        try:
            logging.info("Fetching integer results...")
            integer_results = self.eqc_stub.FetchIntResults(
                eqc_pb2.LockMessage(lock_id=lock_id)
            )
            logging.info("Fetching integer results...done")
        except _InactiveRpcError as exc:
            # Make error easier to read/detect by consumers.
            raise InactiveRpcError(
                "EQC fetch_results failed due to grpc._channel._InactiveRpcError."
            ) from exc

        result = message_to_dict(integer_results)

        if result["solution"]:
            result["solution"] = np.array(result["solution"])
            result["solution"] = [
                [float(f"{np.float32(val):.7f}") for val in soln]
                for soln in result["solution"]
            ]

            result["energy"] = [
                float(f"{np.float32(energy):.7f}") for energy in result["energy"]
            ]

        return result

    def solve_integer(
        self,
        poly_coefficients: Union[List[float], np_typing.NDArray[np.float32]],
        poly_indices: Union[List[List[int]], np_typing.NDArray[np.uint32]],
        num_levels: Union[int, List[int], np_typing.NDArray[np.uint16]],
        num_variables: Optional[int] = None,
        num_samples: int = 1,
        lock_id: str = "",
        relaxation_schedule: int = 1,
        mean_photon_number: Optional[float] = None,
        quantum_fluctuation_coefficient: Optional[int] = None,
    ) -> dict:
        """
        Utilizes Dirac to optimize a polynomial with integer solution values.

        :param poly_coefficients:
            the coefficient values for polynomial to be minimized. Inputs
            should be precision float 32 or less, otherwise precision is
            lost during conversion to 32-bit.
        :param poly_indices:
            the indices for coefficient values for polynomial to be minimized.
        :param num_levels: an array indicating the number of integer values
            for each solution variable. A :code:`num_levels` value of 2 for a variable
            indicates that the possible values for that variable can be {0,1}.
            Similarily if :math`L` is specified for a given variable then possible values
            for that variable will be {0,1, ..., :math:`L`-1}.

            .. math::
               \sum_{i=1}^{n} L_i \le 954

        :param num_variables: optional input to specify number of variables for
            polynomial. Must be greater than or equal to maximum index value in
            :code:`poly_indices`.
        :param num_samples: the number of times to solve the problem on the device.
        :param lock_id: a UUID to control multi-user device access.
        :param relaxation_schedule: four different schedules represented
            in integer parameter. Higher values reduce the variation in
            the analog spin values and therefore, are more probable to lead to
            improved (i.e., lower) objective function energy for input problem.
            Accepts range of values in set {1, 2, 3, 4}.
        :param mean_photon_number: optional parameter that modfies device
            configuration from the defaults for :code:`relaxation_schedule`.
            Sets the average number of photons that are present in a given
            quantum state.
        :param quantum_fluctuation_coefficient:
            Optional, overrides the default value from :code:`relaxation_schedule`. Specifies the
            number of photons (:math:`N`) in each feedback loop, which determines
            the shot noise. Accepts integer values in the range [0, 100].
            Shot noise scales inversely with the square root of the photon number:

        .. math::
            \\delta x \\propto \\frac{1}{\\sqrt{N}}

        :return: dict of results and timings with all keys from
            :class:`.IntegerResult` as well as the following additional keys:

           - start_job_ts: time in ns marking start of job_submission
           - end_job_ts: time in ns marking end of job submission complete includes

        :note: The difference between `end_job_ts` and `start_job_ts` includes a 1
           second polling time which is not part of device solving time. To calculate
           the execution time on the device add together `preprocessing_time`, `runtime`
           and `postprocessing_time` from results object samplewise.
        """
        start_job_ts = time.time_ns()
        submit_job_resp = self.submit_integer_job(
            poly_coefficients=poly_coefficients,
            poly_indices=poly_indices,
            num_levels=num_levels,
            num_variables=num_variables,
            num_samples=num_samples,
            lock_id=lock_id,
            relaxation_schedule=relaxation_schedule,
            mean_photon_number=mean_photon_number,
            quantum_fluctuation_coefficient=quantum_fluctuation_coefficient,
        )
        if submit_job_resp["err_code"] != 0:
            err_msg = f"Submission failed with response: {submit_job_resp}"
            logging.error(err_msg, exc_info=True)
            raise RuntimeError(err_msg)
        sys_code = self.system_status()["status_code"]
        while sys_code != SysStatus.IDLE["status_code"]:
            sys_code = self.system_status()["status_code"]
            # this is based on the error statuses are 3 and above
            if sys_code > 3:
                err_msg = f"System unavailable status_code: {sys_code}"
                logging.error(err_msg, exc_info=True)
                raise RuntimeError(err_msg)
            # only sleep if not idle
            if sys_code != SysStatus.IDLE["status_code"]:
                time.sleep(1)
        # pull in results after is idle
        job_result = self.fetch_integer_result(lock_id=lock_id)
        end_job_ts = time.time_ns()
        if job_result["err_code"] != 0:
            raise RuntimeError(
                "Job execution error\n"
                f"err_code: {job_result['err_code']}\n"
                f"err_desc: {job_result['err_desc']}"
            )
        job_result["start_job_ts"] = start_job_ts
        job_result["end_job_ts"] = end_job_ts

        return job_result

    def submit_sum_constrained_job(  # pylint: disable=R0913, R0914
        self,
        poly_coefficients: Union[List[float], np_typing.NDArray[np.float32]],
        poly_indices: Union[List[List[int]], np_typing.NDArray[np.uint32]],
        num_variables: Optional[int] = None,
        num_samples: int = 1,
        lock_id: str = "",
        relaxation_schedule: int = 1,
        sum_constraint: Union[int, float] = 10000,
        solution_precision: Optional[float] = None,
        mean_photon_number: Optional[float] = None,
        quantum_fluctuation_coefficient: Optional[int] = None,
    ) -> dict:
        """
        Submits polynomial to be minimized by Dirac. All solutions are optimized
        utilizing a sum constraint which limits search to only solutions which have a
        sum equal to the input sum constraint.

        :param poly_coefficients:
            the coefficient values for polynomial to be minimized. Numbers, including
            integers, should be floats with 32-bit (or less) precision, otherwise
            precision is lost during conversion to 32-bit.
        :param poly_indices:
            the indices for coefficient values for polynomial to be minimized.
        :param num_variables: optional input to specify number of variables for
            polynomial. Must be greater than or equal to maximum index value in
            :code:`poly_indices`.
        :param num_samples: the number of times to solve the problem on the device.
        :param lock_id: a UUID to allow for multi-user processing
        :param relaxation_schedule: four different schedules represented
            in integer parameter. Higher values reduce the variation in
            the analog spin values and therefore, are more probable to lead to
            improved objective function energy for input problem.
            Accepts range of values in set {1, 2, 3, 4}.
        :param sum_constraint: a normalization constraint that is applied to the
            problem space that is used to calculate :code:`energy`. This
            parameter will be rounded if exceeds float32 precision
            (e.g. 7-decimal places). Value must be between 1 and 10000.
        :param solution_precision: the level of precision to apply to the solutions.
            This parameter will be rounded if exceeds float32 precision
            (e.g. 7-decimal places). If specified a distillation method is
            applied to the continuous solutions to map them to the submitted
            :code:`solution_precision`. Input :code:`solution_precision` must
            satisfy :code:`solution_precision` greater than or equal to
            :code:`sum_constraint`/10000 in order to be valid.
            Also :code:`sum_constraint` must be divisible by :code:`solution_precision`.
            If :code:`solution_precision` is not specified no distillation will be
            applied to the solution derived by the device.
        :param mean_photon_number: optional parameter that modfies device
            configuration from the defaults for :code:`relaxation_schedule`.
            Sets the average number of photons that are present in a given
            quantum state.
        :param quantum_fluctuation_coefficient:
            Optional, overrides the default value from :code:`relaxation_schedule`. Specifies the
            number of photons (:math:`N`) in each feedback loop, which determines
            the shot noise. Accepts integer values in the range [0, 100].
            Shot noise scales inversely with the square root of the photon number:

        .. math::
            \\delta x \\propto \\frac{1}{\\sqrt{N}}

        :return: a member of :class:`eqc_direct.utils.JobCodes` as a dict
           with the following keys:

           - **err_code**: `int`- job submission error code
           - **err_desc**: `str`- error code description for submission
        """
        # set None values to zero for grpc messages
        if solution_precision is None:
            solution_precision = 0

        if mean_photon_number is None:
            mean_photon_number = 0

        if quantum_fluctuation_coefficient is None:
            quantum_fluctuation_coefficient = 0

        poly_coefficients = np.array(poly_coefficients)
        poly_indices = np.array(poly_indices)
        coefficient_dtype = poly_coefficients.dtype

        if not (
            np.issubdtype(coefficient_dtype, np.integer)
            or (
                np.issubdtype(coefficient_dtype, np.floating)
                and np.finfo(coefficient_dtype).bits <= DIRAC_FLOAT_BITS
            )
        ):
            warn_dtype_msg = (
                "Max precision for EQC device is float32 input type "
                f"was dtype {np.dtype(coefficient_dtype).name}."
                " Input matrix will be rounded"
            )
            logging.warning(warn_dtype_msg)
            warnings.warn(warn_dtype_msg, Warning)

        if get_decimal_places(solution_precision) > 7:
            soln_prec_warn = (
                "`solution_precision`precision is greater than 7 "
                "decimal places. Will be modified on submission to "
                "device to float32 precision"
            )
            logging.warning(soln_prec_warn)
            warnings.warn(soln_prec_warn, Warning)

        if get_decimal_places(sum_constraint) > 7:
            sum_constraint_warn = (
                "`sum_constraint` precision is greater than 7 decimal "
                "places. Will be modified on submission to device "
                "to float32"
            )
            logging.warning(sum_constraint_warn)
            warnings.warn(sum_constraint_warn, Warning)

        try:
            _, degree_poly = poly_indices.shape
        except ValueError as err:
            err_msg = "`poly_indices` array must be two dimensions"
            logging.error(err_msg, exc_info=True)
            raise ValueError(err_msg) from err

        if not num_variables:
            num_variables = np.max(poly_indices)

        logging.info("Submitting sum-constrained job to device...")
        job_input = eqc_pb2.SumConstInput(
            num_variables=num_variables,
            num_samples=num_samples,
            degree=degree_poly,
            poly_indices=poly_indices.flatten(
                order="c"
            ).tolist(),  # flatten rowwise for matrix
            coef_values=poly_coefficients.tolist(),
            sum_constraint=sum_constraint,
            relaxation_schedule=relaxation_schedule,
            soln_precision=solution_precision,
            mean_photon_number=mean_photon_number,
            quantum_fluctuation_coefficient=quantum_fluctuation_coefficient,
            lock_id=lock_id,
        )
        logging.info("Submitting sum-constrained job to device...done")

        try:
            job_results = self.eqc_stub.SolveSumConst(job_input)
        except _InactiveRpcError as exc:
            # Make error easier to read/detect by consumers.
            raise InactiveRpcError(
                "EQC submit_job failed due to grpc._channel._InactiveRpcError."
            ) from exc
        return message_to_dict(job_results)

    def fetch_sum_constrained_result(self, lock_id: str = "") -> SumConstrainedResult:
        """
        Request last EQC job results. Returns results from the most recent
        run on the device.

        :param lock_id: a valid :code:`lock_id` that matches current device
            :code:`lock_id`
        :return: an :class:`.EqcResult` object
        """
        fetch_input = eqc_pb2.LockMessage(lock_id=lock_id)
        try:
            eqc_results = self.eqc_stub.FetchSumConstResults(fetch_input)
        except _InactiveRpcError as exc:
            # Make error easier to read/detect by consumers.
            raise InactiveRpcError(
                "EQC fetch_results failed due to grpc._channel._InactiveRpcError."
            ) from exc
        result = message_to_dict(eqc_results)
        # need to interpret result with correct precision
        # grpc serialization deserialization causes a change in the values
        # in order to ensure that results can be dumped to json
        # must use native python types if use float(np.float32(num))
        # then will get corrupted bits so must cast to str first
        if len(result["solution"]) > 0:
            result["solution"] = np.array(result["solution"])
            result["solution"] = [
                [float(f"{np.float32(val):.7f}") for val in soln]
                for soln in result["solution"]
            ]
        if len(result["distilled_solution"]) > 0:
            result["distilled_solution"] = np.array(result["distilled_solution"])

            result["distilled_solution"] = [
                [float(f"{np.float32(val):.7f}") for val in soln]
                for soln in result["distilled_solution"]
            ]
        result["energy"] = [
            float(f"{np.float32(energy):.7f}") for energy in result["energy"]
        ]
        result["distilled_energy"] = [
            float(f"{np.float32(energy):.7f}") for energy in result["distilled_energy"]
        ]
        return result

    def solve_sum_constrained(  # pylint: disable=R0913
        self,
        poly_coefficients: Union[List[float], np_typing.NDArray[np.float32]],
        poly_indices: Union[List[List[int]], np_typing.NDArray[np.uint32]],
        num_variables: Optional[int] = None,
        num_samples: int = 1,
        lock_id: str = "",
        relaxation_schedule: int = 1,
        sum_constraint: Union[int, float] = 10000,
        solution_precision: Optional[float] = None,
        mean_photon_number: Optional[float] = None,
        quantum_fluctuation_coefficient: Optional[int] = None,
    ) -> dict:
        """
        Utilizes Dirac to optimize a polynomial under the constraint that the
        sum of the solution values must equal the input :code:`sum_constraint`.

        :param poly_coefficients:
            the coefficient values for polynomial to be minimized. Numbers, including
            integers, should be floats with 32-bit (or less) precision, otherwise
            precision is lost during conversion to 32-bit.
        :param poly_indices:
            the indices for coefficient values for polynomial to be minimized.
        :param num_variables: optional input to specify number of variables for
            polynomial. Must be greater than or equal to maximum index value in
            :code:`poly_indices`.
        :param num_samples: the number of times to solve the problem on the device.
        :param lock_id: a UUID to allow for multi-user processing
        :param relaxation_schedule: four different schedules represented
            in integer parameter. Higher values reduce the variation in
            the analog spin values and therefore, are more probable to lead to
            improved objective function energy for input problem.
            Accepts range of values in set {1, 2, 3, 4}.
        :param sum_constraint: a normalization constraint that is applied to the
            problem space that is used to calculate :code:`energy`. This
            parameter will be rounded if exceeds float32 precision
            (e.g. 7-decimal places). Value must be between 1 and 10000.
        :param solution_precision: the level of precision to apply to the solutions.
            This parameter will be rounded if exceeds float32 precision
            (e.g. 7-decimal places). If specified a distillation method is
            applied to the continuous solutions to map them to the submitted
            :code:`solution_precision`. Input :code:`solution_precision` must
            satisfy :code:`solution_precision` greater than or equal to
            :code:`sum_constraint`/10000 in order to be valid.
            Also :code:`sum_constraint` must be divisible by :code:`solution_precision`.
            If :code:`solution_precision` is not specified no distillation will be
            applied to the solution derived by the device.
        :param mean_photon_number: optional parameter that modfies device
            configuration from the defaults for :code:`relaxation_schedule`.
            Sets the average number of photons that are present in a given
            quantum state.
        :param quantum_fluctuation_coefficient:
            Optional, overrides the default value from :code:`relaxation_schedule`. Specifies the
            number of photons (:math:`N`) in each feedback loop, which determines
            the shot noise. Accepts integer values in the range [0, 100].
            Shot noise scales inversely with the square root of the photon number:

        .. math::
            \\delta x \\propto \\frac{1}{\\sqrt{N}}

        :return: dict of results and timings with the following keys:

           - results: :class:`.SumConstrainedResult` dict
           - start_job_ts: time in ns marking start of job_submission
           - end_job_ts: time in ns marking end of job submission complete

        :note: The difference between `end_job_ts` and `start_job_ts` includes a 1
           second polling time which is not part of device solving time. To calculate
           the execution time on the device add together `preprocessing_time`, `runtime`
           and `postprocessing_time` from results object samplewise.
        """
        start_job = time.time_ns()
        submit_sum_constrained_job_resp = self.submit_sum_constrained_job(
            poly_coefficients=poly_coefficients,
            poly_indices=poly_indices,
            num_variables=num_variables,
            num_samples=num_samples,
            lock_id=lock_id,
            sum_constraint=sum_constraint,
            relaxation_schedule=relaxation_schedule,
            solution_precision=solution_precision,
            mean_photon_number=mean_photon_number,
            quantum_fluctuation_coefficient=quantum_fluctuation_coefficient,
        )
        if submit_sum_constrained_job_resp["err_code"] != 0:
            err_msg = (
                f"Submission failed with response: {submit_sum_constrained_job_resp}"
            )
            logging.error(err_msg, exc_info=True)
            raise RuntimeError(err_msg)
        sys_code = self.system_status()["status_code"]
        while sys_code != SysStatus.IDLE["status_code"]:
            sys_code = self.system_status()["status_code"]
            # this is based on the error statuses are 3 and above
            if sys_code > 3:
                err_msg = f"System unavailable status_code: {sys_code}"
                logging.error(err_msg, exc_info=True)
                raise RuntimeError(err_msg)
            # only sleep if not idle
            if sys_code != SysStatus.IDLE["status_code"]:
                time.sleep(1)
        # pull in results after is idle
        logging.info("Fetching sum-constrained results")
        job_result = self.fetch_sum_constrained_result(lock_id=lock_id)
        end_job = time.time_ns()
        if job_result["err_code"] != 0:
            raise RuntimeError(
                f"Job execution error\n"
                f"err_code: {job_result['err_code']}\n"
                f"err_desc: {job_result['err_desc']}"
            )
        job_result["start_job_ts"] = start_job
        job_result["end_job_ts"] = end_job
        return job_result

    def system_status(self) -> dict:
        """
        Client call to obtain EQC system status

        :returns: a member of :class:`eqc_direct.utils.SysStatus` as a dict:

            - **status_code**: `int`- current system status code
            - **status_desc**: `str`- description of current system status
        """
        try:
            sys_resp = self.eqc_stub.SystemStatus(eqc_pb2.Empty())
        except _InactiveRpcError as exc:
            raise InactiveRpcError(
                "EQC system_status failed due to grpc._channel._InactiveRpcError."
            ) from exc
        return message_to_dict(sys_resp)

    def acquire_lock(self) -> dict:
        """
        Makes a single attempt to acquire exclusive lock on hardware execution.
        Locking can be used to ensure orderly processing in multi-user environments.
        Lock can only be acquired when no other user has acquired the lock or when
        the system has been idle for 60 seconds while another user has the lock.
        This idle timeout prevents one user from blocking other users from using
        the machine even if they are not active.

        :return:
           a member of :class:`eqc_direct.utils.LockManageStatus` as a dict along
           with an additional key :code:`lock_id`:

           - **lock_id**: `str`- if acquired the current device `lock_id`
             else empty string
           - **status_code**: `int`- status code for lock id acquisition
           - **status_desc**: `str`- a description for the associated status code
        """
        try:
            acquire_lock_resp = self.eqc_stub.AcquireLock(eqc_pb2.Empty())
        except _InactiveRpcError as exc:
            raise InactiveRpcError(
                "EQC acquire_lock failed due to grpc._channel._InactiveRpcError."
            ) from exc

        return {
            "lock_id": acquire_lock_resp.lock_id,
            "status_code": acquire_lock_resp.lock_status.status_code,
            "status_desc": acquire_lock_resp.lock_status.status_desc,
        }

    def release_lock(self, lock_id: str = "") -> dict:
        """
        Releases exclusive lock for running health check or submitting job

        :param lock_id: a UUID with currently acquired exclusive device lock
        :return: a member of :class:`eqc_direct.utils.LockManageStatus` as a dict:

           - **status_code**: `int`- status code for lock id acquisition
           - **status_desc**: `str`- a description for the associated status code
        """
        release_input = eqc_pb2.LockMessage(lock_id=lock_id)
        try:
            release_lock_resp = self.eqc_stub.ReleaseLock(release_input)
        except _InactiveRpcError as exc:
            raise InactiveRpcError(
                "EQC release_lock failed due to grpc._channel._InactiveRpcError."
            ) from exc
        return message_to_dict(release_lock_resp)

    def check_lock(self, lock_id: str = "") -> dict:
        """
        Checks if submitted :code:`lock_id` has execution lock on the device

        :param lock_id: a UUID which will be checked to determine if has exclusive
            device execution lock
        :return: a member of :class:`eqc_direct.utils.LockCheckStatus` as a dict:

           - **status_code**: `int`- status code for lock check
           - **status_desc**: `str`- a description for the associated status code
        """
        check_input = eqc_pb2.LockMessage(lock_id=lock_id)
        check_output = self.eqc_stub.CheckLock(check_input)
        return message_to_dict(check_output)

    def stop_running_process(self, lock_id: str = "") -> dict:
        """
        Stops a running process either a health check or a Eqc job.
        Process locks will release automatically based on a timeout
        which is maintained in the server code if they are
        not released using this.

        :param lock_id: requires a lock_id that was acquired by
        :return:
           a member of :class:`eqc_direct.utils.SysStatus`
           as dict with following keys:

           - **status_code**: `int`- the system code after stopping
           - **status_desc**: `str`- the associated system status description
        """
        stop_input = eqc_pb2.LockMessage(lock_id=lock_id)
        try:
            stop_resp = self.eqc_stub.StopRunning(stop_input)
        except _InactiveRpcError as exc:
            raise InactiveRpcError(
                "EQC stop_running_process failed due to "
                "grpc._channel._InactiveRpcError."
            ) from exc
        return message_to_dict(stop_resp)

    def wait_for_lock(self) -> tuple:
        """
        Waits for lock indefinitely calling :func:`acquire_lock`

        :return: a tuple of the following items:

           - **lock_id**: `str`- exclusive lock for device execution with a timeout
           - **start_queue_ts**: `int`- time in ns on which lock was acquired is an int
           - **end_queue_ts**: `int`- time in ns on which queue for
             lock ended is an int.
        """
        lock_id = ""
        start_queue_ts = time.time_ns()
        while lock_id == "":
            sys_code = self.system_status()["status_code"]
            # this is based on the error statuses are 3 and above
            if sys_code >= 3:
                raise RuntimeError(f"System unavailable status_code: {sys_code}")
            lock_id = self.acquire_lock()["lock_id"]
            # only sleep if didn't get lock on device
            if lock_id == "":
                time.sleep(1)
        end_queue_ts = time.time_ns()
        return lock_id, start_queue_ts, end_queue_ts

    def system_info(self) -> SystemInfo:
        """
        Provides information regarding Dirac system

        :return: a :class:`eqc_direct.utils.SystemInfo` dict with a these items:

            - **server_version**: `str` - the gRPC server version
            - **device_type**: `str` - the device type (e.g., Dirac-3)
            - **fpga_version**: `str` - version of FPGA in device (None if using the simulator)
            - **device_id**: `str` - unique string to identify device
        """
        try:
            return SystemInfo(
                **message_to_dict(self.eqc_stub.SystemInfo(eqc_pb2.Empty()))
            )
        except _InactiveRpcError as exc:
            raise InactiveRpcError(
                "EQC server_info call failed due to inactive grpc channel"
            ) from exc
