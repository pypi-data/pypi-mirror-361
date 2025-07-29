import time

import numpy as np

from eqc_direct.eqc_client import EqcClient
from eqc_direct.utils import convert_hamiltonian_to_poly_format


def run_single():
    eqc_client = EqcClient()
    ham_mat = np.load("enlight8_alpha1.0.npy")
    poly_idx, poly_coef = convert_hamiltonian_to_poly_format(
        linear_terms=ham_mat[:, 0], quadratic_terms=ham_mat[:, 1:]
    )
    start = time.time()
    lock_id, start_ts, end_ts = eqc_client.wait_for_lock()

    resp = eqc_client.solve_sum_constrained(
        poly_coefficients=poly_coef,
        poly_indices=poly_idx,
        sum_constraint=100,
        relaxation_schedule=2,
        solution_precision=1,
        lock_id=lock_id,
    )

    eqc_client.release_lock(lock_id=lock_id)
    print("Execution time:", time.time() - start)
    print(resp)


if __name__ == "__main__":
    run_single()
