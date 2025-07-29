import time

import numpy as np

from eqc_direct.client import EqcClient
from eqc_direct.utils import convert_hamiltonian_to_poly_format


def run_stop_job(n):
    print("N size:", n)
    h = np.random.normal(size=(n, 1))
    J = np.random.normal(size=(n, n))
    ham_mat = np.hstack((h, J + J.T)).astype(np.float32)
    poly_indices, poly_coefficients = convert_hamiltonian_to_poly_format(
        linear_terms=np.squeeze(ham_mat[:, 0]),
        quadratic_terms=ham_mat[:, 1:],
    )
    eqc_client = EqcClient()
    lock_id, _, _ = eqc_client.wait_for_lock()
    print("Lock:", lock_id)
    print("Submit Job")
    resp = eqc_client.submit_sum_constrained_job(
        poly_coefficients=poly_coefficients,
        poly_indices=poly_indices,
        sum_constraint=100,
        lock_id=lock_id,
    )
    print("Resp Job", resp)
    try:
        stop_message = eqc_client.stop_running_process(lock_id=lock_id)
        print("stop_message", stop_message)
    finally:
        lock_status = eqc_client.release_lock(lock_id=lock_id)
    print("Lock status", lock_status)
    return stop_message


if __name__ == "__main__":
    n = 900
    x = run_stop_job(n=n)

    print("Matched return:", x)
