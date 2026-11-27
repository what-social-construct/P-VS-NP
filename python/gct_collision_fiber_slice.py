"""Test two transverse hyperplane sections of the l=0 pure curve at five."""

from itertools import combinations, product

import numpy as np
import sympy as sp
from sympy.polys.agca.extensions import MonogenicFiniteExtension
from sympy.polys.rings import ring

from gct_collision_direction import relabelings
from gct_collision_eliminant import restricted_sextic_rank
from gct_collision_kernel_reduction import determinant
from gct_collision_quadrics import (
    determinant_of_net, homogeneous_powers, jacobian_multiples, jacobian_rank, quotient_forms_at,
)
from gct_collision_slice import face_edges, kernel_from_edges, slice_equations
from gct_permanent_extensions import reduced_rows
from gct_permanent_plucker import pencil_coefficients


def pure_equations(algebra, a, b, c, d):
    """Restrict the level permanent to l=0, m=1."""
    kernel = kernel_from_edges(face_edges(a, b, c, d))
    equations = pencil_coefficients(algebra, (kernel,))
    assert set(equations) == {(i, 0, 0) for i in (2, 3, 4)}
    return [equations[i, 0, 0] for i in (2, 3, 4)]


def shape_basis(slope, intercept):
    """Set m=1, d=slope*a+intercept and recover a,b as polynomials in c."""
    algebra, a, b, c = ring("a,b,c", sp.GF(5), "grevlex")
    equations = pure_equations(algebra, a, b, c, slope*a + intercept)
    symbols = algebra.symbols
    basis = sp.groebner([f.as_expr() for f in equations], *symbols,
                        order="grevlex", modulus=5).fglm("lex")
    assert [g.LM().exponents for g in basis.polys] == [(1, 0, 0), (0, 1, 0), (0, 0, 24)]
    av, bv, cv = symbols
    return tuple(sp.Poly(expr, cv, modulus=5) for expr in
                 (av - basis[0], bv - basis[1], basis[2]))


def net_at_factor(a_poly, b_poly, factor, slope, intercept):
    """A single residue field represents every geometric conjugate of this point."""
    field = MonogenicFiniteExtension(factor)
    c = field.generator
    a, b = (field(poly.rem(factor).as_expr()) for poly in (a_poly, b_poly))
    d = slope*a + intercept
    raw = face_edges(a, b, c, d)
    edges = next(image for image in relabelings(raw) if image[0])
    scale = field.one / edges[0]
    return determinant_of_net(quotient_forms_at([scale*x for x in edges], field), field)


def check_section_projectors(eliminant, factors):
    """Check the field-factor and diagonal idempotents for one reduced section."""
    projectors = []
    for factor, multiplicity in factors:
        assert multiplicity == 1
        complement = eliminant.exquo(factor)
        projectors.append((complement * complement.invert(factor)).rem(eliminant))
    assert sum(projectors).rem(eliminant).is_one
    for i, left in enumerate(projectors):
        for j, right in enumerate(projectors):
            expected = left if i == j else eliminant.zero
            assert (left*right).rem(eliminant) == expected

    algebra, x, y = ring("x,y", sp.GF(5), "lex")

    def at(poly, variable):
        return sum((int(c)*variable**n for (n,), c in poly.terms()), algebra.zero)

    hx, hy = at(eliminant, x), at(eliminant, y)
    relations = [hx, hy]
    difference = (hx-hy).exquo(x-y)
    inverse_derivative = eliminant.diff().invert(eliminant)
    diagonal = (difference * at(inverse_derivative, x)).rem(relations)
    assert ((x-y)*diagonal).rem(relations) == 0
    assert (diagonal**2-diagonal).rem(relations) == 0
    restriction = sum((c*x**(i+j) for (i,j), c in diagonal.items()), algebra.zero)
    assert restriction.rem([hx]) == 1


def check_section(slope, intercept, degrees):
    a_poly, b_poly, eliminant = shape_basis(slope, intercept)
    factors = eliminant.factor_list()[1]
    assert [(f.degree(), n) for f, n in factors] == [(e, 1) for e in degrees]
    check_section_projectors(eliminant, factors)
    for factor, _ in factors:
        quintic = net_at_factor(a_poly, b_poly, factor, slope, intercept)
        rank = jacobian_rank(quintic, 9)
        print(f"d={slope}a+{intercept}, residue degree {factor.degree()}: rank {rank}", flush=True)
        assert rank == 54


def check_singular_points():
    """Identify the singular scheme on m=1, with two geometric points of length five."""
    algebra, *variables = ring("a,b,c,d", sp.GF(5), "grevlex")
    equations = pure_equations(algebra, *variables)
    columns = [[f.diff(x) for f in equations] for x in variables]
    equations += [determinant(selected) for selected in combinations(columns, 3)]
    a, b, c, d = algebra.symbols
    basis = sp.groebner([f.as_expr() for f in equations], a, b, c, d, modulus=5, order="grevlex")
    leading = [f.LM(order="grevlex").exponents for f in basis.polys]
    bounds = (2, 2, 2, 3)
    assert all(tuple(k if i == j else 0 for j in range(4)) in leading for i, k in enumerate(bounds))
    standard = [p for p in product(*(range(k) for k in bounds))
                if not any(all(i <= j for i, j in zip(term, p)) for term in leading)]
    assert len(standard) == 10
    lex = basis.fglm("lex")
    assert sp.Poly(lex[-1] - (d-1)**5, d, modulus=5).is_zero
    support = sp.groebner([g.subs(d, 1) for g in lex], a, b, c, modulus=5, order="lex")
    assert list(support) == [a, b**2+b+1, c]
    assert sp.Poly(b**2+b+1, b, modulus=5).is_irreducible


def check_resultant_specialization():
    a, b, h = shape_basis(0, 4)
    assert (int(a.eval(0)) % 5, int(b.eval(0)) % 5, int(h.eval(0)) % 5) == (1, 4, 0)
    point = (1, 2, 2, 4, 0, 4)
    image = (1, 0, 4, 2, 2, 4)
    assert image in relabelings(point) and restricted_sextic_rank(image) == 84


def check_quotient_minor():
    """Choose a homogeneous 53-minor nonzero at the specified rational point."""
    field = sp.GF(5)
    point = [field(x) for x in (1, 2, 2, 4, 0, 4)]
    # The squared dual determinant of the quotient bundle is O_C(10).
    quintic = determinant_of_net(quotient_forms_at(point, field), field)

    def weight(exponents):
        return exponents[1] + 2*exponents[2]

    columns = sorted(homogeneous_powers(9), key=weight)
    weighted_rows = [(10 + (index or 0) - weight(shift), list(map(int, row)))
                     for index, shift, row in jacobian_multiples(quintic, 9, columns)]
    weighted_rows.sort(key=lambda item: item[0])
    matrix = np.array([row for _, row in weighted_rows])
    rows = reduced_rows(matrix.T)[1][:53]
    cols = reduced_rows(matrix[rows])[1][:53]
    assert len(reduced_rows(matrix[rows][:, cols])[1]) == 53
    degree = sum(weighted_rows[i][0] for i in rows) + sum(weight(columns[j]) for j in cols)
    assert degree == 755
    print(f"Nonzero quotient minor of degree {degree}; divisor length {24*degree}.")


if __name__ == "__main__":
    # The previous projective base-section calculation gives d != 0 at infinity.
    # For d=a, set d=a=1 there and check that no point satisfies the equations.
    base = slice_equations()
    a, b, c, d = base[0].ring.symbols
    infinity = sp.groebner([f.as_expr().subs({a: 1, d: 1}) for f in base], b, c, modulus=5)
    assert list(infinity) == [1]
    check_section(0, 4, [1, 1, 2, 20])
    check_section(1, 0, [6, 18])
    check_singular_points()
    check_resultant_specialization()
    check_quotient_minor()
