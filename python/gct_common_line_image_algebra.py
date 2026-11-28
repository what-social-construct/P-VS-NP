"""Recover the fixed-face quadratic cuts and test their norms on the vertex quotient.

Input rows are x0,x1,y0,y1,y2,G2,G3,G4 with Y=sum(y)=1. Entries are
little-endian base-five digits in F5[w]/(w^7+3w+3). G2,... are the three
normalized sections computed from the polar cofactor and its quadrics.
"""

import argparse
import json
from itertools import combinations, combinations_with_replacement, permutations, product
from pathlib import Path

import numpy as np
import sympy as sp
from flint import nmod_mat, nmod_poly
from sympy.polys.groebnertools import groebner
from sympy.polys.rings import ring

from gct_collision_slice import kernel_from_edges
from gct_permanent_plucker import pencil_coefficients


ORDERS = tuple(permutations(range(3)))
WEIGHTS = (336, 344, 352)


def vertices(variables, edge_sum):
    x0, x1, y0, y1 = variables
    return (x0, x1, -x0-x1), (y0, y1, edge_sum-y0-y1)


def pure_equations(algebra, x, y):
    edges = (y[2], x[0], y[1], x[1], y[0], x[2])
    coefficients = pencil_coefficients(algebra, (kernel_from_edges(edges),))
    return [coefficients[k, 0, 0] for k in (2, 3, 4)]


def orbit_sum(x, y, exponents):
    a, b, c, d = exponents
    return sum(x[i]**a * x[j]**b * y[i]**c * y[j]**d for i, j, _ in ORDERS)


def secondary_basis(algebra, variables):
    """Compute homogeneous Reynolds generators modulo the parameters Y and q."""
    x, y = vertices(variables, algebra.zero)
    relations = pure_equations(algebra, x, y) + [x[0]*x[1]*x[2]]
    basis = groebner(relations, algebra)
    leading = [g.LM for g in basis]
    bounds = [min(m[i] for m in leading if m[i] and m[i] == sum(m)) for i in range(4)]
    standard = sorted((m for m in product(*(range(n) for n in bounds))
                       if not any(all(a >= b for a, b in zip(m, lm)) for lm in leading)),
                      key=lambda m: (sum(m), m))
    assert len(standard) == 72
    images = [orbit_sum(x, y, m).rem(basis) for m in standard]
    matrix = nmod_mat([[int(f.get(m, 0)) for f in images] for m in standard], 5)
    rows, rank = matrix.rref()
    assert rank == 12
    pivots = [next(j for j in range(len(standard)) if rows[i, j]) for i in range(rank)]
    secondary = [standard[j] for j in pivots]
    assert [sum(m) for m in secondary] == [0, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 8]
    return secondary


def basis_indices(secondary, bound):
    return [(i, j) for i, m in enumerate(secondary)
            for j in range((bound-sum(m))//3 + 1)]


def multiplication_table(algebra, variables, secondary):
    """Expand all secondary products exactly on the affine pure curve Y=1."""
    x, y = vertices(variables, algebra.one)
    pure = pure_equations(algebra, x, y)
    relations = groebner(pure, algebra)
    q = x[0]*x[1]*x[2]
    z = [orbit_sum(x, y, m).rem(relations) for m in secondary]
    bound = 2 * max(map(sum, secondary))
    indices = basis_indices(secondary, bound)
    monomials = [(q**j * z[i]).rem(relations) for i, j in indices]
    pairs = list(combinations_with_replacement(range(len(z)), 2))
    products = [(z[i]*z[j]).rem(relations) for i, j in pairs]
    polys = monomials + products
    powers = sorted(set().union(*(f.keys() for f in polys)))
    matrix = nmod_mat([[int(f.get(m, 0)) for f in polys] for m in powers], 5)
    rows, rank = matrix.rref()
    assert rank == len(indices) and all(rows[i, i] == 1 for i in range(rank))
    table = {}
    for k, (i, j) in enumerate(pairs):
        coefficients = [[0]*((bound-sum(m))//3 + 1) for m in secondary]
        for col, (h, degree) in enumerate(indices):
            a = int(rows[col, rank+k])
            assert not a or sum(secondary[h])+3*degree <= sum(secondary[i])+sum(secondary[j])
            coefficients[h][degree] = a
        table[i, j] = table[j, i] = [nmod_poly(v, 5) for v in coefficients]
    return table, pure


class SampleField:
    """Vectorized exact evaluation on the samples' degree-seven power basis."""

    def __init__(self):
        self.size = 5**7
        self.period = self.size-1
        self.log = np.full(self.size, -1, dtype=np.int32)
        self.exp = np.zeros(self.period, dtype=np.int32)
        a = 1
        for i in range(self.period):
            assert self.log[a] == -1
            self.log[a], self.exp[i] = i, a
            low = a % 5**6 * 5
            high = a // 5**6
            # Multiply by w and substitute w^7 = 2w + 2.
            a = low//25*25 + ((low//5+2*high) % 5)*5 + (2*high % 5)
        assert a == 1
        self.low_sum = self._digit_sum(3)
        self.high_sum = self._digit_sum(4)

    @staticmethod
    def _digit_sum(n):
        entry = np.arange(5**n, dtype=np.int32)
        return sum(((entry[:, None]//5**i + entry[None, :]//5**i) % 5)*5**i
                   for i in range(n))

    def add(self, a, b):
        return self.low_sum[a % 125, b % 125] + 125*self.high_sum[a//125, b//125]

    def mul(self, a, b):
        return np.where((a == 0) | (b == 0), 0, self.exp[(self.log[a]+self.log[b]) % self.period])

    def power(self, a, n):
        if n == 0:
            return np.ones_like(a)
        return np.where(a == 0, 0, self.exp[(self.log[a]*n) % self.period])


def sample_matrix(data, secondary, pure):
    """Expand each section evaluation into seven linear constraints over F5."""
    field = SampleField()
    assert data.ndim == 2 and data.shape[1] == 8 and np.all((0 <= data) & (data < field.size))
    # Validate with int64 before narrowing to the table's int32 indices. The
    # largest field multiplication index is 2*(5**7-2); powers use n <= 8.
    data = data.astype(np.int32)
    x0, x1, y0, y1, y2 = data[:, :5].T
    x = [x0, x1, field.mul(4, field.add(x0, x1))]
    y = [y0, y1, y2]
    assert all(np.all(x[i] != x[j]) for i, j in combinations(range(3), 2))
    assert np.all(field.add(field.add(y0, y1), y2) == 1)
    for f in pure:
        values = np.zeros_like(x0)
        for power, coefficient in f.items():
            term = int(coefficient) % 5
            for a, n in zip((x0, x1, y0, y1), power):
                term = field.mul(term, field.power(a, n))
            values = field.add(values, term)
        assert np.all(values == 0)

    # An unordered triple of (incident, opposite) pairs identifies an S3 orbit at Y=1.
    conjugates = set()
    pairs = list(zip(x, y))
    for _ in range(7):
        rows = zip(*(zip(a, b) for a, b in pairs))
        conjugates.update(tuple(sorted(row)) for row in rows)
        pairs = [(field.power(a, 5), field.power(b, 5)) for a, b in pairs]
    # Six labeled points per orbit. A nonzero degree-d section has 24d zeros
    # counted with multiplicity on the geometrically integral pure curve.
    assert len(conjugates) == 7 * len(data)
    assert len(conjugates) > 4*max(WEIGHTS)
    q = field.mul(field.mul(x[0], x[1]), x[2])
    columns = []
    for m in secondary:
        a, b, c, d = m
        z = np.zeros_like(q)
        for i, j, _ in ORDERS:
            incident = field.mul(field.power(x[i], a), field.power(x[j], b))
            opposite = field.mul(field.power(y[i], c), field.power(y[j], d))
            z = field.add(z, field.mul(incident, opposite))
        for _ in range((max(WEIGHTS)-sum(m))//3+1):
            columns.append(z)
            z = field.mul(z, q)
    columns.extend(data[:, 5:].T)
    packed = np.column_stack(columns)
    digits = np.concatenate([(packed//5**i) % 5 for i in range(7)])
    return nmod_mat(*digits.shape, digits.ravel().tolist(), 5), len(conjugates)


def interpolate(data, secondary, pure):
    matrix, count = sample_matrix(data, secondary, pure)
    indices = basis_indices(secondary, max(WEIGHTS))
    n = len(indices)
    rows, rank = matrix.rref(inplace=True)
    assert rank == n == 1399 and all(rows[i, i] == 1 for i in range(n))
    result = []
    for k, weight in enumerate(WEIGHTS):
        coefficients = [[] for _ in secondary]
        for r, (i, j) in enumerate(indices):
            a = int(rows[r, n+k])
            assert not a or 3*j+sum(secondary[i]) <= weight
            coefficients[i].append(a)
        result.append([nmod_poly(v, 5) for v in coefficients])
    print(f"Verified three sections on {len(data)} degree-seven orbits "
          f"({count} geometric quotient points) with interpolation rank {rank}.")
    return result


def determinant(matrix):
    """Fraction-free determinant in F5[q], verifying every exact division."""
    n = len(matrix)
    a = [row.copy() for row in matrix]
    divisor = nmod_poly([1], 5)
    sign = 1
    for k in range(n-1):
        if not a[k][k]:
            pivot = next((i for i in range(k+1, n) if a[i][k]), None)
            if pivot is None:
                return nmod_poly([], 5)
            a[pivot], a[k] = a[k], a[pivot]
            sign = -sign
        for i in range(k+1, n):
            for j in range(k+1, n):
                value = a[k][k]*a[i][j] - a[i][k]*a[k][j]
                a[i][j], remainder = divmod(value, divisor)
                assert not remainder
        divisor = a[k][k]
    return sign*a[-1][-1]


def check_image(evaluations, emit_norms=None):
    if not __debug__:
        raise RuntimeError("Run this checker without Python optimization so its assertions execute.")
    algebra, *variables = ring("x0,x1,y0,y1", sp.GF(5), "grevlex")
    secondary = secondary_basis(algebra, variables)
    table, pure = multiplication_table(algebra, variables, secondary)
    sections = interpolate(np.loadtxt(evaluations, dtype=np.int64, ndmin=2), secondary, pure)
    zero = nmod_poly([], 5)
    norms = []
    for section in sections:
        matrix = [[sum((a*table[k, j][i] for k, a in enumerate(section)), zero)
                   for j in range(12)] for i in range(12)]
        norm = determinant(matrix)
        for value in range(5):
            specialized = nmod_mat([[int(f(value)) for f in row] for row in matrix], 5)
            assert int(specialized.det()) == int(norm(value))
        norms.append(norm)
    assert [f.degree() for f in norms] == [1344, 1372, 1406]
    one = nmod_poly([1], 5)
    assert all(f.gcd(g) == one for f, g in combinations(norms, 2))
    print("The three norms have degrees 1344, 1372, 1406 and each pair has gcd one.")
    if emit_norms is not None:
        gcd, a, b = norms[0].xgcd(norms[1])
        assert gcd == one and a*norms[0] + b*norms[1] == one
        polynomials = dict(zip(("norm_G2", "norm_G3", "norm_G4"), norms))
        polynomials.update(bezout_G2=a, bezout_G3=b)
        coefficients = {name: list(map(int, f.coeffs())) for name, f in polynomials.items()}
        Path(emit_norms).write_text(json.dumps(coefficients) + "\n", encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evaluations", help="eight-column output from the common-line section evaluator")
    parser.add_argument("--emit-norms", metavar="FILE", type=Path,
                        help="write the three norms and a G2,G3 Bézout identity as JSON arrays of ascending F5 coefficients")
    args = parser.parse_args()
    check_image(args.evaluations, args.emit_norms)
