"""Exact Frobenius relabeling exclusions for order-four level planes at five."""

from itertools import combinations, permutations, product

import numpy as np

from gct_permanent_involutions import verify_double_transposition_positive_sector_at_five
from gct_permanent_modular import (
    verify_no_prime_field_three_plane,
    verify_witt_three_plane_charts,
)


# The monic extension polynomials are x^2-2, x^3+x+1, and x^4+2.
TWISTS = (
    ((1, 0, 2, 3), (3, 0)),
    ((1, 0, 3, 2), (3, 0)),
    ((0, 2, 3, 1), (1, 1, 0)),
    ((1, 2, 3, 0), (2, 0, 0, 0)),
)


def extension_tables(modulus):
    """Encoding with base-five digits and polynomial reduction modulo a monic polynomial."""
    degree = len(modulus)
    place_values = 5**np.arange(degree, dtype=np.int64)
    elements = np.arange(5**degree, dtype=np.int64)
    digits = elements[:, None] // place_values % 5
    add = np.einsum("ijk,k->ij", (digits[:, None] + digits[None, :]) % 5, place_values)

    coefficients = np.zeros((2*degree-1, len(elements), len(elements)), dtype=np.int64)
    for i, j in product(range(degree), repeat=2):
        coefficients[i+j] += digits[:, i, None] * digits[None, :, j]
    for exponent in range(2*degree-2, degree-1, -1):
        for j, coefficient in enumerate(modulus):
            coefficients[exponent-degree+j] -= coefficient*coefficients[exponent]
    multiply = np.einsum("kij,k->ij", coefficients[:degree] % 5, place_values)

    def power(x, exponent):
        result = 1
        while exponent:
            if exponent % 2:
                result = multiply[result, x]
            x = multiply[x, x]
            exponent //= 2
        return result

    # Construction gives quotient-ring arithmetic. Existence of inverses
    # for every nonzero residue certifies that the modulus is irreducible.
    assert np.all(power(elements[1:], len(elements)-1) == 1)
    frobenius = power(elements, 5)
    assert np.array_equal(np.sort(frobenius), elements)
    assert np.array_equal(frobenius[:5], elements[:5])
    return digits, place_values, add, multiply, frobenius


def independent_rows(vectors):
    """Select rows forming a basis of the row span over F5."""
    basis = []
    echelon = []
    for vector in vectors:
        row = vector.copy()
        for pivot, known in echelon:
            row = (row - row[pivot]*known) % 5
        support = np.flatnonzero(row)
        if len(support):
            pivot = int(support[0])
            echelon.append((pivot, row*pow(int(row[pivot]), -1, 5) % 5))
            basis.append(vector)
    return np.array(basis)


def field_sum(add, values):
    result = 0
    for value in values:
        result = add[result, value]
    return result


def fixed_tangent_basis(permutation, digits, places, add, multiply, frobenius):
    """Build the sum-zero fixed subspace for Frob(B)=B[permutation,permutation]."""
    degree = len(places)
    elements = np.arange(len(digits))
    subfield_bases = {}
    iterate = elements.copy()
    for length in range(1, degree+1):
        iterate = frobenius[iterate]
        if degree % length == 0:
            fixed = digits[iterate == elements]
            assert len(fixed) == 5**length
            basis = independent_rows(fixed)
            assert len(basis) == length
            subfield_bases[length] = basis @ places
    assert np.array_equal(iterate, elements)

    slots = set(combinations(range(4), 2)) | {(i, i) for i in range(4)}
    matrices = []
    while slots:
        first = min(slots)
        orbit = [first]
        while True:
            successor = tuple(sorted(permutation[i] for i in orbit[-1]))
            if successor == first:
                break
            orbit.append(successor)
        slots.difference_update(orbit)
        for element in subfield_bases[len(orbit)]:
            matrix = np.zeros((4, 4), dtype=np.int64)
            for i, j in orbit:
                matrix[i, j] = matrix[j, i] = element
                element = frobenius[element]
            matrices.append(matrix)
    basis = np.array(matrices)
    assert len(basis) == 10
    assert np.array_equal(frobenius[basis], basis[:, permutation, :][:, :, permutation])
    assert len(independent_rows(digits[basis].reshape(10, -1))) == 10

    sums = field_sum(add, basis.reshape(10, 16).T)
    assert np.all(sums < 5)
    pivot = next(i for i, value in enumerate(sums) if value)
    scales = -sums*pow(int(sums[pivot]), -1, 5) % 5
    tangent = add[basis, multiply[scales[:, None, None], basis[pivot]]]
    tangent = np.delete(tangent, pivot, axis=0)
    assert np.all(field_sum(add, tangent.reshape(9, 16).T) == 0)
    assert len(independent_rows(digits[tangent].reshape(9, -1))) == 9
    return tangent


def witt_coordinates(gram):
    """Compute four hyperbolic pairs with Gram entry one and a residual line."""
    def pair(left, right):
        return int(left @ gram @ right) % 5

    remainder = np.eye(9, dtype=np.int64)
    basis = []
    while len(remainder) > 1:
        width = min(len(remainder), 3)
        first = next(row for coefficients in product(range(5), repeat=width)
                     if np.any(row := np.array(coefficients) @ remainder[:width] % 5)
                     and pair(row, row) == 0)
        second = next(row*pow(pair(first, row), -1, 5) % 5
                      for row in remainder if pair(first, row))
        second = (second - 3*pair(second, second)*first) % 5
        basis.extend((first, second))
        remainder = independent_rows(
            (row - pair(row, second)*first - pair(row, first)*second) % 5
            for row in remainder
        )
        assert len(remainder) == 9-len(basis)

    basis.append(remainder[0])
    norm = pair(basis[-1], basis[-1])
    expected = np.zeros((9, 9), dtype=np.int64)
    for i in range(0, 8, 2):
        expected[i, i+1] = expected[i+1, i] = 1
    expected[-1, -1] = norm
    basis = np.array(basis)
    assert norm and np.array_equal(basis @ gram @ basis.T % 5, expected)
    return basis, norm


def verify_twisted_three_plane_exclusion(permutation, modulus):
    """Prove absence of a point fixed by Frob followed by inverse relabeling."""
    digits, places, add, multiply, frobenius = extension_tables(modulus)
    tangent = fixed_tangent_basis(permutation, digits, places, add, multiply, frobenius)
    perms = np.array(list(permutations(range(4))))
    rows = np.arange(4)
    quadratic_masks = tuple((i,j) for i,j in combinations(range(4), 2))

    def quadratic(matrices):
        terms = matrices[..., rows, perms]
        return field_sum(add, (
            field_sum(add, np.moveaxis(multiply[terms[..., i], terms[..., j]], -1, 0))
            for i, j in quadratic_masks
        ))

    gram = np.zeros((9, 9), dtype=np.int64)
    for i, j, k, l in product(range(4), repeat=4):
        if j != k and l != i:
            gram = add[gram, multiply[tangent[:, None, i, j], tangent[None, :, k, l]]]
    assert np.all(gram < 5)
    assert np.array_equal(gram, gram.T)
    assert np.array_equal(quadratic(tangent), np.diag(gram))
    assert np.array_equal(quadratic(add[tangent[:, None], tangent[None, :]]),
                          (np.diag(gram)[:, None] + np.diag(gram)[None, :] + 2*gram) % 5)
    transform, norm = witt_coordinates(gram)

    def linear_combination(coordinates, basis):
        return field_sum(add, (
            multiply[coordinates[..., i, None, None], matrix] for i, matrix in enumerate(basis)
        ))

    basis = linear_combination(transform, tangent)
    assert np.array_equal(frobenius[basis], basis[:, permutation, :][:, :, permutation])

    def permanent(matrices):
        terms = matrices[..., rows, perms]
        products = multiply[multiply[terms[..., 0], terms[..., 1]],
                            multiply[terms[..., 2], terms[..., 3]]]
        return field_sum(add, np.moveaxis(products, -1, 0))

    def higher_coefficients_vanish(coordinates):
        matrix = linear_combination(coordinates, basis)
        return (permanent(matrix) == 0) & (permanent(add[matrix, 1]) == 4)

    verify_witt_three_plane_charts(5, norm, higher_coefficients_vanish)


if __name__ == "__main__":
    verify_double_transposition_positive_sector_at_five()
    print("Double-transposition fixed sector: all four Witt charts excluded.")
    verify_no_prime_field_three_plane(5)
    print("Identity twist: all 32 Witt charts excluded.")
    for permutation, modulus in TWISTS:
        verify_twisted_three_plane_exclusion(permutation, modulus)
        print(f"Twist {permutation}: all 32 Witt charts excluded.")
