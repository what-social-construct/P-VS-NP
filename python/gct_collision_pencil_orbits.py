"""Count geometric directions excluded by the three vertex translates of the pencil."""

from itertools import combinations_with_replacement, permutations
from math import prod

import sympy as sp
from sympy.polys.rings import ring

from gct_collision_f25 import projective_census
from gct_collision_face import opposite_edge_product
from gct_collision_slice import kernel_from_edges, verify_quadratic_slice
from gct_collision_translated_sections import section_points
from gct_permanent_plucker import pencil_coefficients


def pencil_orbit_product(p, q, u, v):
    """Vanishes on exactly the prime-field pencil translates in the w=1 chart."""
    opposite_sum = 3*u - 2*p
    return opposite_sum * prod(opposite_edge_product(p, q, u + lam*opposite_sum, v-1)
                               for lam in range(5))


def verify_pencil_norm():
    """Check the norm formula before specializing the incident roots or pencil value."""
    _, x0, x1, u, v, t = ring("x0,x1,u,v,t", sp.GF(5))
    roots = (x0, x1, -x0-x1)
    p = x0*x1 + (x0+x1)*roots[2]
    q = prod(roots)
    opposites = [x**2 + v*x + u for x in roots]
    assert sum(opposites) == 3*u - 2*p
    norm = opposite_edge_product(p, q, u+t, v-1)
    assert norm == prod(t+y-x for x, y in zip(roots, opposites))
    # Keep one symbolic parameter for a direct check of the final product.
    incident = (1, t, -1-t)
    pair_sum = t - (1+t)**2
    opposite = [x**2 + 2*x + 1 for x in incident]
    total = sum(opposite)
    offsets = [x-y for x, y in zip(incident, opposite)]
    assert pencil_orbit_product(pair_sum, prod(incident), 1, 2) == (
        total * prod(total**4*z - z**5 for z in offsets))


def normalized_overlap(offsets):
    """Count directions for one ordered triple z=x-y with sum -1 and sum(y)=1."""
    algebra, x0, x1 = ring("x0,x1", sp.GF(5))
    x3 = -x0-x1
    y0, y1, y3 = (x-z for x, z in zip((x0, x1, x3), offsets))
    edges = (y3, x0, y1, x1, y0, x3)
    pure = pencil_coefficients(algebra, (kernel_from_edges(edges),))
    a, b = algebra.symbols
    basis = sp.groebner([f.as_expr() for f in pure.values()], a, b,
                        modulus=5, order="lex")
    if list(basis) == [1]:
        return 0

    # The two proper ideals in this calculation are triangular. For every
    # geometric root of the eliminant in b, the fiber in a is monic and separable.
    assert len(basis) == 2
    fiber = sp.Poly(basis[0], a)
    eliminant = sp.Poly(basis[1], b, modulus=5)
    assert fiber.degree() > 0 and fiber.LC() == 1
    assert eliminant.gcd(eliminant.diff()).is_one
    discriminant = sp.Poly(fiber.discriminant(), b, modulus=5)
    assert eliminant.gcd(discriminant).is_one
    return eliminant.degree() * fiber.degree()


def check_pencil_orbits():
    finite_sizes = [sum(field.rank for field, _, _ in section_points(r)) for r in range(5)]
    assert finite_sizes == [24, 16, 24, 24, 24]
    add, multiply, _, _, lines = projective_census()
    infinity = verify_quadratic_slice(lines, add, multiply)
    assert all(point[5] != point[0] for point in infinity)  # No pencil base point.

    # Y=sum(y_i)=0 is precisely the section r=1. For Y=1 the three
    # projective pencil values are [z_i:z_i+1], with sum(z_i)=-1.
    # Two prime-field values therefore imply three; count their intersection.
    projective_overlap = finite_overlap = finite_sizes[1]
    types = {}
    for offsets in combinations_with_replacement(range(5), 3):
        if sum(offsets) % 5 != 4:
            continue
        count = normalized_overlap(offsets)
        if count:
            types[offsets] = count
            count *= len(set(permutations(offsets)))
            projective_overlap += count
            finite_hits = 3-offsets.count(4)
            assert finite_hits != 2  # No point belongs to exactly two finite pencils.
            if finite_hits == 3:
                finite_overlap += count
    assert types == {(1, 1, 2): 2, (1, 4, 4): 6}
    assert (finite_overlap, projective_overlap) == (22, 40)

    # Every pairwise overlap equals the triple overlap for each of these unions.
    finite_union = 3*sum(finite_sizes) - 2*finite_overlap
    projective_union = 3*(sum(finite_sizes) + len(infinity)) - 2*projective_overlap
    assert (finite_union, projective_union) == (292, 328)
    print(f"Finite pencil values: triple overlap {finite_overlap}, union {finite_union}.")
    print(f"Projective pencil values: triple overlap {projective_overlap}, union {projective_union}.")


if __name__ == "__main__":
    verify_pencil_norm()
    check_pencil_orbits()
