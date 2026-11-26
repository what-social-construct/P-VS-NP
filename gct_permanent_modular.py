"""Exact modular certificates for permanent level planes.

Run with python3 gct_permanent_modular.py. Requires SymPy and NumPy
(integer arithmetic only).
"""

from collections import deque
from itertools import combinations, combinations_with_replacement, permutations, product

import numpy as np
import sympy as sp
from sympy.polys.rings import ring

from gct_permanent_fiber import (hadamard_basis, hadamard_direction, permanent_difference,
                                 rational_witt_components)


def modular_witt_basis(prime):
    """Build the split nine-dimensional basis over the given prime field."""
    pairs, (u, v, w) = rational_witt_components()
    a, b = next((a, b) for a, b in product(range(prime), repeat=2)
                if (1 + a*a + b*b) % prime == 0)
    pairs = (*pairs, (u + a*v + b*w, (u - a*v - b*w) / 24))
    remainder = -b*v + a*w

    def reduce_matrix(matrix):
        return np.array([[int(entry.p) * pow(int(entry.q), -1, prime) % prime for entry in row]
                         for row in matrix.tolist()], dtype=np.int64)

    vectors = [direction for pair in pairs for direction in pair] + [remainder]
    off_diagonal = sp.ones(4) - sp.eye(4)
    gram = sp.Matrix([[(left * off_diagonal * right * off_diagonal).trace()
                       for right in vectors] for left in vectors])
    expected = sp.diag(*([sp.Matrix([[0, 1], [1, 0]])] * 4), -12)
    assert np.array_equal(reduce_matrix(gram), reduce_matrix(expected))
    assert all(not sum(reduce_matrix(direction).flat) % prime for direction in vectors)
    return np.array([[reduce_matrix(direction) for direction in pair] for pair in pairs]), reduce_matrix(remainder)


def verify_no_prime_field_three_plane(prime):
    """Exclude rational planes by checking necessary conditions on each chart."""
    pairs, remainder = modular_witt_basis(prime)
    masks = [
        np.array([[(row, permutation[row]) for row in rows]
                  for rows in combinations(range(4), degree)
                  for permutation in permutations(range(4))])
        for degree in (3, 4)
    ]

    def higher_coefficients_vanish(directions):
        cubic, quartic = (
            directions[..., mask[:, :, 0], mask[:, :, 1]].prod(axis=-1).sum(axis=-1) % prime
            for mask in masks
        )
        return (cubic == 0) & (quartic == 0)

    choices = np.array(list(product(range(prime), repeat=5)), dtype=np.int64)
    u, v, w = choices[:, :3].T
    diagonal_dual = -u*v + 6*w*w
    for selected in combinations(range(4), 3):
        (omitted,) = set(range(4)) - set(selected)
        residual_basis = np.array([*pairs[omitted], remainder])
        residual = np.einsum("ni,ijk->njk", choices[:, :3], residual_basis)
        for sides in product(range(2), repeat=3):
            pivot = [pairs[index, side] for index, side in zip(selected, sides)]
            dual = [pairs[index, 1-side] for index, side in zip(selected, sides)]
            columns = []
            for j in range(3):
                other = [i for i in range(3) if i != j]
                dual_coordinates = np.zeros((len(choices), 3), dtype=np.int64)
                dual_coordinates[:, j] = diagonal_dual
                dual_coordinates[:, other] = choices[:, 3:]
                directions = (pivot[j] + residual + np.einsum("ni,ijk->njk", dual_coordinates, dual)) % prime
                valid = higher_coefficients_vanish(directions)
                columns.append((directions[valid], choices[valid, :3], dual_coordinates[valid]))

            edges = {}
            for i, j in combinations(range(3), 2):
                left, left_residual, left_dual = columns[i]
                right, right_residual, right_dual = columns[j]
                pairs_in_chart = set()
                gram = np.array([[0, 1, 0], [1, 0, 0], [0, 0, -12]])
                for start in range(0, len(left), 100):
                    block = slice(start, start + 100)
                    mixed_quadratic = (left_residual[block] @ gram @ right_residual.T
                                       + left_dual[block, j, None] + right_dual[None, :, i])
                    row, col = np.where(mixed_quadratic % prime == 0)
                    row += start
                    for scalar in (1, 2, 3):
                        valid = higher_coefficients_vanish((left[row] + scalar*right[col]) % prime)
                        row, col = row[valid], col[valid]
                    pairs_in_chart.update(zip(row, col))
                edges[i, j] = pairs_in_chart

            for i, j in edges[0, 1]:
                assert not any((j, k) in edges[1, 2] for l, k in edges[0, 2] if l == i)


def unit_ideal_at_degree(generators, variable_count, prime, degree_cap):
    """Find a nonzero constant using bounded-degree ideal operations."""
    assert 2 * prime <= 256
    exponents = []
    for degree in range(degree_cap, -1, -1):
        powers = [tuple(indices.count(i) for i in range(variable_count))
                  for indices in combinations_with_replacement(range(variable_count), degree)]
        exponents.extend(sorted(powers, key=lambda term: term[::-1]))
    index = {powers: i for i, powers in enumerate(exponents)}
    width = len(exponents)
    highest = sum(sum(powers) == degree_cap for powers in exponents)
    shifts = [
        np.array([index[powers[:i] + (powers[i] + 1,) + powers[i+1:]]
                  for powers in exponents[highest:]])
        for i in range(variable_count)
    ]

    pending = deque()
    for polynomial in generators:
        row = np.zeros(width, dtype=np.uint8)
        for powers, coefficient in polynomial.items():
            row[index[powers]] = int(coefficient) % prime
        pending.append(row)
    pivots = [None] * width
    # Indexing tables generate residues and negative multiples exactly.
    residues = np.tile(np.arange(prime, dtype=np.uint8), 2)
    scales = (-np.arange(prime) * np.arange(prime)[:, None] % prime).astype(np.uint8)
    while pending:
        row = pending.popleft()
        for i, entry in enumerate(row):
            coefficient = int(entry)
            if not coefficient:
                continue
            if pivots[i] is not None:
                row[i+1:] = residues[row[i+1:] + pivots[i][coefficient]]
                row[i] = 0
                continue
            if i == width - 1:
                return True
            row[i:] = scales[-pow(coefficient, -1, prime) % prime, row[i:]]
            pivots[i] = scales[:, row[i+1:]]
            if i >= highest:
                for shift in shifts:
                    multiple = np.zeros(width, dtype=np.uint8)
                    multiple[shift[i-highest:]] = row[i:]
                    pending.append(multiple)
            break
    return False


def verify_no_row_sum_zero_two_plane():
    """Check the one representative two-plane chart over the algebraic closure of F11."""
    prime, kappa = 11, 4
    assert (2*kappa*kappa + 1) % prime == 0
    pencil_ring, a, b, c, d, g, s, t = ring("a,b,c,d,g,s,t", sp.GF(prime), "grevlex")
    u, v = a*s + b*t, c*s + d*t
    alpha = g*t - (a*u - c*v)/4
    beta = -g*s - (b*u - d*v)/4
    x = (s + alpha, t + beta, u)
    y = (kappa*(s - alpha), kappa*(t - beta), kappa*v)
    assert not sum(xx*xx + 2*yy*yy for xx, yy in zip(x, y))
    cubic = x[0]*x[1]*x[2] + sum(xx*yy*yy for xx, yy in zip(x, y)) + 2*y[0]*y[1]*y[2]
    modal = [[x[0], y[2], y[1]], [y[2], x[1], y[0]], [y[1], y[0], x[2]]]
    # The factor four in the original matrix scales the quartic by a unit.
    characters = (2*hadamard_basis()[:, 1:]).tolist()
    entries = [[sum((int(characters[i][j]) * modal[j][k] * int(characters[l][k])
                     for j in range(3) for k in range(3)), pencil_ring.zero)
                for l in range(4)] for i in range(4)]
    quartic = sum((sp.prod(entries[i][j] for i, j in enumerate(permutation))
                   for permutation in permutations(range(4))), pencil_ring.zero)
    equations = []
    for polynomial in (cubic, quartic):
        by_pencil_degree = {}
        for powers, coefficient in polynomial.items():
            by_pencil_degree.setdefault(powers[-2:], {})[powers[:-2]] = coefficient
        equations.extend(by_pencil_degree[powers] for powers in sorted(by_pencil_degree))
    assert len(equations) == 9
    assert unit_ideal_at_degree(equations, 5, prime, degree_cap=10)


def verify_contrast_diagonal_exclusion(base):
    """Exclude level two-planes with zero Hadamard contrast diagonal modulo 23."""

    def cubic(opposite, arm):
        difference = [entry - row for entry, row in zip(opposite, arm)]
        return sp.prod(difference) + 4 * sp.prod(arm)

    def quartic(opposite, arm):
        u = [entry + row for entry, row in zip(opposite, arm)]
        v = [entry - row for entry, row in zip(opposite, arm)]
        return ((sum(entry**2 for entry in v) - sum(entry**2 for entry in u))**2
                + 4 * sum(a**2 * b**2 for a, b in zip(u, v))
                - 4 * sum(a**2 * b**2 for a, b in combinations(u, 2)))

    opposite = sp.symbols("c:3")
    arm = sp.symbols("b:3")
    difference = permanent_difference(base, (hadamard_direction(arm, (0, 0, 0), opposite),))
    assert difference.nth(1) == 0
    assert sp.expand(difference.nth(2) - 2 * sum(a**2 - 3*b**2 for a, b in zip(opposite, arm))) == 0
    assert sp.expand(difference.nth(3) - 2 * cubic(opposite, arm)) == 0
    assert sp.expand(16 * difference.nth(4) - quartic(opposite, arm)) == 0

    # If none of the arm coordinates vanishes identically, normalize two
    # independent ones as s,t and factor the cubic on the plane.
    prime = 23
    s, t = parameters = sp.symbols("s t")
    alpha, beta, *scales = variables = sp.symbols("alpha beta k:3")
    arm = (s, t, alpha*s + beta*t)
    representatives = ((0, 1, 2), (1, 0, 2), (2, 1, 0), (1, 2, 0))
    for permutation in representatives:
        opposite = tuple(arm[i] + scales[i]*arm[j] for i, j in enumerate(permutation))
        quadratic = sum(a**2 - 3*b**2 for a, b in zip(opposite, arm))
        generators = [sp.prod(scales) + 4]
        generators += sp.Poly(quadratic, *parameters).coeffs()
        generators += sp.Poly(quartic(opposite, arm), *parameters).coeffs()
        basis = sp.groebner(generators, *variables, modulus=prime, order="grevlex")
        assert list(basis) == [1]

    # If the first arm coordinate vanishes, the cubic forces c_j=b_j
    # identically. The two representatives j=0,1 each have four Witt charts.
    skew_entry = sp.Symbol("w")
    skew_times_parameters = (skew_entry*t, -skew_entry*s)
    roots = {2: 5, 3: 7}
    assert all(root**2 % prime == norm for norm, root in roots.items())
    for vanish_index, norms in enumerate(((3, 3), (2, 3))):
        for signs in product((1, -1), repeat=2):
            scaled = [offset * pow(2*norm, -1, prime)
                      for offset, norm in zip(skew_times_parameters, norms)]
            plus = [roots[norm] * (value + correction)
                    for norm, value, correction in zip(norms, parameters, scaled)]
            minus = [sign * (value - correction)
                     for sign, value, correction in zip(signs, parameters, scaled)]
            arm = (0, *minus)
            opposite = (0, *plus) if vanish_index == 0 else (plus[0], minus[0], plus[1])
            quadratic = sum(a**2 - 3*b**2 for a, b in zip(opposite, arm))
            assert sp.Poly(quadratic, *parameters, skew_entry, modulus=prime).is_zero
            assert cubic(opposite, arm) == 0
            coefficients = sp.Poly(quartic(opposite, arm), *parameters).coeffs()
            assert sp.gcd_list(coefficients, skew_entry, modulus=prime) == 1


def main():
    for prime in (5, 7):
        verify_no_prime_field_three_plane(prime)
        print(f"No F{prime}-rational three-plane in any of the 32 Witt charts.")
    verify_no_row_sum_zero_two_plane()
    print("The zero-row-sum two-plane chart ideal contains 1 over F11.")
    verify_contrast_diagonal_exclusion(sp.ones(4))
    print("All 12 zero-contrast-diagonal two-plane branch ideals contain 1 over F23.")


if __name__ == "__main__":
    main()
