"""Exclude the candidate divisor itself over every eligible F25-valued slope."""

from gct_collision_face import (
    descended_net, generic_lift, plane_resultant, prime_slope_points, specialization_polars,
)
from gct_collision_fiber_net import polar_sextic_certificate
from gct_collision_line_divisor import adapted_grams
from gct_collision_quadratic_slopes import quadratic_slope_points


def verify_slope_units(points, polars):
    degrees = []
    for field, values in points:
        p, _, u, _ = values
        # Both point enumerators check u, A, v-3, the cubic discriminant,
        # and all six edges. The final open condition is Y != 0.
        assert 3*u - 2*p
        inclusion, forms = descended_net(polars, values, field)
        # The incident roots sum to zero and their squares sum to -2p.
        # Therefore H = 3i0-2p i2 and D = 3d0-2p d2 in the gauge coordinates.
        incident = [3*row[0] - 2*p*row[1] for row in inclusion]
        diagonal = [3*row[5] - 2*p*row[7] for row in inclusion]
        adapted = adapted_grams(forms, diagonal, incident, field)
        # This excludes infinity in H=0 and verifies an inverse of the
        # invariant sextic on the resulting length-eight D=1 section.
        polar_sextic_certificate(adapted, field)
        degrees.append(field.rank)
    return len(degrees), sum(degrees)


def check_line_divisor_slopes():
    polars = specialization_polars()
    prime = prime_slope_points(plane_resultant(), *generic_lift())
    prime_counts = verify_slope_units(prime, polars)
    quadratic_counts = verify_slope_units(quadratic_slope_points(), polars)
    assert prime_counts == (10, 41) and quadratic_counts == (30, 240)
    print("The common-line resultant is a unit at all 40 eligible closed points "
          "with slope in F25 (281 geometric quotient points).")


if __name__ == "__main__":
    check_line_divisor_slopes()
