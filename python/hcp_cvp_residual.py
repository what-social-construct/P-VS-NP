"""Exact Paper 1 calculations at the decoded cochain boundary.

The fresh-sign profile and the diagonal Gram formula come from Paper 1's
coupled encryption and CVP sections. Its original Lean proofs are in lean/HCP.
"""

from dataclasses import dataclass
from fractions import Fraction


def _dot(left, right):
    return sum(a * b for a, b in zip(left, right))


@dataclass(frozen=True)
class ClosestVector:
    center: tuple
    coefficients: tuple
    point: tuple
    hodge_residual_squared: Fraction
    coefficient_error_squared: Fraction
    hodge_residual: tuple = ()

    @property
    def squared_distance(self):
        return self.hodge_residual_squared + self.coefficient_error_squared


class FreshSignProfile:
    """A public integer matrix with A^T A = d I, d > 0."""

    def __init__(self, matrix, scale, expected_exact):
        self.matrix = tuple(tuple(row) for row in matrix)
        self.width = len(self.matrix[0]) if self.matrix else 0
        if type(scale) is not int or scale <= 0 or type(expected_exact) is not int:
            raise ValueError("expected a positive integer scale and an integer exact coordinate")
        if any(
            len(row) != self.width or any(type(entry) is not int for entry in row)
            for row in self.matrix
        ):
            raise ValueError("expected a rectangular integer matrix")
        self.columns = tuple(zip(*self.matrix))
        for i, column in enumerate(self.columns):
            for j in range(i + 1):
                if _dot(column, self.columns[j]) != (scale if i == j else 0):
                    raise ValueError("public matrix must satisfy A^T A = scale * I")
        self.scale = scale
        self.expected_exact = expected_exact

    def mask_bits(self, cochain):
        """Decode the public mask, using 1 for a negative product of signs."""
        exact, information, parity = cochain
        information, parity = tuple(information), tuple(parity)
        if (
            exact != self.expected_exact
            or len(information) != self.width
            or len(parity) != len(self.matrix)
            or any(type(entry) is not int for entry in (exact, *information, *parity))
            or any(information)
        ):
            return None

        denominator = self.scale * (self.scale + 1)
        dots = tuple(_dot(column, parity) for column in self.columns)
        if any(abs(dot) != denominator for dot in dots):
            return None
        mask_signs = tuple(1 if dot > 0 else -1 for dot in dots)
        if any(
            (self.scale + 1) * _dot(row, mask_signs) != value
            for row, value in zip(self.matrix, parity)
        ):
            return None
        return tuple(int(sign < 0) for sign in mask_signs)

    def closest_vector(self, key, target):
        """Minimize exact squared distance in the supplied sign-key lattice.

        Accepts a rational target (exact, information, parity). Ties round to
        even in each coefficient. A key bit of 1 represents the positive sign.
        """
        key = tuple(key)
        if len(key) != self.width or any(
            type(bit) not in (int, bool) or bit not in (0, 1) for bit in key
        ):
            raise ValueError("expected one bit per lattice column")
        exact, information, parity = target
        information, parity = tuple(information), tuple(parity)
        if len(information) != self.width or len(parity) != len(self.matrix):
            raise ValueError("target and lattice dimensions differ")
        if any(type(value) not in (int, Fraction) for value in (exact, *information, *parity)):
            raise ValueError("expected exact rational target coordinates")

        signs = tuple(2 * bit - 1 for bit in key)
        gram = self.scale + 1
        center = tuple(
            Fraction(x + sign * _dot(column, parity), gram)
            for x, sign, column in zip(information, signs, self.columns)
        )
        coefficients = tuple(round(value) for value in center)
        signed_center = tuple(sign * value for sign, value in zip(signs, center))
        signed_coefficients = tuple(sign * value for sign, value in zip(signs, coefficients))
        projection = tuple(_dot(row, signed_center) for row in self.matrix)
        point = (0, coefficients, tuple(_dot(row, signed_coefficients) for row in self.matrix))
        residual = (
            Fraction(exact),
            tuple(x - value for x, value in zip(information, center)),
            tuple(y - value for y, value in zip(parity, projection)),
        )
        residual_squared = sum(value ** 2 for value in (residual[0], *residual[1], *residual[2]))
        coefficient_error = gram * sum((x - value) ** 2 for x, value in zip(center, coefficients))
        return ClosestVector(
            center, coefficients, point, residual_squared, Fraction(coefficient_error), residual
        )
