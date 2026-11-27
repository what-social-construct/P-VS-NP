"""Check the auxiliary covector square on a split intersection of three quadrics."""

from itertools import product
from math import prod

import sympy as sp
from sympy.polys.rings import ring

from gct_collision_kernel_reduction import determinant
from gct_permanent_extensions import PRIME


def polar_cofactor(columns, covector):
    """Signed maximal minors after appending the auxiliary covector as the last row."""
    result = []
    for omitted in range(5):
        slots = [j for j in range(5) if j != omitted]
        result.append(sum((-1)**(omitted + 3 + pos) * covector[j]
                          * determinant([columns[k] for k in slots if k != j])
                          for pos, j in enumerate(slots)))
    return result


def check_split_octad():
    algebra, *d = ring("d0,d1,d2,d3,d4", sp.GF(PRIME))
    linear_product = sextic_product = algebra.one
    # H = X4. The three quadrics are Xi² − X3² + (i+1) X4², i = 0,1,2.
    # On H all eight simple roots have X3=1 and independent signs.
    for signs in product((-1, 1), repeat=3):
        x = (*signs, 1, 0)
        polars = []
        for i in range(3):
            row = [0] * 5
            row[i], row[3], row[4] = x[i], -x[3], (i+1) * x[4]
            polars.append(row)
        c = polar_cofactor(list(zip(*polars)), d)
        sextic = c[0]**2 - c[3]**2 + c[4]**2
        linear = sum(coordinate * value for coordinate, value in zip(x, d))
        assert sextic == linear**2
        linear_product *= linear
        sextic_product *= sextic
    assert sextic_product == linear_product**2

    # Along this pencil only the all-positive root meets D at t=0.
    t = sp.Symbol("t")
    pencil = dict(zip(algebra.symbols, (1, 1, 1, t-3, 1)))
    linear = sp.Poly(linear_product.as_expr().subs(pencil), t, modulus=PRIME)
    sextic = sp.Poly(sextic_product.as_expr().subs(pencil), t, modulus=PRIME)
    assert linear.nth(0) == 0 and linear.nth(1) != 0
    assert sextic.nth(0) == sextic.nth(1) == 0 and sextic.nth(2) != 0


def section_degree(degrees, twists):
    weight = prod(degrees)
    return 5 * weight + sum(twist * (weight // degree)
                            for twist, degree in zip(twists, degrees))


if __name__ == "__main__":
    check_split_octad()
    raw = section_degree((1, 2, 2, 2, 6), (0, 0, 1, 2, 2*5+6))
    auxiliary = section_degree((1, 2, 2, 2, 1), (0, 0, 1, 2, 0))
    residual = raw - 2 * auxiliary
    quotient_bound = 24 * residual // 6
    assert (raw, auxiliary, residual, quotient_bound) == (440, 52, 336, 1344)
    print("Eight split points verified for symbolic D. At t=0 the two products "
          "have orders one and two. Section degrees 440 = 2·52 + 336, quotient bound 1344.")
