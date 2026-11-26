"""Check a symmetric permanent level plane and its support bound at J4.

Run with python3 gct_permanent_fiber.py. Requires SymPy. The identities
are checked with exact coefficients and hold over the complex numbers.
"""

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

    hessian = symmetric_tangent_hessian(base.rows)
    assert hessian.shape == (9, 9) and hessian.rank() == 9

    print(f"Permanent difference for t times a symmetric star: {expected}")
    print("A rank-two pencil has constant permanent 24.")
    print(f"Maximum level-space dimension within the symmetric star support: {support_bound}")
    print("The symmetric tangent Hessian has rank 9, giving an upper bound of 4.")


if __name__ == "__main__":
    main()
