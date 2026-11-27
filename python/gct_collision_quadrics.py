"""Test for a common line in the three quadratic completion equations.

For a normalized kernel direction over F25, the quadrics descend to the
five-dimensional quotient ker(T_B)/<B>. A common line there forces the
degree-d Jacobian quotient of their determinant quintic to have dimension
at least three for d >= 2. In degree nine the resulting rank ceiling is 52.
"""

import argparse
import subprocess
from functools import lru_cache
from itertools import combinations, product
from pathlib import Path
from tempfile import TemporaryDirectory

import sympy as sp
from sympy.polys.agca.extensions import MonogenicFiniteExtension
from sympy.polys.matrices import DomainMatrix
from sympy.polys.rings import ring

from gct_collision_direction import REPRESENTATIVE
from gct_collision_slice import kernel_from_edges
from gct_collision_kernel_reduction import COORDINATES, evaluate, first_variations
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
    return quotient_forms_at(point, field)


def quotient_forms_at(point, field):
    """Build the quotient forms over a characteristic-five field at B01=1."""
    if len(point) != 6 or point[0] != field.one or field.characteristic() != 5:
        raise ValueError("expected normalized edges over a characteristic-five field")
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
    kernel = kernel_from_edges(algebra(x) for x in point)
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
    return determinant_of_net(quotient_quadrics(edges), quadratic_field())


def determinant_of_net(forms, field):
    algebra, *parameters = ring("l,m,n", field)
    net = [[sum(p * algebra(q[i][j]) for q, p in zip(forms, parameters))
            for j in range(5)] for i in range(5)]
    # Laplace expansion along the last row builds each leading-row minor once.
    minors = {(): algebra.one}
    for size in range(1, 6):
        for cols in combinations(range(5), size):
            minors[cols] = sum(((-1)**(size-1+j) * net[size-1][col] *
                                minors[cols[:j] + cols[j+1:]] for j, col in enumerate(cols)),
                               algebra.zero)
    return minors[tuple(range(5))]


def homogeneous_powers(degree):
    return [(i, j, degree-i-j) for i in range(degree+1) for j in range(degree-i+1)]


def jacobian_multiples(quintic, degree, columns):
    """Yield the derivative index, monomial shift and coefficients of each row."""
    field = quintic.ring.domain
    generators = [(None, quintic, 5)] + [(i, quintic.diff(x), 4) for i, x in enumerate(quintic.ring.gens)]
    for index, polynomial, generator_degree in generators:
        for shift in homogeneous_powers(degree-generator_degree):
            yield index, shift, [polynomial.get(tuple(a-b for a, b in zip(power, shift)), field.zero)
                                 for power in columns]


def jacobian_rank(quintic, degree):
    """Rank of the degree-d multiples of the quintic and all three partials.

    In characteristic five Euler's identity does not put the quintic in
    its gradient ideal. The quintic rows must be included explicitly.
    """
    if degree < 2:
        raise ValueError("the rank ceiling is stated in degrees at least two")
    columns = homogeneous_powers(degree)
    rows = [row for _, _, row in jacobian_multiples(quintic, degree, columns)]
    return DomainMatrix(rows, (len(rows), len(columns)), quintic.ring.domain).rank() if rows else 0


def net_singularity_ranks(edges, degrees=(8, 9)):
    quintic = determinant_quintic(edges)
    return tuple(jacobian_rank(quintic, d) for d in degrees)


def line_frame_slots(pivots):
    return [(i, j) for i, pivot in enumerate(pivots)
            for j in range(pivot + 1, 5) if j not in pivots]


def line_frame(pivots, entries, one, zero):
    free = line_frame_slots(pivots)
    if len(entries) != len(free):
        raise ValueError("wrong number of entries for the line chart")
    slots = dict(zip(free, entries))
    return [[slots.get((i, j), one if pivot == j else zero) for j in range(5)]
            for i, pivot in enumerate(pivots)]


def checked_line_forms(forms, field):
    """Coerce three Gram matrices to the finite coefficient field."""
    if field != sp.GF(5) and not (isinstance(field, MonogenicFiniteExtension) and
                                  field.domain == sp.GF(5) and field.modulus.is_irreducible):
        raise ValueError("expected F5 or a simple finite field over F5")
    if len(forms) != 3 or any(len(q) != 5 or any(len(row) != 5 for row in q) for q in forms):
        raise ValueError("expected three 5 by 5 Gram matrices")
    forms = [[[field.convert(c) for c in row] for row in q] for q in forms]
    if any(q[i][j] != q[j][i] for q in forms for i, j in combinations(range(5), 2)):
        raise ValueError("expected symmetric matrices")
    return forms


def common_line_form_cells(forms, field):
    """Give the ten RREF line ideals over F5, including the coefficient root.

    The input consists of three symmetric Gram matrices over F5 or a
    monogenic finite extension of F5 given by an irreducible polynomial.
    """
    forms = checked_line_forms(forms, field)
    omega = sp.Symbol("omega")
    if isinstance(field, MonogenicFiniteExtension):
        substitution = {field.symbol: omega}
        modulus = field.modulus.as_expr().xreplace(substitution)
    else:
        substitution = {}
        modulus = omega
    expressions = [[[field.to_sympy(c).xreplace(substitution) for c in row]
                    for row in q] for q in forms]
    for pivots in combinations(range(5), 2):
        free = line_frame_slots(pivots)
        names = (*[f"x{i}{j}" for i, j in free], "omega")
        algebra, *values = ring(names, sp.GF(5), "grevlex")
        rows = line_frame(pivots, values[:-1], algebra.one, algebra.zero)
        equations = [algebra.from_expr(modulus)]
        for form in expressions:
            gram = [[algebra.from_expr(c) for c in row] for row in form]
            for i, j in ((0, 0), (0, 1), (1, 1)):
                pairing = sum(rows[i][a] * gram[a][b] * rows[j][b] for a, b in product(range(5), repeat=2))
                if pairing:
                    equations.append(pairing)
        yield pivots, names, equations


def common_line_cells(edges):
    """Specialize the common-line charts to the original F25 direction."""
    yield from common_line_form_cells(quotient_quadrics(edges), quadratic_field())


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
