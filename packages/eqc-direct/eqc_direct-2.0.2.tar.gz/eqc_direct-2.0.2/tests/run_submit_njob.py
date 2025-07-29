import sys

import numpy as np

from eqc_direct.client import EqcClient
from eqc_direct.utils import convert_hamiltonian_to_poly_format


def run_single(nvars):
    np.random.seed(13)
    ham_mat = -1 * np.abs(np.random.normal(size=(nvars, nvars + 1)))
    print(ham_mat)
    print(ham_mat.shape)
    poly_indices, poly_coefficients = convert_hamiltonian_to_poly_format(
        linear_terms=np.squeeze(ham_mat[:, 0]),
        quadratic_terms=ham_mat[:, 1:],
    )
    eqc_client = EqcClient()
    lock_id, _, _ = eqc_client.wait_for_lock()
    print("Lock:", lock_id)
    resp = eqc_client.solve_sum_constrained(
        poly_coefficients=poly_coefficients,
        poly_indices=poly_indices,
        sum_constraint=1,
        lock_id=lock_id,
        num_samples=3,
    )
    print(resp)


if __name__ == "__main__":
    # Default num_variables is 5.
    nvars = int((sys.argv[1:2] or ["5"])[0])
    run_single(nvars=nvars)
