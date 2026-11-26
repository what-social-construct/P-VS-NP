"""Select normalized polynomial agreement certificates over a prime field.

The coefficient system follows Section 8 of Homotopical Encryption Paper 3.
The caller supplies a prime modulus. Integer inputs stand for their residues
modulo that prime. Run this file for four-site examples over F_5.
"""

from __future__ import annotations

from dataclasses import dataclass


def _integer_tuple(values, label):
    try:
        entries = tuple(values)
    except TypeError as error:
        raise ValueError(f"expected an iterable of integers for {label}") from error
    if any(type(value) is not int for value in entries):
        raise ValueError(f"expected an iterable of integers for {label}")
    return entries


@dataclass(frozen=True)
class CoefficientFiber:
    """A particular coefficient vector and a basis of homogeneous directions."""

    prime: int
    particular: tuple[int, ...]
    kernel_basis: tuple[tuple[int, ...], ...]

    @property
    def cardinality(self) -> int:
        return self.prime ** len(self.kernel_basis)

    def point(self, parameters) -> tuple[int, ...]:
        """Return the point with the given kernel coordinates in the field."""
        parameters = _integer_tuple(parameters, "kernel coordinates")
        if len(parameters) != len(self.kernel_basis):
            raise ValueError("expected one field element per kernel basis vector")
        parameters = tuple(value % self.prime for value in parameters)
        return tuple(
            (value + sum(
                scale * direction[index]
                for scale, direction in zip(parameters, self.kernel_basis)
            )) % self.prime
            for index, value in enumerate(self.particular)
        )


@dataclass(frozen=True)
class Certificate:
    """A monic response and its multipliers, with coefficients in ascending order."""

    h0: tuple[int, ...]
    h1: tuple[int, ...]
    response: tuple[int, ...]
    block_length: int

    @property
    def degree(self) -> int:
        return len(self.response) - 1

    @property
    def budget(self) -> int:
        return len(self.h0) - 1

    @property
    def certified_count(self) -> int:
        return self.block_length - self.degree

    @property
    def coefficient_vector(self) -> tuple[int, ...]:
        return self.h0 + self.h1 + self.response[:-1]


def _solve(matrix, rhs, prime):
    """Compute one point and a kernel basis by modular row reduction."""
    width = len(matrix[0])
    rows = [list(row) + [value] for row, value in zip(matrix, rhs)]
    pivots = []
    for column in range(width):
        rank = len(pivots)
        pivot = next((i for i in range(rank, len(rows)) if rows[i][column]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        try:
            inverse = pow(rows[rank][column], -1, prime)
        except ValueError as error:
            raise ValueError("a pivot has no inverse modulo the supplied modulus") from error
        rows[rank] = [(value * inverse) % prime for value in rows[rank]]
        for index, row in enumerate(rows):
            factor = row[column]
            if index != rank and factor:
                rows[index] = [
                    (value - factor * pivot_value) % prime
                    for value, pivot_value in zip(row, rows[rank])
                ]
        pivots.append(column)

    if any(row[-1] for row in rows[len(pivots):]):
        return None

    particular = [0] * width
    for index, column in enumerate(pivots):
        particular[column] = rows[index][-1]

    basis = []
    pivot_set = set(pivots)
    for free_column in range(width):
        if free_column in pivot_set:
            continue
        direction = [0] * width
        direction[free_column] = 1
        for index, column in enumerate(pivots):
            direction[column] = -rows[index][free_column] % prime
        basis.append(tuple(direction))

    return CoefficientFiber(prime, tuple(particular), tuple(basis))


@dataclass(frozen=True)
class PolynomialAgreement:
    """A received pair at distinct sites over F_prime, for 1 ≤ k ≤ n.

    The modulus must be prime. Primality is a caller precondition. Sites and
    pairs of received values are normalized modulo the supplied modulus.
    """

    prime: int
    sites: tuple[int, ...]
    received: tuple[tuple[int, int], ...]
    k: int

    def __post_init__(self):
        if type(self.prime) is not int or self.prime < 2:
            raise ValueError("expected a prime integer modulus of at least two")
        sites = tuple(value % self.prime for value in _integer_tuple(self.sites, "sites"))
        if type(self.k) is not int or not 1 <= self.k <= len(sites):
            raise ValueError("expected an integer code degree bound between one and the site count")
        if len(set(sites)) != len(sites):
            raise ValueError("evaluation sites must be distinct modulo the prime")
        try:
            received = tuple(self.received)
        except TypeError as error:
            raise ValueError("expected one received pair per site") from error
        if len(received) != len(sites):
            raise ValueError("expected one received pair per site")
        pairs = []
        for pair in received:
            pair = _integer_tuple(pair, "a received pair")
            if len(pair) != 2:
                raise ValueError("each received pair must have two coordinates")
            pairs.append((pair[0] % self.prime, pair[1] % self.prime))
        object.__setattr__(self, "sites", sites)
        object.__setattr__(self, "received", tuple(pairs))

    def coefficient_system(self, t, D, *, prefix=()):
        """Build the fixed-degree system for 0 ≤ t and k + t ≤ D < n.

        Columns carry h0, h1, and the lower response coefficients in ascending
        order within each block. A prefix fixes whole field coefficients in
        this vector at the specified degree and budget. The monic term is
        moved to the right-hand side.
        """
        if (
            type(t) is not int
            or type(D) is not int
            or t < 0
            or not self.k + t <= D < len(self.sites)
        ):
            raise ValueError("expected integer degrees with 0 <= t and k + t <= D < n")
        prefix = _integer_tuple(prefix, "coefficient prefix")
        width = 2 * (t + 1) + D
        if len(prefix) > width:
            raise ValueError("coefficient prefix is too long for this degree and budget")

        matrix = []
        rhs = []
        for site, (w0, w1) in zip(self.sites, self.received):
            powers = [1]
            for _ in range(D):
                powers.append(powers[-1] * site % self.prime)
            matrix.append(
                tuple(w0 * power % self.prime for power in powers[:t + 1])
                + tuple(w1 * power % self.prime for power in powers[:t + 1])
                + tuple(-power % self.prime for power in powers[:D])
            )
            rhs.append(powers[D])
        for column, value in enumerate(prefix):
            row = [0] * width
            row[column] = 1
            matrix.append(tuple(row))
            rhs.append(value % self.prime)
        return tuple(matrix), tuple(rhs)

    def fiber(self, t, D, *, prefix=()) -> CoefficientFiber | None:
        """Describe every completion of the prefix, returning None if empty."""
        matrix, rhs = self.coefficient_system(t, D, prefix=prefix)
        return _solve(matrix, rhs, self.prime)

    def select(self, t, D, *, prefix=()) -> Certificate | None:
        """Select a normalized certificate extending the fixed-degree prefix."""
        fiber = self.fiber(t, D, prefix=prefix)
        if fiber is None:
            return None
        vector = fiber.particular
        width = t + 1
        return Certificate(
            vector[:width], vector[width:2 * width], vector[2 * width:] + (1,), len(self.sites)
        )

    def strongest(self) -> Certificate | None:
        """Find the least feasible D < n with maximal budget t = D - k.

        The search leaves the coefficients unrestricted. Multiplying the
        response and both multipliers by X preserves feasibility at the next
        degree, which justifies binary search with n as the empty sentinel.
        """
        low, high = self.k, len(self.sites)
        best = None
        while low < high:
            degree = (low + high) // 2
            certificate = self.select(degree - self.k, degree)
            if certificate is None:
                low = degree + 1
            else:
                high = degree
                best = certificate
        return best


def _evaluate(coefficients, site, prime):
    value = 0
    for coefficient in reversed(coefficients):
        value = (value * site + coefficient) % prime
    return value


def _check_certificate(problem, certificate):
    for site, (w0, w1) in zip(problem.sites, problem.received):
        h0 = _evaluate(certificate.h0, site, problem.prime)
        h1 = _evaluate(certificate.h1, site, problem.prime)
        response = _evaluate(certificate.response, site, problem.prime)
        assert response == (h0 * w0 + h1 * w1) % problem.prime


if __name__ == "__main__":
    sites = (1, 2, 3, 4)
    paired = PolynomialAgreement(5, sites, [(site, 2 * site) for site in sites], 1)
    fiber = paired.fiber(0, 1)
    assert fiber is not None and fiber.cardinality == 5
    assert {fiber.point((a,)) for a in range(5)} == {((1 - 2 * a) % 5, a, 0) for a in range(5)}
    restricted = paired.fiber(0, 1, prefix=(0,))
    assert restricted is not None and restricted.cardinality == 1
    selected = paired.select(0, 1, prefix=(0,))
    assert selected is not None and selected.coefficient_vector == (0, 3, 0)
    assert selected.certified_count == 3
    _check_certificate(paired, selected)
    paired_best = paired.strongest()
    assert paired_best is not None and paired_best.degree == 1 and paired_best.certified_count == 3
    _check_certificate(paired, paired_best)
    print(f"Degree 1 has {fiber.cardinality} certificates. Prefix h0=0 selects {selected}.")

    zero = PolynomialAgreement(5, sites, [(0, 0)] * 4, 1)
    assert zero.fiber(0, 1) is None and zero.strongest() is None
    print("The zero received pair has no certificate with degree below 4.")

    sharp = PolynomialAgreement(5, sites, [(1 - pow(site, -1, 5), 0) for site in sites], 1)
    strongest = sharp.strongest()
    assert strongest is not None and strongest.degree == 3 and strongest.certified_count == 1
    assert sharp.select(0, 1) is None and sharp.select(1, 2) is None
    _check_certificate(sharp, strongest)
    constant_distance = len(sites) - max(sharp.received.count(pair) for pair in sharp.received)
    assert constant_distance == 3
    print(
        f"The sharp example has {constant_distance} errors. Degree {strongest.degree} "
        f"certifies a lower bound of {strongest.certified_count}."
    )
