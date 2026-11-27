"""Test geometric common-line incidence on the four translated sections d=a+r*m."""

from itertools import product

import sympy as sp
from sympy.polys.agca.extensions import MonogenicFiniteExtension
from sympy.polys.rings import ring

from gct_collision_direction import relabelings
from gct_collision_fiber_net import polar_sextic_certificate
from gct_collision_fiber_slice import pure_equations
from gct_collision_quadrics import quotient_forms_at
from gct_collision_slice import face_edges, slice_equations


def quotient_length(basis):
    """Count the standard monomials of a finite lexicographic quotient."""
    leading = [f.LM().exponents for f in basis.polys]
    bounds = [min(p[i] for p in leading if p[i] and sum(p) == p[i])
              for i in range(len(basis.gens))]
    return sum(not any(all(i <= j for i, j in zip(term, monomial)) for term in leading)
               for monomial in product(*(range(bound) for bound in bounds)))


def shape_points(basis):
    """Recover the residue fields and coordinate values from a triangular basis."""
    first, second, parameter = basis.gens
    if [g.LM().exponents for g in basis.polys[:2]] != [(1, 0, 0), (0, 1, 0)]:
        return None
    assert len(basis.polys) == 3
    coords = [sp.Poly(expr, parameter, modulus=5)
              for expr in (first-basis[0], second-basis[1])]
    eliminant = sp.Poly(basis[2], parameter, modulus=5)
    points = []
    for factor, _ in eliminant.factor_list()[1]:
        field = MonogenicFiniteExtension(factor)
        values = {symbol: field(poly.rem(factor).as_expr())
                  for symbol, poly in zip((first, second), coords)}
        values[parameter] = field.generator
        points.append((field, values))
    return points


def section_points(shift):
    """Decompose by tau, then by b on fibers where tau alone fails to separate points."""
    algebra, a, b, tau = ring("a,b,tau", sp.GF(5), "grevlex")
    shear = int(shift != 4)
    eqs = pure_equations(algebra, a, b, tau-shear*b, a+shift)
    a, b, tau = algebra.symbols
    basis = sp.groebner([q.as_expr() for q in eqs], a, b, tau,
                        modulus=5, order="grevlex").fglm("lex")
    assert quotient_length(basis) == 24
    eliminant = sp.Poly(basis[-1], tau, modulus=5)
    for factor, exponent in eliminant.factor_list()[1]:
        fiber = sp.groebner([*basis, factor.as_expr()], a, b, tau, modulus=5, order="lex")
        points = shape_points(fiber)
        if points is None:
            points = shape_points(sp.groebner(list(fiber), a, tau, b, modulus=5, order="lex"))
        assert points
        thick_fiber = fiber if exponent == 1 else sp.groebner(
            [*basis, factor.as_expr()**exponent], a, b, tau, modulus=5, order="lex")
        length = quotient_length(thick_fiber)
        # If the fiber contains several closed points they are all reduced.
        support = sum(field.rank for field, _ in points)
        assert length % support == 0 and (len(points) == 1 or length == support)
        for field, coords in points:
            av, bv = coords[a], coords[b]
            cv = coords[tau] - shear*bv
            yield field, face_edges(av, bv, cv, av+shift), length // support


def check_section(shift, expected):
    data = []
    for field, edges, multiplicity in section_points(shift):
        if shift == 3 and field.rank == 1 and edges[0] in (field(1), field(2)):
            # Swap vertices 2 and 3 at the four rational points with a=1 or 2.
            edges = tuple(edges[i] for i in (0, 2, 1, 4, 3, 5))
        point = next(image for image in relabelings(edges) if image[0])
        scale = field.one / point[0]
        forms = quotient_forms_at([scale*x for x in point], field)
        polar_sextic_certificate(forms, field)
        data.append((field.rank, multiplicity))
        print(f"d=a+{shift}m, residue degree {field.rank}, multiplicity {multiplicity}: "
              "verified polar sextic inverse.", flush=True)
    assert sorted(data) == expected


if __name__ == "__main__":
    # At m=0 the earlier base section has d nonzero; all translates require d=a.
    base = slice_equations()
    a, b, c, d = base[0].ring.symbols
    assert list(sp.groebner([q.as_expr().subs({a: 1, d: 1}) for q in base],
                            b, c, modulus=5)) == [1]
    check_section(1, [(2, 2), (2, 4), (6, 1), (6, 1)])
    check_section(2, [(3, 1)]*2 + [(4, 1)]*2 + [(5, 1)]*2)
    check_section(3, [(1, 1)]*6 + [(2, 1)]*2 + [(7, 1)]*2)
    check_section(4, [(2, 1), (22, 1)])
