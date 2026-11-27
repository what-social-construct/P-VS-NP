"""A projective three-space section of the pure collision-kernel equations at five."""

from itertools import product

import numpy as np
import sympy as sp
from sympy.polys.rings import ring

from gct_permanent_plucker import OFF_DIAGONAL, pencil_coefficients


def slice_equations():
    """Restrict the original permanent to edges (a,-b-d,-c-d,b,c,d)."""
    algebra, a, b, c, d = ring("a,b,c,d", sp.GF(5), "grevlex")
    edges = dict(zip(OFF_DIAGONAL, (a, -b-d, -c-d, b, c, d)))
    half_sum = sum(edges.values()) / 2
    kernel = {**edges, **{(i, i): half_sum - 2*sum(x for edge, x in edges.items() if i in edge)
                          for i in range(4)}}
    coefficients = pencil_coefficients(algebra, [kernel])
    assert set(coefficients) == {(2, 0, 0), (3, 0, 0), (4, 0, 0)}
    equations = [coefficients[i, 0, 0] for i in (2, 3, 4)]
    assert all(all(sum(powers) == degree for powers in f) for degree, f in enumerate(equations, 2))
    return equations


def slice_length(equations):
    """Use the initial ideal to compute the eventual homogeneous Hilbert function."""
    basis = sp.groebner([f.as_expr() for f in equations], *equations[0].ring.symbols,
                       modulus=5, order="grevlex")
    leading = {g.LM(order="grevlex").exponents for g in basis.polys}
    assert leading == {(1, 0, 5, 0), (0, 0, 6, 0), (2, 0, 3, 0), (1, 1, 3, 0),
                       (2, 1, 1, 0), (3, 0, 0, 0), (0, 2, 0, 0)}
    # The pure powers bound a,b,c, and arbitrary powers of d preserve standardness.
    bounds = (3, 2, 6)
    standard = [p for p in product(*(range(n) for n in bounds))
                if not any(all(g <= n for g, n in zip(term[:3], p)) for term in leading)]
    assert [sum(sum(p) == k for p in standard) for k in range(7)] == [1, 3, 5, 6, 5, 3, 1]
    assert len(standard) == 24
    return len(standard)


def verify_quadratic_slice(certified_lines, add, multiply):
    """Verify the entire section is supported on enumerated, excluded F25 lines.

    The input lines use first-nonzero-entry normalization in the six kernel
    edges, in the order 01,02,03,12,13,23. Four section points have edge 01 zero.
    """
    equations = slice_equations()
    length = slice_length(equations)
    on_first_hyperplane = {line for line in certified_lines if add[line[1], add[line[3], line[5]]] == 0}
    points = {line for line in on_first_hyperplane if add[line[2], add[line[4], line[5]]] == 0}
    # Removing the base section leaves the pure F25 points above [0:1].
    assert len(on_first_hyperplane - points) == 40
    assert all(next(x for x in line if x) == 1 for line in points)
    assert len(points) == length and all(line[5] for line in points)
    assert sum(line[0] == 0 for line in points) == 4

    free = np.array([(p[0], p[3], p[4], p[5]) for p in sorted(points)]).T
    power_table = [np.ones_like(free)]
    for _ in range(4):
        power_table.append(multiply[power_table[-1], free])
    for f in equations:
        values = np.zeros(len(points), dtype=int)
        for exponents, coefficient in f.items():
            term = int(coefficient) % 5
            for variable, exponent in enumerate(exponents):
                term = multiply[term, power_table[exponent][variable]]
            values = add[values, term]
        assert not np.any(values)
    return points
