"""Reduce a zero vertex-sum face by its S3 symmetry in characteristic five."""

from math import prod

import sympy as sp
from sympy.polys.agca.extensions import MonogenicFiniteExtension
from sympy.polys.matrices import DomainMatrix
from sympy.polys.rings import ring

from gct_collision_quadrics import determinant_of_net, jacobian_rank, quotient_forms_at
from gct_collision_slice import kernel_from_edges
from gct_permanent_plucker import OFF_DIAGONAL, pencil_coefficients


def pure_equations(edges):
    algebra = edges[0].ring
    kernel = kernel_from_edges(edges)
    coefficients = pencil_coefficients(algebra, (kernel,))
    return [coefficients[i, 0, 0].as_expr() for i in (2, 3, 4)]


def verify_repeated_edges():
    """Exhaust x0=x1 up to scaling, where (x0,x1,x3)=(b02,b12,b23) sums to zero."""
    # If both equal edges vanish, all three vanish. The stabilizer permutes the
    # opposite triangle edges, so we may set its first nonzero edge to one.
    algebra, u, v = ring("u,v", sp.GF(5))
    zero, one = algebra.zero, algebra.one
    equations = pure_equations((one, zero, v, zero, u, zero))
    assert list(sp.groebner(equations, *algebra.symbols, modulus=5)) == [1]

    # Otherwise scale x0=x1 to one. Project onto w, the opposite edge 01.
    algebra, u, w, v = ring("u,w,v", sp.GF(5))
    one = algebra.one
    equations = pure_equations((w, one, v, one, u, -2*one))
    U, W, V = algebra.symbols
    base = sp.groebner(equations, U, V, W, modulus=5, order="grevlex").fglm("lex")
    projection = sp.Poly(base[-1], W, modulus=5)
    factors = projection.factor_list()[1]
    assert sorted((f.degree(), n) for f, n in factors) == [(1, 1), (1, 1), (9, 1)]

    supports = []
    for g, _ in factors:
        # On each factor, v separates the geometric points, including both
        # distinct points in the fiber over w=0 with local length two.
        basis = sp.groebner([*equations, g.as_expr()], U, W, V, modulus=5,
                            order="grevlex").fglm("lex")
        assert len(basis.polys) == 3
        assert [f.LM().exponents[:2] for f in basis.polys] == [(1, 0), (0, 1), (0, 0)]
        upoly, wpoly, eliminant = (sp.Poly(f, V, modulus=5) for f in
                                  (U - basis[0], W - basis[1], basis[2]))
        for h, multiplicity in eliminant.factor_list()[1]:
            field = MonogenicFiniteExtension(h)
            u0, w0 = (field(f.rem(h).as_expr()) for f in (upoly, wpoly))
            # Swap vertices 1 and 2 to put a unit edge in slot 01.
            edges = (field.one, w0, field.generator, field.one, field(-2), u0)
            quintic = determinant_of_net(quotient_forms_at(edges, field), field)
            rank = jacobian_rank(quintic, 9)
            assert rank == 54
            supports.append((h.degree(), multiplicity))
    assert sorted(supports) == [(1, 1), (1, 1), (1, 2), (1, 2), (9, 1), (9, 1)]
    return sum(degree for degree, _ in supports)


def interpolation_equations(quadratic):
    """Descend the pure equations along ordered roots of X³+pX−q."""
    algebra, y, x, p, q, u, v = ring("y,x,p,q,u,v", sp.GF(5), order="lex")
    z = -x-y
    # These monic relations give the ordered splitting algebra. Their leading
    # monomials y² and x³ are relatively prime in the indicated order.
    relations = (y*y+x*y+x*x+p, x**3+p*x-q)

    def opposite(root):
        return u + v*root + quadratic*root**2

    edges = (opposite(z), x, opposite(y), y, opposite(x), z)
    reduced = [algebra.from_expr(f).rem(relations).as_expr() for f in pure_equations(edges)]
    assert all(f.free_symbols <= set(algebra.symbols[2:]) for f in reduced)
    return algebra.symbols[2:], reduced


def check_affine_net(field, incident, slope, offset):
    x, y, z = incident
    # Swap vertices 1 and 2 to normalize at the first incident edge.
    edges = (x, offset+slope*z, offset+slope*y, y, z, offset+slope*x)
    quintic = determinant_of_net(quotient_forms_at([e/x for e in edges], field), field)
    assert jacobian_rank(quintic, 9) == 54


def verify_affine_interpolation():
    """Exclude every distinct-root direction with opposite edges u+v*x_i."""
    (p, q, u, v), equations = interpolation_equations(0)
    zero_intercept = [sp.Poly(f.subs(u, 0), p, q, v, modulus=5) for f in equations]
    expected = (p*(2*v**2+3*v+2), q*v**2*(v+2), 4*p**2*v**2)
    assert all(f == sp.Poly(e, p, q, v, modulus=5) for f, e in zip(zero_intercept, expected))
    # The last and first equations force p=0. Distinct roots then force q!=0
    # and v in {0,3}. Scale the three cubic roots to (1,omega,omega²).
    omega = sp.Symbol("omega")
    field = MonogenicFiniteExtension(sp.Poly(omega**2+omega+1, omega, modulus=5))
    roots = (field.one, field.generator, field.generator**2)
    for slope in (0, 3):
        check_affine_net(field, roots, field(slope), field.zero)

    # For nonzero intercept, scale it to 1. Every conjugate slope and every
    # ordering of the three roots give the same rank by Frobenius and S3.
    basis = sp.groebner([f.subs(u, 1) for f in equations], p, q, v, modulus=5, order="lex")
    assert [f.LM().exponents for f in basis.polys] == [(1, 0, 0), (0, 1, 0), (0, 0, 7)]
    p_value, q_value = p-basis[0], q-basis[1]
    slope_poly = sp.Poly(basis[2], v, modulus=5)
    assert slope_poly.is_irreducible
    a = sp.Symbol("a")
    cubic = a**3+p_value*a-q_value
    ordered = sp.groebner([slope_poly.as_expr(), cubic], v, a, modulus=5,
                          order="grevlex").fglm("lex")
    assert [f.LM().exponents for f in ordered.polys] == [(1, 0), (0, 21)]
    factors = sp.Poly(ordered[1], a, modulus=5).factor_list()[1]
    assert [(f.degree(), n) for f, n in factors] == [(7, 1), (14, 1)]
    extension = factors[1][0]
    field = MonogenicFiniteExtension(extension)
    x = field.generator
    y = x**(5**7)
    z = -x-y
    slope = field(sp.Poly(v-ordered[0], a, modulus=5).rem(extension).as_expr())
    assert len({x, y, z}) == 3 and slope**(5**7) == slope
    check_affine_net(field, (x, y, z), slope, field.one)


def residual_system():
    """Return the four-variable quotient on the surviving open stratum.

    The incident triple must have discriminant -4p³-27q² nonzero. Scaling
    all edges by the nonzero quadratic interpolation coefficient puts it at 1.
    """
    symbols, equations = interpolation_equations(1)
    p, q, u, v = symbols
    expected = (4*v+3)*q + 2*p**2 + 2*p*u + 2*p*v**2 + 3*p*v + 2*p + u**2
    assert sp.Poly(equations[0]-expected, *symbols, modulus=5).is_zero
    return symbols, equations


def ordered_kernel(roots, u, v):
    """Recover B after ordering the incident cubic roots at vertices 0, 1, 3."""
    x, y, z = roots
    opposite = [u+v*r+r**2 for r in roots]
    return kernel_from_edges((opposite[2], x, opposite[1], y, opposite[0], z))


def interpolated_tangent(roots, slots):
    """Evaluate the eight gauge coordinates at the ordered incident edges."""
    i0, i2, o0, o1, o2, d0, d1, d2 = slots
    incident = [i0+i2*r**2 for r in roots]
    opposite = [o0+o1*r+o2*r**2 for r in roots]
    diagonal = [d0+d1*r+d2*r**2 for r in roots]
    tangent = dict(zip(OFF_DIAGONAL, (opposite[2], incident[0], opposite[1],
                                      incident[1], opposite[0], incident[2])))
    tangent.update({(vertex, vertex): entry for vertex, entry in zip((0, 1, 3), diagonal)})
    tangent[2, 2] = -sum(value*(1 if i == j else 2) for (i, j), value in tangent.items())
    return tangent


def residual_polar_system():
    """Descend the three linear polars and three quadratic forms on eight gauge slots.

    Ordering the roots splits the cubic algebra. Evaluation of 1,X,X² at
    the three distinct roots is an isomorphism for each coordinate triple.
    The kernel's incident polynomial is X, so its coefficient is the gauge.
    """
    algebra, y, x, p, q, u, v, i0, i2, o0, o1, o2, d0, d1, d2 = ring(
        "y,x,p,q,u,v,i0,i2,o0,o1,o2,d0,d1,d2", sp.GF(5), order="lex")
    z = -x-y
    relations = (y**2+x*y+x**2+p, x**3+p*x-q)
    roots = (x, y, z)
    kernel = ordered_kernel(roots, u, v)
    tangent = interpolated_tangent(roots, (i0, i2, o0, o1, o2, d0, d1, d2))
    coefficients = pencil_coefficients(algebra, (kernel, tangent))
    polars = {(i, j): f.rem(relations) for (i, j, _), f in coefficients.items() if j in (1, 2)}
    assert set(polars) == {(1, 1), (2, 1), (3, 1), (0, 2), (1, 2), (2, 2)}
    for (i, j), f in polars.items():
        assert all(a[0] == a[1] == 0 and sum(a[6:]) == j for a in f)
    return {powers: f.as_expr() for powers, f in polars.items()}


def descended_net(polars, values, field):
    """Return the 5 by 8 inclusion of the polar kernel and its three Gram matrices."""
    linear = []
    quadrics = []
    base_monomials = {}
    for (_, j), polynomial in sorted(polars.items()):
        rows = [[field.zero for _ in range(8)] for _ in range(1 if j == 1 else 8)]
        for powers, coeff in polynomial.terms():
            slots = [k for k, exponent in enumerate(powers[4:]) for _ in range(exponent)]
            base = powers[:4]
            if base not in base_monomials:
                base_monomials[base] = prod((x**n for x, n in zip(values, base) if n), start=field.one)
            entry = field(int(coeff))*base_monomials[base]
            if j == 1:
                rows[0][slots[0]] += entry
            else:
                r, c = slots
                if r != c:
                    entry *= 3  # 1/2 in F5
                    rows[c][r] += entry
                rows[r][c] += entry
        if j == 1:
            linear.extend(rows)
        else:
            quadrics.append(DomainMatrix(rows, (8, 8), field))
    echelon, pivots = DomainMatrix(linear, (3, 8), field).rref()
    kernel = echelon.nullspace_from_rref(pivots)
    assert kernel.shape == (5, 8)
    return kernel.to_list(), [(kernel * form * kernel.transpose()).to_list() for form in quadrics]


def descended_forms(polars, values, field):
    """Restrict the three descended quadrics to the five-dimensional polar kernel."""
    return descended_net(polars, values, field)[1]


def descended_rank(polars, values, field):
    forms = descended_forms(polars, values, field)
    return jacobian_rank(determinant_of_net(forms, field), 9)


def specialization_polars():
    symbols = sp.symbols("p q u v i0 i2 o0 o1 o2 d0 d1 d2")
    return {powers: sp.Poly(f, *symbols, modulus=5) for powers, f in residual_polar_system().items()}


def opposite_edge_product(p, q, u, v):
    """Product of T²+vT+u over the three roots of T³+pT−q."""
    return p**2*u+p*q*v-2*p*u**2+p*u*v**2+q**2-3*q*u*v+q*v**3+u**3


def verify_exceptional_gauges():
    """Check u=0 and v=3 on the all-edges-nonzero residual over the closure."""
    symbols, equations = residual_system()
    p, q, u, v = symbols
    polars = specialization_polars()
    inverse = sp.Symbol("inverse")
    for fixed, value, order, degrees in [(u, 0, (inverse, q, p, v), [5, 9]),
                                         (v, 3, (inverse, u, p, q), [2, 2, 7])]:
        # q is the product of the three incident edges.
        generators = [f.subs(fixed, value) for f in equations] + [inverse*q-1]
        basis = sp.groebner(generators, *order, modulus=5, order="grevlex").fglm("lex")
        assert len(basis.polys) == 4
        assert [f.LM().exponents[:3] for f in basis.polys] == [
            (1, 0, 0), (0, 1, 0), (0, 0, 1), (0, 0, 0)]
        parameter = order[-1]
        factors = sp.Poly(basis[-1], parameter, modulus=5).factor_list()[1]
        assert [(h.degree(), n) for h, n in factors] == [(d, 1) for d in degrees]
        zero_norm = 0
        for h, _ in factors:
            field = MonogenicFiniteExtension(h)
            vals = {x: field(sp.Poly(x-f, parameter, modulus=5).rem(h).as_expr())
                    for x, f in zip(order[:-1], basis[:-1])}
            vals.update({parameter: field.generator, fixed: field(value)})
            P, Q, U, V = (vals[x] for x in symbols)
            assert -4*P**3-27*Q**2 != field.zero
            if opposite_edge_product(P, Q, U, V):
                assert descended_rank(polars, (P, Q, U, V), field) == 54
            else:
                zero_norm += h.degree()
        assert zero_norm == (2 if fixed == v else 0)


def cleared_pure_equations():
    """Eliminate q on v!=3 and keep the remaining two equations in p."""
    (p, q, u, v), equations = residual_system()
    algebra, P, U, V = ring("P,U,V", sp.GF(5))
    denominator = 4*V+3
    numerator = -(2*P**2+2*P*U+2*P*V**2+3*P*V+2*P+U**2)
    cleared = []
    for f in equations[1:]:
        polynomial = sp.Poly(f, p, q, u, v, modulus=5)
        d = polynomial.degree(q)
        cleared.append(sum(algebra(int(c))*P**i*numerator**j*U**k*V**l*denominator**(d-j)
                           for (i, j, k, l), c in polynomial.terms()))
    assert cleared[0].degree(0) == 4
    assert cleared[0].coeff_wrt(P, 4) == algebra(4)
    return cleared


def plane_resultant():
    """Project the remaining pure equations. Common-line eligibility requires further tests."""
    first, second = cleared_pure_equations()
    resultant = first.resultant(second)
    projection_u, projection_v = resultant.ring.gens
    primitive = resultant.exquo(projection_u**4*(projection_v-3)**8)
    assert (primitive.degree(0), primitive.degree(1)) == (12, 24)
    assert primitive.coeff_wrt(projection_u, 12) == primitive.ring(-1)
    assert primitive % projection_u and primitive % (projection_v-3)
    return primitive


def generic_lift():
    """Return L,C with p=-C/L on the dense open of the plane curve where L!=0."""
    first, second = cleared_pure_equations()
    sequence = first.subresultants(second)
    assert [f.degree(0) for f in sequence] == [5, 4, 3, 2, 1, 0]
    P, U, V = first.ring.gens
    linear = sequence[-2]
    plane, _, v = ring("U,V", sp.GF(5))
    coefficients = [plane.from_expr(linear.coeff_wrt(P, i).as_expr()) for i in (1, 0)]
    content = coefficients[0].gcd(coefficients[1])
    assert content == (v-3)**5
    leading, constant = (f.exquo(content) for f in coefficients)
    assert (leading.degree(0), leading.degree(1)) == (9, 19)
    assert (constant.degree(0), constant.degree(1)) == (10, 17)
    # Since the irreducible plane curve has U-degree 12, its generic point
    # cannot annihilate the nonzero U-degree-nine leading coefficient.
    return leading, constant


def verify_geometric_irreducibility(curve):
    """Certify irreducibility by specializations and a smooth F5 point."""
    U, V = curve.ring.symbols
    expression = curve.as_expr()
    at_two = sp.Poly(expression.subs(V, 2), U, modulus=5).factor_list()[1]
    assert [(f.degree(), n) for f, n in at_two] == [(2, 1), (10, 1)]
    # Any proper factorization has a degree-two factor in U, since the
    # leading U coefficient is a unit. Its norm at a quadratic V would
    # divide the specialized norm and have U degree four.
    algebra, v, _ = ring("V,U", sp.GF(5))
    quadratic = v**2+v+1
    assert sp.Poly(quadratic.as_expr(), V, modulus=5).is_irreducible
    norm = quadratic.resultant(algebra.from_expr(expression))
    factors = sp.Poly(norm.as_expr(), U, modulus=5).factor_list()[1]
    assert [(f.degree(), n) for f, n in factors] == [(10, 1), (14, 1)]
    # A smooth rational point lies on a unique geometric component. That
    # component is Frobenius-stable, so irreducibility over F5 suffices.
    a, b = curve.ring.gens
    assert [int(f(4, 4)) % 5 for f in (curve, curve.diff(a), curve.diff(b))] == [0, 4, 2]


def verify_prime_slopes(curve, leading, constant):
    """Test every geometric plane point with prime-field interpolation slope."""
    polars = specialization_polars()
    u_symbol, v_symbol = curve.ring.symbols
    rank_checks = []
    # The separate v=3 calculation precedes division by 4v+3.
    for slope in (0, 1, 2, 4):
        def specialize(f):
            return sp.Poly(f.as_expr().subs(v_symbol, slope), u_symbol, modulus=5)

        section, denominator, numerator = map(specialize, (curve, leading, constant))
        assert section.degree() == 12
        for factor, _ in section.factor_list()[1]:
            field = MonogenicFiniteExtension(factor)
            u, v = field.generator, field(slope)
            if not u:
                continue
            p = -field(numerator.rem(factor).as_expr()) / field(denominator.rem(factor).as_expr())
            q = -(2*p**2+2*p*u+2*p*v**2+3*p*v+2*p+u**2) / (4*v+3)
            if q and -4*p**3-27*q**2 and opposite_edge_product(p, q, u, v):
                assert descended_rank(polars, (p, q, u, v), field) == 54
                rank_checks.append((slope, factor.degree()))
    assert sorted(rank_checks) == [(0, 8), (1, 2), (1, 4), (1, 4), (2, 2), (2, 10),
                                   (4, 2), (4, 2), (4, 3), (4, 4)]


if __name__ == "__main__":
    count = verify_repeated_edges()
    print(f"Excluded {count} geometric directions per incident-edge equality.", flush=True)
    verify_affine_interpolation()
    print("Excluded the affine interpolation stratum.", flush=True)
    symbols, equations = residual_system()
    print(f"Residual pure equations in {symbols}:")
    for equation in equations:
        print(equation)
    verify_exceptional_gauges()
    result = plane_resultant()
    verify_geometric_irreducibility(result)
    verify_prime_slopes(result, *generic_lift())
    print("Excluded every prime-field interpolation slope.")
    print("Excluded u=0 and v=3 on the all-edges-nonzero residual. "
          f"The geometrically irreducible plane resultant has bidegree ({result.degree(0)}, {result.degree(1)}).")
