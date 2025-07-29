"""
Relies on environment var1 DEVICE_IP_ADDRESS to identify IP_ADDRESS FOR tests
"""
import os
import time
import unittest
import warnings
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
from grpc_server_cls import ServerForTest
from eqc_direct.client import EqcClient
from eqc_direct.utils import JobCodes, LockCheckStatus, LockManageStatus


class TestEqcClient(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_ip_addr = os.getenv("DEVICE_IP_ADDRESS", "localhost")
        # only instantiate server if running on localhost
        if cls.test_ip_addr == "localhost":
            cls.server = ServerForTest(ip_address=cls.test_ip_addr, port="50051")
            cls.server.start()
        print("Running test using ip_address", cls.test_ip_addr)
        cls.eqc_client = EqcClient(ip_address=cls.test_ip_addr)
        cls.poly_indices = np.array(
            [
                [0, 0, 0, 3],
                [0, 0, 2, 2],
                [0, 0, 2, 3],
                [0, 1, 2, 3],
                [0, 1, 1, 1],
                [0, 2, 2, 3],
                [3, 3, 3, 3],
                [1, 1, 2, 3],
            ],
        )
        cls.poly_coefficients = np.array([1, 2, 3, 4, 5, 6, 7, 8], dtype=np.float32)
        cls.num_variables = 3
        cls.num_samples = 7

    @classmethod
    def tearDownClass(cls):
        if cls.test_ip_addr == "localhost":
            cls.server.stop()

    def test_ip_address(self):
        self.assertEqual(
            self.eqc_client.ip_address,
            os.getenv("DEVICE_IP_ADDRESS", "localhost"),
        )

    def test_port(self):
        self.assertEqual(self.eqc_client.port, "50051")

    def test_ip_add_port(self):
        self.assertEqual(
            self.eqc_client.ip_add_port,
            f"{self.eqc_client.ip_address}:{self.eqc_client.port}",
        )

    def test_numpy_dtype_preserved_in_broadcast_to(self):
        self.assertEqual(
            np.broadcast_to(np.array(1, dtype=np.float32), (self.num_variables,)).dtype,
            np.float32,
        )

    def test_numpy_dtype_preserved_in_array_cast(self):
        self.assertEqual(np.array(np.array([1, 2], dtype=np.float32)).dtype, np.float32)

    def test_check_lock(self):
        try:
            lock_av = self.eqc_client.check_lock()
            print("lock_av", lock_av)
            self.assertDictEqual(lock_av, LockCheckStatus.AVAILABLE)
            lock_id = self.eqc_client.acquire_lock()["lock_id"]
            lock_unv = self.eqc_client.check_lock()
            print("lock_unv", lock_unv)
            self.assertDictEqual(lock_unv, LockCheckStatus.UNAVAILABLE)
            lock_user = self.eqc_client.check_lock(lock_id=lock_id)
            self.assertDictEqual(lock_user, LockCheckStatus.USER_LOCKED)
        finally:
            self.eqc_client.release_lock(lock_id=lock_id)

    def test_basic_locking(self):
        try:
            print("Test basic locking")
            succ_lock_resp = self.eqc_client.acquire_lock()
            lock_id = succ_lock_resp["lock_id"]
            self.assertIsInstance(lock_id, str)
            self.assertEqual(36, len(lock_id))
            lock_fail = self.eqc_client.acquire_lock()
            self.assertEqual(lock_fail["lock_id"], "")

            self.assertEqual(lock_fail["status_code"], 2)
            self.assertEqual(
                lock_fail["status_desc"],
                "Lock currently in use unable to perform operation",
            )
        finally:
            release_out = self.eqc_client.release_lock(lock_id=lock_id)
            self.assertEqual(release_out["status_code"], 0)
            self.assertEqual(release_out["status_desc"], "Success")

    def test_wait_for_lock(self):
        print("Test wait for lock")
        try:
            lock_id, start_ts, end_ts = self.eqc_client.wait_for_lock()
            self.assertIsInstance(lock_id, str)
            self.assertEqual(36, len(lock_id))
            self.assertTrue(start_ts < end_ts)
            self.assertIsInstance(start_ts, int)
            self.assertIsInstance(end_ts, int)
        finally:
            self.eqc_client.release_lock(lock_id=lock_id)

    def test_stop_running_process(self):
        try:
            print("Stop test")
            lock_id, _, _ = self.eqc_client.wait_for_lock()
            # this isn't a real problem since isn't symmetric
            # just chose one that is large enough to take a significant
            # time to do data transfer so can cancel.
            print("stop lock", lock_id)
            submit_output = self.eqc_client.submit_sum_constrained_job(
                poly_indices=self.poly_indices,
                poly_coefficients=self.poly_coefficients,
                num_variables=self.num_variables,
                relaxation_schedule=1,
                sum_constraint=40,
                lock_id=lock_id,
            )
            print("SUBMTI OUTPUT", submit_output)
            stop_out = self.eqc_client.stop_running_process(lock_id=lock_id)
            self.assertDictEqual(stop_out, LockManageStatus.SUCCESS)
            stop_res = self.eqc_client.fetch_sum_constrained_result(lock_id=lock_id)
            self.assertEqual(stop_res["err_code"], JobCodes.USER_INTERRUPT["err_code"])
            self.assertEqual(stop_res["err_desc"], JobCodes.USER_INTERRUPT["err_desc"])

        finally:
            self.eqc_client.release_lock(lock_id=lock_id)

    def test_stop_lock_mismatch(self):
        stop_output = self.eqc_client.stop_running_process(lock_id="bad_lock")
        self.assertDictEqual(stop_output, LockManageStatus.MISMATCH)

    def test_system_info(self):
        system_info_resp = self.eqc_client.system_info()
        self.assertIsInstance(system_info_resp["server_version"], str)
        self.assertIsInstance(system_info_resp["device_type"], str)
        self.assertIsInstance(system_info_resp["fpga_version"], str)
        self.assertIsInstance(system_info_resp["device_id"], str)

    def test_system_status(self):
        sys_resp = self.eqc_client.system_status()
        self.assertListEqual(list(sys_resp.keys()), ["status_code", "status_desc"])
        self.assertIsInstance(sys_resp["status_code"], int)
        self.assertIsInstance(sys_resp["status_desc"], str)

    def test_submit_exceeds_size(self):
        print("test submit job sum constraint")
        lock_id, _, _ = self.eqc_client.wait_for_lock()
        # degree 2
        poly_indices_2 = np.array([[0, 950]])
        poly_coefficients = np.array([10], dtype=np.float32)
        try:
            print("DEGREE 2")
            result = self.eqc_client.submit_sum_constrained_job(
                poly_indices=poly_indices_2,
                poly_coefficients=poly_coefficients,
                relaxation_schedule=1,
                sum_constraint=100,
                lock_id=lock_id,
            )
            print("Sum constraint:", result)
            self.assertDictEqual(
                result,
                JobCodes.EXCEEDS_MAX_SIZE,
            )
            print("DEGREE 3")
            poly_indices_3 = [[0, 0, 136]]
            result = self.eqc_client.submit_sum_constrained_job(
                poly_indices=np.array(poly_indices_3),
                poly_coefficients=poly_coefficients,
                relaxation_schedule=1,
                sum_constraint=100,
                lock_id=lock_id,
            )
            print("Sum constraint:", result)
            self.assertDictEqual(
                result,
                JobCodes.EXCEEDS_MAX_SIZE,
            )
            print("DEGREE 4")
            poly_indices_4 = np.array([[0, 0, 0, 40]])
            result = self.eqc_client.submit_sum_constrained_job(
                poly_indices=poly_indices_4,
                poly_coefficients=poly_coefficients,
                relaxation_schedule=1,
                sum_constraint=100,
                lock_id=lock_id,
            )
            print("Sum constraint:", result)
            self.assertDictEqual(
                result,
                JobCodes.EXCEEDS_MAX_SIZE,
            )
            print("DEGREE 5")
            poly_indices_5 = np.array([[0, 0, 0, 0, 20]])
            result = self.eqc_client.submit_sum_constrained_job(
                poly_indices=poly_indices_5,
                poly_coefficients=poly_coefficients,
                relaxation_schedule=1,
                sum_constraint=100,
                lock_id=lock_id,
            )
            print("Sum constraint:", result)
            self.assertDictEqual(
                result,
                JobCodes.EXCEEDS_MAX_SIZE,
            )
        finally:
            self.eqc_client.release_lock(lock_id=lock_id)

    def test_solve_sum_constrained_and_fetch_results_batched_samples_non_distilled(
        self,
    ):
        try:
            print("Process job tests with batched samples for non-distilled solution")
            lock_id, _, _ = self.eqc_client.wait_for_lock()
            solve_sum_constrained_output = self.eqc_client.solve_sum_constrained(
                poly_indices=self.poly_indices,
                poly_coefficients=self.poly_coefficients,
                relaxation_schedule=1,
                sum_constraint=40,
                lock_id=lock_id,
                num_samples=self.num_samples,
            )
            self.assertEqual(solve_sum_constrained_output["err_code"], 0)
            job_result = self.eqc_client.fetch_sum_constrained_result(lock_id=lock_id)
            self.assertEqual(job_result["err_code"], 0)
            self.assertEqual(job_result["err_desc"], "Success")
            self.assertEqual(job_result["num_samples"], self.num_samples)
            self.assertEqual(job_result["num_variables"], self.num_variables)
            self.assertTrue(job_result["preprocessing_time"] > 0)
            self.assertIsInstance(job_result["calibration_time"], float)
            self.assertTrue(len(job_result["postprocessing_time"]) == self.num_samples)
            self.assertTrue(len(job_result["runtime"]) == self.num_samples)
            self.assertTrue(len(job_result["energy"]) == self.num_samples)
            self.assertTrue(len(job_result["solution"]) == self.num_samples)
            self.assertTrue(len(job_result["distilled_energy"]) == 0)
            self.assertTrue(len(job_result["distilled_solution"]) == 0)
            for k in range(self.num_samples):
                self.assertTrue(job_result["runtime"][k] > 0)
                self.assertIsInstance(job_result["energy"][k], float)
                self.assertIsInstance(job_result["postprocessing_time"][k], float)
                self.assertTrue(len(job_result["solution"][k]), self.num_variables)
        finally:
            self.eqc_client.release_lock(lock_id=lock_id)

    def test_solve_sum_constrained_and_fetch_results_batched_samples_distilled(self):
        try:
            print("Process job tests with batched samples for distilled solution")
            lock_id, _, _ = self.eqc_client.wait_for_lock()
            solve_sum_constrained_output = self.eqc_client.solve_sum_constrained(
                poly_indices=self.poly_indices,
                poly_coefficients=self.poly_coefficients,
                relaxation_schedule=1,
                sum_constraint=40,
                solution_precision=0.1,
                lock_id=lock_id,
                num_samples=self.num_samples,
            )
            self.assertEqual(solve_sum_constrained_output["err_code"], 0)
            job_result = self.eqc_client.fetch_sum_constrained_result(lock_id=lock_id)
            print("BATCH RESULT:", job_result)
            self.assertEqual(job_result["err_code"], 0)
            self.assertEqual(job_result["err_desc"], "Success")
            self.assertEqual(job_result["num_samples"], self.num_samples)
            self.assertEqual(job_result["num_variables"], self.num_variables)
            self.assertTrue(job_result["preprocessing_time"] > 0)
            self.assertIsInstance(job_result["calibration_time"], float)
            self.assertTrue(len(job_result["postprocessing_time"]) == self.num_samples)
            self.assertTrue(len(job_result["runtime"]) == self.num_samples)
            self.assertTrue(len(job_result["energy"]) == self.num_samples)
            self.assertTrue(len(job_result["solution"]) == self.num_samples)
            self.assertTrue(len(job_result["distilled_energy"]) == self.num_samples)
            self.assertTrue(len(job_result["distilled_solution"]) == self.num_samples)
            for k in range(self.num_samples):
                self.assertTrue(job_result["runtime"][k] > 0)
                self.assertIsInstance(job_result["postprocessing_time"][k], float)
                self.assertIsInstance(job_result["energy"][k], float)
                self.assertTrue(len(job_result["solution"][k]), self.num_variables)
                self.assertIsInstance(job_result["distilled_energy"][k], float)
                self.assertTrue(
                    len(job_result["distilled_solution"][k]), self.num_variables
                )
        finally:
            self.eqc_client.release_lock(lock_id=lock_id)

    def test_submit_job_and_fetch_results(self):
        try:
            print("Submit job tests")
            lock_id, _, _ = self.eqc_client.wait_for_lock()
            submit_output = self.eqc_client.submit_sum_constrained_job(
                poly_indices=self.poly_indices,
                poly_coefficients=self.poly_coefficients,
                relaxation_schedule=1,
                sum_constraint=40,
                lock_id=lock_id,
            )
            self.assertEqual(submit_output["err_code"], 0)
            while self.eqc_client.system_status()["status_code"] != 0:
                time.sleep(1)
            job_result = self.eqc_client.fetch_sum_constrained_result(lock_id=lock_id)
            print(job_result)
            self.assertEqual(job_result["err_code"], 0)
            print("assert desc")
            print("JOB RESULT", job_result)
            self.assertEqual(job_result["err_desc"], "Success")
            print("assert run")
            self.assertTrue(job_result["runtime"][0] >= 0)
            self.assertIsInstance(job_result["energy"][0], float)
            print("solution length")
            self.assertTrue(len(job_result["solution"][0]), 3)
            bad_res = self.eqc_client.fetch_sum_constrained_result(lock_id="bad")
            self.assertDictEqual(
                {"err_code": bad_res["err_code"], "err_desc": bad_res["err_desc"]},
                JobCodes.LOCK_MISMATCH,
            )
        finally:
            self.eqc_client.release_lock(lock_id=lock_id)

    def test_solve_sum_constrained(self):
        print("Test solve_sum_constrained")
        try:
            lock_id, _, _ = self.eqc_client.wait_for_lock()
            result = self.eqc_client.solve_sum_constrained(
                poly_indices=self.poly_indices,
                poly_coefficients=self.poly_coefficients,
                relaxation_schedule=1,
                sum_constraint=40,
                lock_id=lock_id,
            )
            print(result)
            self.assertEqual(len(result["solution"][0]), np.max(self.poly_indices))
            self.assertEqual(len(result["distilled_solution"]), 0)
        finally:
            self.eqc_client.release_lock(lock_id=lock_id)

    def test_solve_sum_constrained_submit_fail(self):
        print("Test solve_sum_constrained with bad lock")
        with self.assertRaises(RuntimeError):
            self.eqc_client.solve_sum_constrained(
                poly_indices=self.poly_indices,
                poly_coefficients=self.poly_coefficients,
                relaxation_schedule=1,
                sum_constraint=40,
                lock_id="bad_lock",
            )

    def test_submit_job_sum_constraint(self):
        print("test submit job sum constraint")
        lock_id, _, _ = self.eqc_client.wait_for_lock()
        try:
            result = self.eqc_client.submit_sum_constrained_job(
                poly_indices=self.poly_indices,
                poly_coefficients=self.poly_coefficients,
                relaxation_schedule=1,
                sum_constraint=-40,
                lock_id=lock_id,
            )
            print("Sum constraint:", result)
            self.assertDictEqual(
                result,
                JobCodes.INVALID_SUM_CONSTRAINT,
            )
            result = self.eqc_client.submit_sum_constrained_job(
                poly_indices=self.poly_indices,
                poly_coefficients=self.poly_coefficients,
                relaxation_schedule=1,
                sum_constraint=10001,
                lock_id=lock_id,
            )
            print("Sum constraint:", result)
            self.assertDictEqual(
                result,
                JobCodes.INVALID_SUM_CONSTRAINT,
            )

        finally:
            self.eqc_client.release_lock(lock_id=lock_id)

    def test_submit_job_invalid_precision(self):
        print("INVALID PRECISION")
        lock_id, _, _ = self.eqc_client.wait_for_lock()
        try:
            result = self.eqc_client.submit_sum_constrained_job(
                poly_indices=self.poly_indices,
                poly_coefficients=self.poly_coefficients,
                relaxation_schedule=1,
                sum_constraint=9999,
                solution_precision=0.1,
                lock_id=lock_id,
            )
            print("INVALID_PREC_RESULT", result)
            self.assertDictEqual(
                result,
                JobCodes.INVALID_PRECISION,
            )
        finally:
            self.eqc_client.release_lock(lock_id=lock_id)

    def test_submit_job_precision(self):
        print("Test solve_sum_constrained precision")
        lock_id, _, _ = self.eqc_client.wait_for_lock()
        try:
            result = self.eqc_client.solve_sum_constrained(
                poly_indices=self.poly_indices,
                poly_coefficients=self.poly_coefficients,
                relaxation_schedule=1,
                sum_constraint=2.4,
                solution_precision=0.24,
                lock_id=lock_id,
            )
        finally:
            self.eqc_client.release_lock(lock_id=lock_id)

    def test_submit_job_precision_constraint_mismatch(self):
        print("Test constraint precision mismatch")
        lock_id, _, _ = self.eqc_client.wait_for_lock()
        try:
            result = self.eqc_client.submit_sum_constrained_job(
                poly_indices=self.poly_indices,
                poly_coefficients=self.poly_coefficients,
                relaxation_schedule=1,
                sum_constraint=1,
                solution_precision=0.11,
                lock_id=lock_id,
            )
            self.assertDictEqual(
                result,
                JobCodes.PRECISION_CONSTRAINT_MISMATCH,
            )
        finally:
            self.eqc_client.release_lock(lock_id=lock_id)

    def test_submit_job_decreasing_index(self):
        print("Test decreasing")
        lock_id, _, _ = self.eqc_client.wait_for_lock()
        try:
            result = self.eqc_client.submit_sum_constrained_job(
                poly_indices=np.array([[1, 0], [0, 1]]),
                poly_coefficients=np.array([1, 1], dtype=np.float32),
                relaxation_schedule=1,
                sum_constraint=1,
                solution_precision=0.1,
                lock_id=lock_id,
            )
            self.assertDictEqual(
                result,
                JobCodes.DECREASING_INDEX,
            )
        finally:
            self.eqc_client.release_lock(lock_id=lock_id)

    def test_warn_below_recommended_soln_precision(self):
        print("Precision warn below")
        high_prec_coefs = np.random.normal(size=8)
        lock_id, _, _ = self.eqc_client.wait_for_lock()
        with self.assertWarns(
            Warning,
            msg="Minimum recommended levels (sum_constraint/solution_precision) is 200",
        ):
            try:
                result = self.eqc_client.solve_sum_constrained(
                    poly_indices=self.poly_indices,
                    poly_coefficients=high_prec_coefs,
                    relaxation_schedule=1,
                    sum_constraint=100,
                    solution_precision=1,
                    lock_id=lock_id,
                )
            finally:
                self.eqc_client.release_lock(lock_id=lock_id)

    def test_precision_warning(self):
        print("Precision warn")
        high_prec_coefs = np.random.normal(size=8)
        lock_id, _, _ = self.eqc_client.wait_for_lock()
        with self.assertWarns(
            Warning,
            msg="Max precision for EQC device is float32 input type was float64. Input matrix will be rounded",
        ):
            try:
                result = self.eqc_client.solve_sum_constrained(
                    poly_indices=self.poly_indices,
                    poly_coefficients=high_prec_coefs,
                    relaxation_schedule=1,
                    sum_constraint=200,
                    solution_precision=1,
                    lock_id=lock_id,
                )
            finally:
                self.eqc_client.release_lock(lock_id=lock_id)

    def test_integer_conversion_soln(self):
        print("Test Integer")
        try:
            lock_id, _, _ = self.eqc_client.wait_for_lock()
            result = self.eqc_client.solve_sum_constrained(
                poly_indices=self.poly_indices,
                poly_coefficients=self.poly_coefficients,
                relaxation_schedule=1,
                sum_constraint=100,
                lock_id=lock_id,
                solution_precision=1,
            )
            print(result)
            all([val.is_integer() for val in result["solution"][0]])
        finally:
            self.eqc_client.release_lock(lock_id=lock_id)

    def test_precision_soln(self):
        print("Test Continuous Solution")
        try:
            lock_id, _, _ = self.eqc_client.wait_for_lock()
            prec_val = 0.01
            result = self.eqc_client.solve_sum_constrained(
                poly_indices=self.poly_indices,
                poly_coefficients=self.poly_coefficients,
                relaxation_schedule=1,
                sum_constraint=100,
                lock_id=lock_id,
                solution_precision=prec_val,
            )
            print(result)
            print(result["distilled_solution"])
            all([(val / prec_val).is_integer() for val in result["solution"][0]])
        finally:
            self.eqc_client.release_lock(lock_id=lock_id)

    def test_invalid_schedule(self):
        print("invalid schedule")
        try:
            lock_id, _, _ = self.eqc_client.wait_for_lock()
            result = self.eqc_client.submit_sum_constrained_job(
                poly_indices=self.poly_indices,
                poly_coefficients=self.poly_coefficients,
                relaxation_schedule=10,
                sum_constraint=100,
                lock_id=lock_id,
                solution_precision=1,
            )
            self.assertDictEqual(result, JobCodes.INVALID_RELAXATION_SCHEDULE)
        finally:
            self.eqc_client.release_lock(lock_id=lock_id)

    def test_lock_mismatch(self):
        print("lock_mismatch")
        try:
            lock_id, _, _ = self.eqc_client.wait_for_lock()
            result = self.eqc_client.submit_sum_constrained_job(
                poly_indices=self.poly_indices,
                poly_coefficients=self.poly_coefficients,
                relaxation_schedule=1,
                sum_constraint=100,
                solution_precision=1,
                lock_id="a bad lock",
            )
            self.assertDictEqual(result, JobCodes.LOCK_MISMATCH)
        finally:
            self.eqc_client.release_lock(lock_id=lock_id)

    def test_submit_job_precision_default(self):
        print("Test solve_sum_constrained precision default")
        lock_id, _, _ = self.eqc_client.wait_for_lock()
        try:
            result = self.eqc_client.solve_sum_constrained(
                poly_indices=self.poly_indices,
                poly_coefficients=self.poly_coefficients,
                relaxation_schedule=1,
                sum_constraint=2.4,
                lock_id=lock_id,
            )
        finally:
            self.eqc_client.release_lock(lock_id=lock_id)

    def test_solve_sum_constrained_precision_long_decimal(self):
        print("Test solve_sum_constrained precision long decimal")
        lock_id, _, _ = self.eqc_client.wait_for_lock()
        try:
            result = self.eqc_client.solve_sum_constrained(
                poly_indices=self.poly_indices,
                poly_coefficients=self.poly_coefficients,
                relaxation_schedule=1,
                sum_constraint=37.2515,
                solution_precision=0.372515,
                lock_id=lock_id,
            )
        finally:
            self.eqc_client.release_lock(lock_id=lock_id)

    def test_warn_soln_precision_exceeds_decimal(self):
        print("Test submit job precision_exceeds decimal")
        lock_id, _, _ = self.eqc_client.wait_for_lock()
        try:
            with self.assertWarns(Warning) as cm:
                result = self.eqc_client.submit_sum_constrained_job(
                    poly_indices=self.poly_indices,
                    poly_coefficients=self.poly_coefficients,
                    relaxation_schedule=1,
                    sum_constraint=500.25151278,
                    solution_precision=0.50025151278,
                    lock_id=lock_id,
                )
            self.assertEqual(2, len(cm.warnings))
            self.assertEqual(
                "`solution_precision`precision is greater than 7 decimal places. Will be modified on submission to device to float32 precision",
                str(cm.warnings[0].message),
            )
            self.assertEqual(
                "`sum_constraint` precision is greater than 7 decimal places. Will be modified on submission to device to float32",
                str(cm.warnings[1].message),
            )
        finally:
            self.eqc_client.release_lock(lock_id=lock_id)

    def test_no_warnings_solve_sum_constrained(self):
        print("test no warnings solve_sum_constrained")
        lock_id, _, _ = self.eqc_client.wait_for_lock()
        try:
            with warnings.catch_warnings(record=True) as warnings_log:
                result = self.eqc_client.solve_sum_constrained(
                    poly_indices=self.poly_indices,
                    poly_coefficients=self.poly_coefficients,
                    relaxation_schedule=1,
                    sum_constraint=500,
                    solution_precision=1,
                    lock_id=lock_id,
                )
            self.assertEqual([], warnings_log)
        finally:
            self.eqc_client.release_lock(lock_id=lock_id)

    def test_solve_integer_num_levels_out_of_range(self):
        print("Test test_solve_integer_num_levels_out_of_range")
        print("LEVELS", np.arange(self.num_variables, dtype=np.int32) + 1)
        try:
            lock_id, _, _ = self.eqc_client.wait_for_lock()
            with self.assertRaises(RuntimeError) as context:
                self.eqc_client.solve_integer(
                    poly_coefficients=self.poly_coefficients,
                    poly_indices=self.poly_indices,
                    lock_id=lock_id,
                    relaxation_schedule=1,
                    num_levels=np.arange(self.num_variables, dtype=np.int32) + 1,
                )

            self.assertEqual(
                str(context.exception),
                "Submission failed with response: {'err_code': 18, 'err_desc': "
                + "'All elements of input `num_levels` must be greater than 1'}",
            )
        finally:
            self.eqc_client.release_lock(lock_id=lock_id)

    def test_solve_integer(self):
        print("Test solve_integer:", np.arange(self.num_variables, dtype=np.int32) + 2)
        try:
            lock_id, _, _ = self.eqc_client.wait_for_lock()
            result = self.eqc_client.solve_integer(
                poly_coefficients=self.poly_coefficients,
                poly_indices=self.poly_indices,
                lock_id=lock_id,
                relaxation_schedule=1,
                num_levels=np.arange(self.num_variables, dtype=np.int32) + 2,
            )
            print(result)

            for solution in result["solution"]:
                self.assertTrue(
                    # Solutions should be integers with type float32. The integers should be
                    # small enough in magnitude so that they are still exactly represented.
                    all([val.is_integer() for val in solution])
                )
        finally:
            self.eqc_client.release_lock(lock_id=lock_id)

    def test_solve_integer_binary_optimization_via_scalar_num_levels(self):
        print("Test test_solve_integer_binary_optimization_via_scalar_num_levels")
        try:
            lock_id, _, _ = self.eqc_client.wait_for_lock()
            result = self.eqc_client.solve_integer(
                poly_coefficients=self.poly_coefficients,
                poly_indices=self.poly_indices,
                lock_id=lock_id,
                relaxation_schedule=1,
                num_levels=np.array(2, dtype=np.int32),  # Binary optimization.
            )
            print(result)
            self.assertTrue(
                # Solutions should be integers with type float32. The integers should be
                # small enough in magnitude so that they are still exactly represented.
                all([val in (0, 1) for val in result["solution"][0]])
            )
        finally:
            self.eqc_client.release_lock(lock_id=lock_id)

    def test_solve_integer_num_levels_raise_not_int(self):
        print("test num levels must be int")
        try:
            lock_id, _, _ = self.eqc_client.wait_for_lock()
            with self.assertRaises(ValueError) as context:
                self.eqc_client.solve_integer(
                    poly_coefficients=self.poly_coefficients,
                    poly_indices=self.poly_indices,
                    lock_id=lock_id,
                    relaxation_schedule=1,
                    num_levels=2.1,
                )

            self.assertEqual(str(context.exception), "`num_levels` must be type int")
        finally:
            self.eqc_client.release_lock(lock_id=lock_id)

    def test_integer_solve_levels_invalid(self):
        print("Test test_solve_integer levels invalid")
        try:
            lock_id, _, _ = self.eqc_client.wait_for_lock()
            with self.assertRaises(RuntimeError) as context:
                self.eqc_client.solve_integer(
                    poly_coefficients=self.poly_coefficients,
                    poly_indices=self.poly_indices,
                    lock_id=lock_id,
                    relaxation_schedule=1,
                    num_levels=1,
                    mean_photon_number=2,
                    quantum_fluctuation_coefficient=1,
                )

            self.assertEqual(
                str(context.exception),
                "Submission failed with response: {'err_code': 18, 'err_desc': "
                + "'All elements of input `num_levels` must be greater than 1'}",
            )
        finally:
            self.eqc_client.release_lock(lock_id=lock_id)

    def test_integer_solve_mean_photon_number_invalid(self):
        print("Test test_solve_integer mean_photon_number invalid")
        try:
            lock_id, _, _ = self.eqc_client.wait_for_lock()
            with self.assertRaises(RuntimeError) as context:
                self.eqc_client.solve_integer(
                    poly_coefficients=self.poly_coefficients,
                    poly_indices=self.poly_indices,
                    lock_id=lock_id,
                    relaxation_schedule=1,
                    mean_photon_number=2.01,
                    quantum_fluctuation_coefficient=1,
                    num_levels=np.arange(self.num_variables, dtype=np.int32) + 2,
                )

            self.assertEqual(
                str(context.exception),
                "Submission failed with response: {'err_code': 20, 'err_desc': "
                + "'Mean photon number if specified must be in range [0.0000667, 0.0066666]'}",
            )
        finally:
            self.eqc_client.release_lock(lock_id=lock_id)

    def test_integer_solve_mean_photon_number_invalid(self):
        print("Test test_solve_integer quantum_fluctuation_coefficient invalid")
        try:
            lock_id, _, _ = self.eqc_client.wait_for_lock()
            with self.assertRaises(RuntimeError) as context:
                self.eqc_client.solve_integer(
                    poly_coefficients=self.poly_coefficients,
                    poly_indices=self.poly_indices,
                    lock_id=lock_id,
                    num_levels=2,
                    relaxation_schedule=1,
                    mean_photon_number=2,
                    quantum_fluctuation_coefficient=51,
                )

            self.assertEqual(
                str(context.exception),
                "Submission failed with response: {'err_code': 21, 'err_desc': "
                + "Quantum fluctuation coefficient if specified must be in range [1, 50]'}",
            )
        finally:
            self.eqc_client.release_lock(lock_id=lock_id)

    def test_integer_solve_check_edge_mph_nlr(self):
        print("Test test_solve_integer quantum_fluctuation_coefficient invalid")
        try:
            lock_id, _, _ = self.eqc_client.wait_for_lock()
            x1 = self.eqc_client.solve_integer(
                poly_coefficients=self.poly_coefficients,
                poly_indices=self.poly_indices,
                lock_id=lock_id,
                relaxation_schedule=1,
                num_levels=3,
                mean_photon_number=0.0000666,
                quantum_fluctuation_coefficient=1,
            )
            print("INTEGER EDGE", x1)
            x2 = self.eqc_client.solve_integer(
                poly_coefficients=self.poly_coefficients,
                poly_indices=self.poly_indices,
                lock_id=lock_id,
                num_levels=4,
                relaxation_schedule=1,
                mean_photon_number=0.00666666,
                quantum_fluctuation_coefficient=50,
            )
        finally:
            self.eqc_client.release_lock(lock_id=lock_id)

    def test_integer_solve_mean_photon_number_invalid(self):
        print("Test test_solve_integer mean_photon_number invalid")
        try:
            lock_id, _, _ = self.eqc_client.wait_for_lock()
            with self.assertRaises(RuntimeError) as context:
                self.eqc_client.solve_integer(
                    poly_coefficients=self.poly_coefficients,
                    poly_indices=self.poly_indices,
                    lock_id=lock_id,
                    relaxation_schedule=1,
                    num_levels=2,
                    mean_photon_number=0.0066667,
                    quantum_fluctuation_coefficient=0.1,
                )

            self.assertEqual(
                str(context.exception),
                "Submission failed with response: {'err_code': 18, 'err_desc': "
                + "'All elements of input `num_levels` must be greater than 0'}",
            )
        finally:
            self.eqc_client.release_lock(lock_id=lock_id)

    def test_integer_solve_mean_photon_number_invalid(self):
        print("Test test_solve_integer mean_photon_number invalid")
        try:
            lock_id, _, _ = self.eqc_client.wait_for_lock()
            with self.assertRaises(RuntimeError) as context:
                self.eqc_client.solve_integer(
                    poly_coefficients=self.poly_coefficients,
                    poly_indices=self.poly_indices,
                    lock_id=lock_id,
                    relaxation_schedule=1,
                    mean_photon_number=0.0066668,
                    quantum_fluctuation_coefficient=1,
                    num_levels=[2] * self.num_variables,
                )

            self.assertEqual(
                str(context.exception),
                "Submission failed with response: {'err_code': 20, 'err_desc': "
                + "'Mean photon number if specified must be in range [0.0000667, 0.0066666]'}",
            )
        finally:
            self.eqc_client.release_lock(lock_id=lock_id)

    def test_sum_constrained_mean_qf_invalid(self):
        print("Test test_solve_integer quantum_fluctuation_coefficient invalid")
        try:
            lock_id, _, _ = self.eqc_client.wait_for_lock()
            with self.assertRaises(RuntimeError) as context:
                self.eqc_client.solve_sum_constrained(
                    poly_coefficients=self.poly_coefficients,
                    poly_indices=self.poly_indices,
                    lock_id=lock_id,
                    relaxation_schedule=2,
                    mean_photon_number=0.0066,
                    quantum_fluctuation_coefficient=101,
                )

            self.assertEqual(
                str(context.exception),
                "Submission failed with response: {'err_code': 21, 'err_desc': "
                + "'Quantum fluctuation coefficient if specified must be in range [1, 100]'}",
            )
        finally:
            self.eqc_client.release_lock(lock_id=lock_id)

    def test_sum_constrained_solve_check_edge_mph_nlr(self):
        print("Test test_solve_integer quantum_fluctuation_coefficient invalid")
        try:
            lock_id, _, _ = self.eqc_client.wait_for_lock()
            x1 = self.eqc_client.solve_sum_constrained(
                poly_coefficients=self.poly_coefficients,
                poly_indices=self.poly_indices,
                lock_id=lock_id,
                relaxation_schedule=1,
                mean_photon_number=0.0000667,
                quantum_fluctuation_coefficient=1,
            )
            print("MPN EDGE", x1)
            x2 = self.eqc_client.solve_sum_constrained(
                poly_coefficients=self.poly_coefficients,
                poly_indices=self.poly_indices,
                lock_id=lock_id,
                relaxation_schedule=1,
                mean_photon_number=0.0066666,
                quantum_fluctuation_coefficient=50,
            )
            print(x2)
        finally:
            self.eqc_client.release_lock(lock_id=lock_id)
