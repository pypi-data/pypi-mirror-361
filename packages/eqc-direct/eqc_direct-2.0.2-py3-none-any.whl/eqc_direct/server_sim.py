"""
Simulates Server Wrapper for EQC3 (aka. Dirac-3) device
"""
from concurrent import futures
import logging
import math
import os
import signal
import threading
import time
from typing import Optional
import uuid

import grpc

# bypasses pickle serialization in favor of dill
# allows for consolidation of multiprocessing code in single class
# since multiprocessing blocks you from running multiprocessing code
# when module isn't main
import multiprocess
from multiprocess import managers
import numpy as np

import eqc_direct
from eqc_direct import eqc_pb2, eqc_pb2_grpc, utils

# max number of entries for matrix in c++ server
# based on 949 entries
MAX_ENTRIES = 949 * 949 + 949
MIN_CONSTRAINT = 1
MAX_CONSTRAINT = 10000


def calc_scale_factor(float_num: np.float32):
    decimal_places = len(str(np.float32(float_num)).split(".")[1])
    return 10**decimal_places


def convert_float_to_int(float_num: np.float32, scale_factor: int):
    int_number = int(float(str(float_num)) * scale_factor)
    return int_number


def calculate_mats_size(degree, num_variables):
    entries = 0
    for i in range(1, degree + 1):
        entries += num_variables**i
    return entries


def exceeds_max_size(degree: int, num_variables: int):
    # based on 949 variables for degree 2
    if degree <= 2:
        if num_variables > 949:
            return True
    elif degree == 3:
        if num_variables > 135:
            return True
    elif degree == 4:
        if num_variables > 39:
            return True
    elif degree == 5:
        if num_variables > 19:
            return True
    else:
        entries = calculate_mats_size(degree=degree, num_variables=num_variables)
        if entries > MAX_ENTRIES:
            return True
    return False


def check_for_duplicate_poly_index(poly_indices):
    seen = set()
    for sublist in poly_indices:
        if tuple(sublist) in seen:
            return True
        seen.add(tuple(sublist))
    return False


def check_decreasing(poly_indices):
    for sublist in poly_indices:
        for idx in range(len(sublist) - 1):
            if sublist[idx] > sublist[idx + 1]:
                return True
    return False


def calc_energy(poly_indices, poly_coefficients, soln):
    energy = 0
    for idx in range(len(poly_indices)):
        # start with initial coeffcient will be multiplied
        # by variable values for
        iter_energy = poly_coefficients[idx]
        iter_vars = poly_indices[idx]
        for var in iter_vars:
            if var > 0:
                iter_energy *= soln[(var - 1)]
        energy += iter_energy
    return energy


class EqcServer(eqc_pb2_grpc.EqcService):
    """
    Simulates an EQCX where X>=3
    Attributes
    ----------
    sys_tracker: dict with following keys
        - current_status: One of utils.SysStatus from utils.py
        - result: an EQC result object
        - idle_time: time from which EQC has been idle
        - current_pid: process id for job running on EQC
    spinlock: a lock for ensuring only single process can run at a time

    :note:
    context is the server stub.
    request is the input data for the grpc method used on client side.
    Server calibration occurs automatically when eqc-device is running
    and is not implemented in the server sim as there is no hardware.

    To see more info on request values see proto file
    """

    def __init__(self):
        # need to store as managed dict to access from other Processes
        self.manager = managers.SyncManager()
        self.manager.start()
        self.sys_tracker = self.manager.dict()
        self.sys_tracker.update(
            {
                "current_status": utils.SysStatus.IDLE,
                "result": {},
                "mixed_int_result": {},
                "idle_time": time.time(),
                "current_pid": None,
            }
        )
        self.spinlock = multiprocess.Lock()
        self.lock_id = ""
        # Unsure how this will performo windows so adding this as a check
        # If need a different start_method than default would use set_start_method
        logging.info("START TYPE %s", multiprocess.get_start_method())
        mac_addr = uuid.getnode()
        self.mac_addr = ":".join(
            f"{(mac_addr >> ele) & 0xff:02x}" for ele in range(40, -1, -8)
        )

    def __del__(self):
        self.manager.shutdown()

    def AcquireLock(self, request, context):
        """
        Releases spinlock if has been idle for more than 120 seconds
        :return: a bool indicating that spinlock was acquired or not
        """
        # In order to release lock if already locked must meet following:
        # 1. should have been idle for 120 seconds
        # 2. System must be currently idle
        # there are other checks for this last one so probably could be left out
        if (time.time() - self.sys_tracker["idle_time"]) > 120 and self.sys_tracker[
            "current_status"
        ] == utils.SysStatus.IDLE:
            self.sys_tracker["idle_time"] = time.time()
            try:
                self.spinlock.release()
            # if double release raises ValueError
            except ValueError:
                pass
        # race condition is avoided because only one can have spinlock
        lock_acquired = self.spinlock.acquire(block=False)
        if lock_acquired:
            lock_id = str(uuid.uuid4())
            self.lock_id = lock_id
            logging.info("Lock Acquired with lock_id: %s", self.lock_id)
            self.sys_tracker["idle_time"] = time.time()
            self.sys_tracker["result"] = {}
            lock_status = utils.LockManageStatus.SUCCESS
        else:
            lock_id = ""
            lock_status = utils.LockManageStatus.BUSY
        lock_out = {"lock_id": lock_id, "lock_status": lock_status}
        return eqc_pb2.LockOutput(**lock_out)

    def ReleaseLock(self, request, context):
        """
        Releases lock for execution
        """
        logging.info("Attempting lock release...")
        if request.lock_id != self.lock_id:
            logging.error("ReleaseLock failed because requested wrong lock_id")
            return eqc_pb2.StatusOutput(**utils.LockManageStatus.MISMATCH)
        if self.sys_tracker["current_pid"] != None:
            logging.error("ReleaseLock failed due to other process running")
            return eqc_pb2.StatusOutput(**utils.LockManageStatus.BUSY)
        try:
            # this may not be necessary
            self.lock_id = ""
            self.spinlock.release()
        # catch error for double release
        except RuntimeError:
            pass
        return eqc_pb2.StatusOutput(**utils.LockManageStatus.SUCCESS)

    def CheckLock(self, request, context):
        """
        Returns current lock availability to user
        """
        user_locked = self.lock_id == request.lock_id and self.lock_id != ""
        lock_available = self.lock_id == ""
        if user_locked:
            check_output = utils.LockCheckStatus.USER_LOCKED
        elif lock_available:
            check_output = utils.LockCheckStatus.AVAILABLE
        else:
            check_output = utils.LockCheckStatus.UNAVAILABLE
        return eqc_pb2.StatusOutput(**check_output)

    def SystemStatus(self, request, context):
        """
        Returns the current system status as a message
        """
        return eqc_pb2.StatusOutput(**self.sys_tracker["current_status"])

    def SystemInfo(self, request, context):
        """
        Returns server info with eqc-direct package version for Dirac-3 Python-based
        Dirac-3 software simulator.
        """

        return eqc_pb2.VersionOutput(
            server_version=eqc_direct.PACKAGE_VERSION,
            fpga_version="None",
            device_type="Dirac-3-simulator",
            device_id=self.mac_addr,
        )

    def set_idle(self):
        """
        Resets sys_tracker settings
        """
        self.sys_tracker["idle_time"] = time.time()
        self.sys_tracker["current_pid"] = None
        self.sys_tracker["current_status"] = utils.SysStatus.IDLE

    def SolveInt(self, request, context):
        """
        Runs simulated mixed-integer job
        """
        start_val = time.time()
        logging.info("Submit mixed-integer job...")
        job_input = utils.message_to_dict(request)
        # data validation
        if request.lock_id != self.lock_id:
            return eqc_pb2.SubmitOutput(**utils.JobCodes.LOCK_MISMATCH)
        # must not have another process running
        if self.sys_tracker["current_pid"] is not None:
            return eqc_pb2.SubmitOutput(**utils.JobCodes.DEVICE_BUSY)
        if (
            len(job_input["poly_indices"]) / len(job_input["coef_values"])
        ) != request.degree:
            return eqc_pb2.SubmitOutput(**utils.JobCodes.COEF_INDEX_MISMATCH)
        job_input["poly_indices"] = np.array(job_input["poly_indices"]).reshape(
            -1, job_input["degree"]
        )
        if request.num_variables < np.max(job_input["poly_indices"]):
            return eqc_pb2.SubmitOutput(**utils.JobCodes.INDEX_OUT_OF_RANGE)
        if job_input["num_samples"] <= 0:
            return eqc_pb2.SubmitOutput(**utils.JobCodes.NUM_SAMPLES_POSITIVE)
        if request.degree <= 0:
            return eqc_pb2.SubmitOutput(**utils.JobCodes.DEGREE_POSITIVE)
        if request.num_variables <= 0:
            return eqc_pb2.SubmitOutput(**utils.JobCodes.NUM_VARIABLES_POSITIVE)
        if job_input["relaxation_schedule"] not in {1, 2, 3, 4}:
            return eqc_pb2.SubmitOutput(**utils.JobCodes.INVALID_RELAXATION_SCHEDULE)
        if exceeds_max_size(degree=request.degree, num_variables=request.num_variables):
            return eqc_pb2.SubmitOutput(**utils.JobCodes.EXCEEDS_MAX_SIZE)
        if check_decreasing(job_input["poly_indices"]):
            return eqc_pb2.SubmitOutput(**utils.JobCodes.DECREASING_INDEX)
        if len(job_input["num_levels"]) != job_input["num_variables"]:
            return eqc_pb2.SubmitOutput(**utils.JobCodes.NUM_LEVELS_NUM_VARS_MISMATCH)
        if min(job_input["num_levels"]) <= 1:
            return eqc_pb2.SubmitOutput(**utils.JobCodes.NUM_LEVELS_GT_ONE)
        if sum(job_input["num_levels"]) > 954:
            return eqc_pb2.SubmitOutput(**utils.JobCodes.TOTAL_INTEGER_LEVELS)
        if job_input["mean_photon_number"] != 0 and (
            job_input["mean_photon_number"] > 0.0066667
            or job_input["mean_photon_number"] < 0.0000665
        ):
            return eqc_pb2.SubmitOutput(**utils.JobCodes.INVALID_MEAN_PHOTON_NUMBER)
        if job_input["quantum_fluctuation_coefficient"] != 0 and (
            job_input["quantum_fluctuation_coefficient"] > 100
            or job_input["quantum_fluctuation_coefficient"] < 1
        ):
            return eqc_pb2.SubmitOutput(
                **utils.JobCodes.INVALID_QUANTUM_FLUCTUATION_COEFFICIENT
            )
        self.sys_tracker["current_status"] = utils.SysStatus.JOB_RUNNING
        # Python deserialize it as type float which defaults to 64 bit
        # precision in python in order to ensure that it has the same
        # precision as the C++ server use np.float32
        job_input["coef_values"] = np.array(job_input["coef_values"], dtype=np.float32)
        end_val = time.time()
        job_input["preprocessing_time"] = end_val - start_val
        logging.info("Start subprocess...")
        proc_job = multiprocess.Process(
            target=self.run_mixed_integer, args=(job_input,)
        )
        proc_job.start()
        self.sys_tracker["current_pid"] = proc_job.pid
        return eqc_pb2.SubmitOutput(**utils.JobCodes.NORMAL)

    def run_mixed_integer(self, job_input):
        """
        Simulates mixed-integer job
        """
        result = {
            "preprocessing_time": job_input["preprocessing_time"],
            "runtime": [],
            "postprocessing_time": [],
            "energy": [],
            "solution": [],
            "num_samples": job_input["num_samples"],
            "num_variables": job_input["num_variables"],
            "calibration_time": 0,
        }

        logging.info("Run job...")
        for _ in range(job_input["num_samples"]):
            run_start = time.time()
            sim_solution = np.array(
                [
                    # Currently, we simulate only integer solutions.
                    np.random.randint(int(math.floor(num_levels)))
                    for num_levels in job_input["num_levels"]
                ],
                dtype=np.float32,  # Matches type and precision from Dirac.
            )
            post_start = time.time()
            energy = calc_energy(
                poly_indices=job_input["poly_indices"],
                poly_coefficients=job_input["coef_values"],
                soln=sim_solution,
            )
            post_end = time.time()
            result["runtime"].append(post_start - run_start)
            result["postprocessing_time"].append(post_end - post_start)
            result["energy"].append(energy)
            # wait to convert to list since distill process requires numpy array
            result["solution"].append({"values": sim_solution.tolist()})

        result.update(utils.JobCodes.NORMAL)
        self.sys_tracker["mixed_int_result"] = result
        self.set_idle()
        return result

    def SolveSumConst(self, request, context):
        """
        Runs sum-constrained job simulation
        """
        start_val = time.time()
        logging.info("Submit sum-constrained job...")
        job_input = utils.message_to_dict(request)
        # data validation
        if request.lock_id != self.lock_id:
            return eqc_pb2.SubmitOutput(**utils.JobCodes.LOCK_MISMATCH)
        # must not have another process running
        if self.sys_tracker["current_pid"] is not None:
            return eqc_pb2.SubmitOutput(**utils.JobCodes.DEVICE_BUSY)
        # check sum constraint
        scale_factor = max(
            calc_scale_factor(np.float32(request.soln_precision)),
            calc_scale_factor(np.float32(request.sum_constraint)),
        )
        prec_int = convert_float_to_int(
            np.float32(request.soln_precision), scale_factor
        )
        constraint_int = convert_float_to_int(
            np.float32(request.sum_constraint), scale_factor
        )
        if (
            len(job_input["poly_indices"]) / len(job_input["coef_values"])
        ) != request.degree:
            return eqc_pb2.SubmitOutput(**utils.JobCodes.COEF_INDEX_MISMATCH)
        job_input["poly_indices"] = np.array(job_input["poly_indices"]).reshape(
            -1, job_input["degree"]
        )
        if request.num_variables < np.max(job_input["poly_indices"]):
            return eqc_pb2.SubmitOutput(**utils.JobCodes.INDEX_OUT_OF_RANGE)
        if job_input["num_samples"] <= 0:
            return eqc_pb2.SubmitOutput(**utils.JobCodes.NUM_SAMPLES_POSITIVE)
        if request.soln_precision < 0:
            return eqc_pb2.SubmitOutput(**utils.JobCodes.PRECISION_NONNEGATIVE)
        if request.degree <= 0:
            return eqc_pb2.SubmitOutput(**utils.JobCodes.DEGREE_POSITIVE)
        if request.num_variables <= 0:
            return eqc_pb2.SubmitOutput(**utils.JobCodes.NUM_VARIABLES_POSITIVE)
        if request.sum_constraint < 1 or request.sum_constraint > 10000:
            return eqc_pb2.SubmitOutput(**utils.JobCodes.INVALID_SUM_CONSTRAINT)
        if request.soln_precision != 0:
            if (constraint_int / prec_int) > 10000:
                return eqc_pb2.SubmitOutput(**utils.JobCodes.INVALID_PRECISION)
            if not ((constraint_int % prec_int) == 0):
                return eqc_pb2.SubmitOutput(
                    **utils.JobCodes.PRECISION_CONSTRAINT_MISMATCH
                )
        if job_input["relaxation_schedule"] not in {1, 2, 3, 4}:
            return eqc_pb2.SubmitOutput(**utils.JobCodes.INVALID_RELAXATION_SCHEDULE)
        if exceeds_max_size(degree=request.degree, num_variables=request.num_variables):
            return eqc_pb2.SubmitOutput(**utils.JobCodes.EXCEEDS_MAX_SIZE)
        if check_decreasing(job_input["poly_indices"]):
            return eqc_pb2.SubmitOutput(**utils.JobCodes.DECREASING_INDEX)
        print("MPN:", job_input["mean_photon_number"])
        if job_input["mean_photon_number"] != 0 and (
            job_input["mean_photon_number"] > 0.0066667
            or job_input["mean_photon_number"] < 0.0000665
        ):
            return eqc_pb2.SubmitOutput(**utils.JobCodes.INVALID_MEAN_PHOTON_NUMBER)
        if job_input["quantum_fluctuation_coefficient"] != 0 and (
            job_input["quantum_fluctuation_coefficient"] > 100
            or job_input["quantum_fluctuation_coefficient"] < 1
        ):
            return eqc_pb2.SubmitOutput(
                **utils.JobCodes.INVALID_QUANTUM_FLUCTUATION_COEFFICIENT
            )
        self.sys_tracker["current_status"] = utils.SysStatus.JOB_RUNNING
        # Python deserialize it as type float which defaults to 64 bit
        # precision in python in order to ensure that it has the same
        # precision as the C++ server use np.float32
        job_input["coef_values"] = np.array(job_input["coef_values"], dtype=np.float32)
        end_val = time.time()
        job_input["preprocessing_time"] = end_val - start_val
        logging.info("Start subprocess...")
        proc_job = multiprocess.Process(target=self.run_sum_const, args=(job_input,))
        proc_job.start()
        self.sys_tracker["current_pid"] = proc_job.pid
        return eqc_pb2.SubmitOutput(**utils.JobCodes.NORMAL)

    def run_sum_const(self, job_input):
        """
        Simulates running sum-constrained job
        :note: doesn't simulate distillation process so not exact simulation
        """
        result = {
            "preprocessing_time": job_input["preprocessing_time"],
            "runtime": [],
            "postprocessing_time": [],
            "energy": [],
            "solution": [],
            "distilled_energy": [],
            "distilled_solution": [],
            "num_samples": job_input["num_samples"],
            "num_variables": job_input["num_variables"],
            "calibration_time": 0,
        }

        logging.info("Run sum-constrained job...")
        for _ in range(job_input["num_samples"]):
            start_time = time.time()
            sim_solution = np.random.randint(10000, size=(job_input["num_variables"],))
            sim_solution = (
                job_input["sum_constraint"] * sim_solution / np.sum(sim_solution)
            ).astype(
                np.float32
            )  # Matches type and precision from Dirac.
            energy = calc_energy(
                poly_indices=job_input["poly_indices"],
                poly_coefficients=job_input["coef_values"],
                soln=sim_solution,
            )
            end_runtime = time.time()
            runtime = end_runtime - start_time
            result["runtime"].append(runtime)
            result["energy"].append(energy)
            if job_input["soln_precision"] != 0:
                rounded_solution = (
                    np.floor(sim_solution / job_input["soln_precision"])
                    * job_input["soln_precision"]
                )
                p = np.round(
                    (job_input["sum_constraint"] - rounded_solution.sum())
                    / job_input["soln_precision"]
                )
                rounded_solution[0] += p * job_input["soln_precision"]
                dist_energy = calc_energy(
                    poly_indices=job_input["poly_indices"],
                    poly_coefficients=job_input["coef_values"],
                    soln=rounded_solution,
                )
                dist_solution = [np.float32(var) for var in rounded_solution.tolist()]
                result["distilled_solution"].append({"values": dist_solution})
                result["distilled_energy"].append(dist_energy)
            # wait to convert to list since distill process requires numpy array
            sim_solution = [np.float32(var) for var in sim_solution.tolist()]

            result["solution"].append({"values": sim_solution})
            result["postprocessing_time"].append(time.time() - end_runtime)

        result.update(utils.JobCodes.NORMAL)
        self.sys_tracker["result"] = result
        self.set_idle()
        return result

    def FetchSumConstResults(self, request, context):
        """
        Fetch most recent sum-constrained results
        """
        if (
            self.lock_id == request.lock_id
            and self.sys_tracker["current_status"] == utils.SysStatus.IDLE
        ):
            logging.info("Fetch results...")
            return eqc_pb2.SumConstResult(**self.sys_tracker["result"])
        elif self.lock_id != request.lock_id:
            return eqc_pb2.SumConstResult(**utils.JobCodes.LOCK_MISMATCH)
        else:
            return eqc_pb2.SumConstResult(**utils.JobCodes.DEVICE_BUSY)

    def FetchIntResults(self, request, context):
        """
        Fetch most recent mixed-integer result
        """
        if (
            self.lock_id == request.lock_id
            and self.sys_tracker["current_status"] == utils.SysStatus.IDLE
        ):
            logging.info("Fetch mixed-integer results...")
            return eqc_pb2.IntResult(**self.sys_tracker["mixed_int_result"])
        elif self.lock_id != request.lock_id:
            return eqc_pb2.IntResult(**utils.JobCodes.LOCK_MISMATCH)
        else:
            return eqc_pb2.IntResult(**utils.JobCodes.DEVICE_BUSY)

    def StopRunning(self, request, context):
        """
        Stops a running job when using simulator may not work against actual server code
        """
        logging.info("Stop current running process...")
        if request.lock_id != self.lock_id:
            return eqc_pb2.StatusOutput(**utils.LockManageStatus.MISMATCH)
        if self.sys_tracker["current_pid"] is not None:
            logging.info("Killing process: %s", self.sys_tracker["current_pid"])
            os.kill(self.sys_tracker["current_pid"], signal.SIGKILL)
            self.set_idle()
            self.sys_tracker["result"] = utils.JobCodes.USER_INTERRUPT
        return eqc_pb2.StatusOutput(**utils.LockManageStatus.SUCCESS)


class GrpcServer:
    """
    Provides basic functionality to start a threaded gRPC server instance
    this is used to run the server simulator

    :param ip_address: target ip address to start grpc server
    :param port: target port on which to start grpc server
    :param private_key: a private key pem file that is used to run TLS
    :param cert_file: a certificate pem file that is used to run TLS
    """

    def __init__(
        self,
        ip_address: str = "localhost",
        port: str = "50051",
        private_key: Optional[str] = None,
        cert_file: Optional[str] = None,
    ):
        os.environ["GRPC_ENABLE_FORK_SUPPORT"] = "true"
        os.environ["GRPC_POLL_STRATEGY"] = "poll"
        self.stop_event = threading.Event()
        server_cls = EqcServer()
        max_variables = 10000
        max_length = (
            int(
                ((((4 * max_variables**2)) + (4 * max_variables)) / (1024**2))
                + (
                    512
                    - (
                        (((4 * max_variables**2) + (4 * max_variables)) / (1024**2))
                        % 512
                    )
                )
            )
            * 1024**2
        )
        self.server = grpc.server(
            futures.ThreadPoolExecutor(max_workers=10),
            options=(
                ("grpc.max_receive_message_length", max_length),
                ("grpc.max_send_message_length", max_length),
            ),
        )

        eqc_pb2_grpc.add_EqcServiceServicer_to_server(server_cls, self.server)
        ip_address = ip_address if ip_address else "localhost"
        port = port if port else "50051"
        logging.info("grpc server ip_address:port %s:%s", ip_address, port)
        ip_add_port = f"{ip_address}:{port}"
        if private_key and cert_file:
            with open(cert_file, "rb") as f:
                server_cert = f.read()
            with open(private_key, "rb") as f:
                server_key = f.read()
            server_credentials = grpc.ssl_server_credentials(
                [(server_key, server_cert)]
            )
            self.server.add_secure_port(ip_add_port, server_credentials)
        else:
            self.server.add_insecure_port(ip_add_port)

    def serve(self):
        """
        Starts grpc server instance which waits for termination
        """
        logging.info("Server started")
        self.server.start()
        self.server.wait_for_termination()

    def stop(self):
        """
        Stops the classes running grpc server instance
        with a stop event
        """
        self.server.stop(0)
        print("Stopping server")
        self.stop_event.set()
