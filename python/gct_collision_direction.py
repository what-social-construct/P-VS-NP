"""Exclude geometric level three-planes with a rational kernel line at five."""

from itertools import combinations_with_replacement, product

import numpy as np
import sympy as sp
from sympy.polys.rings import ring

from gct_permanent_extensions import COORDINATES, PERMUTATIONS, reduced_rows
from gct_permanent_hodge import OFF_DIAGONAL, PRIME, STAR
from gct_permanent_plucker import corrected_diagonal, pencil_coefficients, tangent_direction


REPRESENTATIVE = (1, 0, 2, 3, 1, 2)  # edges 01, 02, 03, 12, 13, 23
COMPANION_SLOTS = tuple(slot for slot in COORDINATES if slot not in STAR)


def rational_level_lines():
    """Test the permanent on all projective edge directions in ker(z) over F5."""
    row_ids, column_ids = np.array(OFF_DIAGONAL).T
    vertices = np.arange(4)
    directions = set()
    for pivot in range(6):
        suffixes = product(range(PRIME), repeat=5 - pivot)
        edges = np.array([(0,) * pivot + (1,) + suffix for suffix in suffixes])
        matrices = np.zeros((len(edges), 4, 4), dtype=np.int64)
        matrices[:, row_ids, column_ids] = matrices[:, column_ids, row_ids] = edges
        incident = matrices.sum(axis=2)
        matrices[:, vertices, vertices] = (
            pow(2, -1, PRIME) * edges.sum(axis=1)[:, None] - 2 * incident
        ) % PRIME
        valid = np.ones(len(edges), dtype=bool)
        # The restriction has degree at most four, so the five values suffice.
        for scalar in range(1, PRIME):
            pencil = 1 + scalar * matrices
            values = sum(pencil[:, vertices, perm].prod(axis=1) for perm in PERMUTATIONS)
            valid &= (values - 24) % PRIME == 0
        directions.update(tuple(map(int, row)) for row in edges[valid])
    return directions


def relabelings(edges):
    """Return all 24 raw relabelings, with no projective normalization."""
    for perm in PERMUTATIONS:
        yield tuple(edges[OFF_DIAGONAL.index(tuple(sorted((perm[i], perm[j]))))]
                    for i, j in OFF_DIAGONAL)


def projective_orbit(edges):
    orbit = set()
    for image in relabelings(edges):
        scale = pow(next(entry for entry in image if entry), -1, PRIME)
        orbit.add(tuple(scale * entry % PRIME for entry in image))
    return orbit


def companion_polynomials(edges):
    """Evaluate the fraction-free polar elimination at six kernel edges over F5.

    With A*u+B*v+c=0, replace the full companion by its scaled version.
    Its u slots become -adj(A)*(B*v+c), v slots become det(A)*v, and
    its fixed star becomes det(A)*(0,1,0). At a genuine companion this
    is det(A) times that companion, including when the pivot is zero.
    """
    names = tuple(f"c{i}{j}" for i, j in COMPANION_SLOTS)
    coeffs, *variables = ring(names, sp.GF(PRIME), "grevlex")
    if len(edges) != len(OFF_DIAGONAL):
        raise ValueError("Supply the six edges in order 01, 02, 03, 12, 13, 23")
    kernel_values = dict(zip(OFF_DIAGONAL, edges))
    half_sum = pow(2, -1, PRIME) * sum(edges)
    for i in range(4):
        kernel_values[i, i] = half_sum - 2 * sum(kernel_values[e] for e in OFF_DIAGONAL if i in e)
    kernel = {slot: coeffs(value) for slot, value in kernel_values.items()}
    assert not any(corrected_diagonal(kernel))
    free = dict(zip(COMPANION_SLOTS, variables))
    companion = tangent_direction(free.get(slot, coeffs(int(slot == STAR[1]))) for slot in COORDINATES)
    original = pencil_coefficients(coeffs, (kernel, companion))
    linear = [sp.Poly(original.get((i, 1, 0), coeffs.zero).as_expr(), *coeffs.symbols, modulus=PRIME)
              for i in (1, 2, 3)]
    augmented = sp.Matrix([[f.coeff_monomial(v) for v in coeffs.symbols] + [f.coeff_monomial(1)]
                           for f in linear])
    pivot = augmented[:, :3]
    determinant = int(pivot.det()) % PRIME
    numerator = -pivot.adjugate() * augmented[:, 3:]
    small, *remaining = ring(names[3:], sp.GF(PRIME), "grevlex")
    substitutions = [
        small(int(numerator[i, 3])) + sum(int(numerator[i, j]) * v for j, v in enumerate(remaining))
        for i in range(3)
    ]
    free = dict(zip(COMPANION_SLOTS, substitutions + [determinant * v for v in remaining]))
    scaled = tangent_direction(free.get(slot, small(determinant * int(slot == STAR[1]))) for slot in COORDINATES)
    kernel = {slot: small(value) for slot, value in kernel_values.items()}
    equations = pencil_coefficients(small, (kernel, scaled))
    assert all(powers[1] != 1 for powers in equations)
    higher = [((i, j), equations.get((i, j, 0), small.zero))
              for i in range(3) for j in range(2, 5-i)]
    return small, higher, determinant


def obstruction_matrix(edges):
    """Build the determinantal equation in the kernel edges without expanding it.

    Each polar row i=1,2,3 has kernel degree i, so each scaled slot has
    kernel degree 6. The coefficient at s^i t^j has degree i+6j.
    A genuine companion gives a right nullvector consisting of the
    monomials in its three free slots, starting with the constant one.
    """
    coeffs, higher, pivot_det = companion_polynomials(edges)
    powers = [tuple(term.count(i) for i in range(3))
              for degree in range(5) for term in combinations_with_replacement(range(3), degree)]
    multiples, weights = [], []
    for (i, j), polynomial in higher:
        for shift in powers:
            if sum(shift) + j <= 4:
                multiples.append(coeffs.from_dict({shift: 1}) * polynomial)
                weights.append(i + 6*j)
    matrix = np.array([[int(f.get(power, 0)) % PRIME for power in powers] for f in multiples])
    assert matrix.shape == (39, 35)
    selected = [i for i in range(39) if i not in (24, 36, 37, 38)]
    assert sum(weights[i] for i in selected) == 507
    return coeffs, [multiples[i] for i in selected], matrix[selected], pivot_det


def obstruction_value(edges):
    """Evaluate the homogeneous degree-507 determinant at an F5 kernel vector."""
    _, _, square, _ = obstruction_matrix(edges)
    return int(sp.Matrix(square).det(method="domain-ge")) % PRIME


def invariant_obstruction_value(edges):
    """Evaluate the unnormalized S4 orbit sum on raw edge vectors over F5."""
    return sum(obstruction_value(image) for image in relabelings(edges)) % PRIME


def verify_companion_obstruction():
    """Replay the nonzero minors and reconstruct a degree-four identity for one."""
    coeffs, multiples, square, pivot_det = obstruction_matrix(REPRESENTATIVE)
    minor = int(sp.Matrix(square).det(method="domain-ge")) % PRIME
    assert (pivot_det, minor) == (3, 2)
    constant = np.zeros((len(multiples), 1), dtype=np.int64)
    constant[0] = 1
    solved, pivots = reduced_rows(np.column_stack((square.T, constant)))
    assert len(pivots) == len(multiples)
    assert sum((int(c) * f for c, f in zip(solved[:, -1], multiples)), coeffs.zero) == coeffs.one
    assert obstruction_value((0,) * 6) == 0
    for scale in range(2, PRIME):
        assert obstruction_value(tuple(scale*x % PRIME for x in REPRESENTATIVE)) == scale**507 * minor % PRIME
    return pivot_det, minor


if __name__ == "__main__":
    lines = rational_level_lines()
    assert len(lines) == 24 and lines == projective_orbit(REPRESENTATIVE)
    assert sum(line[0] == 1 for line in lines) == 20
    pivot_det, minor = verify_companion_obstruction()
    orbit_sum = invariant_obstruction_value(REPRESENTATIVE)
    assert orbit_sum == 1
    print(f"{len(lines)} projective F5 kernel directions in one vertex-permutation orbit")
    print(f"Polar pivot {pivot_det}, degree-507 determinant {minor} modulo five")
    print(f"Degree-507 S4 orbit sum {orbit_sum} modulo five")
    print("The specialized companion equations give a degree-four polynomial identity for one.")
