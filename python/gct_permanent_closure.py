"""Replay a multiplication-closure certificate for the star invariant quotient."""

import argparse
import json
from itertools import combinations_with_replacement, product

import numpy as np

from gct_permanent_plucker import (
    EDGE_GRAPH_PIVOTS,
    edge_graph_chart,
    star_fourier_chart,
    star_fourier_reflection,
    star_invariant_generators,
    star_leaf_actions,
)


def decode_polynomial(terms, ring):
    """Decode pairs of a residue and a list of variable indices."""
    if not isinstance(terms, list):
        raise ValueError("A polynomial must be a list of terms.")
    polynomial = {}
    for term in terms:
        if not isinstance(term, list) or len(term) != 2:
            raise ValueError("A term must contain a coefficient and a list of variable indices.")
        coefficient, indices = term
        if type(coefficient) is not int or not isinstance(indices, list):
            raise ValueError("A coefficient must be an integer and its variable indices must be a list.")
        powers = [0] * ring.ngens
        for index in indices:
            if type(index) is not int or not 0 <= index < ring.ngens:
                raise ValueError("A term has an invalid variable index.")
            powers[index] += 1
        monomial = tuple(powers)
        polynomial[monomial] = polynomial.get(monomial, ring.domain.zero) + ring.domain(coefficient)
    return ring.from_dict({powers: coefficient for powers, coefficient in polynomial.items() if coefficient})


def verify_closure(certificate, equations, generators, actions):
    """Check that at most seven invariant classes span a multiplicatively stable space."""
    ring = equations[0].ring
    if not isinstance(certificate, dict):
        raise ValueError("Expected an object with a basis and product relations.")
    basis_data = certificate.get("basis")
    if not isinstance(basis_data, list) or not 1 <= len(basis_data) <= 7:
        raise ValueError("The basis must list between one and seven polynomials.")
    basis = [decode_polynomial(terms, ring) for terms in basis_data]
    if basis[0] != ring.one:
        raise ValueError("The first basis polynomial must be one.")
    for polynomial in basis:
        for action in actions:
            transformed = {tuple(powers[index] for index in action): coefficient
                           for powers, coefficient in polynomial.items()}
            if ring.from_dict(transformed) != polynomial:
                raise ValueError("Each basis polynomial must be invariant under relabeling the leaves.")

    proofs = certificate.get("products")
    count = len(generators)*len(basis)
    if not isinstance(proofs, list) or len(proofs) != count:
        raise ValueError(f"Expected {count} product relations, in generator-major order.")
    for number, ((generator, vector), proof) in enumerate(zip(product(generators, basis), proofs)):
        if not isinstance(proof, dict):
            raise ValueError(f"Product {number} must give coordinates and ideal multipliers.")
        coordinates = proof.get("coordinates")
        if not isinstance(coordinates, list) or len(coordinates) != len(basis) or any(
                type(coefficient) is not int for coefficient in coordinates):
            raise ValueError(f"Product {number} must give one integer coefficient per basis polynomial.")
        difference = generator*vector - sum(coefficient*element for coefficient, element in zip(coordinates, basis))
        multipliers = proof.get("multipliers")
        if not isinstance(multipliers, list):
            raise ValueError(f"Product {number} must list the ideal multipliers.")
        for multiple in multipliers:
            if not isinstance(multiple, list) or len(multiple) != 2:
                raise ValueError(f"Product {number} has an invalid ideal multiple.")
            equation, terms = multiple
            if type(equation) is not int or not 0 <= equation < len(equations):
                raise ValueError(f"Product {number} has an invalid equation index.")
            difference -= decode_polynomial(terms, ring)*equations[equation]
        if difference:
            raise ValueError(f"Product {number} is not the stated combination modulo the star equations.")
    return len(basis), count


def verify_degree_seven_obstruction(source):
    """Replay independent functionals on the bounded Macaulay span."""
    cap, count = map(int, next(source, "").split())
    if (cap, count) != (7, 20):
        raise ValueError("Expected 20 functionals at degree seven.")
    seeds = list(map(int, next(source, "").split()))
    if len(seeds) != count or len(set(seeds)) != count:
        raise ValueError("Expected 20 distinct low-degree pairing monomials.")

    names, equations, weights = star_fourier_chart()
    variable_count = len(names)
    reflection = star_fourier_reflection()
    place_values = tuple(9**index for index in range(variable_count))

    def decode_monomial(key):
        if not 0 <= key < 9**variable_count:
            raise ValueError("Invalid monomial key.")
        return tuple(key//place % 9 for place in place_values)

    if any(sum(decode_monomial(key)) > 2 for key in seeds):
        raise ValueError("Pairing monomials must have degree at most two.")
    seed_indices = {key: index for index, key in enumerate(seeds)}
    pairings = np.zeros((count, count), dtype=np.int64)
    value_rows = [np.zeros(count, dtype=np.int64)]
    index_by_monomial = {}
    for line in source:
        key_text, digits = line.split()
        key = int(key_text)
        powers = decode_monomial(key)
        reflected = sum(place_values[index]*power for index, power in zip(reflection, powers))
        if (sum(powers) > cap or sum(power*weight for power, weight in zip(powers, weights)) % 3
                or key > reflected or key in index_by_monomial):
            raise ValueError("Expected distinct weight-zero reflection-orbit representatives.")
        if len(digits) != count or any(digit not in "01234" for digit in digits):
            raise ValueError("Each monomial must give one base-five residue per functional.")
        values = np.array([int(digit) for digit in digits], dtype=np.int64)
        if key in seed_indices:
            pairings[seed_indices[key]] = values
        orbit_size = 1 if key == reflected else 2
        index_by_monomial[key] = index_by_monomial[reflected] = len(value_rows)
        value_rows.append(values*pow(orbit_size, -1, 5) % 5)
    if not np.array_equal(pairings, np.eye(count, dtype=np.int64)):
        raise ValueError("The low-degree pairing matrix is not the identity.")
    values = np.array(value_rows)

    degrees = [max(map(sum, equation)) for equation in equations]
    shifts = [[[] for _ in range(3)] for _ in range(cap-min(degrees)+1)]
    for degree, by_weight in enumerate(shifts):
        for indices in combinations_with_replacement(range(variable_count), degree):
            weight = sum(weights[index] for index in indices) % 3
            by_weight[weight].append(sum(place_values[index] for index in indices))
    checked_rows = 0
    for number, (equation, degree) in enumerate(zip(equations, degrees)):
        weight = sum(power*w for power, w in zip(next(iter(equation)), weights)) % 3
        products = [key for by_weight in shifts[:cap-degree+1] for key in by_weight[-weight % 3]]
        sums = np.zeros((len(products), count), dtype=np.int64)
        for powers, coefficient in equation.items():
            key = sum(place*power for place, power in zip(place_values, powers))
            rows = np.fromiter((index_by_monomial.get(key+shift, 0) for shift in products), dtype=np.int64)
            sums += int(coefficient)*values[rows]
        if np.any(sums % 5):
            raise ValueError(f"A functional is nonzero on a degree-seven multiple of equation {number}.")
        checked_rows += len(products)

    # The selected low-degree generators and 1 have disjoint supports.
    actions = star_leaf_actions()
    ambient = len({
        min(tuple(sorted(action[index] for index in indices)) for action in actions)
        for degree in range(3)
        for indices in combinations_with_replacement(range(variable_count), degree)
    })
    _, low_generators = star_invariant_generators(maximum_degree=2)
    seen_terms = {(0,) * variable_count}
    for generator in low_generators:
        if not generator or not seen_terms.isdisjoint(generator):
            raise ValueError("The selected low-degree orbit sums must be independent with one.")
        seen_terms.update(generator)
    rank_bound = count + len(low_generators) + 1 - ambient
    if rank_bound <= 7:
        raise ValueError("The low-degree functionals do not give an obstruction to a seven-element span.")
    return checked_rows, rank_bound


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", type=argparse.FileType("r"), help="the certificate, or - for stdin")
    parser.add_argument("--degree-seven-obstruction", action="store_true",
                        help="verify the stored obstruction to closure using degree-seven ideal multiples")
    args = parser.parse_args()
    try:
        with args.certificate as source:
            if args.degree_seven_obstruction:
                rows, rank = verify_degree_seven_obstruction(source)
                print(f"Verified {rows:,} bounded products and a low-degree rank of at least {rank}.")
                return
            certificate = json.load(source)
        _, equations = edge_graph_chart(EDGE_GRAPH_PIVOTS["star"])
        _, generators = star_invariant_generators()
        dimension, count = verify_closure(certificate, equations, generators, star_leaf_actions())
    except ValueError as error:
        parser.error(str(error))
    print(f"Verified {count:,} exact products. The star invariant quotient has dimension at most {dimension}.")


if __name__ == "__main__":
    main()
