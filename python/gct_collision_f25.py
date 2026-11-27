"""Exclude geometric completions of every corrected-kernel line defined over F25."""

import argparse
from collections import Counter

import numpy as np

from gct_collision_direction import rational_level_lines, relabelings
from gct_collision_f25_companion import companion_certificate
from gct_collision_kernel_reduction import first_variations
from gct_collision_quadrics import LINE_CELL_REPRESENTATIVES, net_singularity_ranks, verify_no_common_lines
from gct_collision_slice import verify_quadratic_slice
from gct_permanent_frobenius import extension_tables


def evaluate_batch(polynomial, coordinates, add, multiply):
    """Evaluate a sparse F5 polynomial on columns of field-encoded coordinates."""
    powers = []
    for column, max_power in zip(coordinates, polynomial.degrees()):
        column_powers = [1, column]
        for _ in range(2, max_power + 1):
            column_powers.append(multiply[column_powers[-1], column])
        powers.append(column_powers)
    result = np.zeros(coordinates.shape[1], dtype=np.uint8)
    for exponents, coeff in polynomial.items():
        term = int(coeff) % 5
        for i, n in enumerate(exponents):
            if n:
                term = multiply[term, powers[i][n]]
        result = add[result, term]
    return result


def normalized_directions(add, multiply):
    """Test all five free kernel edges with edge 01 normalized to one."""
    pure, _ = first_variations()
    suffixes = np.indices((25,) * 4, dtype=np.uint8).reshape(4, -1)
    directions = set()
    for b02 in range(25):
        coordinates = np.vstack((np.full(suffixes.shape[1], b02, dtype=np.uint8), suffixes))
        for polynomial in pure:
            values = evaluate_batch(polynomial, coordinates, add, multiply)
            coordinates = coordinates[:, values == 0]
        directions.update((1, *map(int, values)) for values in coordinates.T)
    return directions


def projective_orbits(directions, multiply, frobenius):
    """Group all projective lines under vertex relabeling and fifth power."""
    inverse = np.argmax(multiply == 1, axis=1)
    remaining = set(directions)
    orbits = []
    while remaining:
        line = min(remaining)
        orbit = set()
        for image in relabelings(line):
            scale = inverse[next(x for x in image if x)]
            normalized = tuple(int(multiply[scale, x]) for x in image)
            orbit.add(normalized)
            orbit.add(tuple(int(frobenius[x]) for x in normalized))
        in_chart = {point for point in orbit if point[0] == 1}
        assert in_chart <= remaining
        remaining -= in_chart
        orbits.append(orbit)
    return orbits


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-lines", metavar="MSOLVE", help="also replay the 40 common-line Gröbner bases")
    args = parser.parse_args()
    _, _, add, multiply, frobenius = extension_tables((3, 0))
    directions = normalized_directions(add.astype(np.uint8), multiply.astype(np.uint8))
    orbits = projective_orbits(directions, multiply, frobenius)
    lines = set().union(*orbits)
    assert {p for p in lines if all(v < 5 for v in p)} == rational_level_lines()
    assert len(directions) == 904 and len(lines) == 964 and len(orbits) == 31
    quadratic_ranks, companion_ranks = Counter(), Counter()
    line_cell_representatives = set()
    for orbit in orbits:
        sample = min(p for p in orbit if p[0] == 1)
        rank, = net_singularity_ranks(sample, degrees=(9,))
        quadratic_ranks[rank] += 1
        if rank <= 52:
            line_cell_representatives.add(sample)
        certificate = companion_certificate(sample, star_index=1)
        assert certificate is not None and certificate.kind == "degree-four", sample
        companion_ranks[certificate.rank] += 1
    assert quadratic_ranks == {54: 25, 53: 2, 52: 1, 50: 1, 49: 1, 48: 1}
    assert line_cell_representatives == set(LINE_CELL_REPRESENTATIVES)
    assert companion_ranks == {35: 30, 34: 1}
    if args.verify_lines:
        verify_no_common_lines(args.verify_lines)
        print("The remaining four quadratic cases have unit ideal on all ten line cells each.")
    points = verify_quadratic_slice(lines, add, multiply)
    print(f"{len(directions)} lines in the normalized chart, {len(lines)} projective lines")
    print("Orbit sizes and counts:", sorted(Counter(map(len, orbits)).items()))
    print("Degree-nine quadratic-net ranks:", sorted(quadratic_ranks.items()))
    print("Degree-four companion identities by matrix rank:", sorted(companion_ranks.items()))
    print(f"The projective three-space slice has length {len(points)}, exhausted by distinct census points.")


if __name__ == "__main__":
    main()
