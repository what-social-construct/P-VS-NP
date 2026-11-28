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

The [theorem targets](manuscript/03-complexity/theorem-targets.tex) work
backward from two questions. Can a symmetric three-plane through the
all-ones $4\times4$ matrix have constant permanent? Can an algorithm
use a decomposition of an encoded witness family to select a witness in
polynomial time? The [target register](SEMANTIC-PARITY.md#theorem-targets)
identifies the missing certificates and the Lean results that would use them.

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

The public Lean build includes the reviewed Galois sources for orbit
coordinates, permutation commutation and the quotient-annihilator theorem.
The existing `PvsNP` imports also work. Run these checks from the repository root.

~~~sh
python3 python/galois_exports.py
python3 python/galois_exports.py --upstream ../galois-obstruction-theory
~~~

The first command verifies the checked-in bytes. The second also compares
them with Git objects at the recorded revision in a local Galois checkout.
To update the export, review the upstream revision, source ranges and
SHA-256 digests, update the lock file, then add `--restore` to the second
command and run the Lean build. [Export lock](lean/galois-exports.json) ·
[Ownership and handoff](SOURCE-LEDGER.md#handoff-to-galois-collision)

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

For a 2-CNF formula the [prefix compiler](python/two_sat_prefix.py)
prints augmented binary affine rows and the first satisfying assignment
extending the prefix, or JSON null when the prefix cannot extend.
The arguments are the number of ordered variables, clauses written as
signed variable numbers, and an optional bit prefix.

~~~sh
python3 python/two_sat_prefix.py 2 '[[1,2]]' 0
python3 python/test_two_sat_prefix.py
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

Three [localized charts](python/gct_collision_kernel_reduction.py) cover
the possible completions. Each has twelve variables, including an inverse.
The [kernel determinant](python/gct_collision_direction.py) excludes all
24 eligible prime-field lines even for completions over the algebraic closure.

~~~sh
python3 python/gct_collision_direction.py
python3 python/gct_collision_kernel_reduction.py
python3 python/gct_collision_kernel_reduction.py --verify-cover msolve
python3 python/gct_collision_kernel_reduction.py --list-charts
python3 python/gct_collision_kernel_reduction.py --emit-chart 12,22,23 > /tmp/gct-collision-chart.py
~~~

The generated module exposes the reconstructed frame and its equations in
factored form. Put the repository's Python directory on the import path and
evaluate in a commutative algebra of characteristic five.

Over the quadratic field, 964 eligible projective kernel lines form 31
orbits under vertex permutations and Frobenius. A quintic rank test and
40 exact common-line calculations exclude all geometric completions on
these orbits using the quadratic completion equations. A second replay
checks a degree-four identity for one for each orbit's companion system.
A fixed projective three-space slice contains just 24 such points.
On the pencil face $[m_2:m_3]=[0:1]$, the pure directions form an open
of a geometrically integral degree-24 curve. Imposing a common line
gives the empty scheme. Together with the slice exclusion, this makes
the entire quadratic kernel-direction locus finite over both
$\overline{\mathbb F}_5$ and $\mathbb C$. Whether any direction survives
with all four vertex sums nonzero remains open.
[Direction locus](manuscript/03-complexity/collision-kernel-quadrics.tex) · [Fixed-face proof](manuscript/03-complexity/common-line-image-certificate.tex)

~~~sh
python3 python/gct_collision_f25.py --verify-lines msolve
python3 python/gct_collision_eliminant.py
python3 python/gct_collision_fiber_slice.py
python3 python/gct_collision_translated_sections.py
python3 python/gct_collision_pencil_orbits.py
python3 python/gct_collision_vertex_orbits.py
python3 python/gct_collision_line_divisor.py
python3 python/gct_collision_incidence_descent.py
python3 python/gct_collision_quadratic_slopes.py
python3 python/gct_collision_line_divisor_slopes.py
python3 python/gct_collision_resultant_square.py
python3 python/gct_collision_polar_extension.py
python3 python/gct_collision_residual_candidate.py
python3 python/gct_collision_slope_closure.py
python3 python/gct_collision_ordering_fibers.py
python3 python/gct_common_line_witness.py
python3 python/gct_collision_normalization.py
python3 python/gct_collision_fiber_net.py
python3 python/gct_collision_face.py
python3 python/gct_collision_subresultant.py
python3 python/gct_collision_pencil_fiber.py --verify-boundary msolve
python3 python/gct_collision_pencil_fiber.py --emit > /tmp/gct-pencil-fiber.ms
~~~

The surviving vertex-permutation invariants are recovered from two
coordinates on an explicit plane curve of bidegree $(12,24)$. Every
prime-field interpolation slope and the exceptional degree-88 lift
fail the common-line test. [Geometric fiber calculation](manuscript/03-complexity/collision-pencil-fiber.tex)

The five sections $d=a+rm$ for $r\in\mathbb F_5$ contain 112 distinct
geometric directions. Residue-field certificates exclude a common line at
every one of them. The witness checker also recovers an explicit line
over $\mathbb F_{25}$ for a test net defined over $\mathbb F_5$.
Relabeling the vertices gives three pencils whose prime-field values,
including infinity, exclude 328 distinct directions. The smooth model
of the invariant plane curve has genus seven. [Orbit and quotient calculation](manuscript/03-complexity/collision-vertex-orbits.tex)

On the fixed face, an auxiliary linear form contributes a square to
the degree-440 resultant. Removing it gives a degree-336 equation on
the labeled curve. Its zero divisor on the quotient has degree at
most 1,344 and contains the scheme-theoretic image of the common lines.
Above each candidate, the labeled incidence is the product of the
cubic root-ordering scheme with the scheme of common lines.
The three possible ordering types occur in the quadratic-slope test.
The resultant is a unit at all 40 eligible closed points with slope
in $\mathbb F_{25}$, representing 281 geometric points.
For a supplied pure quotient point, `find_ordered_line(values, field)`
tests the net before adjoining cubic roots and verifies any returned
frame against the original permanent through tangent degree two.
At a quotient point where the hyperplane section has eight simple points,
testing the polar kernel at each point gives the complete line fiber.
A successful degree-$d$ point gives a line over that same field. Ordering
the incident cubic as well requires relative degree $\operatorname{lcm}(d,e)$,
where $e$ is its splitting degree. On the actual face, a degree-six
closed point is a simple zero of the residual equation. Its unique
$Q_2$ candidate fails $Q_3$ and $Q_4$. Removing this point lowers the
bound on the degree of the common-line image to 1,338. The other two
closed points above its slope, of degrees 24 and 42, have nonzero
resultant. Taking the schematic closure after removing that slope
therefore removes precisely the degree-six factor. The other two
cofactor equations exclude lines above all remaining candidates.
[Decomposition and closure](manuscript/03-complexity/common-line-decomposition.tex) · [Slope check](python/gct_collision_slope_closure.py) · [Ordered witness recovery](python/gct_collision_incidence_descent.py)

**The fixed-face residual has zero Frobenius orbits.** A common line
would give a simultaneous zero of three univariate polynomials over
$\mathbb F_5$. Their degrees are 1,344, 1,372 and 1,406, and already
the first two have gcd one. The calculation recovers the cofactor
sections from exact values on 18,900 distinct geometric points of
the labeled curve. The largest degree bound for the zero divisor of
a nonzero difference is 8,448, so these values determine the sections
on the whole curve. This proves $Z=Z_{\rm lev}=R_{\rm lev}=0$.
[Proof](manuscript/03-complexity/common-line-image-certificate.tex) · [Resultant evaluator](gct_common_line_resultants.cpp) · [Algebra checker](python/gct_common_line_image_algebra.py)

Replay the quadratic calculation from the repository root with C++17,
NumPy, SymPy and python-flint. The five input columns encode
$x_0,x_1,y_0,y_1,y_2$ with $Y=1$ as seven base-five digits, constant
coefficient first, in $\mathbb F_5[w]/(w^7+3w+3)$.

~~~sh
c++ -std=c++17 -O3 gct_common_line_resultants.cpp -o /tmp/common-line-resultants
/tmp/common-line-resultants < python/data/common_line_samples_f5_7.txt > /tmp/common-line-values.txt
python3 python/gct_common_line_image_algebra.py /tmp/common-line-values.txt
~~~

Pass the optional flag `--emit-norms /tmp/common-line-norms.json` to
write the three norm polynomials and a Bézout identity for the first
pair. Coefficient arrays begin with the constant term.

The earlier full-level exclusion has a separate replay. Six exact
Gröbner bases exclude a cubic companion in the pencil center. A
seventh excludes a level companion in the normalized chart. These
commands use msolve 0.11.0. [Level theorem](manuscript/03-complexity/common-line-decomposition.tex) · [Checker](python/gct_collision_pencil_center.py)

~~~sh
python3 python/gct_collision_pencil_center.py --verify msolve
python3 python/gct_collision_pencil_center.py --verify-level msolve
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
