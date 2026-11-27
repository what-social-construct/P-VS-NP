"""Check the common-line obstruction at the exceptional degree-88 lift."""

import numpy as np
import sympy as sp
from sympy.polys.agca.extensions import MonogenicFiniteExtension

from gct_collision_face import descended_forms, specialization_polars
from gct_collision_quadrics import determinant_of_net, homogeneous_powers, jacobian_multiples
from gct_permanent_extensions import reduced_rows


def power_coefficients(element, degree):
    """Ascending prime-field coefficients padded to the power basis length."""
    coefficients = [int(c) % 5 for c in reversed(element.rep.to_list())]
    return coefficients + [0] * (degree - len(coefficients))


def monogenic_coordinates(data):
    """Flatten the quadratic tower in the basis 1,p,...,p^87, checking independence."""
    base, v, u, quadratic, q = data
    algebra = quadratic.ring
    p, = algebra.gens
    degree = 2*base.rank

    def vector(value):
        return sum((power_coefficients(value.get((i,), base.zero), base.rank) for i in (0, 1)), [])

    powers = []
    power = algebra.one
    for _ in range(degree):
        powers.append(vector(power))
        power = (power*p).rem([quadratic])
    targets = [power, p, q, algebra(u), algebra(v)]
    columns = [*powers, *(vector(value) for value in targets)]
    reduced, pivots = reduced_rows(np.asarray(columns, dtype=np.int16).T)
    assert list(pivots) == list(range(degree))
    omega = sp.Symbol("omega")
    expressions = [sum(int(c)*omega**i for i, c in enumerate(column) if c)
                   for column in reduced[:, degree:].T]
    modulus = sp.Poly(omega**degree-expressions[0], omega, modulus=5)
    field = MonogenicFiniteExtension(modulus)
    values = [field(expr) for expr in expressions[1:]]
    assert degree == 88 and values[0] == field.generator
    return field, values


def multiplication_table(field):
    """Flatten the structure constants for power-basis multiplication mod h."""
    d = field.rank
    # reductions[k] holds the coordinates of omega^k for 0 <= k <= 2d-2.
    reductions = np.eye(2*d-1, d, dtype=np.int16)
    reductions[d] = [-int(c) % 5 for c in reversed(field.modulus.all_coeffs()[1:])]
    for k in range(d+1, 2*d-1):
        previous = reductions[k-1]
        reductions[k] = previous[-1]*reductions[d]
        reductions[k, 1:] += previous[:-1]
        reductions[k] %= 5
    structure = np.stack([reductions[k:k+d] for k in range(d)]).reshape(d, d*d)
    # All dot products below sum at most d<=88 terms, each at most 4*4.
    assert 16*d < np.iinfo(np.int16).max
    return structure


def power_basis_rank(quintic, degree):
    """Gaussian elimination over F5[omega]/h using exact integer dot products."""
    d = quintic.ring.domain.rank
    structure = multiplication_table(quintic.ring.domain)
    cols = homogeneous_powers(degree)
    rows = [[power_coefficients(x, d) for x in row]
            for _, _, row in jacobian_multiples(quintic, degree, cols)]
    matrix = np.asarray(rows, dtype=np.int16)
    one = np.eye(1, d, dtype=np.int16)[0]
    rank = 0
    for col in range(len(cols)):
        nonzero = np.flatnonzero(np.any(matrix[rank:, col], axis=1))
        if not nonzero.size:
            continue
        pivot = rank+nonzero[0]
        matrix[[rank, pivot]] = matrix[[pivot, rank]]
        # Rows of the multiplication matrix are (omega^j*a) in the power basis.
        multiplication = (matrix[rank, col] @ structure).reshape(d, d) % 5
        inverse_system, pivots = reduced_rows(np.column_stack((multiplication.T, one)))
        assert len(pivots) == d and pivots[-1] == d-1
        inverse = inverse_system[:, -1]
        inverse_matrix = (inverse @ structure).reshape(d, d) % 5
        normalized = (matrix[rank, col:] @ inverse_matrix) % 5
        assert np.array_equal(normalized[0], one)
        # The middle index is the input power-basis coordinate. Multiply
        # every elimination factor by every entry of the normalized row.
        width = len(normalized)
        blocks = (normalized @ structure).reshape(width, d, d) % 5
        operator = blocks.transpose(1, 0, 2).reshape(d, width*d)
        products = (matrix[rank+1:, col] @ operator).reshape(-1, width, d)
        matrix[rank+1:, col:] = (matrix[rank+1:, col:]-products) % 5
        rank += 1
    return rank


def verify_exceptional_rank(data):
    field, values = monogenic_coordinates(data)
    forms = descended_forms(specialization_polars(), values, field)
    quintic = determinant_of_net(forms, field)
    rank = power_basis_rank(quintic, 9)
    assert rank == 54
    return rank
