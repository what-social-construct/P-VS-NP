"""Check the pencil center and full level companions on the characteristic-five face."""

import argparse
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

import sympy as sp
from sympy.polys.rings import ring

from gct_collision_line_divisor import invariant_covectors
from gct_collision_pencil_fiber import incident
from gct_collision_slice import face_edges, kernel_from_edges
from gct_permanent_plucker import OFF_DIAGONAL, pencil_coefficients, write_msolve_system


# Coordinates of a representative with H=m_3=0 and prescribed D.
FREE_SLOTS = ((0, 1), (1, 2), (1, 3), (2, 3), (1, 1), (3, 3))


def companion_coefficients(algebra, base_coordinates, coordinates, diagonal_sum):
    """Restrict the original permanent to B and the normalized representative X."""
    base = kernel_from_edges(face_edges(*base_coordinates))
    outer = (0, 1, 3)
    opposite_sum = base[0, 1] + base[0, 3] + base[1, 3]
    assert invariant_covectors(base) == (0, 0) and incident(base, 3) == 1
    assert sum(incident(base, i) for i in outer) == 2*opposite_sum

    x, y, z, w, e, f = coordinates
    tangent = dict(zip(OFF_DIAGONAL, face_edges(x, y, z, w, 0)))
    edge_sum = sum(tangent.values())
    tangent.update({(0, 0): diagonal_sum-e-f, (1, 1): e,
                    (2, 2): -diagonal_sum-2*edge_sum, (3, 3): f})
    assert [tangent[slot] for slot in FREE_SLOTS] == coordinates
    assert invariant_covectors(tangent) == (0, diagonal_sum) and incident(tangent, 3) == 0
    assert sum(tangent[i, i] for i in range(4)) + 2*edge_sum == 0

    return pencil_coefficients(algebra, (base, tangent))


def center_cell(pivot):
    """Pure moving base with m_3(B)=1, and first nonzero tangent coordinate set to 1."""
    if pivot not in range(len(FREE_SLOTS)):
        raise ValueError("expected a tangent pivot from 0 through 5")
    tangent_names = tuple(f"x{i}{j}" for i, j in FREE_SLOTS[pivot+1:])
    names = tangent_names + ("a", "b", "c", "d")
    algebra, *variables = ring(names, sp.GF(5), "grevlex")
    coordinates = [algebra.zero]*pivot + [algebra.one] + variables[:-4]
    coefficients = companion_coefficients(algebra, variables[-4:], coordinates, algebra.zero)
    # per(J+sB+tX): pure terms, first polars, quadrics and q_3(X).
    powers = [(i, 0) for i in (2, 3, 4)] + [(i, 1) for i in (1, 2, 3)]
    powers += [(i, 2) for i in (0, 1, 2)] + [(0, 3)]
    return names, [coefficients[i, j, 0] for i, j in powers if (i, j, 0) in coefficients]


def level_chart():
    """All nonconstant coefficients after imposing H(X)=m_3(X)=0 and D(X)=1."""
    names = ("X", "Y", "Z", "W", "E", "F", "a", "b", "c", "d")
    algebra, *variables = ring(names, sp.GF(5), "grevlex")
    coefficients = companion_coefficients(algebra, variables[-4:], variables[:-4], algebra.one)
    assert set(coefficients) == {(i, degree-i, 0) for degree in (2, 3, 4)
                                 for i in range(degree+1)}
    return names, list(coefficients.values())


def verify_unit_ideal(executable, system):
    with TemporaryDirectory() as directory:
        source = Path(directory) / "system.ms"
        result = source.with_suffix(".out")
        with source.open("w") as stream:
            write_msolve_system(*system, stream)
        subprocess.run([executable, "-f", str(source), "-o", str(result),
                        "-t", "1", "-g", "2", "-l", "2"], check=True)
        header, _, body = result.read_text().partition("[")
        if "#Reduced Groebner basis data" not in header or body.strip() != "1]:":
            raise AssertionError("the computed reduced Groebner basis is not [1]")


def verify_center(executable):
    for pivot in range(len(FREE_SLOTS)):
        verify_unit_ideal(executable, center_cell(pivot))
    print("Verified six unit ideals for the pencil center on the moving m3=1 face.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--verify", metavar="MSOLVE", help="verify all six cell ideals")
    mode.add_argument("--emit", type=int, choices=range(len(FREE_SLOTS)),
                      help="emit one cell in msolve format")
    mode.add_argument("--verify-level", metavar="MSOLVE", help="verify the D=1 level ideal")
    mode.add_argument("--emit-level", action="store_true", help="emit the D=1 level ideal")
    args = parser.parse_args()
    if args.verify:
        verify_center(args.verify)
    elif args.verify_level:
        verify_unit_ideal(args.verify_level, level_chart())
        print("Verified the unit ideal for H=0, D=1 full level companions on the moving m3=1 face.")
    elif args.emit_level:
        write_msolve_system(*level_chart(), sys.stdout)
    else:
        write_msolve_system(*center_cell(args.emit), sys.stdout)
