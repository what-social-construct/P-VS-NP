"""Test for a common line in the three quadratic completion equations.

For a normalized kernel direction over F25, the quadrics descend to the
five-dimensional quotient ker(T_B)/<B>. A common line there forces the
degree-d Jacobian quotient of their determinant quintic to have dimension
at least three for d >= 2. In degree nine the resulting rank ceiling is 52.
"""

import argparse
import subprocess
from functools import lru_cache
from itertools import combinations, permutations, product
from math import prod
from pathlib import Path
from tempfile import TemporaryDirectory

import sympy as sp
from sympy.polys.agca.extensions import MonogenicFiniteExtension
from sympy.polys.matrices import DomainMatrix
from sympy.polys.rings import ring

from gct_collision_direction import REPRESENTATIVE
from gct_collision_kernel_reduction import COORDINATES, OFF_DIAGONAL, evaluate, first_variations
from gct_permanent_plucker import pencil_coefficients, tangent_direction, write_msolve_system


# Canonical S4 × Frobenius representatives surviving the degree-nine rank test.
LINE_CELL_REPRESENTATIVES = (
    (1, 0, 12, 5, 9, 16),
    (1, 1, 4, 3, 10, 15),
    (1, 1, 8, 2, 15, 15),
    (1, 1, 12, 18, 17, 17),
)


@lru_cache(maxsize=1)
def quadratic_field():
    omega = sp.Symbol("omega")
    return MonogenicFiniteExtension(sp.Poly(omega**2 - 2, omega, modulus=5))


@lru_cache(maxsize=1)
def polar_equations():
    return first_variations()


def quotient_quadrics(edges):
    """Return the three symmetric 5×5 forms at an eligible edge direction.

    Codes a+5b denote a+b*omega, with omega²=2. Normalizing B01 to one
    makes the slice X01=0 a vector space model of the quotient by B.
    """
    if len(edges) != 6 or edges[0] != 1 or any(int(v) != v or not 0 <= v < 25 for v in edges):
        raise ValueError("supply six packed F25 entries, with the first edge normalized to one")
    field = quadratic_field()
    point = [field(int(v) % 5) + (int(v) // 5) * field.generator for v in edges]
    pure, polars = polar_equations()
    if any(evaluate(f, point[1:]) for f in pure):
        raise ValueError("the direction fails a pure kernel equation")
    rows = [[evaluate(polars[slot][i], point[1:]) for slot in COORDINATES] for i in range(3)]
    rows.append([field(int(slot == (0, 1))) for slot in COORDINATES])
    echelon, pivots = DomainMatrix(rows, (4, 9), field).rref()
    assert len(pivots) == 4
    free = [j for j in range(9) if j not in pivots]
    algebra, *variables = ring("v0,v1,v2,v3,v4", field)
    coordinates = dict(zip(free, variables))
    for row, pivot in zip(echelon.to_list(), pivots):
        coordinates[pivot] = -sum(algebra(row[j]) * coordinates[j] for j in free)
    tangent = tangent_direction(coordinates[j] for j in range(9))
    kernel = dict(zip(OFF_DIAGONAL, (algebra(x) for x in point)))
    half_sum = 3 * sum(kernel.values())
    for i in range(4):
        kernel[i, i] = half_sum - 2 * sum(kernel[e] for e in OFF_DIAGONAL if i in e)
    coefficients = pencil_coefficients(algebra, (kernel, tangent))
    assert all(powers[1] >= 2 for powers in coefficients)
    forms = []
    for i in range(3):
        quadratic = coefficients.get((i, 2, 0), algebra.zero)
        assert all(sum(power) == 2 for power in quadratic)
        gram = []
        for r in range(5):
            row = []
            for c in range(5):
                monomial = tuple(int(j == r) + int(j == c) for j in range(5))
                row.append(quadratic.get(monomial, field.zero) * (1 if r == c else 3))
            gram.append(row)
        forms.append(gram)
    return forms


def determinant_quintic(edges):
    """Compute det(l Q0 + m Q1 + n Q2) in the parameter plane of the net."""
    field = quadratic_field()
    algebra, *parameters = ring("l,m,n", field)
    forms = quotient_quadrics(edges)
    net = [[sum(p * algebra(q[i][j]) for q, p in zip(forms, parameters))
            for j in range(5)] for i in range(5)]
    determinant = algebra.zero
    for permutation in permutations(range(5)):
        inversions = sum(permutation[i] > permutation[j] for i in range(5) for j in range(i+1, 5))
        term = prod(net[i][permutation[i]] for i in range(5))
        determinant += (-1)**inversions * term
    return determinant


def homogeneous_powers(degree):
    return [(i, j, degree-i-j) for i in range(degree+1) for j in range(degree-i+1)]


def jacobian_rank(quintic, degree):
    """Rank of the degree-d multiples of the quintic and all three partials.

    In characteristic five Euler's identity does not put the quintic in
    its gradient ideal. The quintic rows must be included explicitly.
    """
    if degree < 2:
        raise ValueError("the rank ceiling is stated in degrees at least two")
    field = quadratic_field()
    columns = homogeneous_powers(degree)
    generators = [(quintic, 5), *((quintic.diff(x), 4) for x in quintic.ring.gens)]
    rows = []
    for polynomial, generator_degree in generators:
        for shift in homogeneous_powers(degree-generator_degree):
            rows.append([polynomial.get(tuple(a-b for a, b in zip(power, shift)), field.zero)
                         for power in columns])
    return DomainMatrix(rows, (len(rows), len(columns)), field).rank() if rows else 0


def net_singularity_ranks(edges, degrees=(8, 9)):
    quintic = determinant_quintic(edges)
    return tuple(jacobian_rank(quintic, d) for d in degrees)


def common_line_cells(edges):
    """Give the ten disjoint row-echelon systems for lines in the three quadrics.

    The additional coordinate omega makes each system a prime-field input
    for msolve. Both embeddings of the quadratic coefficient field are tested.
    """
    field = quadratic_field()
    codes = {field(i % 5) + (i // 5) * field.generator: i for i in range(25)}
    forms = quotient_quadrics(edges)
    for pivots in combinations(range(5), 2):
        free = [(i, j) for i, pivot in enumerate(pivots) for j in range(pivot+1, 5) if j not in pivots]
        names = (*[f"x{i}{j}" for i, j in free], "omega")
        algebra, *values = ring(names, sp.GF(5), "grevlex")
        omega = values[-1]
        slots = dict(zip(free, values[:-1]))
        rows = [[slots.get((i, j), algebra(int(pivot == j))) for j in range(5)]
                for i, pivot in enumerate(pivots)]
        equations = [omega**2 - 2]
        for form in forms:
            gram = [[algebra(codes[c] % 5) + (codes[c] // 5) * omega for c in row] for row in form]
            for i, j in ((0, 0), (0, 1), (1, 1)):
                pairing = sum(rows[i][a] * gram[a][b] * rows[j][b] for a, b in product(range(5), repeat=2))
                if pairing:
                    equations.append(pairing)
        yield pivots, names, equations


def verify_no_common_lines(msolve):
    with TemporaryDirectory() as path:
        for sample in LINE_CELL_REPRESENTATIVES:
            for pivots, names, equations in common_line_cells(sample):
                stem = "-".join(map(str, (*sample, *pivots)))
                source = Path(path) / (stem + ".ms")
                result = Path(path) / (stem + ".out")
                with source.open("w") as stream:
                    write_msolve_system(names, equations, stream)
                subprocess.run([msolve, "-f", str(source), "-o", str(result),
                                "-t", "1", "-g", "2", "-l", "2"], check=True)
                header, sep, body = result.read_text().partition("[")
                if not sep or "#Reduced Groebner basis data" not in header or body.strip() != "1]:":
                    raise AssertionError(f"cell {pivots} of {sample} did not yield the unit basis")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-lines", metavar="MSOLVE", help="check all forty remaining line cells")
    args = parser.parse_args()
    assert net_singularity_ranks(REPRESENTATIVE) == (42, 54)
    for direction, expected in [((1, 22, 11, 7, 16, 2), 54),
                                ((1, 4, 4, 10, 15, 2), 52)]:
        rank, = net_singularity_ranks(direction, (9,))
        assert rank == expected
        print(f"F25 kernel direction {direction}: degree-nine rank {rank} (ceiling 52)")
    if args.verify_lines:
        verify_no_common_lines(args.verify_lines)
        print("All ten common-line cells in each of the four remaining orbits have reduced basis [1].")
