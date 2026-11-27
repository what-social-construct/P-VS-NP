"""Check the entire slope section through the degree-six excess point at five."""

import sympy as sp
from sympy.polys.agca.extensions import MonogenicFiniteExtension
from sympy.polys.rings import ring

from gct_collision_face import (
    generic_lift, opposite_edge_product, plane_resultant, residual_system, specialization_polars,
)
from gct_collision_fiber_net import polar_sextic_certificate
from gct_collision_kernel_reduction import evaluate
from gct_collision_line_divisor_slopes import adapted_slope_net
from gct_collision_residual_candidate import candidate_point, check_residual_candidate, check_simple_zero
from gct_common_line_witness import horner


def excess_slope_points():
    """Yield each closed quotient point above the excess slope, over the prime field."""
    original_field, original = candidate_point()
    curve = plane_resultant()
    u_symbol, v_symbol = curve.ring.symbols
    minimal = sp.Poly(v_symbol**6 - 2*v_symbol**5 + v_symbol**3 - v_symbol**2 + v_symbol - 2,
                      v_symbol, modulus=5)
    assert minimal.is_irreducible and not horner(minimal.all_coeffs(), original[3], original_field)

    # Eliminate v over F5[u]. A linear subresultant recovers v from u at
    # every root of the norm because its leading coefficient is a unit there.
    domain = sp.GF(5).poly_ring(u_symbol)
    slope = sp.Poly(minimal.as_expr(), v_symbol, domain=domain)
    section = sp.Poly(curve.as_expr(), v_symbol, domain=domain).rem(slope, auto=False)
    sequence = slope.subresultants(section)
    assert [row.degree() for row in sequence] == [6, 5, 4, 3, 2, 1, 0]
    norm = sp.Poly(sequence[-1].as_expr(), u_symbol, modulus=5)
    linear, constant = (sp.Poly(c, u_symbol, modulus=5) for c in sequence[-2].all_coeffs())
    assert norm.degree() == 72 and norm.gcd(linear).is_one
    factors = norm.factor_list()[1]
    assert sorted((f.degree(), n) for f, n in factors) == [(6, 1), (24, 1), (42, 1)]

    leading, offset = generic_lift()
    variables, equations = residual_system()
    pure_ring, *_ = ring(variables, sp.GF(5))
    pure = [pure_ring.from_expr(eq) for eq in equations]
    for factor, _ in factors:
        field = MonogenicFiniteExtension(factor)
        u = field.generator
        v = -field(constant.rem(factor).as_expr()) / field(linear.rem(factor).as_expr())
        assert not horner(minimal.all_coeffs(), v, field) and not evaluate(curve, (u, v))
        denominator = evaluate(leading, (u, v))
        assert denominator and u and v != field(3)
        p = -evaluate(offset, (u, v)) / denominator
        q = -(2*p**2 + 2*p*u + 2*p*v**2 + 3*p*v + 2*p + u**2) / (4*v+3)
        values = p, q, u, v
        assert q and -4*p**3-27*q**2 and opposite_edge_product(*values) and 3*u-2*p
        assert all(not evaluate(eq, values) for eq in pure)
        if field.rank == 6:
            # Identify this factor in the *original* certificate's field basis.
            assert not horner(factor.all_coeffs(), original[2], original_field)
            assert tuple(horner(a.rep.to_list(), original[2], original_field)
                         for a in values) == original
        yield field, values


def check_slope_closure():
    polars = specialization_polars()
    for field, values in excess_slope_points():
        if field.rank != 6:
            grams = adapted_slope_net(field, values, polars)
            polar_sextic_certificate(grams, field)
    print("The complete excess slope has closed-point degrees 6, 24 and 42. "
          "The original resultant is a unit on the degree-24 and degree-42 factors.")


if __name__ == "__main__":
    check_residual_candidate()
    check_simple_zero()
    check_slope_closure()
