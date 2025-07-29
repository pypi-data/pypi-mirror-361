import unittest
import numpy as np
from eqc_direct.utils import (
    convert_hamiltonian_to_poly_format,
    get_decimal_places,
)


class TestUtils(unittest.TestCase):
    def test_convert_hamiltonian_to_poly_format(self):
        n = 5
        lin_terms = np.random.normal(size=n)
        quad_terms = np.random.normal(size=(n, n))
        quad_terms = quad_terms.T + quad_terms
        indices, coefs = convert_hamiltonian_to_poly_format(
            linear_terms=lin_terms, quadratic_terms=quad_terms
        )

        n_terms = (n**2 - n) / 2 + 2 * n
        self.assertEqual(n_terms, len(indices))
        self.assertEqual(n_terms, len(coefs))
        for i in range(len(indices)):
            idx = indices[i]
            if idx[0] == 0:
                term_iter = lin_terms[idx[1] - 1]
            elif idx[0] == idx[1]:
                term_iter = quad_terms[idx[0] - 1, idx[1] - 1]
            elif idx[0] != idx[1]:
                term_iter = quad_terms[idx[0] - 1, idx[1] - 1] * 2
            self.assertEqual(coefs[i], term_iter)

    def test_get_decimal_places(self):
        dec_5 = 1.23458
        dec_7 = 1.45678910
        dec_8 = 1.45678911
        dec_0 = 1
        dec_3_0 = 3.0
        self.assertEqual(get_decimal_places(dec_5), 5)
        self.assertEqual(get_decimal_places(dec_7), 7)
        self.assertEqual(get_decimal_places(dec_8), 8)
        self.assertEqual(get_decimal_places(dec_0), 0)
        self.assertEqual(get_decimal_places(dec_3_0), 0)
