"""Certify nonvanishing of the vertex-invariant common-line resultant at five."""

from itertools import combinations

import sympy as sp
from sympy.polys.matrices import DomainMatrix
from sympy.polys.rings import ring

from gct_collision_fiber_net import polar_sextic_certificate
from gct_collision_kernel_reduction import COORDINATES, evaluate
from gct_collision_quadrics import polar_equations, quotient_forms_at
from gct_collision_slice import face_edges, kernel_from_edges
from gct_permanent_plucker import tangent_direction


def invariant_covectors(tangent):
    incident = tangent[0, 2] + tangent[1, 2] + tangent[2, 3]
    diagonal = tangent[0, 0] + tangent[1, 1] + tangent[3, 3]
    return incident, diagonal


def adapted_grams(grams, diagonal, incident, field):
    """Express the three quadrics in a frame with fourth coordinate D and fifth H."""
    for slots in combinations(range(5), 3):
        chart = [[field(int(i == j)) for j in range(5)] for i in slots]
        change = DomainMatrix([*chart, list(diagonal), list(incident)], (5, 5), field)
        if change.det():
            frame = change.inv().transpose()
            return [(frame * DomainMatrix(q, (5, 5), field) * frame.transpose()).to_list()
                    for q in grams]
    raise ValueError("D and H are dependent on the polar kernel")


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


if __name__ == "__main__":
    check_line_divisor()
