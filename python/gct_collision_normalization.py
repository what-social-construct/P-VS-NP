"""Check the critical jet that determines the genus of the pure degree-24 curve."""

from fractions import Fraction

import sympy as sp
from sympy.polys.agca.extensions import MonogenicFiniteExtension
from sympy.polys.rings import ring

from gct_collision_f25 import normalization_frobenius_prefix, pure_curve_point_counts
from gct_collision_fiber_slice import check_singular_points, pure_equations
from gct_collision_kernel_reduction import determinant


def check_critical_jet():
    algebra, a, b, c, d = ring("a,b,c,d", sp.GF(5))
    q2, q3, q4 = pure_equations(algebra, a, b, c, d)
    polar = determinant([[f.diff(x) for f in (q2, q4, q3)] for x in (a, b, c)])
    surface_minor = q2.diff(a)*q4.diff(b) - q2.diff(b)*q4.diff(a)
    critical_minor = determinant([[f.diff(x) for f in (q2, q4, polar)] for x in (a, b, c)])

    symbol = sp.Symbol("s")
    field = MonogenicFiniteExtension(sp.Poly(symbol**2 + symbol + 1, symbol, modulus=5))
    s = field.generator
    jets, t = ring("t", field)
    modulus = [t**7]
    # Proposed coefficients through degree six of a, b-s, and c, with d=1+t.
    coefficients = (
        (1, 1, 0, 2, 0, -2),
        (2, s-2, -2*s-1, 2-s, 2-s, 2-s),
        (s, 2-s, 2-s, 2*s+1, -2*s-1, s-2),
    )
    av, bv, cv = [sum((jets(x)*t**i for i, x in enumerate(row, 1)), jets.zero)
                  for row in coefficients]
    coordinates = (av, jets(s)+bv, cv, 1+t)
    polynomials = (q2, q4, polar, q3, surface_minor, critical_minor)
    powers = []
    for i, coordinate in enumerate(coordinates):
        table = [jets.one]
        for _ in range(max(f.degree(i) for f in polynomials)):
            table.append((table[-1]*coordinate).rem(modulus))
        powers.append(table)

    def along_jet(f):
        value = jets.zero
        for exponents, coeff in f.items():
            term = jets(int(coeff))
            for table, exponent in zip(powers, exponents):
                term *= table[exponent]
            value += term
        return value.rem(modulus)

    assert all(along_jet(f) == 0 for f in (q2, q4, polar))
    assert along_jet(q3) == -2*t**6
    minor = along_jet(surface_minor)[(0,)]
    critical = along_jet(critical_minor)[(0,)]
    assert minor == -2*s-1 and critical == -field.one
    # Implicit differentiation gives F_cc = critical/minor² on the critical locus.
    assert critical/minor**2 == field(2)
    assert (2*s+1)**2 == field(2)


if __name__ == "__main__":
    check_singular_points()
    check_critical_jet()
    print("Critical value -2t^6 modulo t^7 at both conjugate singularities.")
    print("Two branches of contact three at each point. Normalization genus 49 - 2*3 = 43.")
    curve_counts = pure_curve_point_counts()
    assert curve_counts == (18, 64)
    counts, traces, prefix = normalization_frobenius_prefix(curve_counts, (0, 2), (0, 4))
    assert (counts, traces, prefix) == ((18, 66), (-12, -40), (1, 12, 92))
    print(f"Smooth point counts {counts}, Frobenius traces {traces}, zeta numerator prefix {prefix}.")
    genus = 49 - 2*3
    cross_coefficient = Fraction(traces[0], genus)
    degree_difference = 1 - cross_coefficient + 5
    assert degree_difference == Fraction(270, 43)
    print(f"Q_H(Frobenius - identity) = {degree_difference}.")
