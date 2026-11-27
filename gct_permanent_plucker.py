"""Exact chart systems and a rank-drop witness for the two Plücker cuts."""

import argparse
import sys
from itertools import combinations, combinations_with_replacement, permutations, product

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
from gct_permanent_modular import unit_ideal_at_degree

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
MATCHING_CROSS_EDGES = ((0, 2), (0, 3), (1, 2), (1, 3))
MATCHING_PIVOT_PAIRS = tuple(combinations(MATCHING_CROSS_EDGES[:3], 2))
ADJACENT_PIVOT_PAIRS = tuple(combinations((edge for edge in OFF_DIAGONAL if edge != (0, 1)), 2))
EDGE_GRAPH_PIVOTS = {
    "star": ((0, 1), (0, 2), (0, 3)),
    "triangle": ((0, 1), (0, 2), (1, 2)),
    "path": ((0, 1), (1, 2), (2, 3)),
}
PATH_REVERSAL_ODD = frozenset(
    6*column + slot for column in range(3) for slot in range(6)
    if (slot in (1, 2, 4)) != (column == 1)
)
FOUR_CYCLE_EDGES = ((0, 1), (1, 2), (2, 3), (0, 3))


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
    """Check the coordinate change and the finite chart covers."""
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
    graph_orbits = [
        {tuple(sorted(tuple(sorted((permutation[i], permutation[j]))) for i, j in triple))
         for permutation in PERMUTATIONS}
        for triple in EDGE_GRAPH_PIVOTS.values()
    ]
    assert sorted(map(len, graph_orbits)) == [4, 4, 12]
    assert set().union(*graph_orbits) == set(combinations(OFF_DIAGONAL, 3))
    path_orbit = graph_orbits[2]
    for triple in (EDGE_GRAPH_PIVOTS["star"], EDGE_GRAPH_PIVOTS["triangle"]):
        outside = set(OFF_DIAGONAL) - set(triple)
        for edge in outside:
            for pivot in triple:
                replacement = tuple(sorted((set(triple) - {pivot}) | {edge}))
                assert (replacement in path_orbit) == bool(set(edge) & set(pivot))


def pencil_coefficients(coefficient_ring, directions):
    pencil_ring, s, t, z = ring("s,t,z", coefficient_ring.to_domain(), "grevlex")
    pencil = [[pencil_ring.one + sum(
        parameter * direction[tuple(sorted((i, j)))]
        for parameter, direction in zip((s, t, z), directions))
        for j in range(4)] for i in range(4)]
    permanent = sum((sp.prod(pencil[i][j] for i, j in enumerate(permutation))
                     for permutation in PERMUTATIONS), pencil_ring.zero)
    return {powers: coefficient for powers, coefficient in sorted(permanent.items()) if sum(powers)}


def verify_opposite_edge_obstruction():
    """Exclude a level pencil on two distinct pairs of opposite edges."""
    matchings = (((0, 1), (2, 3)), ((0, 2), (1, 3)))
    for field in (sp.QQ, sp.GF(PRIME)):
        coefficients, h, x, y, inverse = ring("h,x,y,inverse", field, "grevlex")

        def direction(matching, signs, multiplier):
            values = {}
            for (i, j), sign, scale in zip(matching, signs, (coefficients.one, multiplier)):
                values[i, i] = scale * (-1 + sign*h)
                values[j, j] = scale * (-1 - sign*h)
                values[i, j] = scale
            return tangent_direction(values.get(slot, coefficients.zero) for slot in COORDINATES)

        for signs in product((1, -1), repeat=4):
            a = direction(matchings[0], signs[:2], x)
            b = direction(matchings[1], signs[2:], y)
            mixed = [coefficient for powers, coefficient in
                     pencil_coefficients(coefficients, (a, b)).items() if powers[0] and powers[1]]
            generators = [h*h - 2, inverse*x*y - 1, *mixed]
            if field == sp.QQ:
                basis = sp.groebner([polynomial.as_expr() for polynomial in generators],
                                    *coefficients.symbols, domain=field, order="grevlex")
                assert list(basis) == [1]
            else:
                assert unit_ideal_at_degree(generators, 4, PRIME, degree_cap=7)


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


def edge_graph_chart(pivots):
    """Return the full permanent equations for an off-diagonal pivot triple."""
    remaining = tuple(slot for slot in COORDINATES if slot not in pivots)
    names = tuple(f"{label}{i}{j}" for label in "abc" for i, j in remaining)
    coefficient_ring, *variables = ring(names, sp.GF(PRIME), "grevlex")
    entries = iter(variables)
    directions = [tangent_direction(
        coefficient_ring(int(slot == pivot)) if slot in pivots else next(entries)
        for slot in COORDINATES
    ) for pivot in pivots]
    coefficients = pencil_coefficients(coefficient_ring, directions)
    assert all(sum(powers) >= 2 for powers in coefficients)
    return names, list(coefficients.values())


def path_reversal_chart():
    """Return the path equations in coordinates adapted to path reversal."""
    names = tuple(f"{label}{coordinate}" for label in "abc" for coordinate in "uvwxyz")
    coefficients, *variables = ring(names, sp.GF(PRIME), "grevlex")
    directions = []
    for index in range(3):
        diag_sum, diag_diff, outer_diff, cross_sum, cross_diff, edge03 = variables[6*index:6*(index+1)]
        pivot_sum, pivot_diff, middle = (coefficients(int(index == j)) for j in range(3))
        outer_sum = -diag_sum - 2*(pivot_sum + cross_sum + edge03 + middle)
        directions.append({
            (0, 0): (outer_sum + outer_diff)/2,
            (0, 1): (pivot_sum + pivot_diff)/2,
            (0, 2): (cross_sum + cross_diff)/2,
            (0, 3): edge03,
            (1, 1): (diag_sum + diag_diff)/2,
            (1, 2): middle,
            (1, 3): (cross_sum - cross_diff)/2,
            (2, 2): (diag_sum - diag_diff)/2,
            (2, 3): (pivot_sum - pivot_diff)/2,
            (3, 3): (outer_sum - outer_diff)/2,
        })
    coefficients_by_degree = pencil_coefficients(coefficients, directions)
    assert len(PATH_REVERSAL_ODD) == 9 and len(coefficients_by_degree) == 31
    for powers, polynomial in coefficients_by_degree.items():
        assert all(sum(monomial[i] for i in PATH_REVERSAL_ODD) % 2 == powers[1] % 2
                   for monomial in polynomial)
    return names, list(coefficients_by_degree.values())


def four_cycle_chart(omitted_frequency):
    """Normalize three Fourier coordinates on a four-cycle over F5."""
    pivots = tuple(frequency for frequency in range(4) if frequency != omitted_frequency)
    coordinates = ("d1", "d2", "d3", "e", "o0", "o2")
    names = tuple(f"{column}{coordinate}" for column, coordinate in product("abc", coordinates))
    coefficients, *variables = ring(names, sp.GF(PRIME), "grevlex")
    directions = []
    weights = []
    # Two is a primitive fourth root of unity in F5.
    inverse_fourier = [[2**((-i*k) % 4) for k in range(4)] for i in range(4)]
    for column, pivot in enumerate(pivots):
        d1, d2, d3, free_edge, opposite_sum, opposite_difference = variables[6*column:6*(column+1)]
        cycle = [free_edge if j == omitted_frequency else coefficients(int(j == pivot)) for j in range(4)]
        diagonal = [-2*(cycle[0] + opposite_sum), d1, d2, d3]
        direction = {
            (0, 2): (opposite_sum + opposite_difference)/2,
            (1, 3): (opposite_sum - opposite_difference)/2,
        }
        for i, (edge, row) in enumerate(zip(FOUR_CYCLE_EDGES, inverse_fourier)):
            direction[edge] = sum(value*factor for value, factor in zip(cycle, row))/4
            direction[i, i] = sum(value*factor for value, factor in zip(diagonal, row))/4
        directions.append(direction)
        weights.extend((frequency-pivot) % 4 for frequency in (1, 2, 3, omitted_frequency, 0, 2))
    equations = pencil_coefficients(coefficients, directions)
    assert len(equations) == 31
    for powers, polynomial in equations.items():
        pivot_weight = sum(power*pivot for power, pivot in zip(powers, pivots))
        assert all((sum(power*weight for power, weight in zip(term, weights)) + pivot_weight) % 4 == 0
                   for term in polynomial)
    return names, list(equations.values()), weights


def star_fourier_chart():
    """Diagonalize leaf rotation in the fixed star chart and descend to F5."""
    names = tuple(f"{column}{kind}{mode}" for column, kind, mode in product("abc", "de", range(3)))
    extended, *variables, omega = ring((*names, "omega"), sp.GF(PRIME), "grevlex")
    coefficients, *_ = ring(names, sp.GF(PRIME), "grevlex")
    relation = omega**2 + omega + 1
    directions = []
    for pivot in range(3):
        diagonal = variables[6*pivot:6*pivot+3]
        opposite = variables[6*pivot+3:6*pivot+6]
        values = {}
        for i in range(3):
            values[0, i+1] = omega**((-i*pivot) % 3)/3
            values[i+1, i+1] = sum(omega**((-i*k) % 3)*diagonal[k] for k in range(3))/3
            edge = tuple(j+1 for j in range(3) if j != i)
            values[edge] = sum(omega**((-i*k) % 3)*opposite[k] for k in range(3))/3
        directions.append(tangent_direction(values[slot] for slot in COORDINATES))

    equations = {}
    for powers, polynomial in pencil_coefficients(extended, directions).items():
        reduced = polynomial.rem([relation])
        assert all(term[-1] == 0 for term in reduced)
        equations[powers] = coefficients.from_dict({term[:-1]: value for term, value in reduced.items()})
    weights = [(mode-pivot) % 3 for pivot, _, mode in product(range(3), range(2), range(3))]
    reflection = [6*(-pivot % 3) + 3*kind + (-mode % 3)
                  for pivot, kind, mode in product(range(3), range(2), range(3))]
    assert len(equations) == 31
    for (a, b, c), polynomial in equations.items():
        assert all((sum(power*weight for power, weight in zip(term, weights)) + b + 2*c) % 3 == 0
                   for term in polynomial)
        reflected = {tuple(term[i] for i in reflection): value for term, value in polynomial.items()}
        assert coefficients.from_dict(reflected) == equations[a, c, b]
    return names, list(equations.values()), weights


def verify_path_degree_dual(source):
    """Check a functional taking 1 to 1 and killing all bounded invariant products."""
    header = next(source, "").split()
    if len(header) not in (1, 2):
        raise ValueError("Expected the degree cap and an optional Fourier chart.")
    degree_cap = int(header[0])
    if degree_cap < 2:
        raise ValueError("The degree cap must be at least two.")
    if len(header) == 2 and header[1] == "star":
        names, equations, weights = star_fourier_chart()
        symmetry_order = 3
    elif len(header) == 2:
        omitted_frequency = int(header[1])
        if omitted_frequency not in range(4):
            raise ValueError("The omitted frequency must be between zero and three.")
        names, equations, weights = four_cycle_chart(omitted_frequency)
        symmetry_order = 4
    else:
        names, equations = path_reversal_chart()
        weights = [int(i in PATH_REVERSAL_ODD) for i in range(len(names))]
        symmetry_order = 2

    def weight_of(powers):
        return sum(power*weight for power, weight in zip(powers, weights)) % symmetry_order

    width = degree_cap.bit_length()
    mask = (1 << width) - 1
    values = {}
    for line in source:
        key, residue = map(int, line.split())
        if not 0 <= key < 1 << (width*len(names)) or key in values or not 0 < residue < PRIME:
            raise ValueError("Invalid or duplicate nonzero dual entry.")
        powers = tuple((key >> (width*i)) & mask for i in range(len(names)))
        if sum(powers) > degree_cap or weight_of(powers):
            raise ValueError("Dual entries must index invariant monomials within the degree cap.")
        values[key] = residue
    if values.get(0) != 1:
        raise ValueError("The functional must take the constant monomial to one.")

    degrees = [max(map(sum, equation)) for equation in equations]
    multipliers = [[[] for _ in range(symmetry_order)] for _ in range(degree_cap - min(degrees) + 1)]
    for degree, by_weight in enumerate(multipliers):
        for indices in combinations_with_replacement(range(len(names)), degree):
            weight = sum(weights[i] for i in indices) % symmetry_order
            by_weight[weight].append(sum(1 << (width*i) for i in indices))
    count = 0
    for index, (equation, degree) in enumerate(zip(equations, degrees)):
        multiplier_weight = -weight_of(next(iter(equation))) % symmetry_order
        terms = [(sum(power << (width*i) for i, power in enumerate(powers)), int(coefficient))
                 for powers, coefficient in equation.items()]
        for multiplier_degree in range(degree_cap-degree+1):
            for multiplier in multipliers[multiplier_degree][multiplier_weight]:
                # The degree bound prevents carries between adjacent exponent fields.
                value = sum(coefficient*values.get(key+multiplier, 0) for key, coefficient in terms)
                if value % PRIME:
                    raise ValueError(f"Nonzero pairing for generator {index} with multiplier {multiplier}.")
                count += 1
    return degree_cap, count


def matching_direction(coefficient_ring, r, h):
    """Normalize a level direction on the matching (01, 23)."""
    values = {
        (0, 1): coefficient_ring.one,
        (1, 1): -1-h,
        (2, 2): r*(-1+h),
        (2, 3): r,
        (3, 3): r*(-1-h),
    }
    return tangent_direction(values.get(slot, coefficient_ring.zero) for slot in COORDINATES)


def verify_matching_direction_identities():
    """Check the polar identities used to cover the matching incidence."""
    coefficients, *entries, r, h = ring("p,q,a,b,c,d,e,f,r,h", sp.QQ, "grevlex")
    trial = tangent_direction((coefficients.zero, *entries))
    direction = matching_direction(coefficients, r, h)
    pencil = pencil_coefficients(coefficients, (direction, trial))
    relation = h*h - 2
    cross = trial[0, 2] - trial[0, 3] - trial[1, 2] + trial[1, 3]
    assert (pencil[2, 1, 0] - 4*r*cross).rem([relation]) == 0
    assert (pencil[1, 1, 0].diff(trial[1, 1]) - 4*h).rem([relation]) == 0


def matching_direction_chart(pivots):
    """Return the extension system through a direction with two opposite edges."""
    fixed = ((0, 1), (1, 1), MATCHING_CROSS_EDGES[-1], *pivots)
    remaining = tuple(slot for slot in COORDINATES if slot not in fixed)
    names = (*(f"{label}{i}{j}" for label in "ab" for i, j in remaining), "r", "h", "u")
    coefficients, *entries, r, h, inverse = ring(names, sp.GF(PRIME), "grevlex")
    relation = h*h - 2
    direction = matching_direction(coefficients, r, h)
    entries = iter(entries)
    frame = []
    for pivot in pivots:
        values = {slot: next(entries) if slot in remaining else coefficients(int(slot == pivot))
                  for slot in COORDINATES}
        x, y, z, w = MATCHING_CROSS_EDGES
        values[w] = -values[x] + values[y] + values[z]
        mixed_quadratic = pencil_coefficients(coefficients, (direction, tangent_direction(values.values())))
        values[1, 1] = (-h*mixed_quadratic[1, 1, 0]/8).rem([relation])
        frame.append(tangent_direction(values.values()))
    pencil = pencil_coefficients(coefficients, (*frame, direction))
    equations = [equation for value in pencil.values() if (equation := value.rem([relation]))]
    assert len(equations) == 22
    return names, [relation, inverse*r - 1, *equations]


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


def order_three_chart():
    """Return the symmetric order-three level two-plane system."""
    names = ("a12", "a11", "a22", "b12", "b11", "b22")
    coefficients, *_ = ring(names, sp.GF(PRIME), "grevlex")
    a12, a11, a22, b12, b11, b22 = coefficients.symbols
    directions = (
        sp.Matrix([[-2-2*a12-a11-a22, 1, 0], [1, a11, a12], [0, a12, a22]]),
        sp.Matrix([[-2-2*b12-b11-b22, 0, 1], [0, b11, b12], [1, b12, b22]]),
    )
    difference = permanent_difference(sp.ones(3), directions)
    assert len(difference.terms()) == 7
    assert all(sum(powers) >= 2 for powers, _ in difference.terms())
    return names, [coefficients.from_expr(value) for value in difference.coeffs()]


def verify_isolated_row_identities():
    """Check the isolated-row coefficients and the determinant for adjacent edges."""
    d, e, f, p, q, r, w = sp.symbols("d e f p q r w")
    block = sp.Matrix([[d, p, q], [p, e, r], [q, r, f]])
    cofactors = sp.Matrix(3, 3, lambda i, j: block.minor_submatrix(i, j).per())
    direction = sp.diag(block, sp.zeros(1))
    isolated = permanent_difference(sp.ones(4), (sp.diag(block, w),))
    assert sp.expand(isolated.nth(1) - 6*(sum(block) + w)) == 0
    assert sp.expand(isolated.nth(2) - 2*(sum(cofactors) + w*sum(block))) == 0
    assert sp.expand(isolated.nth(3) - block.per() - w*sum(cofactors)) == 0
    assert sp.expand(isolated.nth(4) - w*block.per()) == 0

    a, b, c, x, y, z, u, v, l, m = sp.symbols("a b c x y z u v l m")
    top = sp.Matrix([[a, x, y], [x, b, z], [y, z, c]])
    side = sp.Matrix([u, v, l])
    trial = top.row_join(side).col_join(side.T.row_join(sp.Matrix([[m]])))
    first = permanent_difference(sp.ones(4), (direction, trial)).nth(2, 1)
    second = permanent_difference(sp.zeros(4), (direction, trial)).nth(2, 2)
    polar = sum(top.multiply_elementwise(cofactors))
    assert sp.expand(first - polar - m*sum(cofactors) - 2*(side.T*cofactors*sp.ones(3, 1))[0]) == 0
    assert sp.expand(second - m*polar - (side.T*cofactors*side)[0]) == 0

    adjacent = {p: 1, r: 0}
    determinant = cofactors.det().subs(adjacent)
    assert sp.expand(determinant - (d*e*f - e*q*q - f)*block.per().subs(adjacent) - 4*e*f*q*q) == 0


def adjacent_direction_chart(pivots):
    """Return the extension system through the singular adjacent-edge direction."""
    fixed = ((0, 1), (1, 1), (2, 2), *pivots)
    remaining = tuple(slot for slot in COORDINATES if slot not in fixed)
    names = tuple(f"{label}{i}{j}" for label in "ab" for i, j in remaining)
    coefficients, *entries = ring(names, sp.GF(PRIME), "grevlex")
    direction = tangent_direction((coefficients.one, -coefficients.one, *([coefficients.zero] * 7)))
    frame = []
    entries = iter(entries)
    for pivot in pivots:
        values = {slot: next(entries) if slot in remaining else coefficients(int(slot == pivot))
                  for slot in COORDINATES}
        d, e, f = (values[slot] for slot in ((1, 2), (1, 3), (2, 3)))
        values[1, 1] = d + (f-e)/2
        values[2, 2] = d + (e-f)/2
        frame.append(tangent_direction(values.values()))
    pencil = pencil_coefficients(coefficients, (*frame, direction))
    assert all(not value for powers, value in pencil.items()
               if sum(powers) <= 1 or sum(powers[:2]) == 0 or powers[-1] >= 3
               or (powers[-1] == 1 and sum(powers[:2]) == 1))
    equations = [value for value in pencil.values() if value]
    assert len(equations) == 22
    return names, equations


def triangle_direction(coefficient_ring, b, c, q, r):
    """Normalize the (01) entry of a direction on the triangle 01, 02, 12."""
    return tangent_direction(map(coefficient_ring, (1, q, 0, b, r, 0, c, 0, 0)))


def triangle_cofactors(direction):
    """The permanent cofactors of the upper three-by-three block."""
    complements = ((1, 2), (0, 2), (0, 1))

    def entry(i, j):
        return direction[min(i, j), max(i, j)]

    return [[entry(i, k)*entry(j, l) + entry(i, l)*entry(j, k)
             for k, l in complements] for i, j in complements]


def verify_triangle_cofactor_rank():
    """Exclude rank at most one for a genuine level triangle direction."""
    coefficients, b, c, q, r, inverse = ring("b,c,q,r,w", sp.GF(PRIME), "grevlex")
    direction = triangle_direction(coefficients, b, c, q, r)
    cofactors = triangle_cofactors(direction)
    minors = [
        cofactors[i][k]*cofactors[j][l] - cofactors[i][l]*cofactors[j][k]
        for (i, j), (k, l) in product(combinations(range(3), 2), repeat=2)
    ]
    pencil = pencil_coefficients(coefficients, (direction,))
    assert set(pencil) == {(2, 0, 0), (3, 0, 0)}
    equations = [inverse*q*r-1, *pencil.values(), *minors]
    basis = sp.groebner([equation.as_expr() for equation in equations],
                        *coefficients.symbols, order="grevlex", modulus=PRIME)
    assert list(basis) == [1]


def triangle_radical_chart():
    """Return the pencil system for a genuine triangle and its cofactor radical."""
    names = ("b", "c", "q", "r", "u", "v", "d", "e", "y", "i", "j", "w")
    coefficients, b, c, q, r, u, v, d, e, y, i, j, inverse = ring(names, sp.GF(PRIME), "grevlex")
    direction = triangle_direction(coefficients, b, c, q, r)
    trial = tangent_direction(map(coefficients, (0, u, y+1, d, v, y+i, e, y+j, y)))
    # The cross entries of the trial minus its last diagonal give (1, i, j).
    radical = [sum(entry*value for entry, value in zip(row, (1, i, j)))
               for row in triangle_cofactors(direction)]
    pencil = pencil_coefficients(coefficients, (direction, trial))
    equations = [inverse*q*r-1, *radical, *pencil.values()]
    assert len(equations) == 15
    return names, equations


def verify_characteristic_three_plane():
    """Check a point of the integral tangent model after reduction at three."""
    directions = (
        sp.Matrix([[0, 0, 0, 0], [0, 1, -1, 0], [0, -1, 0, 1], [0, 0, 1, -1]]),
        sp.Matrix([[0, 0, 0, 0], [0, 0, -1, 1], [0, -1, 1, 0], [0, 1, 0, -1]]),
        sp.Matrix([[0, -1, -1, -1], [-1, 1, 1, 1], [-1, 1, 1, 1], [-1, 1, 1, 1]]),
    )
    pivots = ((0, 1), (1, 1), (2, 2))
    assert all(direction.is_symmetric() and sum(direction) % 3 == 0 for direction in directions)
    assert sp.Matrix([[direction[pivot] for direction in directions] for pivot in pivots]).det() % 3
    assert all(coefficient % 3 == 0 for coefficient in permanent_difference(sp.ones(4), directions).coeffs())


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
    modes.add_argument("--matching", type=int, choices=range(len(MATCHING_PIVOT_PAIRS)),
                       help="emit one of the three opposite-edge direction systems, numbered 0 to 2")
    modes.add_argument("--adjacent-edge", type=int, choices=range(len(ADJACENT_PIVOT_PAIRS)),
                       help="emit one of the ten adjacent-edge direction systems, numbered 0 to 9")
    modes.add_argument("--triangle-radical", action="store_true",
                       help="emit the triangle radical-pencil system over F5")
    modes.add_argument("--order-three", action="store_true", help="emit the order-three level two-plane system")
    modes.add_argument("--star", action="store_true", help="emit the unrestricted star chart over F5")
    modes.add_argument("--star-fourier", action="store_true",
                       help="emit the star chart in coordinates adapted to leaf rotation")
    modes.add_argument("--path", action="store_true", help="emit the unrestricted path chart over F5")
    modes.add_argument("--path-reversal", action="store_true",
                       help="emit the path chart in coordinates adapted to path reversal")
    modes.add_argument("--four-cycle", type=int, choices=range(4), metavar="OMITTED",
                       help="emit the four-cycle chart omitting the given Fourier frequency")
    modes.add_argument("--verify-path-dual", type=argparse.FileType("r"), metavar="FILE",
                       help="check a bounded-degree functional for the path chart")
    args = parser.parse_args()
    if args.chart:
        first, second, third = args.chart
        try:
            system = extension_chart((first, second), third)
        except ValueError as error:
            parser.error(str(error))
    elif args.single_edge is not None:
        system = single_edge_chart(EDGE_PIVOT_PAIRS[args.single_edge])
    elif args.matching is not None:
        system = matching_direction_chart(MATCHING_PIVOT_PAIRS[args.matching])
    elif args.adjacent_edge is not None:
        system = adjacent_direction_chart(ADJACENT_PIVOT_PAIRS[args.adjacent_edge])
    elif args.triangle_radical:
        system = triangle_radical_chart()
    elif args.order_three:
        system = order_three_chart()
    elif args.star:
        system = edge_graph_chart(EDGE_GRAPH_PIVOTS["star"])
    elif args.star_fourier:
        names, equations, _ = star_fourier_chart()
        system = names, equations
    elif args.path:
        system = edge_graph_chart(EDGE_GRAPH_PIVOTS["path"])
    elif args.path_reversal:
        system = path_reversal_chart()
    elif args.four_cycle is not None:
        names, equations, _ = four_cycle_chart(args.four_cycle)
        system = names, equations
    elif args.verify_path_dual is not None:
        try:
            with args.verify_path_dual as source:
                degree, rows = verify_path_degree_dual(source)
        except ValueError as error:
            parser.error(str(error))
        print(f"Checked {rows:,} invariant products over F{PRIME}. No unit-ideal identity through degree {degree}.")
        return
    else:
        verify_chart_data()
        verify_matching_direction_identities()
        verify_isolated_row_identities()
        verify_triangle_cofactor_rank()
        verify_characteristic_three_plane()
        names, equations = order_three_chart()
        assert unit_ideal_at_degree(equations, len(names), PRIME, degree_cap=7)
        for pivots in ADJACENT_PIVOT_PAIRS:
            adjacent_direction_chart(pivots)
        print("Checked the isolated-row and adjacent-edge formulas and the order-three unit ideal over F5.")
        print("Excluded cofactor rank at most one on genuine level triangle directions over F5.")
        print("Verified a three-plane in the special fiber at 3 of the integral tangent model.")
        print(f"No cut zeros among {verify_rational_rank_cut()} rational rank-drop two-planes over F5.")
        verify_extension_field_witness()
        print("Verified a rank-six point on the cuts over F25. Its only possible extension fails q2.")
        verify_opposite_edge_obstruction()
        print("Checked all 16 opposite-edge pencil cases over Q and F5. Every candidate has a path pivot.")
        return
    write_msolve_system(*system, sys.stdout)


if __name__ == "__main__":
    main()
