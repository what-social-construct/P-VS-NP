"""A single common-line chart for the [0:1] pencil fiber over the closure at five."""

import argparse
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

import sympy as sp
from sympy.polys.rings import ring

from gct_collision_slice import face_edges, kernel_from_edges
from gct_permanent_extensions import COORDINATES
from gct_permanent_plucker import OFF_DIAGONAL, pencil_coefficients, tangent_direction, write_msolve_system


# In ker(m_3), X03 = -X13-X23. The full entry sum determines X00.
SLOTS = ((0, 1), (0, 2), (1, 2), (1, 3), (2, 3), (1, 1), (2, 2), (3, 3))


def incident(column, vertex):
    return sum(column[edge] for edge in OFF_DIAGONAL if vertex in edge)


def chart_system(pivots, *, exceptional=False):
    """Use one echelon row for boundary tests or two rows for the surviving chart."""
    free = [(i, j) for i, pivot in enumerate(pivots)
            for j in range(pivot + 1, len(SLOTS)) if j not in pivots]
    names = tuple(f"x{i}{j}" for i, j in free) + ("a", "b", "c", "d")
    algebra, *variables = ring(names, sp.GF(5), "grevlex")
    a, b, c, d = variables[-4:]
    kernel = kernel_from_edges(face_edges(a, b, c, d))
    values = dict(zip(free, variables[:-4]))
    columns = [kernel]
    for i, pivot in enumerate(pivots):
        entries = {slot: values.get((i, j), algebra(int(j == pivot)))
                   for j, slot in enumerate(SLOTS)}
        entries[0, 3] = -entries[1, 3] - entries[2, 3]
        columns.append(tangent_direction(entries[slot] for slot in COORDINATES))
    coefficients = pencil_coefficients(algebra, columns)
    equations = [value for (i, j, k), value in coefficients.items()
                 if i + j + k >= 2 and j + k <= 2]
    if exceptional:
        assert pivots == (2,)
        row = columns[1]
        for vertex, opposite in ((0, (1, 3)), (1, (0, 3))):
            equations.append(incident(kernel, vertex)*row[opposite]
                             - kernel[opposite]*incident(row, vertex))
    return names, equations


def verify_boundary(executable):
    """Check all five one-vector cells and the residual symmetry exception."""
    cases = [((i,), False) for i in range(3, 8)] + [((2,), True)]
    with TemporaryDirectory() as path:
        source = Path(path) / "cell.ms"
        result = Path(path) / "basis.out"
        for pivots, exceptional in cases:
            names, equations = chart_system(pivots, exceptional=exceptional)
            with source.open("w") as stream:
                write_msolve_system(names, equations, stream)
            result.unlink(missing_ok=True)
            subprocess.run([executable, "-f", str(source), "-o", str(result),
                            "-t", "1", "-g", "2", "-l", "2"], check=True)
            header, sep, body = result.read_text().partition("[")
            if not sep or "#Reduced Groebner basis data" not in header or body.strip() != "1]:":
                raise AssertionError(f"expected a unit basis for {pivots}, exceptional={exceptional}")
    print("All five projection cells and the symmetry exception have unit Gröbner basis.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--emit", action="store_true", help="emit the remaining chart in msolve format")
    mode.add_argument("--verify-boundary", metavar="MSOLVE", help="replay the six exact boundary exclusions")
    args = parser.parse_args()
    if args.emit:
        names, equations = chart_system((0, 1))
        assert len(names) == 16 and len(equations) == 18
        write_msolve_system(names, equations, sys.stdout)
    else:
        verify_boundary(args.verify_boundary)
