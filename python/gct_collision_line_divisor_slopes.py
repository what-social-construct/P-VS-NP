"""Exclude the candidate divisor itself over every eligible F25-valued slope."""

import sympy as sp
from sympy.polys.agca.extensions import MonogenicFiniteExtension

from gct_collision_face import (
    descended_net, generic_lift, plane_resultant, prime_slope_points, specialization_polars,
)
from gct_collision_fiber_net import polar_sextic_certificate
from gct_collision_line_divisor import adapted_grams
from gct_collision_ordering_fibers import ordering_factors
from gct_collision_polar_extension import polar_kernel_line
from gct_collision_quadratic_slopes import quadratic_slope_points
from gct_common_line_witness import horner


def adapted_slope_net(field, values, polars):
    p, _, u, _ = values
    # The point enumerators check the chart conditions except for Y != 0.
    assert 3*u - 2*p
    inclusion, forms = descended_net(polars, values, field)
    # The incident roots sum to zero and their squares sum to -2p.
    # Thus H = 3i0-2p i2 and D = 3d0-2p d2 in the gauge coordinates.
    incident = [3*row[0] - 2*p*row[1] for row in inclusion]
    diagonal = [3*row[5] - 2*p*row[7] for row in inclusion]
    return adapted_grams(forms, diagonal, incident, field)


def verify_slope_units(points, polars):
    degrees = []
    for field, values in points:
        adapted = adapted_slope_net(field, values, polars)
        # This excludes infinity in H=0 and verifies an inverse of the
        # invariant sextic on the resulting length-eight D=1 section.
        polar_sextic_certificate(adapted, field)
        degrees.append(field.rank)
    return len(degrees), sum(degrees)


def check_line_divisor_slopes():
    polars = specialization_polars()
    prime = prime_slope_points(plane_resultant(), *generic_lift())
    prime_counts = verify_slope_units(prime, polars)
    quadratic_counts = verify_slope_units(quadratic_slope_points(), polars)
    assert prime_counts == (10, 41) and quadratic_counts == (30, 240)
    print("The common-line resultant is a unit at all 40 eligible closed points "
          "with slope in F25 (281 geometric quotient points).")


def check_transverse_slope_example():
    """Compute the eight-point section and the ordering factors at a fixed-face point."""
    points = prime_slope_points(plane_resultant(), *generic_lift())
    field, values = next((k, values) for k, values in points
                         if k.rank == 2 and values[-1] == k.one)
    p, q, u, _ = values
    t = field.modulus.gens[0]
    assert field.modulus.as_expr() == t**2 - 2*t - 1
    assert p == -2*u-2 and q == u-2
    assert ordering_factors(field, p, q) == (2, 2, 2)
    grams = adapted_slope_net(field, values, specialization_polars())
    polar_sextic_certificate(grams, field)

    # On D=1, H=0 use w=z+u to separate both F5-conjugates of the section.
    x, y, w = sp.symbols("x y w")
    point = (x, y, w-t, 1, 0)
    quadrics = [sum(c.as_expr()*point[i]*point[j]
                    for i, row in enumerate(gram) for j, c in enumerate(row)) for gram in grams]
    basis = sp.groebner([*quadrics, field.modulus.as_expr()], x, y, t, w,
                        modulus=5, order="grevlex").fglm("lex")
    assert [g.LM().exponents for g in basis.polys] == [
        (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 16)]
    factors = sp.Poly(basis[-1], w, modulus=5).factor_list()[1]
    assert sorted((f.degree(), m) for f, m in factors) == [(2, 1), (2, 1), (6, 1), (6, 1)]
    coordinates = [sp.Poly(a-g, w, modulus=5) for a, g in zip((x, y, t), basis)]
    for factor, _ in factors:
        residue = MonogenicFiniteExtension(factor)
        xv, yv, uv = (residue(f.rem(factor).as_expr()) for f in coordinates)
        assert uv**2 - 2*uv - 1 == residue.zero
        net = [[[horner(c.rep.to_list(), uv, residue) for c in row] for row in gram]
               for gram in grams]
        section_point = (xv, yv, residue.generator-uv, residue.one, residue.zero)
        assert polar_kernel_line(net, section_point, residue) is None
    print("At v=1, u²−2u−1=0 over F25, the eight-point section has residue degrees "
          "1,1,3,3 and the ordering algebra has degrees 2,2,2. There is no geometric common line.")


if __name__ == "__main__":
    check_line_divisor_slopes()
    check_transverse_slope_example()
