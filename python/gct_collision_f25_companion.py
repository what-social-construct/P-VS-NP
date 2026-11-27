"""Degree-four polynomial certificates for a companion to a kernel line over F25.

Field elements a+b*sqrt(2) are encoded as a+5*b, with a,b in {0,...,4}.
The interpolation nodes are used to recover an identity of bounded degree,
so success excludes companions over every extension of F25.
"""

from dataclasses import dataclass
from itertools import product
from math import prod

import numpy as np

from gct_collision_direction import COMPANION_SLOTS, OFF_DIAGONAL, REPRESENTATIVE, STAR
from gct_permanent_extensions import COORDINATES, PERMUTATIONS
from gct_permanent_frobenius import extension_tables, field_sum


_, _, ADD, MUL, _ = extension_tables((3, 0))
NEG = np.argmax(ADD == 0, axis=1)
INV = np.argmax(MUL == 1, axis=1)


def rref(matrix, coefficient_columns):
    """Reduce all rows, choosing pivots only in the specified coefficients."""
    rows = matrix.copy()
    pivots = []
    for column in range(coefficient_columns):
        index = len(pivots)
        nz = np.flatnonzero(rows[index:, column])
        if not nz.size:
            continue
        other = index + nz[0]
        rows[[index, other]] = rows[[other, index]]
        pivot = MUL[INV[rows[index, column]], rows[index]]
        factors = NEG[rows[:, column]].copy()
        rows = ADD[rows, MUL[factors[:, None], pivot]]
        rows[index] = pivot
        pivots.append(column)
    return rows, pivots


def simplex(dimension):
    return [node for node in product(range(5), repeat=dimension) if sum(node) <= 4]


def monomial_values(nodes):
    """The degree-four evaluation matrix on the integer simplex over F5."""
    return np.array([[prod(x**d for x, d in zip(node, powers)) % 5
                      for powers in nodes] for node in nodes], dtype=np.int64)


PENCIL_POWERS = simplex(2)
PENCIL_NODES = np.array(PENCIL_POWERS)
NODES = simplex(3)
MONOMIALS = monomial_values(NODES)


def evaluation_inverse(matrix):
    size = len(matrix)
    identity = np.eye(size, dtype=np.int64)
    reduced, pivots = rref(np.column_stack((matrix, identity)), size)
    assert len(pivots) == size
    inverse = reduced[:, size:]
    assert np.array_equal((matrix @ inverse) % 5, identity)
    return inverse


PENCIL_INVERSE = evaluation_inverse(monomial_values(PENCIL_POWERS))
COMPANION_INVERSE = evaluation_inverse(MONOMIALS)


def interpolate(values, inverse):
    """Prime-field interpolation acts separately on the two base-five digits."""
    return ((values % 5) @ inverse.T) % 5 + 5 * (((values // 5) @ inverse.T) % 5)


def kernel_matrix(edges):
    if (len(edges) != 6 or edges[0] != 1 or
            any(not isinstance(x, (int, np.integer)) or not 0 <= x < 25 for x in edges)):
        raise ValueError("expected six F25 edge coordinates with first entry one")
    matrix = np.zeros((4, 4), dtype=np.int64)
    for edge, value in zip(OFF_DIAGONAL, edges):
        i, j = edge
        matrix[i, j] = matrix[j, i] = value
    half = MUL[3, field_sum(ADD, edges)]
    for i in range(4):
        matrix[i, i] = ADD[half, MUL[3, field_sum(ADD, matrix[i])]]
    return matrix


def companion_matrices(entries, star_index):
    matrices = np.zeros((len(entries), 4, 4), dtype=np.int64)
    i, j = STAR[star_index]
    matrices[:, i, j] = matrices[:, j, i] = 1
    for (i, j), values in zip(COMPANION_SLOTS, entries.T):
        matrices[:, i, j] = matrices[:, j, i] = values
    matrices[:, 0, 0] = NEG[field_sum(ADD, (MUL[1 if i == j else 2, matrices[:, i, j]]
                                            for i, j in COORDINATES))]
    return matrices


def pencil_coefficients(kernel, companions):
    """Evaluate the full permanent and interpolate all coefficients of s^i t^j."""
    s, t = PENCIL_NODES.T
    pencil = ADD[1, ADD[MUL[s[:, None, None], kernel],
                        MUL[t[None, :, None, None], companions[:, None]]]]
    values = field_sum(ADD, (MUL[MUL[pencil[..., 0, a], pencil[..., 1, b]],
                                 MUL[pencil[..., 2, c], pencil[..., 3, d]]]
                             for a, b, c, d in PERMUTATIONS))
    coefficients = interpolate(values, PENCIL_INVERSE)
    return dict(zip(PENCIL_POWERS, coefficients.T))


@dataclass(frozen=True)
class CompanionCertificate:
    kind: str
    rank: int
    weights: tuple


def verify_identity(values, rows, weights):
    """Recover the six polynomials, then multiply and add in the monomial basis."""
    coefficient_vectors = {power: interpolate(values[power], COMPANION_INVERSE)
                           for power in PENCIL_POWERS if power[1] >= 2}
    monomial_index = {exponent: k for k, exponent in enumerate(NODES)}
    result = np.zeros(len(NODES), dtype=np.int64)
    for ((i, j), h), weight in zip(rows, weights):
        terms = coefficient_vectors[i, j]
        for term in np.flatnonzero(terms):
            assert sum(NODES[term]) <= j
            shifted = tuple(a + b for a, b in zip(NODES[term], NODES[h]))
            k = monomial_index[shifted]
            result[k] = ADD[result[k], MUL[weight, terms[term]]]
    assert result[monomial_index[0, 0, 0]] == 1 and np.count_nonzero(result) == 1


def companion_certificate(edges, star_index=1):
    """Return an exact obstruction to a star-02 or star-03 companion, if found.

    'polar' weights combine the three affine rows to 0=1. 'degree-four'
    weights combine the 39 specified polynomial multiples to one. None means
    that this calculation has furnished neither certificate.
    """
    if star_index not in (1, 2):
        raise ValueError("the companion must have star 02 or 03")
    kernel = kernel_matrix(edges)
    initial = np.vstack((np.zeros(6, dtype=np.int64), np.eye(6, dtype=np.int64)))
    samples = pencil_coefficients(kernel, companion_matrices(initial, star_index))
    if any(np.any(samples[i, 0]) for i in (1, 2, 3, 4)):
        raise ValueError("the supplied kernel direction is not level")
    polar = np.array([samples[i, 1] for i in (1, 2, 3)])
    slopes = ADD[polar[:, 1:], NEG[polar[:, :1]]]
    rhs = NEG[polar[:, 0]]
    system = np.column_stack((slopes, rhs, np.eye(3, dtype=np.int64)))
    reduced, pivots = rref(system, 6)
    for row in reduced[len(pivots):]:
        if row[6]:
            weights = MUL[INV[row[6]], row[7:]]
            assert not np.any(field_sum(ADD, MUL[weights[:, None], slopes]))
            assert field_sum(ADD, MUL[weights, rhs]) == 1
            return CompanionCertificate("polar", len(pivots), tuple(map(int, weights)))
    if len(pivots) != 3:
        return None

    free = [i for i in range(6) if i not in pivots]
    entries = np.zeros((len(NODES), 6), dtype=np.int64)
    entries[:, free] = NODES
    for i, pivot in enumerate(pivots):
        entries[:, pivot] = ADD[reduced[i, 6], NEG[field_sum(ADD, (MUL[reduced[i, j], entries[:, j]]
                                                                  for j in free))]]
    values = pencil_coefficients(kernel, companion_matrices(entries, star_index))
    assert all(not np.any(values[i, 1]) for i in (1, 2, 3))
    rows = [((i, j), h) for i, j in PENCIL_POWERS if j >= 2
            for h, exponent in enumerate(NODES) if sum(exponent) <= 4-j]
    multiples = np.array([MUL[values[power], MONOMIALS[:, h]] for power, h in rows])
    assert multiples.shape == (39, 35)
    rhs = np.ones(35, dtype=np.int64)
    solutions, columns = rref(np.column_stack((multiples.T, rhs)), len(multiples))
    if np.any(solutions[len(columns):, -1]):
        return None
    weights = np.zeros(len(multiples), dtype=np.int64)
    weights[columns] = solutions[:len(columns), -1]
    assert np.array_equal(field_sum(ADD, MUL[weights[:, None], multiples]), rhs)
    verify_identity(values, rows, weights)
    return CompanionCertificate("degree-four", len(columns), tuple(map(int, weights)))


if __name__ == "__main__":
    proof = companion_certificate(REPRESENTATIVE)
    assert proof is not None and proof.kind == "degree-four" and proof.rank == 35
    print("A degree-four identity excludes a geometric star-02 companion at the prime-field representative.")
