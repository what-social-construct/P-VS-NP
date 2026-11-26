"""Select a compatible witness for the decoded Paper 1 fresh-sign profile.

The input is the public integer matrix, its positive scale, the expected
exact coordinate and the decoded integer cochain. Optional constraints
are binary rows (key_coefficients, message_coefficients, rhs).
Key and message bits use 0 for the negative sign and 1 for the positive
sign. A mask bit marks a negative product of signs.
"""

from dataclasses import dataclass
from hcp_cvp_residual import FreshSignProfile


@dataclass(frozen=True)
class Witness:
    key: tuple
    message: tuple


@dataclass(frozen=True)
class WitnessFamily:
    selected: Witness
    kernel_basis: tuple

    @property
    def unique(self):
        return not self.kernel_basis

    @property
    def cardinality(self):
        return 1 << len(self.kernel_basis)

    def residual_collision(self):
        """Return one ordered pair of distinct witnesses, if it exists."""
        if self.unique:
            return None
        return self.selected, self.witness((1,) + (0,) * (len(self.kernel_basis) - 1))

    def witness(self, parameters):
        """Select any member from its coordinates in the affine family."""
        parameters = tuple(parameters)
        if len(parameters) != len(self.kernel_basis) or any(
            type(bit) not in (int, bool) or bit not in (0, 1) for bit in parameters
        ):
            raise ValueError("expected one bit per kernel basis vector")
        key = list(self.selected.key)
        message = list(self.selected.message)
        for bit, direction in zip(parameters, self.kernel_basis):
            if bit:
                for index, value in enumerate(direction):
                    key[index] ^= value
                    message[index] ^= value
        return Witness(tuple(key), tuple(message))


def _affine_decomposition(rows, width):
    """Return a particular solution and kernel basis, or None."""
    pivot_columns = []
    for column in range(width):
        rank = len(pivot_columns)
        pivot = next((i for i in range(rank, len(rows)) if rows[i][column]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for index, row in enumerate(rows):
            if index != rank and row[column]:
                rows[index] = [left ^ right for left, right in zip(row, rows[rank])]
        pivot_columns.append(column)
    if any(row[-1] for row in rows[len(pivot_columns):]):
        return None

    particular = [0] * width
    for index, column in enumerate(pivot_columns):
        particular[column] = rows[index][-1]

    pivot_set = set(pivot_columns)
    basis = []
    for free in range(width):
        if free in pivot_set:
            continue
        direction = [0] * width
        direction[free] = 1
        for index, column in enumerate(pivot_columns):
            direction[column] = rows[index][free]
        basis.append(tuple(direction))
    return tuple(particular), tuple(basis)


def select_witness_family(
    matrix, scale, expected_exact, cochain, constraints=(), *, residual_coordinates=()
):
    """Return the entire family in affine form, or None for an empty fiber.

    Invalid public parameters or constraint encodings raise ValueError.
    Cochains outside the generated profile yield None.
    """
    profile = FreshSignProfile(matrix, scale, expected_exact)
    return select_for_profile(
        profile, cochain, constraints, residual_coordinates=residual_coordinates
    )


def select_for_profile(profile, cochain, constraints=(), *, residual_coordinates=()):
    """Select compatible witnesses for optional disclosed residual coordinates.

    Each disclosure is a pair (index, value) in the residual's information
    block. In the fresh-sign profile, these coordinates are the negatives of
    the harmonic message coefficients.
    """
    mask = profile.mask_bits(cochain)
    if mask is None:
        return None
    width = profile.width
    rows = []
    for key, message, rhs in constraints:
        key, message = tuple(key), tuple(message)
        if len(key) != width or len(message) != width or any(
            type(value) not in (int, bool) or value not in (0, 1)
            for value in (*key, *message, rhs)
        ):
            raise ValueError("expected binary key and message coefficient rows and RHS")
        rows.append(
            [int(a) ^ int(b) for a, b in zip(key, message)]
            + [int(rhs) ^ (sum(a * t for a, t in zip(key, mask)) % 2)]
        )
    for index, value in residual_coordinates:
        if type(index) is not int or not 0 <= index < width:
            raise ValueError("residual coordinate index is outside the information block")
        if value not in (profile.scale, -profile.scale):
            return None
        row = [0] * (width + 1)
        row[index] = 1
        row[-1] = int(value == -profile.scale)
        rows.append(row)

    solution = _affine_decomposition(rows, width)
    if solution is None:
        return None
    message, kernel_basis = solution
    key = tuple(t ^ bit for t, bit in zip(mask, message))
    return WitnessFamily(Witness(key, message), kernel_basis)


if __name__ == "__main__":
    # Paper 1's dense example with d = 2, mask signs (+1, -1), and the
    # additional constraint that the two message bits agree.
    profile = FreshSignProfile(((1, 1), (1, -1)), 2, 0)
    cochain = (0, (0, 0), (0, 6))
    family = select_for_profile(profile, cochain, [((0, 0), (1, 1), 0)])
    assert family is not None
    print("Selected witness:", family.selected)
    print("Kernel basis:", family.kernel_basis)
    pair = family.residual_collision()
    assert pair is not None
    print("Off-diagonal witness pair:", pair)
    for witness in pair:
        closest = profile.closest_vector(witness.key, cochain)
        print(
            f"Key {witness.key} gives message {witness.message}, "
            f"nearest coefficients {closest.coefficients}, "
            f"Hodge residual² {closest.hodge_residual_squared}, "
            f"coefficient penalty {closest.coefficient_error_squared}"
        )
    residual = profile.closest_vector(family.selected.key, cochain).hodge_residual
    disclosed = select_for_profile(
        profile, cochain, [((0, 0), (1, 1), 0)], residual_coordinates=[(0, residual[1][0])]
    )
    assert disclosed is not None and disclosed.unique
    print(f"Disclosing the first residual information coordinate leaves {disclosed.cardinality} witness.")
