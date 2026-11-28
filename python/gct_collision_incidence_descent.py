"""Recover an ordered permanent frame from a line in the invariant net at five."""

from itertools import combinations, combinations_with_replacement, permutations, product
from typing import NamedTuple

import sympy as sp
from sympy.polys.agca.extensions import MonogenicFiniteExtension
from sympy.polys.rings import ring

from gct_collision_face import (descended_net, interpolated_tangent, ordered_kernel,
                                residual_system, specialization_polars)
from gct_collision_kernel_reduction import evaluate
from gct_collision_ordering_fibers import ordering_factors
from gct_collision_fiber_net import polar_sextic_inverse
from gct_collision_quadrics import common_line_form_cells, line_frame, quadratic_field
from gct_common_line_witness import (
    LineWitness, common_line_witness, extension_of_degree, field_elements, horner, verifies_line,
)
from gct_permanent_plucker import PERMUTATIONS, pencil_coefficients


LEVEL_SAMPLES = tuple(point for v in range(4)
                      for point in ((0, 1, v), (0, -1, -v), (1, 1, v))) + ((0, 1, 4),)


class OrderedLineWitness(NamedTuple):
    field: object
    coefficient_root: object
    roots: tuple
    frame: tuple

    def is_level(self):
        """Test whether this recovered common line lifts to a level three-plane."""
        return not any(level_residual_values(self.frame, self.field))


def level_residual_values(frame, field):
    """Evaluate per(J+sB+tX+uY)-per(J) after the quadratic-stage check.

    On a frame from ordered_line_frame all 13 values vanish exactly when
    its plane is level. An arbitrary frame may still have lower-degree terms.
    """
    if field.characteristic() != 5:
        raise ValueError("the thirteen-point test is defined in characteristic five")
    return _level_samples(frame, field.one)


def _level_samples(frame, one):
    base, x, y = frame
    residuals = []
    for s, t, u in LEVEL_SAMPLES:
        entries = {ij: one + s*base[ij] + t*x[ij] + u*y[ij] for ij in base}
        value = sum(sp.prod(entries[min(i, j), max(i, j)] for i, j in enumerate(order))
                    for order in PERMUTATIONS)
        residuals.append(value - 24*one)
    return tuple(residuals)


def embed(value, source, root, target):
    if isinstance(source, MonogenicFiniteExtension):
        return horner(source.convert(value).rep.to_list(), root, target)
    return target(int(value))


def _split_parameters(values, source):
    """Choose a coefficient embedding and order the three incident roots."""
    relative = ordering_factors(source, values[0], values[1])[0]
    target = source if relative == 1 else extension_of_degree(getattr(source, "rank", 1)*relative)
    image = getattr(source, "generator", source.zero)
    if relative > 1:
        image = target.zero
        if isinstance(source, MonogenicFiniteExtension):
            modulus = source.modulus.all_coeffs()
            image = next(t for t in field_elements(target) if not horner(modulus, t, target))
        values = tuple(embed(a, source, image, target) for a in values)
    p, q, _, _ = values
    roots = []
    for a in field_elements(target):
        if a**3+p*a == q:
            roots.append(a)
            if len(roots) == 2:
                roots.append(-sum(roots))
                break
    if len(set(roots)) != 3 or any(a**3+p*a != q for a in roots):
        raise ArithmeticError("failed to split a separable incident cubic")
    return target, image, values, tuple(roots)


def split_witness_data(values, coefficients, witness):
    """Embed the net witness and its coefficient embedding into a cubic splitting field."""
    source = witness.field
    values = tuple(embed(a, coefficients, witness.coefficient_root, source) for a in values)
    target, image, values, roots = _split_parameters(values, source)
    rows, root = witness.rows, witness.coefficient_root
    if target != source:
        rows = [[embed(a, source, image, target) for a in row] for row in rows]
        root = embed(root, source, image, target)
    return target, root, values, roots, rows


def _pure_parameters(values, field):
    if field != sp.GF(5) and not (isinstance(field, MonogenicFiniteExtension) and
                                 field.domain == sp.GF(5) and field.modulus.is_irreducible):
        raise ValueError("expected F5 or a simple finite extension of F5")
    values = tuple(field.convert(a) for a in values)
    p, q, _, _ = values
    if -4*p**3-27*q**2 == field.zero:
        raise ValueError("the incident cubic must be separable")
    symbols, equations = residual_system()
    algebra, *_ = ring(symbols, sp.GF(5))
    if any(evaluate(algebra.from_expr(f), values) for f in equations):
        raise ValueError("invariant parameters fail the pure permanent equations")
    return values


def find_ordered_line(values, field):
    """Search a pure w=1 quotient point for geometric quadratic line incidence.

    The result contains a chosen coefficient embedding, ordered roots, and
    the three original matrices over a finite extension. None certifies an
    empty geometric fiber. Field enumeration and chart search have no
    polynomial bit-cost bound here.
    """
    values = _pure_parameters(values, field)
    _, forms = descended_net(specialization_polars(), values, field)
    witness = common_line_witness(forms, field)
    if witness is None:
        return None
    target, root, parameters, roots, rows = split_witness_data(values, field, witness)
    frame = ordered_line_frame(parameters, roots, rows, target)
    return OrderedLineWitness(target, root, roots, frame)


def lift_row(row, inclusion):
    """Send a polar-kernel row to the eight interpolation coordinates."""
    return [sum(a*b for a, b in zip(row, column)) for column in zip(*inclusion)]


def _matrix_in_span(row, directions):
    return {ij: sum(a*d[ij] for a, d in zip(row, directions)) for ij in directions[0]}


def _has_level_line(forms, field, base, directions):
    """Test the joint ideals on all ten geometric RREF cells of the polar net."""
    for pivots, _, equations in common_line_form_cells(forms, field):
        algebra = equations[0].ring
        gram = sp.groebner([f.as_expr() for f in equations], *algebra.symbols,
                           modulus=5, order="grevlex")
        if list(gram) == [1]:
            continue
        # The last variable presents the coefficient field modulo its defining polynomial.
        def lift(matrix):
            return {ij: embed(c, field, algebra.gens[-1], algebra) for ij, c in matrix.items()}

        rows = line_frame(pivots, algebra.gens[:-1], algebra.one, algebra.zero)
        lifted = [lift(d) for d in directions]
        frame = [lift(base), *(_matrix_in_span(row, lifted) for row in rows)]
        extra = [gram.reduce(f.as_expr())[1] for f in _level_samples(frame, algebra.one)]
        if not any(extra) or list(sp.groebner([*gram, *extra], *algebra.symbols,
                                              modulus=5, order="grevlex")) != [1]:
            return True
    return False


def level_three_plane_exists(values, field):
    """Decide whether any geometric level three-plane lies over a pure quotient point.

    The decision is over the algebraic closure. It gives no rationality or
    running-time bound. Testing one incident line would only decide its own lift.
    """
    values = _pure_parameters(values, field)
    polars = specialization_polars()
    inclusion, forms = descended_net(polars, values, field)
    if polar_sextic_inverse(forms, field) is not None:
        return False
    target, _, values, roots = _split_parameters(values, field)
    if target != field:
        inclusion, forms = descended_net(polars, values, target)
    base = ordered_kernel(roots, *values[2:])
    directions = [interpolated_tangent(roots, slots) for slots in inclusion]
    return _has_level_line(forms, target, base, directions)


def ordered_line_frame(values, roots, rows, field):
    """Return B,X,Y for a verified common line, in the original symmetric matrices.

    Supply p,q,u,v, all three ordered cubic roots, and the two rows returned
    by the net's line search using compatible embeddings into one field.
    The output uses the incident-linear-coefficient gauge on X and Y.
    """
    if field.characteristic() != 5:
        raise ValueError("the incidence chart is defined in characteristic five")
    p, q, u, v = (field.convert(a) for a in values)
    roots = tuple(field.convert(a) for a in roots)
    if len(roots) != 3 or len(set(roots)) != 3 or any(r**3+p*r != q for r in roots):
        raise ValueError("supply three distinct ordered roots of the incident cubic")
    rows = [[field.convert(a) for a in row] for row in rows]
    if len(rows) != 2 or any(len(row) != 5 for row in rows):
        raise ValueError("supply two rows in the five-dimensional net")
    x, y = rows
    if not any(x[i]*y[j] != x[j]*y[i] for i, j in combinations(range(5), 2)):
        raise ValueError("the line frame has dependent rows")

    inclusion, _ = descended_net(specialization_polars(), (p, q, u, v), field)
    frame = (ordered_kernel(roots, u, v),
             *(interpolated_tangent(roots, lift_row(row, inclusion)) for row in rows))
    constants, _ = ring("c", field)
    coefficients = pencil_coefficients(constants, [
        {slot: constants(entry) for slot, entry in matrix.items()} for matrix in frame])
    if any(j+k <= 2 for _, j, k in coefficients):
        raise ValueError("frame fails the original pure, polar, or quadratic permanent equations")
    return frame


def check_transport():
    """Compare all polar and quadratic coefficients for an actual nonsplit cubic."""
    field = quadratic_field()
    p, q, u, v = (field(4) for _ in range(4))
    elements = [field(i)+j*field.generator for i, j in product(range(5), repeat=2)]
    roots = tuple(r for r in elements if r**3+p*r == q)
    assert len(roots) == 3 and sum(r**5 == r for r in roots) == 1
    inclusion, forms = descended_net(specialization_polars(), (p, q, u, v), field)

    # The first five variables form a general vector in the descended net.
    # The sixth adds an arbitrary multiple of B to its tangent representative.
    algebra, *variables = ring("h0,h1,h2,h3,h4,g", field)
    row, gauge = variables[:5], variables[5]
    slots = lift_row(row, inclusion)
    expected = [sum(row[i]*row[j]*gram[i][j] for i, j in product(range(5), repeat=2))
                for gram in forms]
    base = ordered_kernel(roots, u, v)
    tangent = interpolated_tangent(roots, slots)
    coeffs = pencil_coefficients(algebra, [
        {slot: algebra(entry) for slot, entry in base.items()},
        {slot: entry+gauge*base[slot] for slot, entry in tangent.items()}])
    assert all(j >= 2 for _, j, _ in coeffs)
    assert [coeffs.get((i, 2, 0), algebra.zero) for i in range(3)] == expected

    # Reordering the roots permutes the original matrix rows and columns.
    vertices = (0, 1, 3)
    for order in permutations(range(3)):
        perm = {**dict(zip(vertices, (vertices[i] for i in order))), 2: 2}
        ordered = tuple(roots[i] for i in order)
        matrices = (ordered_kernel(ordered, u, v), interpolated_tangent(ordered, slots))
        for reference, matrix in zip((base, tangent), matrices):
            assert all(entry == reference[tuple(sorted((perm[i], perm[j])))]
                       for (i, j), entry in matrix.items())
    assert find_ordered_line((4, 4, 4, 4), sp.GF(5)) is None
    print("Verified the three complete quadratic forms on the polar kernel of (4,4,4,4),")
    print("including arbitrary gauge shifts and all six orderings of the cubic roots.")


def check_extension_transport():
    """Check a known positive net whose chosen labeling needs a further extension."""
    field = quadratic_field()
    omega = field.generator
    forms = [sp.diag(*entries).tolist() for entries in
             ((2, 1, 0, 0, 0), (0, 0, -2, 1, 0), (0, 0, 0, 0, 1))]
    forms[0][0][1] = forms[0][1][0] = -omega
    witness = common_line_witness(forms, field, field)
    assert witness is not None
    # This test pairs the control net with T*(T²-omega). Its nonzero roots
    # exist first over F625. It is separate from the pure permanent chart.
    values = (-omega, field.zero, field.zero, field.zero)
    target, root, parameters, roots, rows = split_witness_data(values, field, witness)
    assert target.rank == 4 and parameters[0] == -root and root**2 == target(2)
    assert len(set(roots)) == 3 and all(r**3-root*r == target.zero for r in roots)
    assert verifies_line(forms, field, LineWitness(target, root, rows))
    print("Verified the transported F25 control frame and ordered cubic roots over F625.")


def check_level_residual_values():
    # After the quadratic-stage equations, the only possible terms are the
    # two binary cubics (without/with s) and the binary quartic.
    powers = [(i, degree-k, k) for i, degree in ((0, 3), (1, 3), (0, 4))
              for k in range(degree+1)]
    evaluation = sp.Matrix([[s**i*t**j*u**k for i, j, k in powers]
                            for s, t, u in LEVEL_SAMPLES])
    assert evaluation.det() % 5 != 0

    # A level two-plane of symmetric stars gives a rank-two positive
    # control. A separate diagonal direction gives a pure quartic residual.
    field = sp.GF(5)
    slots = tuple(combinations_with_replacement(range(4), 2))
    x = {ij: field({(0, 1): 1, (0, 2): -1}.get(ij, 0)) for ij in slots}
    y = {ij: field({(0, 2): 1, (0, 3): -1}.get(ij, 0)) for ij in slots}
    diagonal = {ij: field((1, -1, 2, -2)[ij[0]] if ij[0] == ij[1] else 0)
                for ij in slots}
    zero = dict.fromkeys(slots, field.zero)
    constants, _ = ring("c", field)
    for frame, expected in (((zero, x, y), {}), ((zero, zero, diagonal), {(0, 0, 4): 4})):
        coefficients = pencil_coefficients(constants, [
            {ij: constants(a) for ij, a in direction.items()} for direction in frame])
        assert coefficients == {power: constants(a) for power, a in expected.items()}
        assert level_residual_values(frame, field) == tuple(
            sum((a*s**i*t**j*u**k for (i, j, k), a in expected.items()), field.zero)
            for s, t, u in LEVEL_SAMPLES)
    print("Verified the invertible 13-point permanent test and the level and quartic controls.")


def check_level_existence():
    field = sp.GF(5)
    assert not level_three_plane_exists((4, 4, 4, 4), field)

    # Four geometric lines, with independent choices of two signs. Map the
    # first two net coordinates to multiples of a pure-quartic diagonal.
    # This synthetic map distinguishes the signs without using a face witness.
    forms = [sp.diag(*q).tolist() for q in
             ((-1, 1, 0, 0, 0), (0, 0, -1, 1, 0), (0, 0, 0, 0, 1))]
    first = common_line_witness(forms, field, field)
    x, y = first.rows
    assert x[0] == field.one and x[1]**2 == field.one
    slots = tuple(combinations_with_replacement(range(4), 2))
    diagonal = {ij: field((1, -1, 2, -2)[ij[0]] if ij[0] == ij[1] else 0) for ij in slots}
    zero = dict.fromkeys(slots, field.zero)
    scaled = {ij: x[1]*a for ij, a in diagonal.items()}
    directions = [scaled, diagonal, zero, zero, zero]
    frame = [zero, _matrix_in_span(x, directions), _matrix_in_span(y, directions)]
    assert any(level_residual_values(frame, field))
    assert _has_level_line(forms, field, zero, directions)
    assert not _has_level_line(forms, field, zero, [diagonal, zero, zero, zero, zero])
    print("Verified geometric level existence on a four-line control and an empty face fiber.")


if __name__ == "__main__":
    check_transport()
    check_extension_transport()
    check_level_residual_values()
    check_level_existence()
