"""Unit-ideal certificates for the involution sectors of level planes."""

from itertools import combinations, permutations, product

import sympy as sp
from sympy.polys.rings import ring

from gct_permanent_fiber import permanent_difference


def _verify_involution_charts(prime, matrix, pairs, remainder=(), extra=()):
    """Check all maximal-isotropic projection charts in the indicated slice."""
    pairs = tuple(tuple(matrix(coordinates) for coordinates in pair) for pair in pairs)
    remainder = tuple(matrix(coordinates) for coordinates in remainder)
    basis = tuple(direction for pair in pairs for direction in pair) + remainder
    assert all(direction.is_symmetric() and sum(direction) % prime == 0 for direction in basis)
    difference = sp.ones(4) - sp.eye(4)
    gram = sp.Matrix([[(left * difference * right * difference).trace() % prime
                       for right in basis] for left in basis])
    dimension = len(pairs)
    residual_count = len(remainder)
    residual_gram = gram[2*dimension:, 2*dimension:]
    assert gram == sp.diag(*[sp.Matrix([[0, 1], [1, 0]])]*dimension, residual_gram)
    assert residual_gram.det() % prime != 0  # Empty complement has determinant one.

    skew = sp.zeros(dimension)
    position_pairs = tuple(combinations(range(dimension), 2))
    entries = sp.symbols(f"k:{len(position_pairs)}")
    for (i, j), entry in zip(position_pairs, entries):
        skew[i, j], skew[j, i] = entry, -entry
    residual_entries = sp.symbols(f"m:{residual_count*dimension}")
    matrix_m = sp.Matrix(residual_count, dimension, residual_entries)
    adjusted = skew - pow(2, -1, prime)*matrix_m.T*residual_gram*matrix_m
    unknowns = (*entries, *residual_entries)

    for sides in product((0, 1), repeat=dimension):
        primal = [pair[side] for pair, side in zip(pairs, sides)]
        dual = [pair[1-side] for pair, side in zip(pairs, sides)]
        directions = tuple(
            primal[j] + sum((adjusted[i,j]*dual[i] for i in range(dimension)), sp.zeros(4))
            + sum((matrix_m[i,j]*remainder[i] for i in range(residual_count)), sp.zeros(4))
            for j in range(dimension))

        pencil = sp.symbols(f"t:{len(extra)+dimension}")
        algebra, *generators = ring([*unknowns, *pencil], sp.GF(prime), "grevlex")
        entries_in_ring = [[algebra.one + sum(
            (generator*algebra.from_expr(direction[i,j])
             for generator, direction in zip(generators[len(unknowns):], (*extra, *directions))),
            algebra.zero) for j in range(4)] for i in range(4)]
        permanent = sum((sp.prod(entries_in_ring[i][j] for i,j in enumerate(permutation))
                         for permutation in permutations(range(4))), algebra.zero)
        coefficients = {}
        for powers, value in permanent.items():
            pencil_powers = powers[len(unknowns):]
            if sum(pencil_powers):
                assert sum(pencil_powers) > 2
                coefficients.setdefault(pencil_powers, {})[powers[:len(unknowns)]] = value

        ideal = [sp.Poly.from_dict(c, *unknowns, modulus=prime) for c in coefficients.values()]
        assert list(sp.groebner(ideal, *unknowns, modulus=prime, order="grevlex")) == [1]


def double_transposition_positive(coordinates):
    a,b,c,d,e = coordinates
    f = -a-b-2*c-2*d-e
    return sp.Matrix([[a,b,c,d], [b,a,d,c], [c,d,e,f], [d,c,f,e]])


def verify_double_transposition_positive_sector_at_five():
    """Exclude level two-planes in the fixed sector of (01)(23) at five."""
    _verify_involution_charts(5, double_transposition_positive, (
        ((0,0,0,1,4), (0,0,1,3,2)),
        ((1,2,3,0,0), (2,4,1,2,0)),
    ), ((1,0,1,1,0),))


def verify_involution_exclusion(base):
    """Check geometric emptiness of the five involution slices modulo 11."""
    prime = 11

    def swap(coordinates):
        a,b,c,d,e,f = coordinates
        return sp.Matrix([[a,b,c,d], [b,a,c,d], [c,c,e,f],
                          [d,d,f,-2*a-2*b-4*c-4*d-e-2*f]])

    def double_minus(coordinates):
        a,b,c,d = coordinates
        return sp.Matrix([[a,0,c,d], [0,-a,-d,-c], [c,-d,b,0], [d,-c,0,-b]])

    def anti_direction(v):
        u = sp.Matrix([1,-1,0,0])
        v = sp.Matrix(v)
        return u*v.T + v*u.T

    x,y,z = sp.symbols("x y z")
    negative = permanent_difference(base, (anti_direction((x,x,y,z)),))
    assert sp.expand(negative.nth(2) + 8*(x*x+2*x*y+2*x*z+y*z)) == 0
    assert negative.nth(3) == 0
    assert negative.nth(4) == 4*y*y*z*z

    a,b,c,d,e,f = variables = sp.symbols("a b c d e f")
    for first, expected in [(0,2*(a-b)), (-2,2*(17*a+15*b+40*c+40*d+8*e+8*f))]:
        polynomial = permanent_difference(base, (anti_direction((first,first,0,1)), swap(variables)))
        assert polynomial.coeff_monomial((2,1)) == expected

    def swap_star(coordinates):
        a,c,d,e,f = coordinates
        return swap((a,a,c,d,e,f))

    def swap_other(coordinates):
        a,c,d,e,f = coordinates
        b = -(17*a+40*c+40*d+8*e+8*f)*pow(15,-1,prime)
        return swap((a,b,c,d,e,f))

    _verify_involution_charts(prime, swap, (
        ((0,0,0,1,0,-2), (-3,0,0,5,0,1)),
        ((5,-4,0,0,1,1), (-4,-1,2,0,4,4)),
        ((-4,-4,3,5,0,1), (-3,3,-3,-5,3,1)),
    ))
    _verify_involution_charts(prime, swap_star, (
        ((0,0,1,0,-2), (4,0,4,0,3)),
        ((2,3,0,1,0), (-4,-1,4,4,0)),
    ), ((-3,5,1,0,1),), (anti_direction((0,0,0,1)),))
    _verify_involution_charts(prime, swap_other, (
        ((0,0,0,0,1), (5,0,0,0,-4)),
        ((2,-4,0,1,1), (-5,4,-3,-3,-3)),
    ), ((-3,1,3,-5,1),), (anti_direction((-2,-2,0,1)),))
    _verify_involution_charts(prime, double_transposition_positive, (
        ((0,0,0,1,-1), (-2,0,0,-3,3)),
        ((2,1,1,0,-2), (1,0,4,2,3)),
    ), ((-1,-5,-2,0,1),))
    _verify_involution_charts(prime, double_minus, (
        ((0,1,1,-5), (-2,4,4,2)),
        ((-4,-1,1,1), (-3,3,2,5)),
    ))


if __name__ == "__main__":
    verify_involution_exclusion(sp.ones(4))
    print("Both involution types excluded by all 24 charts modulo 11.")
