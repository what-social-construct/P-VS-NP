"""Affine consistency for prefixes of satisfying assignments to an explicit 2-CNF.

Literals are signed variable numbers starting at one. Variable order determines
the witness bits, including variables absent from the formula. Rows consist of
n binary coefficients followed by the right hand side.
"""

import argparse
import json

from affine_witness_selector import binary_affine_decomposition


def _reachable(graph, start):
    seen = {start}
    stack = [start]
    while stack:
        for target in graph[stack.pop()]:
            if target not in seen:
                seen.add(target)
                stack.append(target)
    return seen


class TwoCNF:
    def __init__(self, width, clauses):
        if type(width) is not int or width < 0:
            raise ValueError("expected a nonnegative number of variables")
        self.width = width
        self.clauses = tuple(tuple(clause) for clause in clauses)
        graph = {lit: [] for i in range(1, width + 1) for lit in (i, -i)}
        self._base_rows = [self._row((), 1)] if () in self.clauses else []
        for clause in self.clauses:
            if len(clause) > 2 or any(type(lit) is not int or lit not in graph for lit in clause):
                raise ValueError("expected at most two nonzero signed variable numbers per clause")
            if not clause:
                continue
            a, b = clause[0], clause[-1]
            graph[-a].append(b)
            graph[-b].append(a)

        self._reach = {lit: _reachable(graph, lit) for lit in graph}
        # Literal truth values agree inside each strongly connected component.
        for lit in graph:
            representative = min(v for v in self._reach[lit] if lit in self._reach[v])
            if lit != representative:
                self._base_rows.append(self._row((lit, representative), (lit < 0) ^ (representative < 0)))

    def _row(self, literals, rhs):
        coefficients = [0] * self.width
        for literal in literals:
            coefficients[abs(literal) - 1] ^= 1
        return (*coefficients, int(rhs))

    def prefix_rows(self, prefix):
        """Return an affine system consistent exactly when the prefix extends."""
        prefix = tuple(prefix)
        if len(prefix) > self.width or any(type(b) not in (int, bool) or b not in (0, 1) for b in prefix):
            raise ValueError("expected a binary prefix of length at most the number of variables")
        forced = set()
        for i, bit in enumerate(prefix, 1):
            forced.update(self._reach[i if bit else -i])
        return self._base_rows + [self._row((lit,), lit > 0) for lit in sorted(forced)]

    def prefix_extends(self, prefix):
        return binary_affine_decomposition(self.prefix_rows(prefix), self.width) is not None

    def select(self, prefix=()):
        """Recover the lexicographically first original model with this prefix."""
        prefix = tuple(prefix)
        if not self.prefix_extends(prefix):
            return None
        while len(prefix) < self.width:
            prefix += (0,) if self.prefix_extends(prefix + (0,)) else (1,)
        return prefix


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("width", type=int)
    parser.add_argument("clauses", type=json.loads, help='JSON array such as [[1,2],[-2,3]]')
    parser.add_argument("prefix", nargs="?", default="", help="initial bits in variable order")
    args = parser.parse_args()
    try:
        formula = TwoCNF(args.width, args.clauses)
        prefix = tuple(map(int, args.prefix))
        rows = formula.prefix_rows(prefix)
        witness = formula.select(prefix)
    except (TypeError, ValueError) as error:
        parser.error(str(error))
    print(json.dumps({"augmented_rows": rows, "witness": witness}))
