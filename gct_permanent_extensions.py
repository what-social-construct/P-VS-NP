"""Exact extension obstruction for F5-rational level two-planes at J4."""

from collections import Counter
from itertools import combinations, combinations_with_replacement, permutations, product

import numpy as np
import sympy as sp
from sympy.polys.rings import ring

PRIME = 5
COORDINATES = tuple(combinations_with_replacement(range(4), 2))[1:]
ROWS, COLUMNS = np.array(COORDINATES).T
OFF_DIAGONAL = np.ones((4, 4), dtype=np.int64) - np.eye(4, dtype=np.int64)
PERMUTATIONS = tuple(permutations(range(4)))


def tangent_matrices(coordinates):
    matrices = np.zeros((*coordinates.shape[:-1], 4, 4), dtype=np.int64)
    matrices[..., ROWS, COLUMNS] = coordinates
    matrices[..., COLUMNS, ROWS] = coordinates
    matrices[..., 0, 0] = -matrices.sum(axis=(-2, -1)) % PRIME
    return matrices


def reduced_rows(matrix):
    matrix = matrix.copy() % PRIME
    pivots = []
    for column in range(matrix.shape[1]):
        pivot_row = len(pivots)
        choices = np.flatnonzero(matrix[pivot_row:, column])
        if not len(choices):
            continue
        source_row = pivot_row + choices[0]
        matrix[[pivot_row, source_row]] = matrix[[source_row, pivot_row]]
        matrix[pivot_row] *= pow(int(matrix[pivot_row, column]), -1, PRIME)
        matrix[pivot_row] %= PRIME
        factors = matrix[:, column].copy()
        factors[pivot_row] = 0
        matrix = (matrix - factors[:, None]*matrix[pivot_row]) % PRIME
        pivots.append(column)
    return matrix, pivots


def level_two_planes():
    masks = [
        np.array([[(row, perm[row]) for row in rows]
                  for rows in combinations(range(4), degree)
                  for perm in PERMUTATIONS])
        for degree in (3, 4)
    ]

    def higher_coefficients_vanish(matrices):
        return np.logical_and.reduce([
            matrices[..., mask[:, :, 0], mask[:, :, 1]].prod(axis=-1).sum(axis=-1) % PRIME == 0
            for mask in masks
        ])

    directions = []
    for pivot in range(9):
        powers = PRIME**np.arange(8-pivot, dtype=np.int64)
        count = PRIME**(8-pivot)
        for start in range(0, count, 12000):
            serials = np.arange(start, min(start+12000, count))
            coordinates = np.zeros((len(serials), 9), dtype=np.int64)
            coordinates[:, pivot] = 1
            coordinates[:, pivot+1:] = serials[:, None]//powers % PRIME
            matrices = tangent_matrices(coordinates)
            q2 = np.einsum("nij,nij->n", matrices, OFF_DIAGONAL@matrices@OFF_DIAGONAL)
            isotropic = matrices[q2 % PRIME == 0]
            directions.append(isotropic[higher_coefficients_vanish(isotropic)])
    directions = np.concatenate(directions)
    assert len(directions) == 3918

    flattened = directions.reshape(-1, 16)
    paired_vectors = (OFF_DIAGONAL@directions@OFF_DIAGONAL).reshape(-1, 16)
    planes = {}
    pair_count = 0
    for start in range(0, len(directions), 48):
        i, j = np.where(flattened[start:start+48]@paired_vectors.T % PRIME == 0)
        i += start
        ordered = i < j
        i, j = i[ordered], j[ordered]
        # After pure terms vanish, the three evaluations kill every mixed term.
        for scalar in (1, 2, 3):
            valid = higher_coefficients_vanish((directions[i]+scalar*directions[j]) % PRIME)
            i, j = i[valid], j[valid]
        pair_count += len(i)
        for a, b in zip(i, j):
            plane, pivots = reduced_rows(directions[[a,b]][:, ROWS, COLUMNS])
            assert len(pivots) == 2
            planes[tuple(plane.flat)] = plane
    assert pair_count == 2340 and len(planes) == 156
    return np.array(list(planes.values()))


def extension_derivatives(planes):
    bases = tangent_matrices(planes)
    coordinates = tangent_matrices(np.eye(9, dtype=np.int64))
    derivative = np.zeros((len(planes), 9, 9), dtype=np.int64)
    offset = 0
    for degree in (2, 3, 4):
        for permutation in PERMUTATIONS:
            for rows in combinations(range(4), degree):
                for z_row in rows:
                    other_rows = [row for row in rows if row != z_row]
                    for choice in product(range(2), repeat=degree-1):
                        coefficient = np.ones(len(planes), dtype=np.int64)
                        for row, basis in zip(other_rows, choice):
                            coefficient *= bases[:, basis, row, permutation[row]]
                        derivative[:, offset+sum(choice), :] += (
                            coefficient[:, None]*coordinates[None, :, z_row, permutation[z_row]]
                        )
        offset += degree
    assert not np.any(derivative@planes.swapaxes(1, 2) % PRIME)
    return derivative % PRIME


def extension_generators(plane, derivative):
    _, plane_pivots = reduced_rows(plane)
    # Fix representatives modulo U by setting the frame's pivot entries to zero.
    slice_matrix = np.vstack((derivative, np.eye(9, dtype=np.int64)[plane_pivots]))
    normal, pivots = reduced_rows(slice_matrix)
    complement = []
    for column in sorted(set(range(9))-set(pivots)):
        coordinate = np.eye(9, dtype=np.int64)[:, column].copy()
        coordinate[pivots] = -normal[:len(pivots), column]
        complement.append(coordinate % PRIME)
    dimension = len(complement)
    assert dimension <= 2
    if dimension == 0:
        return dimension

    u, v = sp.symbols("u v")
    parameters = (u, v)[:dimension]
    algebra, *symbols = ring((*parameters, *sp.symbols("s t z")), sp.GF(PRIME), "grevlex")
    s, t, z = symbols[dimension:]
    basis = tangent_matrices(plane)
    representatives = tangent_matrices(np.array(complement))
    pencil = [[algebra.one + s*int(basis[0,i,j]) + t*int(basis[1,i,j]) + z*sum(
        (symbol*int(matrix[i,j]) for symbol, matrix in zip(symbols[:dimension], representatives)),
        algebra.zero) for j in range(4)] for i in range(4)]
    permanent = sum(
        (sp.prod(pencil[i][j] for i, j in enumerate(permutation))
         for permutation in PERMUTATIONS), algebra.zero,
    )
    coefficients = {}
    for exponent, value in permanent.items():
        powers = exponent[-3:]
        if sum(powers):
            assert powers[-1] >= 2
            coefficients.setdefault(powers, {})[exponent[:dimension]] = value
    equations = [sp.Poly.from_dict(term, *parameters, modulus=PRIME).as_expr()
                 for term in coefficients.values()]
    assert equations  # At least one excludes the only projective point when dimension is one.
    if dimension == 2:
        assert sp.gcd_list([equation.subs(u, 1) for equation in equations], v, modulus=PRIME) == 1
        assert any(equation.subs({u: 0, v: 1}) % PRIME != 0 for equation in equations)
    return dimension


def verify_f5_two_plane_extensions():
    """Every F5-rational level two-plane lacks an extension even over Fbar5."""
    planes = level_two_planes()
    derivatives = extension_derivatives(planes)
    residual_dimensions = Counter(
        extension_generators(plane, derivative) for plane, derivative in zip(planes, derivatives)
    )
    assert residual_dimensions == {0: 44, 1: 96, 2: 16}
    return residual_dimensions


if __name__ == "__main__":
    print(verify_f5_two_plane_extensions())
