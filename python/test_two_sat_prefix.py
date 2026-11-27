import unittest
from itertools import product

from two_sat_prefix import TwoCNF


def models(width, clauses):
    return [bits for bits in product((0, 1), repeat=width)
            if all(any(bits[abs(lit) - 1] == (lit > 0) for lit in clause)
                   for clause in clauses)]


def satisfies_rows(bits, rows):
    return all(sum(x * a for x, a in zip(bits, row[:-1])) % 2 == row[-1] for row in rows)


class TwoSATPrefixTests(unittest.TestCase):
    def check_all_prefixes(self, width, clauses):
        formula = TwoCNF(width, clauses)
        witnesses = models(width, clauses)
        assignments = list(product((0, 1), repeat=width))
        for length in range(width + 1):
            for prefix in product((0, 1), repeat=length):
                expected = [w for w in witnesses if w[:length] == prefix]
                rows = formula.prefix_rows(prefix)
                self.assertEqual(any(satisfies_rows(v, rows) for v in assignments), bool(expected))
                self.assertEqual(formula.select(prefix), expected[0] if expected else None)

    def test_all_normalized_two_variable_formulas(self):
        clauses = [(1,), (-1,), (2,), (-2,), *product((1, -1), (2, -2))]
        for included in product((False, True), repeat=len(clauses)):
            self.check_all_prefixes(2, [c for use, c in zip(included, clauses) if use])

    def test_closure_component_and_boundary_cases(self):
        self.check_all_prefixes(4, [(-1, 3), (-3, 4), (-4, -2)])
        self.check_all_prefixes(4, [(-2, -3), (3, 4), (-4, 2), (4,), (-2,)])
        self.check_all_prefixes(3, [(2, -2), (1, 1), (1, 1)])
        self.check_all_prefixes(0, [])
        self.check_all_prefixes(0, [()])
        self.check_all_prefixes(2, [(1, 2), ()])

    def test_affine_point_can_require_prefix_reconstruction(self):
        formula = TwoCNF(2, [(1, 2)])
        self.assertTrue(satisfies_rows((0, 0), formula.prefix_rows(())))
        self.assertEqual(formula.select(), (0, 1))
        self.assertFalse(formula.prefix_extends((0, 0)))

    def test_invalid_inputs(self):
        for clauses in [((1, 2, 3),), ((0,),), ((-3,),)]:
            with self.assertRaises(ValueError):
                TwoCNF(2, clauses)
        for prefix in [(2,), (0, 1, 0)]:
            with self.assertRaises(ValueError):
                TwoCNF(2, []).select(prefix)


if __name__ == "__main__":
    unittest.main()
