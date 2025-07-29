"""
From https://qplib.zib.de/. Best known solution is:
[
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.209636569541294, 0.0, 0.0, 0.275230558068530, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.226997921553671, 0.0, 0.288134950836505, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0
]
with energy -6.386014981598350.
"""

import time

import numpy as np

from eqc_direct.client import EqcClient
from eqc_direct.utils import convert_hamiltonian_to_poly_format


def run_single():
    eqc_client = EqcClient()
    ham_mat = np.loadtxt("QPLIB_0018_OBJ.csv", delimiter=",", dtype=float)
    poly_idx, poly_coef = convert_hamiltonian_to_poly_format(
        linear_terms=ham_mat[:, 0], quadratic_terms=ham_mat[:, 1:]
    )
    start = time.time()
    lock_id, start_ts, end_ts = eqc_client.wait_for_lock()

    resp = eqc_client.solve_sum_constrained(
        poly_indices=poly_idx,
        poly_coefficients=poly_coef,
        relaxation_schedule=1,
        sum_constraint=1,
        lock_id=lock_id,
    )

    eqc_client.release_lock(lock_id=lock_id)
    print("Execution time:", time.time() - start)
    print(resp)


if __name__ == "__main__":
    run_single()
