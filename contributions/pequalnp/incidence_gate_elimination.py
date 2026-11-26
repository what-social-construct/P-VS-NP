"""Check the L-meta-18649 gate savings on two explicit incidence circuits.

Wire functions are evaluated as antichains of minimal true input sets,
encoded as bit masks.
The restricted circuits produced here are certificates of upper bounds.
"""

from collections import Counter
from dataclasses import dataclass


SIDE_SIZE = 13
POINTS = range(SIDE_SIZE)
LINES = range(SIDE_SIZE, 2 * SIDE_SIZE)
INPUTS = 2 * SIDE_SIZE
EDGES = tuple(
    (point, line)
    for point in POINTS
    for line in LINES
    if (point + line - SIDE_SIZE) % SIDE_SIZE in {0, 1, 3, 9}
)
FALSE = frozenset()
TRUE = frozenset({0})


@dataclass(frozen=True)
class Circuit:
    gates: tuple[tuple[str, int, int], ...]
    output: int


def cover_circuit(edges, cover, free=()):
    """Factor each edge at its endpoint in the chosen side of the graph."""
    neighbors = {vertex: [] for vertex in cover}
    for left, right in edges:
        if left in neighbors:
            neighbors[left].append(right)
        else:
            neighbors[right].append(left)

    gates = []

    def add(op, left, right):
        gates.append((op, left, right))
        return INPUTS + len(gates) - 1

    def disjoin(wires):
        first, *rest = wires
        for wire in rest:
            first = add("or", first, wire)
        return first

    terms = list(free)
    for vertex, adjacent in neighbors.items():
        if adjacent:
            terms.append(add("and", vertex, disjoin(adjacent)))
    output = disjoin(terms)
    return Circuit(tuple(gates), output)


def antichain(terms):
    minimal = []
    # Every proper subset of a mask is a smaller integer.
    for term in sorted(set(terms)):
        if not any((other & term) == other for other in minimal):
            minimal.append(term)
    return frozenset(minimal)


def wire_functions(circuit, fixed=None):
    wires = [frozenset({1 << vertex}) for vertex in range(INPUTS)]
    if fixed is not None:
        vertex, value = fixed
        wires[vertex] = TRUE if value else FALSE
    for op, left, right in circuit.gates:
        first, second = wires[left], wires[right]
        if op == "and":
            wires.append(antichain(a | b for a in first for b in second))
        else:
            wires.append(antichain(first | second))
    return wires


def prune(circuit, fixed, wires):
    """Build the shortened circuit for a nonconstant restricted output."""
    constant = {wire for wire, terms in enumerate(wires) if terms in (FALSE, TRUE)}
    readers = [[] for _ in wires]
    eliminate = set()
    for wire, (_, left, right) in enumerate(circuit.gates, INPUTS):
        readers[left].append(wire)
        readers[right].append(wire)
        if wire in constant or left in constant or right in constant:
            eliminate.add(wire)

    prunable = set()
    for wire in range(len(wires) - 1, INPUTS - 1, -1):
        if wire == circuit.output or wire in eliminate:
            continue
        if all(reader in prunable or reader in constant for reader in readers[wire]):
            prunable.add(wire)

    fixed_vertex, _ = fixed
    remap = {vertex: vertex for vertex in range(INPUTS) if vertex != fixed_vertex}
    gates = []
    for wire, (op, left, right) in enumerate(circuit.gates, INPUTS):
        if wire in constant or wire in prunable:
            continue
        if wire in eliminate:
            # This gate is nonconstant, so the constant argument is neutral.
            remap[wire] = remap[right if left in constant else left]
        else:
            remap[wire] = INPUTS + len(gates)
            gates.append((op, remap[left], remap[right]))
    assert len(gates) == len(circuit.gates) - len(eliminate) - len(prunable)
    return Circuit(tuple(gates), remap[circuit.output]), len(eliminate), len(prunable)


def monomials(edges, free=()):
    return frozenset(
        [(1 << left) | (1 << right) for left, right in edges]
        + [1 << vertex for vertex in free]
    )


def run():
    assert len(EDGES) == 52
    restricted = {}
    for side in (POINTS, LINES):
        other_side = LINES if side == POINTS else POINTS
        for vertex in side:
            neighbors = sorted(
                right if left == vertex else left
                for left, right in EDGES
                if vertex in (left, right)
            )
            for value in (0, 1):
                free = neighbors if value else []
                removed = {vertex, *free}
                edges = [edge for edge in EDGES if removed.isdisjoint(edge)]
                cover = [v for v in (other_side if value else side) if v not in removed]
                bound = cover_circuit(edges, cover, free)
                expected = monomials(edges, free)
                assert wire_functions(bound)[bound.output] == expected
                assert (len(edges), len(free), len(bound.gates)) == (
                    (36, 4, 48) if value else (48, 0, 59)
                )
                restricted[vertex, value] = expected

    print("Input fixed to 0: 48 edges and a 59-gate cover construction.")
    print("Input fixed to 1: 36 edges, 4 singleton terms and a 48-gate cover construction.")
    print("Factor side | fixed input | value | K | P | gates left | vertices")
    for factor_name, cover in (("point", POINTS), ("line", LINES)):
        circuit = cover_circuit(EDGES, cover)
        assert len(circuit.gates) == 64
        assert wire_functions(circuit)[circuit.output] == monomials(EDGES)
        for side_name, side in (("point", POINTS), ("line", LINES)):
            for value in (0, 1):
                counts = Counter()
                for vertex in side:
                    fixed = vertex, value
                    wires = wire_functions(circuit, fixed)
                    expected = restricted[fixed]
                    assert wires[circuit.output] == expected
                    shorter, k, p = prune(circuit, fixed, wires)
                    assert wire_functions(shorter)[shorter.output] == expected
                    counts[k, p, len(shorter.gates)] += 1
                for (k, p, gates), vertices in sorted(counts.items()):
                    print(f"{factor_name:>11} | {side_name:>11} | {value:>5} | "
                          f"{k:>2} | {p:>2} | {gates:>10} | {vertices:>8}")


if __name__ == "__main__":
    run()
