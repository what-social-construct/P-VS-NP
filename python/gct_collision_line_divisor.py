"""Certify nonvanishing of the common-line and level-plane resultants at five."""

from itertools import combinations

import sympy as sp
from sympy.polys.matrices import DomainMatrix
from sympy.polys.rings import ring

from gct_collision_fiber_net import polar_sextic_certificate
from gct_collision_kernel_reduction import COORDINATES, evaluate
from gct_collision_quadrics import polar_equations, quotient_forms_at
from gct_collision_slice import face_edges, kernel_from_edges
from gct_permanent_plucker import pencil_coefficients, tangent_direction


def invariant_covectors(tangent):
    incident = tangent[0, 2] + tangent[1, 2] + tangent[2, 3]
    diagonal = tangent[0, 0] + tangent[1, 1] + tangent[3, 3]
    return incident, diagonal


def invariant_frame(diagonal, incident, field):
    """Return the frame with fourth coordinate D and fifth H."""
    for slots in combinations(range(5), 3):
        chart = [[field(int(i == j)) for j in range(5)] for i in slots]
        change = DomainMatrix([*chart, list(diagonal), list(incident)], (5, 5), field)
        if change.det():
            return change.inv().transpose()
    raise ValueError("D and H are dependent on the polar kernel")


def adapted_grams(grams, diagonal, incident, field):
    """Express the three quadrics in invariant coordinates."""
    frame = invariant_frame(diagonal, incident, field)
    return [(frame * DomainMatrix(q, (5, 5), field) * frame.transpose()).to_list()
            for q in grams]


def check_cubic_section(edges, basis, incident_row, diagonal_row, field):
    """Check the section at H=0 and compute the companion algebra on H=1."""
    frame = invariant_frame(diagonal_row, incident_row, field) * DomainMatrix(basis, (5, 9), field)
    algebra, *parameters = ring("a,b,c,d,h", field)
    tangent = tangent_direction(sum(t*c for t, c in zip(parameters, column))
                                for column in zip(*frame.to_list()))
    assert invariant_covectors(tangent) == (parameters[4], parameters[3])
    base = kernel_from_edges(algebra(x) for x in edges)
    coefficients = pencil_coefficients(algebra, (base, tangent))
    equations = [coefficients[i, 2, 0].as_expr() for i in range(3)]
    equations.append(coefficients[0, 3, 0].as_expr())
    *coordinates, h = algebra.symbols
    for pivot in coordinates:
        variables = [v for v in coordinates if v != pivot]
        chart = [f.subs({h: 0, pivot: 1}) for f in equations]
        assert list(sp.groebner(chart, *variables, modulus=5, order="grevlex")) == [1]
    chart = [f.subs(h, 1) for f in equations]
    lex = sp.groebner(chart, *coordinates, modulus=5, order="grevlex").fglm("lex")
    # With these leading monomials the entire projective companion scheme
    # has algebra F5[d]/(g), d=D/H. Its normalized pencil is
    # Norm(s + t*d) = t^24*g(-s/t), including nonreduced multiplicities.
    assert [p.LM().exponents for p in lex.polys] == [
        (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 24)]
    d = coordinates[-1]
    g = sp.Poly(lex[-1], d, modulus=5)
    assert g.is_monic
    # Compute Frobenius minus identity on the full quotient, including the double point.
    length = g.degree()
    rows = []
    for i in range(length):
        difference = sp.Poly(d**(5*i) - d**i, d, modulus=5).rem(g)
        rows.append([field.convert(difference.nth(j)) for j in range(length)])
    fixed_dimension = length - DomainMatrix(rows, (length, length), field).rank()
    assert fixed_dimension == 4
    _, factors = g.factor_list()
    rational_factors = [(factor, m) for factor, m in factors if factor.degree() == 1]
    assert {int(-factor.TC()) % 5: m for factor, m in rational_factors} == {1: 1, 2: 2}
    assert sorted((f.degree(), m) for f, m in factors if f.degree() > 1) == [(10, 1), (11, 1)]
    # Replay the five pencil members other than H=0 in the original equations.
    # Their zeros have D/H=value. The previous four chart checks cover H=0.
    for value in range(5):
        section = [f.subs(d, value) for f in chart]
        empty = list(sp.groebner(section, *coordinates[:-1], modulus=5, order="grevlex")) == [1]
        assert empty == (g.eval(value) != 0)
    binary_coefficients = [(-1)**j * int(c) % 5 for j, c in enumerate(g.all_coeffs())]
    print(f"Normalized pencil coefficients in increasing t degree: {binary_coefficients}")
    print("The degree-24 H,D pencil has factors of degrees 1,1,10,11 with "
          "multiplicities 1,2,1,1. Its rational zeros are H-D and H+2D.")
    print(f"The Frobenius fixed subspace of the companion algebra has dimension {fixed_dimension}.")
    # The cubic carries no twist in B; each quadratic has multiplicity 12.
    degree = 24*5 + 12*(0+1+2)
    assert degree == 156
    print(f"The four cubic-section charts are empty at (1,1,3,0,3,4). "
          f"Degree {degree}, quotient bound {24*degree//6}.")


def check_line_divisor():
    field = sp.GF(5)
    _, a, b, c, d, m = ring("a,b,c,d,m", field)
    # The two functionals kill the tautological direction on the entire face.
    assert invariant_covectors(kernel_from_edges(face_edges(a, b, c, d, m))) == (0, 0)

    edges = [field(x) for x in (1, 1, 3, 0, 3, 4)]
    incident, diagonal = invariant_covectors(kernel_from_edges(edges))
    assert not incident and not diagonal
    assert edges[0] + edges[2] + edges[4]  # Sum of opposite edges Y is nonzero.
    pure, polars = polar_equations()
    assert all(not evaluate(q, edges[1:]) for q in pure)

    # Quotient by B in the X01=0 chart, with the same ordered free
    # coordinates as quotient_forms_at. Each nullspace row is a tangent.
    rows = [[evaluate(polars[slot][i], edges[1:]) for slot in COORDINATES]
            for i in range(3)]
    rows.append([field(int(slot == (0, 1))) for slot in COORDINATES])
    echelon, pivots = DomainMatrix(rows, (4, 9), field).rref()
    assert len(pivots) == 4
    basis = echelon.nullspace_from_rref(pivots).to_list()
    free = [j for j in range(9) if j not in pivots]
    assert [[row[j] for j in free] for row in basis] == [
        [field(int(i == j)) for j in range(5)] for i in range(5)]
    incident_row, diagonal_row = zip(*(invariant_covectors(tangent_direction(row)) for row in basis))
    # In the new coordinates the fourth coordinate is D and the fifth is H.
    adapted = adapted_grams(quotient_forms_at(edges, field), diagonal_row, incident_row, field)
    polar_sextic_certificate(adapted, field)

    # For degrees (1,2,2,2,6) the determinant character uses 48 copies
    # of det W*. The sextic also carries two copies of det W* and twist 6.
    degree = 5*48 + 24*(0+1+2) + 8*(2*5+6)
    assert degree == 440
    print(f"The common-line resultant is nonzero at (1,1,3,0,3,4). "
          f"Degree {degree}, divisor length {24*degree}, quotient bound {24*degree//6}.")
    check_cubic_section(edges, basis, incident_row, diagonal_row, field)


if __name__ == "__main__":
    check_line_divisor()
