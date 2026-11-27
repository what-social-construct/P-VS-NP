"""Check a nonzero specialization of the degree-180 companion resultant at five.

The seven forms are homogeneous in six companion entries and the scale of
its prescribed star. Restricting to the common polar kernel at a supplied
point leaves three quadrics and one cubic in four homogeneous coordinates.
"""

from collections import Counter
from itertools import combinations_with_replacement
from math import prod

import numpy as np
import sympy as sp
from sympy.polys.rings import ring

from gct_collision_direction import COMPANION_SLOTS, REPRESENTATIVE, relabelings
from gct_permanent_extensions import COORDINATES, PRIME, reduced_rows
from gct_permanent_hodge import OFF_DIAGONAL, STAR
from gct_permanent_plucker import pencil_coefficients, tangent_direction


# Powers of the kernel and companion parameters in the restricted permanent.
INDICES = ((1, 1), (2, 1), (3, 1), (0, 2), (1, 2), (2, 2), (0, 3))
TEST_DIRECTION = (3, 0, 2, 1, 1, 2)


def monomials(width, degree):
    return [tuple(term.count(i) for i in range(width))
            for term in combinations_with_replacement(range(width), degree)]


def companion_forms(edges):
    """Specialize the seven resultant inputs at a prime-field edge vector."""
    if len(edges) != 6:
        raise ValueError("expected six kernel edges in order 01,02,03,12,13,23")
    names = [f"c{i}{j}" for i, j in COMPANION_SLOTS] + ["scale"]
    algebra, *variables = ring(names, sp.GF(PRIME), "grevlex")
    entries = dict(zip(OFF_DIAGONAL, edges))
    half_sum = pow(2, -1, PRIME) * sum(edges)
    for i in range(4):
        entries[i, i] = half_sum - 2 * sum(entries[e] for e in OFF_DIAGONAL if i in e)
    kernel = {slot: algebra(value) for slot, value in entries.items()}
    companion = dict(zip(COMPANION_SLOTS, variables[:-1]))
    companion[STAR[1]] = variables[-1]
    column = tangent_direction(companion.get(slot, algebra.zero) for slot in COORDINATES)
    coeffs = pencil_coefficients(algebra, (kernel, column))
    return [coeffs.get((i, j, 0), algebra.zero) for i, j in INDICES]


def restricted_sextic_rank(edges):
    """Return the rank on sextics, or None when the three polars are dependent."""
    forms = companion_forms(edges)
    linear = np.array([[int(f.get(e, 0)) for e in monomials(7, 1)] for f in forms[:3]])
    rows, pivots = reduced_rows(linear)
    if len(pivots) < 3:
        return None
    free = [j for j in range(7) if j not in pivots]
    algebra, *parameters = ring("z0,z1,z2,z3", sp.GF(PRIME), "grevlex")
    coordinates = dict(zip(free, parameters))
    for i, pivot in enumerate(pivots):
        coordinates[pivot] = -sum(int(rows[i, j]) * coordinates[j] for j in free)

    sextics = monomials(4, 6)
    column_index = {powers: i for i, powers in enumerate(sextics)}
    multiples = []
    for f, (_, degree) in zip(forms[3:], INDICES[3:]):
        restricted = sum((int(coefficient) * prod(coordinates[j] ** power
                         for j, power in enumerate(term) if power)
                         for term, coefficient in f.items()), algebra.zero)
        for shift in monomials(4, 6 - degree):
            row = np.zeros(len(sextics), dtype=np.int64)
            for term, coefficient in restricted.items():
                powers = tuple(a + b for a, b in zip(term, shift))
                row[column_index[powers]] = int(coefficient)
            multiples.append(row)
    matrix = np.array(multiples)
    assert matrix.shape == (125, 84)
    return len(reduced_rows(matrix)[1])


if __name__ == "__main__":
    degrees = [j for _, j in INDICES]
    degree = sum(i * (prod(degrees) // j) for i, j in INDICES)
    assert degree == 180
    assert TEST_DIRECTION in relabelings(REPRESENTATIVE)
    forms = companion_forms(TEST_DIRECTION)
    assert all(all(sum(term) == j for term in f) for f, (_, j) in zip(forms, INDICES))
    assert companion_forms(tuple(2 * b for b in TEST_DIRECTION)) == [
        2**i * f for f, (i, _) in zip(forms, INDICES)
    ]
    assert restricted_sextic_rank((0,) * 6) is None
    ranks = {edges: restricted_sextic_rank(edges) for edges in relabelings(REPRESENTATIVE)}
    assert ranks[TEST_DIRECTION] == 84
    print(f"Degree {degree} in the kernel coordinates; sextic rank 84/84 at {TEST_DIRECTION}.")
    print("Sextic ranks on the 24 raw vertex relabelings:", dict(Counter(ranks.values())))
