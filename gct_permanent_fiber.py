"""Check exact polynomial constraints for symmetric permanent level planes at J4.

Run with python3 gct_permanent_fiber.py. Requires SymPy. The identities
are checked with exact coefficients and hold over the complex numbers.
"""

from itertools import combinations, combinations_with_replacement

import sympy as sp


def permanent_difference(base, directions):
    """Return the permanent difference as a polynomial in the pencil parameters."""
    parameters = sp.symbols(f"t:{len(directions)}")
    pencil = base.copy()
    for parameter, direction in zip(parameters, directions):
        pencil += parameter * direction
    return sp.Poly(pencil.per() - base.per(), *parameters)


def symmetric_star(corner, arm):
    """Build a symmetric perturbation supported on the first row and column."""
    matrix = sp.zeros(1 + len(arm))
    matrix[0, 0] = corner
    for index, entry in enumerate(arm, start=1):
        matrix[0, index] = entry
        matrix[index, 0] = entry
    return matrix


def symmetric_tangent_hessian(order):
    """Hessian at the all-ones matrix on symmetric, entry-sum-zero directions."""
    basis = []
    for i in range(order):
        for j in range(i, order):
            if i == j == 0:
                continue
            direction = sp.zeros(order)
            direction[i, j] = direction[j, i] = 1
            direction[0, 0] = -sum(direction)
            basis.append(direction)
    off_diagonal = sp.ones(order) - sp.eye(order)
    images = [off_diagonal * direction * off_diagonal for direction in basis]
    return sp.factorial(order - 2) * sp.Matrix([
        [(direction.T * image).trace() for image in images]
        for direction in basis
    ])


def verify_star_maximality_at_j4(base, directions):
    """Check that an arbitrary symmetric extension lies in the star plane."""
    coordinates = tuple(combinations_with_replacement(range(4), 2))
    entries = sp.symbols("b:10")
    extension = sp.zeros(4)
    for (row, column), entry in zip(coordinates, entries):
        extension[row, column] = extension[column, row] = entry

    difference = permanent_difference(base, (*directions, extension))
    _, _, z = difference.gens
    linear = [coefficient for powers, coefficient in difference.terms() if powers[-1] == 1]
    constraints, rhs = sp.linear_eq_to_matrix(linear, entries)
    assert constraints.rank() == 6 and rhs.is_zero_matrix

    arm = sp.symbols("w:3")
    tail = sp.Symbol("c")
    arm_sum = sum(arm)
    parameterized = symmetric_star(-2 * arm_sum - 9 * tail, arm)
    parameterized[1:, 1:] = tail * sp.ones(3)
    entries_on_kernel = sp.Matrix([parameterized[row, column] for row, column in coordinates])
    assert entries_on_kernel.jacobian((*arm, tail)).rank() == 4
    assert (constraints * entries_on_kernel).is_zero_matrix

    # The parametrization spans the kernel of the six linear constraints.
    reduced = difference.as_expr().subs(dict(zip(entries, entries_on_kernel)))
    # Over c != 0, z = -1/c zeros the bottom block and hence the permanent.
    assert sp.cancel(reduced.subs(z, -1 / tail)) == -24
    reduced_at_zero_tail = sp.Poly(reduced.subs(tail, 0), *difference.gens)
    assert sp.expand(reduced_at_zero_tail.coeff_monomial(z**2) - 2 * arm_sum**2) == 0

    # Thus c = 0 and sum(w) = 0, leaving exactly the original plane.
    assert parameterized.subs({tail: 0, arm[2]: -arm[0] - arm[1]}) == (
        arm[0] * directions[0] + arm[1] * directions[1]
    )


def verify_rank_one_expansion(base):
    entries = sp.symbols("x:4")
    vector = sp.Matrix(entries)
    difference = permanent_difference(base, (vector * vector.T,))
    for degree in range(1, 5):
        elementary = sum(sp.prod(term) for term in combinations(entries, degree))
        expected = sp.factorial(degree) * sp.factorial(4 - degree) * elementary**2
        assert sp.expand(difference.nth(degree) - expected) == 0


def verify_klein_four_coefficients(base):
    """Check the four character spaces for simultaneous regular permutations."""
    ones = sp.ones(4, 1)
    characters = (
        sp.Matrix([1, 1, -1, -1]),
        sp.Matrix([1, -1, 1, -1]),
        sp.Matrix([1, -1, -1, 1]),
    )
    u, v = sp.symbols("u v")
    for index, character in enumerate(characters):
        left, right = (entry for j, entry in enumerate(characters) if j != index)
        direction = u * (ones * character.T + character * ones.T)
        direction += v * (left * right.T + right * left.T)
        difference = permanent_difference(base, (direction,))
        (t,) = difference.gens
        expected = 32 * (v**2 - 3 * u**2) * t**2 + 64 * (u**2 + v**2)**2 * t**4
        assert difference == sp.Poly(expected, t)

    a, b, c = sp.symbols("a b c")
    d = -a - b - c
    invariant = sp.Matrix([[d, a, b, c], [a, d, c, b], [b, c, d, a], [c, b, a, d]])
    difference = permanent_difference(base, (invariant,))
    assert difference.nth(1) == 0
    assert sp.expand(difference.nth(2) - 8 * (a**2 + a*b + a*c + b**2 + b*c + c**2)) == 0
    assert sp.expand(difference.nth(3) + 8 * (a + b) * (a + c) * (b + c)) == 0
    assert sp.rem(difference.nth(4).subs(b, -a), a**2 + c**2, c) == -8 * a**4


def main():
    base = sp.ones(4)
    assert base.per() == 24

    corner, a, b, c = sp.symbols("d a b c")
    arm_sum = a + b + c
    support_difference = permanent_difference(base, (symmetric_star(corner, (a, b, c)),))
    (t,) = support_difference.gens
    expected = 6 * (corner + 2 * arm_sum) * t + 2 * arm_sum**2 * t**2
    assert support_difference == sp.Poly(expected, t)

    # In a linear level space, both coefficients vanish along every direction.
    # The quadratic coefficient forces a + b + c = 0, then the linear one gives d = 0.
    constraints = sp.Matrix([[1, 0, 0, 0], [0, 1, 1, 1]])
    support_bound = constraints.cols - constraints.rank()
    directions = (
        symmetric_star(0, (1, 0, -1)),
        symmetric_star(0, (0, 1, -1)),
    )
    basis = sp.Matrix.hstack(*(direction.reshape(base.rows * base.cols, 1) for direction in directions))
    assert basis.rank() == support_bound == 2
    assert permanent_difference(base, directions).is_zero
    verify_star_maximality_at_j4(base, directions)
    verify_rank_one_expansion(base)
    verify_klein_four_coefficients(base)

    hessian = symmetric_tangent_hessian(base.rows)
    assert hessian.shape == (9, 9) and hessian.rank() == 9

    print(f"Permanent difference for t times a symmetric star: {expected}")
    print("A rank-two pencil has constant permanent 24.")
    print(f"Maximum level-space dimension within the symmetric star support: {support_bound}")
    print("The symmetric star plane is maximal by inclusion in the full level fiber.")
    print("Checked the rank-one identity and all four Klein-four character spaces.")
    print("The symmetric tangent Hessian has rank 9, giving an upper bound of 4.")


if __name__ == "__main__":
    main()
