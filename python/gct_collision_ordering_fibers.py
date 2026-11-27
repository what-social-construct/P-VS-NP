"""Split the six ordered labelings of each separable incident cubic over its residue field."""

from collections import Counter

import sympy as sp
from sympy.polys.agca.extensions import MonogenicFiniteExtension
from sympy.polys.rings import ring


def ordering_factors(field, p, q):
    """Return the residue degrees over field of the factors of its ordering algebra."""
    if field == sp.GF(5):
        degree = 1
    elif (isinstance(field, MonogenicFiniteExtension) and field.domain == sp.GF(5)
          and field.modulus.is_irreducible):
        degree = field.rank
    else:
        raise ValueError("expected a finite field over F5")
    p, q = field.convert(p), field.convert(q)
    if not -4*p**3 - 27*q**2:
        raise ValueError("ordering fibers require a separable incident cubic")

    algebra, x = ring("x", field)
    cubic = x**3 + algebra(p)*x - algebra(q)
    image = x
    for order in (1, 2, 3):
        for _ in range(degree):
            image = (image**5).rem([cubic])
        if image == x:
            return (order,) * (6 // order)
    raise ArithmeticError("Frobenius did not return the roots of the separable cubic")


def check_quadratic_labelings():
    from gct_collision_quadratic_slopes import quadratic_slope_points

    tally = Counter()
    for field, (p, q, _, _) in quadratic_slope_points():
        factors = ordering_factors(field, p, q)
        tally[factors[0]] += 1
    assert tally == {1: 7, 2: 16, 3: 7}
    print("Quotient closed points by splitting degree:", dict(sorted(tally.items())))
    print("Labeled closed points:", sum(count * (6 // h) for h, count in tally.items()))


if __name__ == "__main__":
    check_quadratic_labelings()
