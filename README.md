# Affine Witness Collisions and Boolean Agreement

For an explicitly presented binary affine witness family, the pairs with
equal disclosures form a product of the witness fiber and the kernel of the
disclosure restricted to its directions. The manuscript gives Boolean
equations for that space, its diagonal and residual factors, and a
polynomial-time selector for the explicit affine system. A finite
candidate–target example shows how coefficient equations detect Boolean
agreement and how projection identifies the represented targets.

The polynomial agreement example from Homotopical Encryption Paper 3
uses a second affine family over a finite field. Its coefficient system
supports fixed-degree certificate selection under a prefix and a search
for the strongest certified error bound.

[Read the manuscript PDF](output/pdf/affine-witness-collisions.pdf)

Start with the [TeX source](manuscript/main.tex) and the
[semantic parity table](SEMANTIC-PARITY.md). The
[source ledger](SOURCE-LEDGER.md) traces the mathematical claims to the Lean
proofs, computations, and cited results.

## Reproduce the draft

Build the PDF with a TeX distribution that includes Latexmk and Biber.

~~~sh
cd manuscript
latexmk -pdf -outdir=.build main.tex
cp .build/main.pdf ../output/pdf/affine-witness-collisions.pdf
~~~

Build the Lean development from the repository root with Elan installed.
Lake reads the toolchain and Mathlib revision pinned in the project.

~~~sh
cd lean
lake exe cache get
lake build
~~~

The permanent proofs are available through `import PvsNP`.
The [parity table](SEMANTIC-PARITY.md) identifies the checked
minor-chart algebra, orientation descent, field-degree bound,
and edge-chart calculations, with the external inputs to each.

The [Python tools](python/) run from the repository root with Python 3.
The Boolean agreement example uses SymPy.

~~~sh
python3 python/affine_witness_selector.py
python3 python/agreement_scheme.py
python3 python/polynomial_agreement_selector.py
~~~

The permanent checks use SymPy. The modular certificates also use NumPy
for exact integer arithmetic.

~~~sh
python3 python/gct_permanent_fiber.py
python3 python/gct_permanent_modular.py
python3 python/gct_permanent_involutions.py
python3 python/gct_permanent_extensions.py
python3 python/gct_permanent_plucker.py
~~~

The Plücker checker also exports exact input for msolve. Choose
`--single-edge` from 0 through 3 to reproduce the four unit-ideal checks.
`--matching` from 0 through 2 reproduces the three checks for a direction
supported on two opposite edges. For adjacent edges, use `--order-three`
and `--adjacent-edge` from 0 through 9. The triangle radical pencil can
be exported with `--triangle-radical`.
The full systems use an ordered pivot pair from `PIVOT_PAIRS` and a
different extension pivot from `PIVOT_COORDINATES`.
The unrestricted path chart can also be exported in coordinates adapted
to path reversal.

~~~sh
python3 python/gct_permanent_plucker.py --single-edge 0 > /tmp/gct-edge.ms
msolve -g 2 -l 2 -f /tmp/gct-edge.ms -o /tmp/gct-edge.out
python3 python/gct_permanent_plucker.py --matching 0 > /tmp/gct-matching.ms
python3 python/gct_permanent_plucker.py --order-three > /tmp/gct-order-three.ms
python3 python/gct_permanent_plucker.py --adjacent-edge 0 > /tmp/gct-adjacent.ms
python3 python/gct_permanent_plucker.py --triangle-radical > /tmp/gct-triangle.ms
python3 python/gct_permanent_plucker.py --chart u P v > /tmp/gct-plucker.ms
python3 python/gct_permanent_plucker.py --star > /tmp/gct-star.ms
python3 python/gct_permanent_plucker.py --path > /tmp/gct-path.ms
python3 python/gct_permanent_plucker.py --path-reversal > /tmp/gct-path-reversal.ms
~~~

The fixed star chart in Fourier coordinates has its own
degree-seven functional. Its data header selects the star chart.

~~~sh
python3 python/gct_permanent_plucker.py --star-fourier > /tmp/gct-star-fourier.ms
gzip -dc gct_permanent_star_degree7.dual.gz | python3 python/gct_permanent_plucker.py --verify-path-dual -
~~~

The permanent's quadratic form gives a corrected diagonal readout.
Its determinant splits the star chart into a collision branch and an
injective branch. The collision branch has a unique kernel line
at each geometric point. The following Gröbner check excludes a
two-plane in the kernel and returns the reduced basis `1`.

~~~sh
python3 python/gct_permanent_plucker.py --star-hodge collision > /tmp/gct-hodge-collision.ms
python3 python/gct_permanent_plucker.py --star-hodge injective > /tmp/gct-hodge-injective.ms
python3 python/gct_permanent_hodge.py --emit-collision-kernel > /tmp/gct-hodge-kernel.ms
python3 python/gct_permanent_hodge.py --emit-chart > /tmp/gct-hodge-two-plane.ms
msolve -f /tmp/gct-hodge-two-plane.ms -o /tmp/gct-hodge-two-plane.out -t 1 -g 2 -l 2
~~~

Use `--emit-edge-family` on `gct_permanent_hodge.py` with `cyclic`
or `transposition` for the edge symmetry checks. The options
`transverse` and `transverse-pair` export the ramified edge pencil
and its two fixed columns. Each system gives a unit Gröbner basis
with the same msolve command.

The exact Frobenius searches show that a nonempty fiber at five must
have at least 48 geometric points. An upper bound of seven on the
dimension of the star chart's invariant quotient would settle the
nonexistence question. The generator command lists the 127 orbit sums
needed for a multiplication-closure check.

~~~sh
python3 python/gct_permanent_frobenius.py
python3 python/gct_permanent_plucker.py --star-invariants
~~~

The centered Fourier chart replaces the quartics by 15 equations
that reduce degree-four center-diagonal monomials to lower degree.
The degree-seven obstruction below shows that expressing all 127
generators in a seven-dimensional span requires a higher-degree
ideal multiple in at least one identity.

~~~sh
python3 python/gct_permanent_plucker.py --star-fourier-center > /tmp/gct-star-center.ms
gzip -dc gct_permanent_star_span_degree7.dual.gz | python3 python/gct_permanent_closure.py --degree-seven-obstruction -
~~~

Use `python3 python/gct_permanent_closure.py certificate.json` to
replay a proposed closure certificate. The `basis` array must list
one to seven invariant polynomials, starting with one. A polynomial
is a list of terms `[coefficient, variable_indices]` with repeated,
zero-based indices in the variable order printed by `--star`.
The constant one is `[[1, []]]`.

The `products` array gives one object for each generator from
`--star-invariants` times each basis element, in generator-major
order. Each object gives `coordinates` in the proposed basis and
`multipliers` as pairs `[equation_index, polynomial]` in the order
printed by `--star`. The checker uses these multiples of the original
equations to verify the difference from the claimed basis combination.

The exact degree-seven certificate search found a functional that
takes the constant to one and annihilates every even monomial multiple
of the path generators within the degree cap. Replay all 147,622
pairings with

~~~sh
gzip -dc gct_permanent_path_degree7.dual.gz | python3 python/gct_permanent_plucker.py --verify-path-dual -
~~~

The data contains the degree cap followed by nonzero entries
`key residue` over `F5`. In generator variable order, `key` packs
each exponent into enough bits to hold the degree cap, starting at
the least significant end. Unlisted monomials have value zero.

The four-cycle chart omitting Fourier frequency two has a separate
degree-eight witness. Its data header includes the omitted frequency
after the cap and selects the corresponding chart for replay.

~~~sh
python3 python/gct_permanent_plucker.py --four-cycle 2 > /tmp/gct-cycle-2.ms
gzip -dc gct_permanent_cycle_omit2_degree8.dual.gz | python3 python/gct_permanent_plucker.py --verify-path-dual -
~~~

The quadratic-field check uses a C++17 compiler.

~~~sh
c++ -O3 -std=c++17 gct_permanent_f25.cpp -o /tmp/gct_permanent_f25
/tmp/gct_permanent_f25
~~~

The imported Homotopical Encryption Lean sources retain their
[MIT notice](lean/LICENSE). The quadratic valuation proof adapted from
JC3 retains its [MIT notice](lean/PvsNP/LICENSE-JC3). The
[source ledger](SOURCE-LEDGER.md) identifies the copied modules,
revisions, and local source snapshots.
