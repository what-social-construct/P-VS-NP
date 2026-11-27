"""Test every geometric pure direction with interpolation slope in F25 outside F5."""

from itertools import product
from math import prod

import sympy as sp
from sympy.polys.agca.extensions import MonogenicFiniteExtension

from gct_collision_exceptional_rank import power_basis_rank
from gct_collision_face import (
    descended_forms, generic_lift, opposite_edge_product, plane_resultant,
    residual_system, specialization_polars,
)
from gct_collision_pencil_orbits import pencil_orbit_product
from gct_collision_quadrics import determinant_of_net


def linear_in_slope(polynomial, modulus):
    """Write a plane polynomial as a(u)+b(u)v modulo the quadratic in v."""
    _, v = polynomial.ring.gens
    u_symbol, _ = polynomial.ring.symbols
    reduced = polynomial.rem([modulus])
    return tuple(sp.Poly(reduced.coeff_wrt(v, i).as_expr(), u_symbol, modulus=5)
                 for i in (0, 1))


def quadratic_slope_points():
    """Yield (residue field, (p,q,u,v)) once per closed point over a quadratic slope."""
    curve = plane_resultant()
    leading, constant = generic_lift()
    _, V = curve.ring.gens
    symbols, equations = residual_system()
    pure = [sp.Poly(eq, *symbols, modulus=5) for eq in equations]
    for s, t in product(range(5), range(1, 5)):
        if (s*s - 4*t) % 5 not in (2, 3):
            continue
        modulus = V**2 + s*V + t
        a, b = linear_in_slope(curve, modulus)
        norm = a*a - s*a*b + t*b*b
        assert a.gcd(b).is_one and norm.degree() == 24 and norm.gcd(norm.diff()).is_one
        lift_rows = [linear_in_slope(f, modulus) for f in (leading, constant)]
        for factor, multiplicity in norm.factor_list()[1]:
            assert multiplicity == 1
            field = MonogenicFiniteExtension(factor)

            def at_u(poly):
                return field(poly.rem(factor).as_expr())

            u = field.generator
            v = -at_u(a) / at_u(b)
            assert v*v + s*v + t == field.zero and v**5 != v
            denominator, numerator = (at_u(c) + at_u(d)*v for c, d in lift_rows)
            assert u and denominator
            p = -numerator / denominator
            q = -(2*p**2 + 2*p*u + 2*p*v**2 + 3*p*v + 2*p + u**2) / (4*v+3)
            values = p, q, u, v
            assert q and -4*p**3 - 27*q**2 and opposite_edge_product(*values)
            for equation in pure:
                assert not sum((field(int(c)) * prod((x**i for x, i in zip(values, powers)),
                                                      start=field.one)
                                for powers, c in equation.terms()), field.zero)
            yield field, values


def verify_quadratic_slopes():
    polars = specialization_polars()
    pencil_degrees, rank_degrees = [], []
    for field, values in quadratic_slope_points():
        if not pencil_orbit_product(*values):
            pencil_degrees.append(field.rank)
            continue
        forms = descended_forms(polars, values, field)
        assert power_basis_rank(determinant_of_net(forms, field), 9) == 54
        rank_degrees.append(field.rank)
    assert pencil_degrees == [2, 2, 2]
    assert len(rank_degrees) == 27 and sum(rank_degrees) == 234
    print("Quadratic slopes: 30 closed points, 240 geometric quotient points.")
    print("Three degree-two points on the excluded pencils; 27 net ranks equal 54.")


if __name__ == "__main__":
    verify_quadratic_slopes()
