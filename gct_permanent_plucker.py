"""Exact chart systems and a rank-drop witness for the two Plücker cuts."""

import argparse
import sys
from itertools import combinations, permutations

import numpy as np
import sympy as sp
from sympy.polys.rings import ring

from gct_permanent_extensions import (
    COORDINATES,
    extension_derivatives,
    level_two_planes,
    reduced_rows,
)
from gct_permanent_fiber import permanent_difference

PRIME = 5
PLUCKER_CUTS = (
    ((-1, (1, 2), (1, 3)), (1, (0, 1), (2, 3)), (1, (1, 3), (2, 3))),
    ((-1, (1, 2), (2, 3)), (-1, (0, 3), (1, 2)), (1, (0, 1), (0, 2))),
)
PERMUTATIONS = tuple(permutations(range(4)))
OFF_DIAGONAL = tuple(slot for slot in COORDINATES if slot[0] != slot[1])
NORMAL_COORDINATES = ("u", "v", "P", "Q", "R", "S", "d1", "d2", "d3")
PIVOT_COORDINATES = ("u", "v", "P", "Q", "S")
PIVOT_PAIRS = tuple(pair for pair in combinations(PIVOT_COORDINATES, 2)
                    if pair not in (("u", "v"), ("P", "Q")))
EDGE_PIVOT_PAIRS = (
    ((0, 1), (0, 2)),
    ((0, 1), (0, 3)),
    ((0, 1), (1, 2)),
    ((0, 1), (2, 3)),
)


def cut_values(left, right):
    """Evaluate the two alternating forms on an ordered pair of directions."""
    return tuple(sum(sign * (left[i] * right[j] - left[j] * right[i])
                     for sign, i, j in terms) for terms in PLUCKER_CUTS)


def verify_rational_rank_cut():
    """Check the cut on rational points over F5."""
    planes = level_two_planes()
    derivatives = extension_derivatives(planes)
    rank_drop = np.array([plane for plane, derivative in zip(planes, derivatives)
                          if len(reduced_rows(derivative)[1]) <= 6])
    assert len(rank_drop) == 112
    first, second = cut_values(
        dict(zip(COORDINATES, rank_drop[:, 0, :].T)),
        dict(zip(COORDINATES, rank_drop[:, 1, :].T)),
    )
    assert not np.any((first % PRIME == 0) & (second % PRIME == 0))
    return len(rank_drop)


def verify_extension_field_witness():
    """Check a cut point of rank six over F25 and exclude its only extension."""
    w = sp.Symbol("w")
    field_relation = sp.Poly(w**2 - 2, w, modulus=PRIME)
    assert field_relation.is_irreducible

    def reduce(value):
        return sp.Poly(value, w, modulus=PRIME).rem(field_relation).as_expr()

    a = sp.Matrix([[1, 0, 1, 2], [0, 2, 0, 3], [1, 0, 1, 2], [2, 3, 2, 0]])
    b = sp.Matrix([[4+w, 0, 1, 0], [0, 0, 0, 0], [1, 0, 4-w, 0], [0, 0, 0, 0]])
    c = sp.Matrix([[-2*w-1, 1, 0, 0], [1, 4, 1, 4], [0, 1, 2*w+4, 0], [0, 4, 0, 1]])
    assert all(matrix.is_symmetric() and reduce(sum(matrix)) == 0 for matrix in (a, b, c))
    assert reduce(a[0, 2]*b[0, 3] - a[0, 3]*b[0, 2]) == -2
    assert c[0, 1] == 1 and a[0, 1] == b[0, 1] == 0
    assert tuple(map(reduce, cut_values(a, b))) == (0, 0)

    base = sp.ones(4)
    difference = permanent_difference(base, (a, b, c))
    expected = {(2, 0, 2): -1, (1, 0, 2): 1, (0, 0, 4): -2, (0, 0, 3): 1, (0, 0, 2): -1}
    assert {powers: residue for powers, value in difference.terms() if (residue := reduce(value))} == expected

    tangent_entries = sp.symbols("c:9")
    tangent = sp.zeros(4)
    for (i, j), entry in zip(COORDINATES, tangent_entries):
        tangent[i, j] = tangent[j, i] = entry
    tangent[0, 0] = -sum(tangent)
    generic = permanent_difference(base, (a, b, tangent))
    monomials = ((1, 0, 1), (0, 1, 1), (2, 0, 1), (1, 1, 1), (3, 0, 1), (2, 1, 1))
    minor = sp.Matrix([[reduce(generic.coeff_monomial(powers).diff(entry)) for entry in tangent_entries[:6]]
                       for powers in monomials])
    assert reduce(minor.det(method="domain-ge")) == 2*w - 1


def tangent_direction(entries):
    """Restore the entry at (0,0) by making the full entry sum zero."""
    result = dict(zip(COORDINATES, entries))
    result[0, 0] = -sum(value * (1 if i == j else 2) for (i, j), value in result.items())
    return result


def from_normal_coordinates(normal):
    u, v, p, q, r, s, d1, d2, d3 = normal
    return tangent_direction((p, r, v+s, d1, q, u-p, d2, v-q, d3))


def verify_chart_data():
    """Check the coordinate change and the four pivot-pair orbits."""
    left = sp.symbols("a:9")
    right = sp.symbols("b:9")
    alpha, beta = cut_values(from_normal_coordinates(left), from_normal_coordinates(right))

    def minor(i, j):
        return left[i]*right[j] - left[j]*right[i]

    assert sp.expand(alpha - minor(0, 1) + minor(2, 3)) == 0
    assert sp.expand(beta - minor(2, 4) - minor(3, 5)) == 0
    assert len(PIVOT_PAIRS) == 8

    permutations_fixing_edge = ((0, 1, 2, 3), (2, 1, 0, 3), (0, 3, 2, 1), (2, 3, 0, 1))
    covered = {tuple(sorted(tuple(sorted((permutation[i], permutation[j]))) for i, j in pair))
               for pair in EDGE_PIVOT_PAIRS for permutation in permutations_fixing_edge}
    assert covered == set(combinations((slot for slot in OFF_DIAGONAL if slot != (1, 3)), 2))


def pencil_coefficients(coefficient_ring, directions):
    pencil_ring, s, t, z = ring("s,t,z", coefficient_ring.to_domain(), "grevlex")
    pencil = [[pencil_ring.one + sum(
        parameter * direction[tuple(sorted((i, j)))]
        for parameter, direction in zip((s, t, z), directions))
        for j in range(4)] for i in range(4)]
    permanent = sum((sp.prod(pencil[i][j] for i, j in enumerate(permutation))
                     for permutation in PERMUTATIONS), pencil_ring.zero)
    return {powers: coefficient for powers, coefficient in sorted(permanent.items()) if sum(powers)}


def extension_chart(pivots, extension_slot):
    """Return a full extension ideal in one of the 24 cut charts over F5."""
    if pivots not in PIVOT_PAIRS or extension_slot in pivots or extension_slot not in PIVOT_COORDINATES:
        raise ValueError("Use a listed pivot pair and a different extension slot from u, v, P, Q, S.")
    first_slot, second_slot = pivots
    fixed = (
        {first_slot: 1, second_slot: 0},
        {first_slot: 0, second_slot: 1},
        {first_slot: 0, second_slot: 0, extension_slot: 1},
    )
    names = tuple(f"{label}{coordinate}" for label, prescribed in zip("abc", fixed)
                  for coordinate in NORMAL_COORDINATES if coordinate not in prescribed)
    coefficient_ring, *variables = ring(names, sp.GF(PRIME), "grevlex")
    entries = iter(variables)
    directions = []
    for prescribed in fixed:
        normal = [coefficient_ring(prescribed[key]) if key in prescribed else next(entries)
                  for key in NORMAL_COORDINATES]
        directions.append(from_normal_coordinates(normal))
    coefficients = pencil_coefficients(coefficient_ring, directions)
    assert all(sum(powers) >= 2 for powers in coefficients)
    equations = list(coefficients.values())
    equations.extend(equation for equation in cut_values(*directions[:2]) if equation)
    return names, equations


def single_edge_chart(pivots):
    """Return a chart used to exclude three-planes through a single-edge direction."""
    fixed_edge = (1, 3)
    last_diagonal = (3, 3)
    remaining = tuple(slot for slot in COORDINATES if slot not in (*pivots, fixed_edge, last_diagonal))
    names = (*[f"{label}{i}{j}" for label in "ab" for i, j in remaining], "h")
    coefficient_ring, *variables = ring(names, sp.GF(PRIME), "grevlex")
    *parameters, h = variables
    entries = iter(parameters)
    directions = []
    for pivot in pivots:
        values = {slot: next(entries) if slot in remaining else coefficient_ring(int(slot == pivot))
                  for slot in COORDINATES}
        values[last_diagonal] = (1+h)*(
            2*h*values[0, 1] - 2*h*values[0, 3] + (h+1)*values[1, 1]
            + 2*h*values[1, 2] - 2*values[fixed_edge] - 2*h*values[2, 3]
        )
        directions.append(tangent_direction(values.values()))
    edge_direction = [coefficient_ring.zero] * len(COORDINATES)
    edge_direction[COORDINATES.index((1, 1))] = h-1
    edge_direction[COORDINATES.index(fixed_edge)] = coefficient_ring.one
    edge_direction[COORDINATES.index(last_diagonal)] = -h-1
    directions.append(tangent_direction(edge_direction))

    def reduce_h(polynomial):
        result = coefficient_ring.zero
        for powers, value in polynomial.items():
            reduced_powers = (*powers[:-1], powers[-1] % 2)
            term = coefficient_ring.term_new(reduced_powers, value * 2**(powers[-1]//2))
            result += term
        return result

    coefficients = {powers: reduce_h(value)
                    for powers, value in pencil_coefficients(coefficient_ring, directions).items()}
    assert all(not value for powers, value in coefficients.items()
               if sum(powers) <= 1 or sum(powers[:2]) == 0 or powers[-1] >= 3
               or (powers[-1] == 1 and sum(powers[:2]) == 1))
    equations = [h*h-2, *(value for value in coefficients.values() if value)]
    assert len(equations) == 20
    return names, equations


def write_msolve_system(names, equations, output):
    """Emit the generators as prime-field polynomials for msolve."""
    def polynomial_text(polynomial):
        return "+".join("*".join(
            [str(int(coefficient))] +
            [f"{name}^{degree}" if degree > 1 else name
             for name, degree in zip(names, powers) if degree]
        ) for powers, coefficient in sorted(polynomial.items(), reverse=True))

    output.write(",".join(names) + "\n" + str(PRIME) + "\n")
    output.write(",\n".join(map(polynomial_text, equations)) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--chart", nargs=3, metavar=("A", "B", "C"),
                       help="emit a full cut system with pivot coordinates such as u P v")
    modes.add_argument("--single-edge", type=int, choices=range(len(EDGE_PIVOT_PAIRS)),
                       help="emit one of the four single-edge systems, numbered 0 to 3")
    args = parser.parse_args()
    if args.chart:
        first, second, third = args.chart
        try:
            system = extension_chart((first, second), third)
        except ValueError as error:
            parser.error(str(error))
    elif args.single_edge is not None:
        system = single_edge_chart(EDGE_PIVOT_PAIRS[args.single_edge])
    else:
        verify_chart_data()
        print(f"No cut zeros among {verify_rational_rank_cut()} rational rank-drop two-planes over F5.")
        verify_extension_field_witness()
        print("Verified a rank-six point on the cuts over F25. Its only possible extension fails q2.")
        return
    write_msolve_system(*system, sys.stdout)


if __name__ == "__main__":
    main()
