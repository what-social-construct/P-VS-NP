"""Eliminate six completion coordinates on the normalized permanent collision chart."""

import argparse
import subprocess
import sys
from functools import lru_cache
from itertools import combinations, product
from math import prod
from pathlib import Path
from tempfile import TemporaryDirectory

import sympy as sp
from sympy.polys.rings import ring

from gct_permanent_extensions import COORDINATES, PRIME
from gct_permanent_hodge import STAR, collision_kernel_chart
from gct_permanent_modular import unit_ideal_at_degree
from gct_permanent_plucker import OFF_DIAGONAL, pencil_coefficients, tangent_direction, write_msolve_system

KERNEL_NAMES = tuple(f"b{i}{j}" for i, j in OFF_DIAGONAL if (i, j) != STAR[0])
FREE = tuple(slot for slot in COORDINATES if slot not in STAR)
POWERS = sorted(p for p in product(range(5), repeat=3) if 2 <= sum(p) <= 4)
PIVOT_COVER = (
    ((1, 2), (2, 2), (2, 3)),
    ((1, 1), (1, 2), (2, 2)),
    ((1, 2), (1, 3), (3, 3)),
)


def determinant(columns):
    a, b, c = columns
    return (a[0] * (b[1]*c[2] - b[2]*c[1]) + a[1] * (b[2]*c[0] - b[0]*c[2])
            + a[2] * (b[0]*c[1] - b[1]*c[0]))


def first_variations():
    """Return pure kernel equations and derivatives in all nine tangent coordinates."""
    algebra, *variables = ring(KERNEL_NAMES, sp.GF(PRIME), "grevlex")
    edges = dict(zip(OFF_DIAGONAL, [algebra.one, *variables]))
    total = sum(edges.values())
    kernel = {
        **edges,
        **{(i, i): total/2 - 2*sum(v for edge, v in edges.items() if i in edge)
           for i in range(4)},
    }
    pure = list(pencil_coefficients(algebra, [kernel]).values())
    columns = {}
    for slot in COORDINATES:
        tangent = tangent_direction(algebra(int(other == slot)) for other in COORDINATES)
        mixed = pencil_coefficients(algebra, [kernel, tangent])
        columns[slot] = [mixed.get((i, 1, 0), algebra.zero) for i in (1, 2, 3)]
    return pure, columns


def minors(columns, slots):
    result = {}
    for pivots in combinations(slots, 3):
        value = determinant([columns[slot] for slot in pivots])
        if value:
            result[pivots] = value
    return result


def chart_name(pivots):
    return ",".join(f"{i}{j}" for i, j in pivots)


def verify_pivot_cover(msolve, pure, free_minors):
    """Compare exact reduced Gröbner bases in the same variable and term order."""
    def basis(directory, name, pivots):
        source = directory / (name + ".ms")
        result = directory / (name + ".out")
        with source.open("w") as stream:
            write_msolve_system(KERNEL_NAMES, [*pure, *(free_minors[p] for p in pivots)], stream)
        subprocess.run([msolve, "-f", str(source), "-o", str(result), "-t", "1", "-g", "2", "-l", "2"],
                       check=True)
        header, sep, body = result.read_text().partition("[")
        if not sep or "#Reduced Groebner basis data" not in header or not body.rstrip().endswith("]:"):
            raise ValueError("msolve did not return a reduced Gröbner basis")
        return body.strip()

    with TemporaryDirectory() as path:
        directory = Path(path)
        assert basis(directory, "three", PIVOT_COVER) == basis(directory, "all", free_minors)


def evaluate(polynomial, values):
    """Evaluate a sparse prime-field polynomial in the algebra of its arguments."""
    zero = 0 * values[0]
    return sum((int(coeff) * prod(x**n for x, n in zip(values, powers) if n)
                for powers, coeff in polynomial.items()), zero)


@lru_cache(maxsize=1)
def chart_data():
    pure, columns = first_variations()
    _, equations = collision_kernel_chart()
    return pure, columns, equations


def chart_evaluators(pivots):
    """Construct the lift and the 26 residuals on one of the three pivot charts.

    Arguments are the five normalized kernel coordinates, the three free
    entries in each completion column (in FREE order), and the inverse minor.
    The operations work over any commutative F5-algebra.
    """
    if pivots not in PIVOT_COVER:
        raise ValueError("unknown completion pivot triple")
    _, columns, originals = chart_data()
    free_slots = [slot for slot in FREE if slot not in pivots]
    surviving = [f for powers, f in zip(POWERS, originals) if powers[1] + powers[2] != 1]

    def lift(*parameters):
        if len(parameters) != 12:
            raise ValueError("a reduced chart requires 12 coordinates")
        kernel = parameters[:5]
        inverse = parameters[-1]
        jacobian = {slot: [evaluate(f, kernel) for f in column] for slot, column in columns.items()}
        selected = [jacobian[slot] for slot in pivots]
        lifted = list(kernel)
        for star, entries in zip(STAR[1:], [parameters[5:8], parameters[8:11]]):
            coordinates = dict(zip(free_slots, entries))
            # The prescribed star slot in this completion has coefficient one.
            rhs = [-jacobian[star][row] - sum(jacobian[slot][row] * value
                                              for slot, value in coordinates.items())
                   for row in range(3)]
            for i, slot in enumerate(pivots):
                replaced = selected.copy()
                replaced[i] = rhs
                coordinates[slot] = inverse * determinant(replaced)
            lifted.extend(coordinates[slot] for slot in FREE)
        return determinant(selected), tuple(lifted)

    def equations(*parameters):
        delta, lifted = lift(*parameters)
        return (parameters[-1] * delta - 1, *(evaluate(f, lifted) for f in surviving))

    return lift, equations


def reduced_chart_source(pivots):
    free = [slot for slot in FREE if slot not in pivots]
    names = (*KERNEL_NAMES, *(f"{col}{i}{j}" for col in "cd" for i, j in free), "inverse")
    return (f'"""Chart coordinates in order: {", ".join(names)}."""\n'
            "from gct_collision_kernel_reduction import chart_evaluators\n\n"
            f"lift, equations = chart_evaluators({pivots!r})\n")


def verify_original_derivatives(pure, columns, equations):
    """Compare both blocks of three eliminated rows with the original equations."""
    algebra = equations[0].ring
    by_name = {str(name): value for name, value in zip(algebra.symbols, algebra.gens)}
    original = dict(zip(POWERS, equations))
    for degree in (2, 3, 4):
        assert original[degree, 0, 0] == pure[degree-2].set_ring(algebra)
        for col, star, extra in zip("cd", STAR[1:], [(1, 0), (0, 1)]):
            derivative = columns[star][degree-2].set_ring(algebra)
            for i, j in FREE:
                derivative += columns[i, j][degree-2].set_ring(algebra) * by_name[f"{col}{i}{j}"]
            assert original[(degree-1, *extra)] == derivative


def verify_reconstruction(pivots, pure, columns, equations, minor):
    """Replay the emitted equations against the original polynomials at an invertible pivot."""
    selected = [columns[slot] for slot in pivots]
    for row in range(3):
        unit = [int(k == row) for k in range(3)]
        cofactors = []
        for i in range(3):
            replaced = selected.copy()
            replaced[i] = unit
            cofactors.append(determinant(replaced))
        for k in range(3):
            assert sum(c * col[k] for c, col in zip(cofactors, selected)) == minor * unit[k]
    lift, reduced_equations = chart_evaluators(pivots)
    for kernel_values in product(range(PRIME), repeat=len(KERNEL_NAMES)):
        if any(evaluate(f, kernel_values) % PRIME for f in pure):
            continue
        d = evaluate(minor, kernel_values) % PRIME
        if d:
            break
    else:
        raise AssertionError("no prime-field level kernel direction for this pivot")
    values = (*kernel_values, 0, 1, 2, 3, 4, 1, pow(d, -1, PRIME))
    points = [sp.GF(PRIME)(x) for x in values]
    delta, lifted = lift(*points)
    assert int(delta) == d
    # SymPy substitutes in the original ring independently of the sparse evaluator.
    substitutions = list(zip(equations[0].ring.gens, lifted))
    expected = [int(f.evaluate(substitutions)) for f in equations]
    reduced = [int(value) for value in reduced_equations(*points)]
    assert reduced == [0, *(v for p, v in zip(POWERS, expected) if p[1]+p[2] != 1)]
    assert all(v == 0 for p, v in zip(POWERS, expected) if p[1]+p[2] == 1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--emit-rank-system", action="store_true", help="write the 5-variable msolve rank test")
    mode.add_argument("--verify-cover", metavar="MSOLVE", help="compare the three-minor and all-minor ideals using msolve")
    mode.add_argument("--list-charts", action="store_true", help="list the three completion pivot triples")
    mode.add_argument("--emit-chart", metavar="SLOTS", help="write the reduced Python polynomial evaluator, e.g. 12,22,23")
    args = parser.parse_args()
    charts = {chart_name(pivots): pivots for pivots in PIVOT_COVER}
    if args.list_charts:
        print("\n".join(charts))
        return
    if args.emit_chart is not None:
        if args.emit_chart not in charts:
            parser.error("choose a nonzero minor from --list-charts")
        print(reduced_chart_source(charts[args.emit_chart]), end="")
        return
    pure, columns, equations = chart_data()
    free_minors = minors(columns, FREE)
    if args.verify_cover:
        verify_pivot_cover(args.verify_cover, pure, free_minors)
        print("The pure kernel equations with three or all 19 completion minors give the same reduced basis.")
        return
    all_minors = minors(columns, COORDINATES)
    if args.emit_rank_system:
        write_msolve_system(KERNEL_NAMES, [*pure, *all_minors.values()], sys.stdout)
        return
    verify_original_derivatives(pure, columns, equations)
    assert len(pure) == 3 and len(all_minors) == 83 and len(free_minors) == 19
    assert unit_ideal_at_degree([*pure, *all_minors.values()], len(KERNEL_NAMES), PRIME, 7)
    for pivots in PIVOT_COVER:
        verify_reconstruction(pivots, pure, columns, equations, free_minors[pivots])
    print("Kernel equations and rank-drop minors generate 1 over F5 (degree cap 7).")
    print("Both completion blocks match the original coefficients. All three reduced evaluators replayed.")


if __name__ == "__main__":
    main()
