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

Start with the [TeX manuscript](manuscript/main.tex) and the
[semantic parity table](SEMANTIC-PARITY.md). The
[source ledger](SOURCE-LEDGER.md) traces the mathematical claims to the Lean
proofs, computations, and cited results.

## Reproduce the draft

Build the PDF with a TeX distribution that includes Latexmk and Biber.

~~~sh
cd manuscript
latexmk -pdf -outdir=.build main.tex
~~~

Build the Lean development from the repository root with Elan installed.
Lake reads the toolchain and Mathlib revision pinned in the project.

~~~sh
cd lean
lake exe cache get
lake build
~~~

Run the examples from the repository root with Python 3.
The Boolean agreement example uses SymPy.

~~~sh
python3 affine_witness_selector.py
python3 agreement_scheme.py
python3 polynomial_agreement_selector.py
~~~

The permanent checks use SymPy. The modular certificates also use NumPy
for exact integer arithmetic.

~~~sh
python3 gct_permanent_fiber.py
python3 gct_permanent_modular.py
python3 gct_permanent_involutions.py
python3 gct_permanent_extensions.py
python3 gct_permanent_plucker.py
~~~

The Plücker checker also exports exact input for msolve. Choose
`--single-edge` from 0 through 3 to reproduce the four unit-ideal checks.
`--matching` from 0 through 2 reproduces the three checks for a direction
supported on two opposite edges. For adjacent edges, use `--order-three`
and `--adjacent-edge` from 0 through 9.
The full systems use an ordered pivot pair from `PIVOT_PAIRS` and a
different extension pivot from `PIVOT_COORDINATES`.
The unrestricted path chart can also be exported in coordinates adapted
to path reversal.

~~~sh
python3 gct_permanent_plucker.py --single-edge 0 > /tmp/gct-edge.ms
msolve -g 2 -l 2 -f /tmp/gct-edge.ms -o /tmp/gct-edge.out
python3 gct_permanent_plucker.py --matching 0 > /tmp/gct-matching.ms
python3 gct_permanent_plucker.py --order-three > /tmp/gct-order-three.ms
python3 gct_permanent_plucker.py --adjacent-edge 0 > /tmp/gct-adjacent.ms
python3 gct_permanent_plucker.py --chart u P v > /tmp/gct-plucker.ms
python3 gct_permanent_plucker.py --path > /tmp/gct-path.ms
python3 gct_permanent_plucker.py --path-reversal > /tmp/gct-path-reversal.ms
~~~

The quadratic-field check uses a C++17 compiler.

~~~sh
c++ -O3 -std=c++17 gct_permanent_f25.cpp -o /tmp/gct_permanent_f25
/tmp/gct_permanent_f25
~~~

The imported Homotopical Encryption Lean sources retain their
[MIT notice](lean/LICENSE). The
[source ledger](SOURCE-LEDGER.md) identifies the copied modules,
revisions, and local source snapshots.
