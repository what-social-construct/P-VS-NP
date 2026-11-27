"""Check the Hodge pairing and export corrected-diagonal kernel charts."""

import argparse
import sys
from collections import Counter

import numpy as np
import sympy as sp
from sympy.polys.rings import ring

from gct_permanent_extensions import (
    COORDINATES, PRIME, level_two_planes, reduced_rows, tangent_matrices,
)
from gct_permanent_fiber import hadamard_direction
from gct_permanent_plucker import (
    EDGE_GRAPH_PIVOTS, OFF_DIAGONAL, corrected_diagonal, edge_metric,
    pencil_coefficients, tangent_direction, write_msolve_system,
)

EDGE_SLOTS = tuple(COORDINATES.index(edge) for edge in OFF_DIAGONAL)


def verify_hodge_profiles():
    planes = level_two_planes()
    edges = planes[:, :, EDGE_SLOTS]
    matrices = tangent_matrices(planes)
    diagonal = np.diagonal(matrices, axis1=-2, axis2=-1)
    trace = diagonal.sum(axis=-1)[..., None]
    corrected = 2*matrices.sum(axis=-1) - diagonal + pow(4, -1, PRIME)*trace
    metric = np.array([[edge_metric(left, right) for right in OFF_DIAGONAL]
                       for left in OFF_DIAGONAL], dtype=np.int64)
    ordinary = edges @ edges.swapaxes(1, 2)
    compatible = edges @ metric @ edges.swapaxes(1, 2)
    assert np.array_equal(compatible % PRIME, (corrected @ corrected.swapaxes(1, 2)) % PRIME)

    def rank(matrix):
        return len(reduced_rows(matrix)[1])

    assert all(rank(edge_plane) == rank(diagonal_plane) == 2
               for edge_plane, diagonal_plane in zip(edges, corrected))
    ordinary_ranks = Counter(map(rank, ordinary))
    compatible_ranks = Counter(map(rank, compatible))
    assert ordinary_ranks == {0: 8, 1: 12, 2: 136}
    assert compatible_ranks == {2: 156}
    return ordinary_ranks, compatible_ranks


def corrected_diagonal_chart():
    """Generate the F5 chart for level two-planes in the corrected-diagonal kernel."""
    names = ("x", "y", "u", "v", "w", "h")
    coefficients, x, y, u, v, w, h = ring(names, sp.GF(PRIME), "grevlex")
    relation = h**2 - 3
    frames = (
        ((coefficients.one, coefficients.zero, x), (-x*y, -w, y)),
        ((coefficients.zero, coefficients.one, u), (w - x*v - y*u, -u*v, v)),
    )
    directions = []
    for e, f in frames:
        arms = [(left - right).as_expr() for left, right in zip(e, f)]
        diagonal = [(h * (left + right)).as_expr() for left, right in zip(e, f)]
        matrix = hadamard_direction(arms, diagonal, [3 * arm for arm in arms])
        direction = {}
        for i in range(4):
            for j in range(i, 4):
                polynomial = sp.Poly(matrix[i, j], *coefficients.symbols, domain=sp.QQ)
                direction[i, j] = coefficients.from_dict({
                    powers: int(value.p) * pow(int(value.q), -1, PRIME) % PRIME
                    for powers, value in polynomial.terms()
                })
        assert all(not entry for entry in corrected_diagonal(direction))
        directions.append(direction)

    reduced = {powers: value.rem(relation) for powers, value in
               pencil_coefficients(coefficients, directions).items()}
    assert all(not value for powers, value in reduced.items() if sum(powers) <= 2)
    equations = [value for powers, value in reduced.items() if sum(powers) > 2]
    assert Counter(sum(powers) for powers, value in reduced.items() if value) == {3: 4, 4: 5}
    return names, [relation, *equations]


def collision_kernel_chart():
    """Normalize one kernel direction after permuting the three leaves."""
    pivots = EDGE_GRAPH_PIVOTS["star"]
    first = pivots[0]
    names = tuple(f"b{i}{j}" for i, j in OFF_DIAGONAL if (i, j) != first)
    names += tuple(f"{label}{i}{j}" for label in "cd" for i, j in COORDINATES if (i, j) not in pivots)
    coefficients, *variables = ring(names, sp.GF(PRIME), "grevlex")
    entries = iter(variables)
    edges = {edge: coefficients.one if edge == first else next(entries) for edge in OFF_DIAGONAL}
    edge_sum = sum(edges.values())
    kernel = {
        **edges,
        **{(i, i): edge_sum/2 - 2*sum(value for edge, value in edges.items() if i in edge)
           for i in range(4)},
    }
    assert sum(kernel[i, i] for i in range(4)) == -2*edge_sum
    assert not any(corrected_diagonal(kernel))
    directions = [kernel]
    directions.extend(tangent_direction(
        coefficients(int(slot == pivot)) if slot in pivots else next(entries)
        for slot in COORDINATES
    ) for pivot in pivots[1:])

    equations = pencil_coefficients(coefficients, directions)
    metric_pairings = {
        edge: sum(edge_metric(edge, other)*value for other, value in edges.items())
        for edge in OFF_DIAGONAL
    }
    for index, direction in enumerate(directions):
        powers = tuple(int(slot == 0) + int(slot == index) for slot in range(3))
        pairing = sum(metric_pairings[edge]*direction[edge] for edge in OFF_DIAGONAL)
        assert equations[powers] == (1 if index == 0 else 2)*pairing
    assert len(names) == 17
    assert Counter(map(sum, equations)) == {2: 6, 3: 10, 4: 15}
    return names, list(equations.values())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--emit-chart", action="store_const", dest="export", const=corrected_diagonal_chart,
                       help="emit the corrected-diagonal two-plane chart in msolve input format")
    modes.add_argument("--emit-collision-kernel", action="store_const", dest="export", const=collision_kernel_chart,
                       help="emit the 17-variable star collision chart in msolve input format")
    args = parser.parse_args()
    if args.export is not None:
        names, equations = args.export()
        write_msolve_system(names, equations, sys.stdout)
        return
    ordinary, compatible = verify_hodge_profiles()
    print("F5 level two-plane ordinary Gram ranks", dict(sorted(ordinary.items())))
    print("F5 level two-plane compatible Gram ranks", dict(sorted(compatible.items())))


if __name__ == "__main__":
    main()
