"""Replay a degree-six zero of the auxiliary-free common-line resultant at five."""

import sympy as sp
from sympy.polys.agca.extensions import MonogenicFiniteExtension
from sympy.polys.matrices import DomainMatrix
from sympy.polys.rings import ring

from gct_collision_face import generic_lift, opposite_edge_product, residual_system, specialization_polars
from gct_collision_fiber_net import polar_sextic_certificate
from gct_collision_kernel_reduction import determinant, evaluate
from gct_collision_line_divisor_slopes import adapted_slope_net
from gct_collision_ordering_fibers import ordering_factors
from gct_collision_pencil_orbits import pencil_orbit_product
from gct_collision_polar_extension import polar_kernel_line
from gct_collision_subresultant import monic_gcd


def decode(field, integer):
    """Read the base-five digits as coefficients in the specified power basis."""
    assert 0 <= integer < 5**field.rank
    value = field.zero
    for i in range(field.rank):
        integer, digit = divmod(integer, 5)
        value += digit * field.generator**i
    return value


def candidate_point():
    """Return the field and pure quotient parameters found by finite-field search."""
    t = sp.Symbol("t")
    modulus = sp.Poly(t**6+t**5+t**4+1, t, modulus=5)
    assert modulus.is_irreducible
    field = MonogenicFiniteExtension(modulus)
    values = tuple(decode(field, n) for n in (14790, 13475, 6884, 332))
    p, q, u, v = values
    assert all(v**(5**d) != v for d in (1, 2, 3))
    symbols, equations = residual_system()
    pure, *_ = ring(symbols, sp.GF(5))
    assert all(not evaluate(pure.from_expr(f), values) for f in equations)
    leading, _ = generic_lift()
    assert evaluate(leading, (u, v)) and u*(v-3)*q*(3*u-2*p)
    assert -4*p**3-27*q**2 and opposite_edge_product(*values)
    assert pencil_orbit_product(*values)
    return field, values


def check_residual_candidate():
    field, values = candidate_point()
    p, q, _, _ = values
    assert ordering_factors(field, p, q) == (2, 2, 2)
    grams = adapted_slope_net(field, values, specialization_polars())
    # The Q3 sextic inverse also certifies no points at infinity on H=0.
    # In particular B_D is a unit, so a zero of R here gives a zero of G.
    polar_sextic_certificate([grams[1], grams[0], grams[2]], field)

    # Separating-coordinate certificate of the eight points on H=0,D=1.
    # Each tuple gives coefficients in ascending powers of x.
    algebra, x = ring("x", field)

    def poly(words):
        return algebra.from_dict({(i,): decode(field, word) for i, word in enumerate(words)})

    equation = x**8 - poly((11706, 221, 2355, 7290, 7606, 9210, 10364, 9361))
    y = poly((4679, 13709, 13297, 10643, 4364, 2438, 14894, 5213))
    z = poly((12491, 8925, 1455, 205, 3701, 2246, 595, 8485))
    assert monic_gcd(equation, equation.diff(x)) == algebra.one
    # The third relative Frobenius fixes all eight points and the first
    # fixes two. The complete factor degrees over the residue field are 1,1,3,3.
    frobenius = x
    for orbit in range(1, 4):
        for _ in range(field.rank):
            frobenius = (frobenius**5).rem([equation])
        if orbit == 1:
            assert monic_gcd(equation, frobenius-x).degree() == 2
    assert frobenius == x
    point = (x, y, z, algebra.one, algebra.zero)
    forms = [[[algebra(c) for c in row] for row in gram] for gram in grams]

    def polar(form, vector):
        return [sum((a*b for a, b in zip(row, vector)), algebra.zero).rem([equation])
                for row in form]

    def pair(row, vector):
        return sum((a*b for a, b in zip(row, vector)), algebra.zero).rem([equation])

    polars = [polar(form, point) for form in forms]
    assert all(not pair(row, point) for row in polars)
    # D is the fourth coordinate, so cofactors along ker D use these slots.
    slots = (0, 1, 2, 4)
    columns = list(zip(*polars))
    cofactor = [algebra.zero] * 5
    for i, j in enumerate(slots):
        minor = determinant([columns[k] for k in slots if k != j])
        cofactor[j] = ((-1)**i * minor).rem([equation])
    sextics = [pair(polar(form, cofactor), cofactor) for form in forms]
    factors = [monic_gcd(equation, s) for s in sextics]
    root = decode(field, 2032)
    assert factors == [x-algebra(root), algebra.one, algebra.one]
    section_point = (root, decode(field, 6560), decode(field, 931), field.one, field.zero)
    assert y.rem([x-algebra(root)]) == algebra(section_point[1])
    assert z.rem([x-algebra(root)]) == algebra(section_point[2])
    assert polar_kernel_line(grams, section_point, field) is None
    print("Degree-six quotient point with B_D nonzero and G zero. The transverse section "
          "has residue degrees 1,1,3,3. The Q2 sextic vanishes at one residue-field point. "
          "The Q3 and Q4 sextics are units. The geometric common-line fiber is empty.")


def check_simple_zero():
    """Check transversality of the unique Q2 zero along the base curve."""
    field, parameters = candidate_point()
    base, pure = residual_system()
    p = base[0]
    x, y = sp.symbols("x:8"), sp.symbols("y:8")
    functions = specialization_polars()
    linear = [functions[i, 1] for i in (1, 2, 3)]
    quadrics = [functions[i, 2] for i in (0, 1, 2)]

    def at(poly, slots):
        return poly.as_expr().xreplace(dict(zip(poly.gens[4:], slots)))

    # x marks a point in the D=1, H=0 section. Choose its polar companion
    # y by fixing the o1 and o2 slots to (1,0). These two slots distinguish
    # x and y here because the o2 slot of x is nonzero.
    xy = tuple(a+b for a, b in zip(x, y))
    equations = [
        *pure, 3*x[0]-2*p*x[1], 3*x[5]-2*p*x[7]-1,
        *(at(f, x) for f in linear), *(at(f, x) for f in quadrics),
        *(at(f, y) for f in linear),
        *(at(f, xy)-at(f, x)-at(f, y) for f in quadrics),
        y[3]-1, y[4], at(quadrics[0], y),
    ]
    # Representatives in the eight interpolation coordinates of the net.
    section_point = (7923, 6969, 4864, 2032, 6560, 931, 11049, 643)
    companion = (11157, 11842, 1364, 1, 0, 1164, 2136, 1645)
    point = (*parameters, *(decode(field, n) for n in (*section_point, *companion)))
    variables = (*base, *x, *y)
    jacobian = sp.Matrix(equations).jacobian(variables)
    evaluate_all = sp.lambdify(variables, equations + list(jacobian), modules="math",
                               cse=True, docstring_limit=0)
    size = len(equations)
    assert len(variables) == size == 20
    entries = [field.convert(c) for c in evaluate_all(*point)]
    assert not any(entries[:size])
    rows = [entries[i:i+size] for i in range(size, len(entries), size)]
    assert DomainMatrix(rows, (size, size), field).rank() == size
    print("The marked Q2 zero has Jacobian rank 20, hence multiplicity one on the base.")


if __name__ == "__main__":
    check_residual_candidate()
    check_simple_zero()
