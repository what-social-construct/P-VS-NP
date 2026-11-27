"""Exclude the six coordinate edge faces of the [0:1] quadratic collision fiber."""

from itertools import product

import sympy as sp
from sympy.polys.agca.extensions import MonogenicFiniteExtension
from sympy.polys.matrices import DomainMatrix
from sympy.polys.matrices.exceptions import DMNonInvertibleMatrixError
from sympy.polys.rings import ring

from gct_collision_kernel_reduction import determinant
from gct_collision_quadrics import quotient_forms_at
from gct_collision_slice import face_edges, kernel_from_edges
from gct_permanent_plucker import pencil_coefficients


def face_points(incident):
    """Use a separating coordinate t on the e12=0 or e13=0 pure section."""
    algebra, a, u, t = ring("a,u,tau", sp.GF(5), "grevlex")
    if incident:
        b, c, d = algebra.zero, u, t
        factors_expected = [(8, 1), (12, 1)]
    else:
        b, c, d = u, algebra.zero, t - 2*u
        factors_expected = [(1, 2), (1, 3), (2, 2), (2, 3), (4, 1)]
    kernel = kernel_from_edges(face_edges(a, b, c, d))
    pure = pencil_coefficients(algebra, (kernel,))
    assert set(pure) == {(i, 0, 0) for i in (2, 3, 4)}
    basis = sp.groebner([f.as_expr() for f in pure.values()], *algebra.symbols,
                        modulus=5, order="grevlex").fglm("lex")
    aa, uu, tt = algebra.symbols
    degree = sum(n*m for n, m in factors_expected)
    assert [g.LM().exponents for g in basis.polys] == [(1, 0, 0), (0, 1, 0), (0, 0, degree)]
    a_poly, u_poly, eliminant = (sp.Poly(f, tt, modulus=5) for f in
                                 (aa-basis[0], uu-basis[1], basis[2]))
    factors = eliminant.factor_list()[1]
    assert sorted((f.degree(), m) for f, m in factors) == factors_expected
    for factor, _ in factors:
        field = MonogenicFiniteExtension(factor)
        av, uv = (field(g.rem(factor).as_expr()) for g in (a_poly, u_poly))
        bv, cv, dv = ((field.zero, uv, field.generator) if incident
                      else (uv, field.zero, field.generator - 2*uv))
        yield field, face_edges(av, bv, cv, dv)


def polar_sextic_inverse(forms, field):
    """Return a checked inverse, or None if this chart and sextic give no exclusion."""
    algebra, x, y, z = ring("x,y,z", field, "grevlex")
    point = (x, y, z, algebra.one, algebra.zero)
    grams = [[[algebra(c) for c in row] for row in gram] for gram in forms]

    def covector(gram, vector):
        return [sum((c*v for c, v in zip(row, vector)), algebra.zero) for row in gram]

    def dot(left, right):
        return sum((a*b for a, b in zip(left, right)), algebra.zero)

    polars = [covector(gram, point) for gram in grams]
    quadrics = [dot(row, point) for row in polars]
    powers = sorted((p for p in product(range(5), repeat=3) if sum(p) <= 4),
                    key=algebra.order, reverse=True)
    monomials = {p: algebra.from_dict({p: field.one}) for p in powers}

    def coefficients(polynomials, columns):
        rows = [[f.get(p, field.zero) for p in columns] for f in polynomials]
        return DomainMatrix(rows, (len(rows), len(columns)), field)

    multiples = [m*q for q in quadrics for p, m in monomials.items() if sum(p) <= 2]
    reduced, pivots = coefficients(multiples, powers).rref()
    free = [p for j, p in enumerate(powers) if j not in pivots]
    # Every quartic reduces to terms of degree <= 3. Homogenizing these
    # identities excludes all points of the hyperplane section at infinity.
    if len(free) != 8 or any(sum(p) > 3 for p in free):
        return None
    rules = [algebra.from_dict({p: c for p, c in zip(powers, row) if c})
             for row in reduced.to_list()[:len(pivots)]]

    # The kernel of the polar rows contains any common line through point.
    # At rank three it equals that line; at smaller rank all cofactors vanish.
    # Intersect the kernel with Y3=0 using signed 3x3 cofactors.
    columns = list(zip(*polars))
    slots = (0, 1, 2, 4)
    tangent = [algebra.zero] * 5
    for i, j in enumerate(slots):
        tangent[j] = (-1)**i * determinant([columns[k] for k in slots if k != j])
    sextic = dot(covector(grams[0], tangent), tangent).rem(rules)
    products = [(monomials[p]*sextic).rem(rules) for p in free]
    if any(not set(f).issubset(free) for f in products):
        raise ArithmeticError("a reduced sextic multiple is outside the quartic basis")
    # Rows are products of the free monomials with the reduced sextic.
    # The row of the inverse indexed by 1 gives an explicit unit certificate.
    try:
        inverse_matrix = coefficients(products, free).inv()
    except DMNonInvertibleMatrixError:
        return None
    inverse_row = inverse_matrix.to_list()[free.index((0, 0, 0))]
    inverse = algebra.from_dict({p: c for p, c in zip(free, inverse_row) if c})
    if (inverse*sextic).rem(rules) != algebra.one:
        raise ArithmeticError("the proposed polar sextic inverse fails the unit identity")
    return inverse


def polar_sextic_certificate(forms, field):
    """Require a geometric common-line exclusion for this net and chart."""
    inverse = polar_sextic_inverse(forms, field)
    if inverse is None:
        raise AssertionError("this polar sextic chart gives no unit certificate")
    return inverse


if __name__ == "__main__":
    for incident, edge in ((True, "12"), (False, "13")):
        for field, point in face_points(incident):
            if not incident:
                # The vertex order (0,2,3,1) gives a single working frame on this face.
                point = tuple(point[k] for k in (1, 2, 0, 5, 3, 4))
            scale = field.one / point[0]
            forms = quotient_forms_at([scale*x for x in point], field)
            polar_sextic_certificate(forms, field)
            print(f"e{edge}=0, residue degree {field.rank}: polar sextic gives a unit.", flush=True)
