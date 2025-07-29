"""
Integration test for running parallel jobs
This is kept separate from unittest because of
undefined behavior when running unittests on thread leads to
InactiveRPC error even though server is running and available.
"""
import concurrent.futures
import time

import numpy as np

from eqc_direct.client import EqcClient
from eqc_direct.utils import convert_hamiltonian_to_poly_format


def run_eqc_job(n):
    print("N input:", n)
    h = np.random.normal(size=(n, 1)).astype(np.float32)
    J = np.random.normal(size=(n, n)).astype(np.float32)
    ham_mat = np.hstack((h, J + J.T))
    print(ham_mat)
    poly_indices, poly_coefficients = convert_hamiltonian_to_poly_format(
        linear_terms=np.squeeze(ham_mat[:, 0]),
        quadratic_terms=ham_mat[:, 1:],
    )
    start = time.time()
    eqc_client = EqcClient()
    lock_id, start_ts, end_ts = eqc_client.wait_for_lock()
    print("Lock:", lock_id)
    resp = eqc_client.solve_sum_constrained(
        poly_coefficients=poly_coefficients, poly_indices=poly_indices, lock_id=lock_id
    )
    eqc_client.release_lock(lock_id=lock_id)
    print("Time Job:", time.time() - start)
    print("Time_Queue:", (end_ts - start_ts) / (10**9))
    print("Time_Run:", (resp["end_job_ts"] - resp["start_job_ts"]) / 10**9)
    print("Matches input:", n == len(resp["solution"][0]))
    print("N returned", len(resp["solution"][0]))
    return n == len(resp["solution"][0])


if __name__ == "__main__":
    # max problem size is 949
    n_jobs = 10
    start = time.time()
    prob_sizes = np.random.randint(20, 949, size=n_jobs).tolist()
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as process_pool:
        x = list(process_pool.map(run_eqc_job, prob_sizes))
    print("Matched return:", x)
    print("TOTAL TIME:", time.time() - start)
