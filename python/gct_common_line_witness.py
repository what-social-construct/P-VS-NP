"""Recover a common line of three quadrics on P4 over finite extensions of F5."""

from dataclasses import dataclass
from itertools import combinations, count, product
from math import prod

import sympy as sp
from sympy.polys.agca.extensions import MonogenicFiniteExtension

from gct_collision_fiber_net import polar_sextic_inverse
from gct_collision_quadrics import checked_line_forms, common_line_form_cells, line_frame, quadratic_field


@dataclass
class LineWitness:
    field: object
    coefficient_root: object
    rows: list


def horner(coefficients, root, field):
    value = field.zero
    for coefficient in coefficients:
        value = value * root + field(int(coefficient))
    return value


def verifies_line(forms, coefficients, witness):
    """Check the coefficient embedding, row rank, and all nine Gram pairings."""
    field, root, rows = witness.field, witness.coefficient_root, witness.rows
    if len(rows) != 2 or any(len(row) != 5 for row in rows):
        return False
    if isinstance(coefficients, MonogenicFiniteExtension):
        if horner(coefficients.modulus.all_coeffs(), root, field):
            return False
    elif coefficients != sp.GF(5) or root != field.zero:
        return False
    if not any(rows[0][i]*rows[1][j] != rows[0][j]*rows[1][i] for i, j in combinations(range(5), 2)):
        return False
    for form in forms:
        if isinstance(coefficients, MonogenicFiniteExtension):
            matrix = [[horner(coefficients.convert(c).rep.to_list(), root, field) for c in row]
                      for row in form]
        else:
            matrix = [[field(int(c)) for c in row] for row in form]
        for x, y in ((rows[0], rows[0]), (rows[0], rows[1]), (rows[1], rows[1])):
            if sum((x[i]*matrix[i][j]*y[j] for i, j in product(range(5), repeat=2)), field.zero):
                return False
    return True


def extension_of_degree(degree):
    """Choose a monic irreducible deterministically in base five."""
    if degree == 1:
        return sp.GF(5)
    t = sp.Symbol("t")
    for suffix in product(range(5), repeat=degree):
        if suffix[-1]:
            f = sp.Poly.from_list([1, *suffix], t, modulus=5)
            if f.is_irreducible:
                return MonogenicFiniteExtension(f)
    raise AssertionError("no irreducible polynomial of the requested degree")


def field_elements(field):
    if isinstance(field, MonogenicFiniteExtension):
        for digits in product(range(5), repeat=field.rank):
            yield horner(digits, field.generator, field)
    else:
        yield from (field(i) for i in range(5))


def point_in_cell(basis, field, coefficient_root=None):
    """Search a named finite field, pruning prefixes using the lex basis."""
    size = len(basis.gens)
    tests = [[] for _ in range(size)]
    for polynomial in basis.polys:
        terms = [(field(int(c)), [(j, e) for j, e in enumerate(powers) if e])
                 for powers, c in polynomial.terms()]
        first = min(j for _, exponents in terms for j, _ in exponents)
        tests[first].append(terms)
    values = [field.zero] * size

    def evaluate(terms):
        return sum((c * prod((values[k]**e for k, e in exponents), start=field.one)
                    for c, exponents in terms), field.zero)

    def extend(j):
        if j < 0:
            return values.copy()
        candidates = ((coefficient_root,) if j == size-1 and coefficient_root is not None
                      else field_elements(field))
        for value in candidates:
            values[j] = value
            if any(evaluate(terms) for terms in tests[j]):
                continue
            solution = extend(j-1)
            if solution is not None:
                return solution
        return None

    return extend(size-1)


def common_line_witness(forms, coefficients, search_field=None):
    """Return a checked frame, or None for empty incidence.

    With a named F5 extension, None means no line over that field. Otherwise
    test geometric emptiness by the polar sextic and the cell ideals. A proper cell has a
    closed point over some finite extension, so increasing extension degrees
    eventually recovers a frame. No practical running-time bound is implied.
    The returned coefficient root specifies the embedding used for the frame.
    """
    forms = checked_line_forms(forms, coefficients)
    degree = getattr(coefficients, "rank", 1)
    if search_field is not None:
        if search_field != sp.GF(5) and not (
            isinstance(search_field, MonogenicFiniteExtension) and search_field.domain == sp.GF(5)
            and search_field.modulus.is_irreducible
        ):
            raise ValueError("expected a finite search field over F5")
        if getattr(search_field, "rank", 1) % degree:
            raise ValueError("search field must contain the coefficient field")
    if polar_sextic_inverse(forms, coefficients) is not None:
        return None
    for pivots, names, equations in common_line_form_cells(forms, coefficients):
        symbols = sp.symbols(names)
        basis = sp.groebner([f.as_expr() for f in equations], *symbols, modulus=5, order="lex")
        if list(basis) == [1]:
            continue
        fields = ((search_field,) if search_field is not None else
                  (coefficients if n == degree else extension_of_degree(n) for n in count(degree, degree)))
        for field in fields:
            root = coefficients.generator if field == coefficients and isinstance(
                coefficients, MonogenicFiniteExtension) else None
            point = point_in_cell(basis, field, root)
            if point is not None:
                rows = line_frame(pivots, point[:-1], field.one, field.zero)
                witness = LineWitness(field, point[-1], rows)
                if not verifies_line(forms, coefficients, witness):
                    raise ArithmeticError("recovered frame fails direct incidence verification")
                return witness
    return None


if __name__ == "__main__":
    # The signs of the two independent square roots determine four geometric lines.
    base = sp.GF(5)
    forms = [sp.diag(*diagonal).tolist() for diagonal in
             ((-2, 1, 0, 0, 0), (0, 0, -2, 1, 0), (0, 0, 0, 0, 1))]
    assert common_line_witness(forms, base, base) is None
    witness = common_line_witness(forms, base)
    assert witness.field.rank == 2
    print(f"No F5 line. Over {witness.field.modulus.as_expr()} = 0 the recovered rows are:")
    for row in witness.rows:
        print(tuple(map(str, row)))

    # A coefficient that genuinely depends on the residue-field generator.
    field = quadratic_field()
    forms[0][0][1] = forms[0][1][0] = field.generator
    forms[0][0][0] = field.generator**2
    witness = common_line_witness(forms, field, field)
    assert witness is not None
    print(f"Verified all nine pairings for the F25-coefficient control with root {witness.coefficient_root}.")
