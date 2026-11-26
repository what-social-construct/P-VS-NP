# Affine Witness Collisions and Boolean Agreement

For an explicitly presented binary affine witness family, the pairs with
equal disclosures form a product of the witness fiber and the kernel of the
disclosure restricted to its directions. The manuscript gives Boolean
equations for that space, its diagonal and residual factors, and a
polynomial-time selector for the explicit affine system. A finite
candidate–target example shows how coefficient equations detect Boolean
agreement and how projection identifies the represented targets.

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

Run the two examples from the repository root with Python 3.
The Boolean agreement example uses SymPy.

~~~sh
python3 affine_witness_selector.py
python3 agreement_scheme.py
~~~

The imported Homotopical Encryption Lean sources retain their
[MIT notice](lean/LICENSE). The
[source ledger](SOURCE-LEDGER.md#he-p1-code) identifies the copied modules
and upstream revision.
