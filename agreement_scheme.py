"""Exact finite Boolean model of a computational agreement scheme.

Run with: python3 agreement_scheme.py
Requires SymPy. All polynomial computations are over F_2, modulo z^2-z
for every parameter and input bit. This is a toy construction, not a
complexity lower bound or a formal Lean proof.
"""

from itertools import product
import json

import sympy as sp


def boolean_reduce(expression, variables):
    """The canonical multilinear representative in the Boolean quotient."""
    coefficients = {}
    for powers, coefficient in sp.Poly(expression, *variables, modulus=2).terms():
        reduced = tuple(int(power != 0) for power in powers)
        coefficients[reduced] = (coefficients.get(reduced, 0) + int(coefficient)) % 2
    return sp.expand(sum(
        coefficient * sp.prod(variable ** power for variable, power in zip(variables, powers))
        for powers, coefficient in coefficients.items()
    ))


def bit_value(expression, assignment):
    return int(expression.subs(assignment)) % 2


def agreement_model(name, deterministic, circuit_parameters, target, target_parameters, x):
    parameters = tuple(circuit_parameters) + tuple(target_parameters)
    delta = boolean_reduce(deterministic - target, parameters + (x,))
    equations = [
        sp.expand(coefficient)
        for coefficient in reversed(sp.Poly(delta, x).all_coeffs())
        if coefficient != 0
    ]
    # Agreement means equality at BOTH Boolean inputs, equivalently equality
    # of every coefficient of the canonical multilinear difference.
    agreement = boolean_reduce(
        sp.prod(1 - delta.subs(x, bit) for bit in (0, 1)), parameters
    )
    disagreement = boolean_reduce(1 - agreement, parameters)
    assert boolean_reduce(agreement ** 2 - agreement, parameters) == 0
    assert boolean_reduce(agreement * disagreement, parameters) == 0
    for equation in equations:
        assert boolean_reduce(agreement * equation, parameters) == 0

    boolean_equations = [parameter ** 2 - parameter for parameter in parameters]
    basis = sp.groebner(equations + boolean_equations, *parameters, order="lex", modulus=2)
    # Circuit parameters occur first, so lexicographic elimination projects
    # the equality scheme onto the target parameter scheme.
    image_equations = [
        polynomial.as_expr() for polynomial in basis.polys
        if not (polynomial.as_expr().free_symbols & set(circuit_parameters))
    ]

    # A target is unrepresented precisely when EVERY candidate disagrees.
    unrepresented = sp.Integer(1)
    for bits in product((0, 1), repeat=len(circuit_parameters)):
        unrepresented *= disagreement.subs(dict(zip(circuit_parameters, bits)))
    unrepresented = boolean_reduce(unrepresented, tuple(target_parameters))

    equal_pairs = 0
    missing_targets = 0
    for target_bits in product((0, 1), repeat=len(target_parameters)):
        target_assignment = dict(zip(target_parameters, target_bits))
        matching_candidates = 0
        for circuit_bits in product((0, 1), repeat=len(circuit_parameters)):
            assignment = dict(target_assignment)
            assignment.update(zip(circuit_parameters, circuit_bits))
            matches = all(bit_value(delta.subs(x, bit), assignment) == 0 for bit in (0, 1))
            assert bit_value(agreement, assignment) == int(matches)
            matching_candidates += int(matches)
        equal_pairs += matching_candidates
        missing = matching_candidates == 0
        missing_targets += int(missing)
        assert bit_value(unrepresented, target_assignment) == int(missing)
        in_image = all(bit_value(equation, target_assignment) == 0 for equation in image_equations)
        assert in_image == (not missing)

    total_pairs = 2 ** len(parameters)
    return {
        "model": name,
        "deterministic_polynomial": str(deterministic),
        "existential_polynomial": str(target),
        "coefficient_difference_equations": [str(equation) for equation in equations],
        "agreement_idempotent": str(agreement),
        "disagreement_idempotent": str(disagreement),
        "projected_image_equations_including_boolean_relations": [str(equation) for equation in image_equations],
        "unrepresented_target_idempotent": str(unrepresented),
        "equal_pairs": equal_pairs,
        "disagreeing_pairs": total_pairs - equal_pairs,
        "unrepresented_targets": missing_targets,
    }


def main():
    a, b, c, d, x, y = sp.symbols("a b c d x y")
    verifier = a * x * y + b * (1 - x) * (1 - y)
    # Existential acceptance is OR, not a sum modulo two (which is parity).
    target = boolean_reduce(
        1 - sp.prod(1 - verifier.subs(y, bit) for bit in (0, 1)), (a, b, x)
    )
    assert target == a * x + b * x + b
    for bits in product((0, 1), repeat=3):
        assignment = dict(zip((a, b, x), bits))
        existential = any(bit_value(verifier.subs(y, bit), assignment) for bit in (0, 1))
        assert bit_value(target, assignment) == int(existential)
    models = [
        agreement_model("constant candidates", c, (c,), target, (a, b), x),
        agreement_model("all affine candidates", c + d * x, (c, d), target, (a, b), x),
    ]
    assert models[0]["unrepresented_target_idempotent"] == "a + b"
    assert models[1]["unrepresented_targets"] == 0
    print(json.dumps({"field": "F_2", "models": models, "verification": "all exact checks passed"}, indent=2))


if __name__ == "__main__":
    main()
