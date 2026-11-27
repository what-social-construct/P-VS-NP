"""Projective fixed directions of the vertex relabelings on the pure curve at five."""

import sympy as sp
from sympy.polys.agca.extensions import MonogenicFiniteExtension
from sympy.polys.rings import ring

from gct_collision_slice import kernel_from_edges
from gct_permanent_plucker import pencil_coefficients


def fixed_chart_basis(algebra, edges, relations=()):
    """Restrict the original pure permanent coefficients to an eigenchart."""
    pure = pencil_coefficients(algebra, (kernel_from_edges(edges),))
    equations = [f.as_expr() for f in (*pure.values(), *relations)]
    return sp.groebner(equations, *algebra.symbols, modulus=5, order="lex")


def check_transposition():
    algebra, u, w = ring("u,w", sp.GF(5))
    one, zero = algebra.one, algebra.zero
    # If all three edges incident to vertex 2 vanish, one opposite edge
    # can be scaled to one after relabeling. This also excludes the
    # eigenvalue-one chart for a three-cycle: equal incident edges sum to zero.
    assert list(fixed_chart_basis(algebra, (one, zero, u, zero, w, zero))) == [1]

    # Edge order 01,02,03,12,13,23. For the swap (01), both remaining
    # projective sign cases have a nonzero 02 edge, which we set to one.
    for sign, edges in (
        (1, (w, one, u, one, u, -2*one)),
        (-1, (zero, one, u, -one, -u, zero)),
    ):
        assert tuple(edges[i] for i in (0, 3, 4, 1, 2, 5)) == tuple(sign*e for e in edges)
        assert list(fixed_chart_basis(algebra, edges)) == [1]
    print("A transposition fixes no geometric point on the pure curve.")


def check_three_cycle():
    algebra, omega, v = ring("omega,v", sp.GF(5))
    unity = omega**2 + omega + 1
    # With incident triple (1,omega,omega^2), the opposite triple is v
    # times the same eigenvector. Both nontrivial eigenvalues occur here.
    edges = (v*omega**2, algebra.one, v*omega, omega, v, omega**2)
    for i, j in enumerate((4, 3, 0, 5, 2, 1)):
        assert (edges[j] - omega*edges[i]).rem([unity]) == 0
    basis = fixed_chart_basis(algebra, edges, (unity,))
    assert list(basis) == [unity.as_expr(), (v**2*(v+2)).as_expr().expand()]

    # Compare the reduced support to the singular locus in the m=1 chart.
    # How many branches lift a singular point uses the separate normalization proof.
    symbol = algebra.symbols[0]
    field = MonogenicFiniteExtension(sp.Poly(unity.as_expr(), symbol, modulus=5))
    singular = set()
    smooth = set()
    for root in (field.generator, field.generator**2):
        for slope in (field.zero, field(3)):
            e01, e02, e03, e12, e13, e23 = (
                slope*root**2, field.one, slope*root, root, slope, root**2)
            m = e03 + e13 + e23
            assert m and e02 + e12 + e23 == field.zero
            a, b, c, d = (e/m for e in (e01, e12, e13, e23))
            is_singular = a == c == field.zero and d == field.one and b*b+b+1 == field.zero
            assert is_singular == (slope == field.zero)
            (singular if is_singular else smooth).add((a, b, c, d))
    assert len(singular) == len(smooth) == 2
    print("A three-cycle fixes two smooth and two singular geometric directions.")


if __name__ == "__main__":
    check_transposition()
    check_three_cycle()
