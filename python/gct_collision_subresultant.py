"""Recover the exceptional lift on the open plane curve at five."""

import sympy as sp
from sympy.polys.agca.extensions import MonogenicFiniteExtension
from sympy.polys.rings import ring

from gct_collision_face import cleared_pure_equations, generic_lift, opposite_edge_product, plane_resultant


def specialize_tail(polynomial, target, values):
    """Keep the first variable and specialize the remaining ones in the residue field."""
    powers = [[value**j for j in range(polynomial.degree(i + 1) + 1)]
              for i, value in enumerate(values)]
    x, = target.gens
    return sum((target(int(c)) * x**indices[0] *
                target(sp.prod(table[j] for table, j in zip(powers, indices[1:])))
                for indices, c in polynomial.items()), target.zero)


def monic_gcd(left, right):
    """Use monic divisors for polynomial remainder over a finite extension."""
    while right:
        right = right * right.ring(right.ring.domain.one / right.LC)
        left, right = right, left.rem([right])
    return left


def exceptional_plane_lift():
    """Return (K,v,u,f,q) with f quadratic irreducible in K[p] and K of degree 44."""
    leading, constant = generic_lift()
    curve = plane_resultant()
    projection = leading.resultant(curve)
    v_symbol, = projection.ring.symbols
    factors = sp.Poly(projection.as_expr(), v_symbol, modulus=5).factor_list()[1]
    assert sorted((h.degree(), n) for h, n in factors) == [(1, 4), (1, 8), (5, 4), (9, 4), (44, 2)]
    assert {int(-h.TC()) % 5 for h, _ in factors if h.degree() == 1} == {0, 3}
    for factor, multiplicity in factors:
        if factor.degree() == 1 and factor.eval(3) == 0:
            assert multiplicity == 8
            continue
        field = MonogenicFiniteExtension(factor)
        v = field.generator
        algebra, x = ring("x", field)
        a, d, r = (specialize_tail(f, algebra, (v,)) for f in (leading, constant, curve))
        common = monic_gcd(monic_gcd(a, d), r)
        if factor.degree() != 44:
            assert common == (x**2 if factor.degree() == 1 else x)
            continue
        assert common.degree() == 1 and common.get((0,), field.zero)
        u = -common[(0,)]
        field_data = field, v, u, algebra

    field, v, u, algebra = field_data
    p, = algebra.gens
    first, second = (specialize_tail(f, algebra, (u, v)) for f in cleared_pure_equations())
    lift = monic_gcd(first, second)
    assert lift.degree() == 2
    discriminant = lift[(1,)]**2 - 4*lift[(0,)]
    assert discriminant**((5**44 - 1)//2) == -field.one
    U, V = algebra(u), algebra(v)
    q = (-(2*p**2 + 2*p*U + 2*p*V**2 + 3*p*V + 2*p + U**2)
         * algebra(field.one / (4*v + 3))).rem([lift])
    incident_discriminant = -4*p**3 - 27*q**2
    opposite_norm = opposite_edge_product(p, q, U, V)
    assert all(value.rem([lift]) for value in (q, incident_discriminant, opposite_norm))
    return field, v, u, lift, q


if __name__ == "__main__":
    from gct_collision_exceptional_rank import verify_exceptional_rank

    rank = verify_exceptional_rank(exceptional_plane_lift())
    print(f"The unique degree-88 lift of the exceptional plane point has Jacobian rank {rank}.")
