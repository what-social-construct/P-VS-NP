"""Recover lines through polar-section points and check their extension degrees at five."""

from collections import Counter
from itertools import permutations, product

import sympy as sp
from sympy.polys.matrices import DomainMatrix

from gct_collision_ordering_fibers import ordering_factors
from gct_collision_quadrics import checked_line_forms, quadratic_field
from gct_common_line_witness import LineWitness, verifies_line


def polar_kernel_line(forms, point, field):
    """Return canonical RREF rows of the common line through a rank-three polar point.

    Supply the three symmetric Gram matrices and a nonzero common point in the
    same finite field. At rank three the polar kernel is the sole candidate.
    None certifies that this point lies on no common line. Lower rank raises
    ValueError because several lines can pass through that point. Testing every
    point of a transverse hyperplane section gives complete geometric coverage.
    """
    forms = checked_line_forms(forms, field)
    if len(point) != 5:
        raise ValueError("expected a vector in five coordinates")
    point = DomainMatrix([[field.convert(c) for c in point]], (1, 5), field)
    if point.is_zero_matrix:
        raise ValueError("expected a nonzero vector over the supplied field")
    grams = [DomainMatrix(form, (5, 5), field) for form in forms]
    polar_rows = [point * gram for gram in grams]
    if any(not (row * point.transpose()).is_zero_matrix for row in polar_rows):
        raise ValueError("the point must lie on all three quadrics")
    polars = DomainMatrix([row.to_list()[0] for row in polar_rows], (3, 5), field)
    echelon, pivots = polars.rref()
    if len(pivots) != 3:
        raise ValueError("polar rank below three leaves the line undetermined")
    basis, _ = echelon.nullspace_from_rref(pivots).rref()
    if any(not (basis * gram * basis.transpose()).is_zero_matrix for gram in grams):
        return None
    return tuple(tuple(row) for row in basis.to_list())


def check_extension_degrees():
    """A split-quadrics control with conjugate lines and irreducible cubic labels."""
    base = sp.GF(5)
    field = quadratic_field()
    # Coordinates (a,b,c,d,t). The third quadric is t(t-a-c);
    # the off-diagonal entry -1/2 is 2 in characteristic five.
    third = sp.zeros(5)
    third[4, 4] = 1
    third[0, 4] = third[4, 0] = third[2, 4] = third[4, 2] = 2
    forms = [sp.diag(-2, 1, 0, 0, 0).tolist(), sp.diag(0, 0, -2, 1, 0).tolist(),
             third.tolist()]
    # On H=c-a=0 every point has a!=0. With a=1 the section becomes
    # b²=d²=2 and t(t-2)=0. These three separated equations have simple roots.
    lines = set()
    for sigma, tau, epsilon in product((1, -1), (1, -1), (0, 1)):
        b, d = sigma * field.generator, tau * field.generator
        point = (field.one, b, field.one, d, field(2 * epsilon))
        rows = polar_kernel_line(forms, point, field)
        expected = ((field.one, b, field.zero, field.zero, field(epsilon)),
                    (field.zero, field.zero, field.one, d, field(epsilon)))
        assert rows == expected and verifies_line(forms, base, LineWitness(field, field.zero, rows))
        lines.add(rows)
    assert len(lines) == 8

    # The unique candidate at this same section point becomes nonisotropic
    # after adding (a-c)². Its derivative at the section point is zero.
    h = sp.Matrix([-1, 0, 1, 0, 0])
    changed = [*forms[:2], (third + h*h.T).tolist()]
    sample = (field.one, field.generator, field.one, field.generator, field.zero)
    assert polar_kernel_line(changed, sample, field) is None

    # Frobenius acts entrywise on the unique RREF basis. The ordered roots
    # of T³+T+1 have period three, so name the roots in cyclic order.
    conjugate = {rows: tuple(tuple(c**5 for c in row) for row in rows) for rows in lines}
    assert all(image != rows and conjugate[image] == rows for rows, image in conjugate.items())
    assert ordering_factors(base, base.one, base(-1)) == (3, 3)
    labels = tuple(permutations(range(3)))
    pairs = set(product(lines, labels))
    orbit_sizes = Counter()
    while pairs:
        start = next(iter(pairs))
        rows, label = start
        size = 0
        while (rows, label) in pairs:
            pairs.remove((rows, label))
            rows, label = conjugate[rows], tuple((i + 1) % 3 for i in label)
            size += 1
        assert (rows, label) == start
        orbit_sizes[size] += 1
    assert orbit_sizes == {6: 8}
    print("Eight simple section points and eight lines in four degree-two Frobenius orbits.")
    print("Cubic ordering degree three. The 48 labeled lines form eight degree-six orbits.")


if __name__ == "__main__":
    check_extension_degrees()
