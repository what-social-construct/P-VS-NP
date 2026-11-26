"""Check exact polynomial constraints for symmetric permanent level planes at J4.

Run with python3 gct_permanent_fiber.py. Requires SymPy. The identities
are checked with exact coefficients and hold over the complex numbers.
"""

from collections import defaultdict
from itertools import combinations, combinations_with_replacement, permutations, product

import sympy as sp
from sympy.polys.matrices import DomainMatrix


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


def hadamard_basis():
    """An orthonormal basis beginning with half the all-ones vector."""
    return sp.Matrix([[1, 1, 1, 1], [1, 1, -1, -1],
                      [1, -1, 1, -1], [1, -1, -1, 1]]) / 2


def hadamard_direction(arms, diagonal, opposite):
    """Return a tangent matrix from the all-ones and Klein character coordinates."""
    b0, b1, b2 = arms
    d0, d1, d2 = diagonal
    c0, c1, c2 = opposite
    modal = sp.Matrix([[0, b0, b1, b2], [b0, d0, c2, c1],
                      [b1, c2, d1, c0], [b2, c1, c0, d2]])
    hadamard = hadamard_basis()
    return hadamard * modal * hadamard.T


def rational_witt_components():
    """Three hyperbolic pairs and three orthogonal norm-12 vectors."""
    columns = hadamard_basis()
    one = columns[:, 0]
    characters = [columns[:, index] for index in range(1, 4)]
    pairs, perpendicular = [], []
    for index, character in enumerate(characters):
        left, right = (vector for j, vector in enumerate(characters) if j != index)
        diagonal = character * character.T
        opposite = left * right.T + right * left.T
        arm = one * character.T + character * one.T
        pairs.append((2 * diagonal + opposite + arm, (2 * diagonal - opposite - arm) / 8))
        perpendicular.append(3 * opposite + arm)
    return tuple(pairs), tuple(perpendicular)


def witt_basis():
    """Four hyperbolic pairs and a norm-12 direction for the quadratic coefficient."""
    pairs, (u, v, h) = rational_witt_components()
    return (*pairs, (u + sp.I * v, (u - sp.I * v) / 24)), h


WITT_CHART_REPRESENTATIVES = (
    ((1, 0), (2, 0), (3, 0)),
    ((0, 0), (1, 0), (3, 0)),
    ((0, 0), (1, 0), (2, 0)),
    ((0, 1), (1, 0), (2, 0)),
)


def witt_chart(pivots):
    """Normalize a projection onto three Witt lines, using (pair, side) pivots."""
    pairs, h = witt_basis()
    pivot_basis = [pairs[pair][side] for pair, side in pivots]
    dual_basis = [pairs[pair][1 - side] for pair, side in pivots]
    (omitted,) = set(range(4)) - {pair for pair, _ in pivots}
    residual_basis = [*pairs[omitted], h]
    gram = sp.Matrix([[0, 1, 0], [1, 0, 0], [0, 0, 12]])
    entries = sp.symbols("m:9")
    skew_entries = s01, s02, s12 = sp.symbols("s01 s02 s12")
    matrix = sp.Matrix(3, 3, entries)
    skew = sp.Matrix([[0, s01, s02], [-s01, 0, s12], [-s02, -s12, 0]])
    dual_coordinates = skew - matrix.T * gram * matrix / 2
    directions = tuple(
        pivot + sum((dual_coordinates[i, j] * dual_basis[i] + matrix[i, j] * residual_basis[i]
                     for i in range(3)), sp.zeros(4))
        for j, pivot in enumerate(pivot_basis)
    )
    return (*entries, *skew_entries), directions


def witt_chart_equations(pivots):
    """Return parameters and the cubic and quartic coefficient equations by multidegree."""
    parameters, directions = witt_chart(pivots)
    terms = defaultdict(list)
    for perm in permutations(range(4)):
        for degree in (3, 4):
            for rows in combinations(range(4), degree):
                for indices in product(range(3), repeat=degree):
                    powers = tuple(indices.count(index) for index in range(3))
                    terms[powers].append(sp.prod(directions[index][row, perm[row]]
                                                  for row, index in zip(rows, indices)))
    return parameters, {powers: sp.Add(*summands) for powers, summands in sorted(terms.items())}


def verify_witt_charts(base):
    pairs, h = witt_basis()
    vectors = [direction for pair in pairs for direction in pair] + [h]
    assert all(direction.is_symmetric() and sum(direction) == 0 for direction in vectors)
    off_diagonal = base - sp.eye(4)
    gram = sp.Matrix([[(left * off_diagonal * right * off_diagonal).trace()
                       for right in vectors] for left in vectors]).applyfunc(sp.expand)
    assert gram == sp.diag(*([sp.Matrix([[0, 1], [1, 0]])] * 4), 12)

    def permute(direction, permutation):
        return direction.extract(permutation, permutation)

    operations = (
        lambda direction: permute(direction, [1, 0, 3, 2]),
        lambda direction: permute(direction, [2, 3, 0, 1]),
        lambda direction: permute(direction, [0, 2, 1, 3]),
        lambda direction: direction.conjugate(),
    )
    line_maps = []
    flat_basis = sp.Matrix.hstack(*(direction.reshape(16, 1) for direction in vectors))
    inverse = (flat_basis.T * flat_basis).inv() * flat_basis.T
    for operation in operations:
        line_map = {}
        for index, direction in enumerate(vectors):
            image = operation(direction).reshape(16, 1)
            coordinates = (inverse * image).applyfunc(sp.expand)
            (target,) = [j for j, coefficient in enumerate(coordinates) if coefficient != 0]
            assert (flat_basis * coordinates - image).applyfunc(sp.expand).is_zero_matrix
            if index < 8:
                line_map[divmod(index, 2)] = divmod(target, 2)
            else:
                assert target == 8
        line_maps.append(line_map)

    charts = {tuple(zip(pairs, sides)) for pairs in combinations(range(4), 3)
              for sides in product(range(2), repeat=3)}
    covered = set(WITT_CHART_REPRESENTATIVES)
    pending = list(covered)
    while pending:
        pivots = pending.pop()
        for line_map in line_maps:
            transformed = tuple(sorted(line_map[line] for line in pivots))
            if transformed not in covered:
                covered.add(transformed)
                pending.append(transformed)
    assert covered == charts and len(charts) == 32

    for pivots in WITT_CHART_REPRESENTATIVES:
        parameters, directions = witt_chart(pivots)
        _, equations = witt_chart_equations(pivots)
        assert len(parameters) == 12 and len(equations) == 25
        values = dict(zip(parameters, range(1, 13)))
        sample = tuple(direction.xreplace(values).applyfunc(sp.expand) for direction in directions)
        difference = permanent_difference(base, sample)
        coefficients = sp.Poly.from_dict(
            {powers: sp.expand(equation.xreplace(values)) for powers, equation in equations.items()},
            difference.gens,
        )
        assert coefficients == difference


def verify_row_sum_zero_exclusion(base):
    """Check the cubic identity and degree-four unit-ideal certificate on this slice."""
    x0, x1, x2 = sp.symbols("x:3")
    y0, y1, y2 = sp.symbols("y:3")
    small = sp.Matrix([[x0, y2, y1], [y2, x1, y0], [y1, y0, x2]])
    difference = permanent_difference(base, (hadamard_direction((0, 0, 0), (x0, x1, x2), (y0, y1, y2)),))
    assert difference.nth(1) == 0
    assert sp.expand(difference.nth(2) - (small**2).trace()) == 0
    assert sp.expand(difference.nth(3) - small.per()) == 0

    a, b, c = variables = sp.symbols("a b c")
    skew = sp.Matrix([[0, a, b], [-a, 0, c], [-b, -c, 0]])
    coordinates = sp.Matrix(sp.symbols("t:3"))
    x = (sp.eye(3) + skew) * coordinates
    z = (sp.eye(3) - skew) * coordinates
    kappa = sp.Symbol("kappa")
    cubic = 2 * sp.prod(x) - sum(u * v**2 for u, v in zip(x, z)) - 2 * kappa * sp.prod(z)

    def monomials(degree):
        return [sp.prod(factors) for order in range(degree + 1)
                for factors in combinations_with_replacement(variables, order)]

    # Reduce the coefficient matrix over Z[1/2, kappa], with 2*kappa**2 = -1.
    # Full column rank after reduction implies full rank before reduction.
    prime, root = 11, 4
    assert (2 * root**2 + 1) % prime == 0
    products = []
    for coefficient in sp.Poly(cubic, *coordinates).coeffs():
        degree = sp.Poly(coefficient, *variables).total_degree()
        products.extend(sp.Poly(coefficient.subs(kappa, root) * multiplier, *variables, modulus=prime)
                        for multiplier in monomials(4 - degree))
    matrix = sp.Matrix([[polynomial.coeff_monomial(term) for term in monomials(4)]
                        for polynomial in products])
    assert matrix.shape == (46, 35)
    assert DomainMatrix.from_Matrix(matrix).convert_to(sp.GF(prime)).rank() == 35


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


def verify_three_cycle_coefficients(base):
    """Check the fixed sector, nontrivial eigencubic, and standard two-plane profiles."""
    b, c, d = sp.symbols("b c d")

    def pencil(profile):
        return permanent_difference(base, (hadamard_direction(
            [b * entry for entry in profile], [d * entry for entry in profile],
            [c * entry for entry in profile],
        ),))

    fixed = pencil((1, 1, 1))
    equations = [32 * fixed.nth(degree) for degree in (2, 3, 4)]
    for field in (sp.QQ, sp.GF(5), sp.GF(7), sp.GF(11)):
        assert list(sp.groebner([equation.subs(b, 1) for equation in equations], c, d, domain=field)) == [1]
        assert list(sp.groebner([equation.subs({b: 0, c: 1}) for equation in equations], d, domain=field)) == [1]
    assert fixed.nth(2).subs({b: 0, c: 0}) == 3 * d**2

    cubic = d**3 + 3 * (b+c)**2 * d + 8*c**3 - 12*c*(b+c)**2 + 6*(b+c)**3
    omega = sp.Symbol("omega")
    eigen = pencil((1, omega, omega**2))
    for degree, expected in ((2, 0), (3, cubic), (4, 0)):
        assert sp.rem(eigen.nth(degree) - expected, omega**2 + omega + 1, omega) == 0

    r, s = sp.symbols("r s")
    profile = (r, s, -r-s)
    norm = r**2 + r*s + s**2
    standard = pencil(profile)
    assert sp.expand(standard.nth(2) - 2 * (d**2 + 2*c**2 - 6*b**2) * norm) == 0
    assert sp.expand(standard.nth(3) + r*s*(r+s)*cubic) == 0
    assert sp.expand(4 * standard.nth(4) - ((b-c)**2 - d**2)**2 * norm**2) == 0
    star = hadamard_direction(profile, [2*entry for entry in profile], [-entry for entry in profile])
    assert star == symmetric_star(0, [2*entry for entry in profile])


def verify_actual_diagonal_exclusion(base):
    """Verify the equal-diagonal syzygy and maximality of its level two-planes."""
    diagonal = sp.symbols("d:3")
    opposite = sp.symbols("c:3")
    arm = sp.symbols("b:3")
    variables = (*diagonal, *opposite, *arm)
    direction = hadamard_direction(arm, diagonal, opposite)
    trace = sum(diagonal)
    uniform = {entry: -row for entry, row in zip(opposite, arm)}
    assert all(sp.expand(entry.subs(uniform) - trace/4) == 0 for entry in direction.diagonal())
    difference = permanent_difference(base, (direction,))
    coefficients = [sp.expand(difference.nth(j)) for j in (2, 3, 4)]
    quadratic, cubic, quartic = coefficients
    arm_square_sum = sum(entry**2 for entry in arm)
    assert sp.expand(quadratic.subs(uniform) - sum(entry**2 for entry in diagonal) + 4*arm_square_sum) == 0
    assert sp.expand(cubic.subs(uniform) - sp.prod(diagonal) - 2*trace*arm_square_sum + 8*sp.prod(arm)) == 0
    syzygy = 32*quartic + trace**4 - 2*quadratic**2 - 2*trace**2*quadratic - 8*trace*cubic
    assert sp.expand(syzygy.subs(uniform)) == 0

    gradients = [sp.Matrix([coefficient]).jacobian(variables) for coefficient in coefficients]
    s, t = sp.symbols("s t")
    plane_diagonal = (s, t, -s-t)
    common = sp.Matrix([1, 1, 1, 1, 1, 1, 0, 0, 0])
    first = sp.Matrix([1, -1, -1, -1, 0, 0, 1, 0, 0])
    second = sp.Matrix([-1, 1, -1, -1, 0, 0, 1, 0, 0])
    cases = (((0, 1, 2), (common, first)), ((1, 0, 2), (common, second)), ((1, 2, 0), (second,)))
    for permutation, complement in cases:
        plane_arm = tuple(plane_diagonal[i]/2 for i in permutation)
        plane = sp.Matrix([*plane_diagonal, *(-entry for entry in plane_arm), *plane_arm])
        plane_substitution = dict(zip(variables, plane))
        assert all(sp.expand(coefficient.xreplace(plane_substitution)) == 0 for coefficient in coefficients)
        # Vanishing at first order in any new direction is a linear system.
        rows = []
        for gradient in gradients:
            polynomials = [sp.Poly(entry.xreplace(plane_substitution), s, t) for entry in gradient]
            powers = set().union(*(polynomial.monoms() for polynomial in polynomials))
            rows.extend([polynomial.coeff_monomial(power) for polynomial in polynomials]
                        for power in sorted(powers))
        constraints = sp.Matrix(rows)
        kernel = sp.Matrix.hstack(plane.jacobian((s, t)), *complement)
        assert kernel.rank() == 2 + len(complement) == 9 - constraints.rank()
        assert (constraints * kernel).is_zero_matrix

        u, v = sp.symbols("u v")
        if len(complement) == 1:
            assert sp.expand(quadratic.xreplace(dict(zip(variables, u*complement[0])))) == -u**2
        else:
            substitution = dict(zip(variables, u*complement[0] + v*complement[1]))
            quadratic_restriction = sp.expand(quadratic.xreplace(substitution))
            cubic_restriction = sp.expand(cubic.xreplace(substitution))
            assert quadratic_restriction == 9*u**2 - 6*u*v - v**2
            assert cubic_restriction == sp.expand((u-v)*(6*u**2 - 6*u*v + v**2))
            assert sp.gcd(quadratic_restriction, cubic_restriction) == 1


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
    verify_three_cycle_coefficients(base)
    verify_actual_diagonal_exclusion(base)

    hessian = symmetric_tangent_hessian(base.rows)
    assert hessian.shape == (9, 9) and hessian.rank() == 9
    verify_witt_charts(base)
    verify_row_sum_zero_exclusion(base)

    print(f"Permanent difference for t times a symmetric star: {expected}")
    print("A rank-two pencil has constant permanent 24.")
    print(f"Maximum level-space dimension within the symmetric star support: {support_bound}")
    print("The symmetric star plane is maximal by inclusion in the full level fiber.")
    print("Checked the rank-one identity and all four Klein-four character spaces.")
    print("Checked the fixed and nontrivial sectors for a simultaneous three-cycle.")
    print("Checked that each level two-plane with zero diagonal is maximal.")
    print("The symmetric tangent Hessian has rank 9, giving an upper bound of 4.")
    print("Four representative Witt-chart systems cover all 32 projection charts.")
    print("The row-sum-zero slice has no level three-plane (coefficient rank 35 modulo 11).")


if __name__ == "__main__":
    main()
