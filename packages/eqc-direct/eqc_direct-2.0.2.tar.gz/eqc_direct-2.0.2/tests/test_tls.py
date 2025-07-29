import os
import threading
import time
import unittest
import warnings

import numpy as np
from grpc_server_cls import ServerForTest
from eqc_direct.client import EqcClient
from eqc_direct.server_sim import GrpcServer
from eqc_direct.utils import JobCodes, LockCheckStatus, LockManageStatus


class TestEqcClient(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_ip_addr = "localhost"
        # only instantiate server if running on localhost
        cls.server = ServerForTest(
            ip_address=cls.test_ip_addr,
            port="50051",
            private_key="private.pem",
            cert_file="certificate.pem",
        )
        cls.server.start()
        cls.eqc_client = EqcClient(
            ip_address=cls.test_ip_addr, cert_file="certificate.pem"
        )
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

    def test_system_info(self):
        version_resp = self.eqc_client.system_info()
        print("VERSION", version_resp)
        self.assertIsInstance(version_resp["server_version"], str)
        self.assertIsInstance(version_resp["device_type"], str)

    def test_system_status(self):
        sys_resp = self.eqc_client.system_status()
        self.assertListEqual(list(sys_resp.keys()), ["status_code", "status_desc"])
        self.assertIsInstance(sys_resp["status_code"], int)
        self.assertIsInstance(sys_resp["status_desc"], str)

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
            self.assertTrue(len(job_result["postprocessing_time"]), self.num_samples)
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
