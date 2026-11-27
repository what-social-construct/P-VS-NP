# Source ledger

Reviewed 2026-11-26. Source IDs refer to a specific text, code revision, or
external definition. The [parity register](SEMANTIC-PARITY.md) records the
local statements and their proof or execution status. Full entries for cited
manuscript sources are in the [bibliography](manuscript/references.bib).

| Source ID | Source and version | Reviewed material | Role here |
| --- | --- | --- | --- |
| [HE-P1-Code](#he-p1-code) | Homotopical Encryption at `e619391` | Fresh-sign and residual Lean import closure | Copied source proofs and fixed-mask cost comparison |
| [HE-P1-Text](#he-p1-text) | Homotopical Encryption Paper 1 at `62f20ff` | Fresh-sign normal form, explicit residual, cost gap, disclosure and oracle scope | Originating cochain and residual data |
| [HE-P3](#he-p3) | Homotopical Encryption Paper 3 local §8 draft based on `62f20ff` | Normalized certificate coefficients, degree feasibility, completeness, and sharpness | Finite-field selector and certificate collision square |
| [GOT](#got) | Local Galois Obstruction Theory manuscript, §4 and proof spine | Tagged graph pullback, idempotent comparison, and first-colon quotient | Agreement square and affine residual calculation |
| [GCT](#gct) | Galois Obstruction Theory at `ad5e755`, published geometric complexity results, and PEqualNP GCT rows | Orbit coordinates, polynomial separation, multiplicity comparison, and permanent level spaces | Finite symmetry and geometric complexity in Section 4 |
| [GODEL](#godel) | Grabmayr and Goldfarb | Coding and substitution, fixed-point lemma | Exact tracking and provability comparisons |
| [LOGIC](#logic) | Open Logic Text, release `2e19d09` | First-order completeness and arithmetic incompleteness | Semantic kernel examples |
| [CR](#cr) | Cook and Reckhow, JSL 44 (1979) | Proof systems, p-simulation, polynomial boundedness | Resource-bounded comparison |
| [VV](#vv) | Valiant and Vazirani, TCS 47 (1986) | Randomized reduction to distinguishing zero and one satisfying assignments | Empty off-diagonal residual and witness feasibility |
| [ML](#ml) | Mathlib at `56a0058` | Linear-map kernels, finite-dimensional rank–nullity | Lean algebra and the cardinality derivation |
| [ST](#st) | Stacks Project, Tags 00DT and 04PN | Chinese remainder and idempotents of spectra | Background for the finite split scheme realization |
| [PEQ](#peq) | PEqualNP public `MetaComplexity.lean` | Bounded circuit semantics | External comparison target |

## HE-P1-Code

Homotopical Encryption's Lean sources were copied from
[`e619391ec7d40c5349ebe31846e24461e0b49649`](https://github.com/what-social-construct/homotopical-encrypt/tree/e619391ec7d40c5349ebe31846e24461e0b49649/lean).
The 40 files are the local import closure of
[`HCP.CoupledSignResidual`](lean/HCP/CoupledSignResidual.lean), including
the [general residual split](lean/HCP/CoupledCVPResidual.lean) and
the [native fresh-sign sampler](lean/Protocol/Transfer/PathSignature/NativeSignSampler.lean).
The [MIT notice](lean/LICENSE) accompanies the copies. They were checked
byte for byte against that revision. The local
[`distinct_messages_same_minimum`](lean/PvsNP.lean) combines mask
injectivity and the copied `cost_at_message` theorem.

## HE-P1-Text

Paper 1, *Homotopical Encryption*, reviewed in the local repository at
[`62f20ffd0dc8bf643fe72511dc80c04b8825883f`](https://github.com/what-social-construct/homotopical-encrypt/tree/62f20ffd0dc8bf643fe72511dc80c04b8825883f/papers/paper1).
The fresh-sign section gives $b=(a,0,(d+1)A\tau)$. The CVP section gives the
projection, explicit residual, gap, and the finite disclosure count for
unconstrained sign keys. The update records the original recovery comparison
in its fixed-oracle query model. The affine constraint and disclosure-kernel
comparison in this repo specialize the witness family at the decoded cochain
boundary. Probability claims here refer to uniform finite affine fibers.

## HE-P3

Paper 3, *Capacity-Radius Proximity for Smooth-Domain Reed–Solomon
Codes*, local §8 working draft reviewed on 2026-11-26. The checked-out
base was [`62f20ffd0dc8bf643fe72511dc80c04b8825883f`](https://github.com/what-social-construct/homotopical-encrypt/tree/62f20ffd0dc8bf643fe72511dc80c04b8825883f).
The draft section and four agreement modules were local additions at
that base. Their content hashes identify the source snapshot.

| Source path | SHA-256 |
| --- | --- |
| `papers/paper3/sections/07a-polynomial-agreement.tex` | `33508eb5da1420bafcc340faf882af19c5813168568483e55fc567f192794610` |
| `lean/Proximity/Core/PolynomialAgreement.lean` | `b54583df4e2c6a59c6b60d1d548a520fa6da2b95699b0a87d408ffca5ba6654e` |
| `lean/Proximity/Core/PolynomialAgreement/Boundary.lean` | `c2368673020040713476b27dabdd8920d577814b9d7b2610275a46ad3a72bc66` |
| `lean/Proximity/Core/PolynomialAgreement/Completeness.lean` | `79a4f6c76831f00c3969ecfee0c810874b1e8e577dbe8d42ca81f23832d90124` |
| `lean/Proximity/Core/PolynomialAgreement/Sharpness.lean` | `1e4b365d299e474529d19eb33140778caa8534d5bb897d02cecd481e32772e63` |

The 16 Lean files under [`lean/Proximity/`](lean/Proximity/) are the
byte-identical import closure under the [MIT notice](lean/LICENSE).
The other 12 files match the base commit. The closure's SHA-256 over
lines `<file SHA-256>  <repo-relative path>` in ascending path order
with a trailing newline per line is
`591f59fb42003ca3aac0bd23e62f6fbfe0a9e805768cccb60410758274d2f874`.

The local [Lean bridge](lean/PvsNP/AgreementCertificate.lean) applies
the affine collision square to the imported coefficient map. The
[prime-field executable](polynomial_agreement_selector.py) implements
the draft's row-reduction and degree search for these equations.

## GOT

Galois Obstruction Theory, local manuscript §4,
`manuscript/04-realization-comparisons/section.tex`. Reviewed the agreement
pullback and the square carrying multiplication by the diagonal idempotent
to multiplication by the equal-pair indicator. The local source
`GaloisObstructionTheory/Hodge/Collision/Agreement.lean` also identifies a
graph pullback with the equalizer. Its semantic-parity register also records
the tracked substitution diagram and the provable fixed point as separate
rows under arithmetized syntax. This repository uses those comparison
conventions with affine witness fibers and finite split schemes.

The local proof spine's first-colon comparison identifies the colon
quotient with the collision algebra modulo the annihilator of the diagonal
ideal. The [Boolean calculation](manuscript/02-affine-disclosure/section.tex)
identifies that annihilator with the diagonal factor. The
[agreement square](manuscript/03-complexity/section.tex) specializes the
tagged graph pullback to the two Boolean evaluations on the common
parameter space.

The reviewed local files are pinned by SHA-256.

| File in the local Galois tree | SHA-256 |
| --- | --- |
| `GaloisObstructionTheory/Hodge/Collision/Agreement.lean` | `24df316a759740f09287950f0c2130ed72aec382ead208273608aada4005d0dc` |
| `GaloisObstructionTheory/Jacobian/General/GenericFiber/ResidualBaseChange.lean` | `1cdd25cb5d1eef0f5bb576c58b316df5a2e6b6b7a07b649d1b5e4cb207233bcc` |

## GCT

The committed Galois Obstruction Theory
[`OrbitMatrices.lean`](https://github.com/what-social-construct/galois-obstruction-theory/blob/ad5e75521550e4a1dbcbe47150305e9624001915/GaloisObstructionTheory/Hodge/LinearAlgebra/OrbitMatrices.lean)
is copied byte-for-byte to [the local orbit-coordinate module](lean/PvsNP/GaloisOrbitMatrices.lean).
Its SHA-256 is `07349c8b74bdba9a3d305561e79d79719c5aaa1a8fa959bba096a6a0d1347619`.
Both projects pin Lean 4.35.0 and Mathlib `56a0058`.
The [local Lean bridge](lean/PvsNP/FiniteSymmetry.lean) adds the inverse
pullback action on coefficient functions, the commutation equivalence,
and the dimension formula. The separate [closure criterion](lean/PvsNP/OrbitClosureSeparation.lean)
uses Mathlib's `MvPolynomial.vanishingIdeal` and `zeroLocus`.

[Bürgisser, Ikenmeyer, and Panova, Theorem 1.4](https://arxiv.org/html/1604.06431v3)
supplies the occurrence-support barrier for padded permanent versus
determinant when $n\ge m^{25}$. The coordinate-ring multiplicity argument
is the graded version of their restriction comparison. [Dörfler,
Ikenmeyer, and Panova](https://arxiv.org/abs/1901.04576) give a separate
setting where multiplicities separate the varieties.

PEqualNP's [`L-gct-086`](https://data.pequalnp.com/data/lemma/L-gct-086.ab79638c0716.json)
asks for a uniform linear bound on the dimension of a constant-permanent
level space at the all-ones matrix. Its checked
[`L-gct-077`](https://data.pequalnp.com/data/lemma/L-gct-077.7d7a761736dd.json)
gives the conditional border determinantal lower bound from a dimension
bound. [`L-gct-231`](https://data.pequalnp.com/data/lemma/L-gct-231.c93684f58e76.json)
asks for a symmetric three-dimensional level space at $J_4$. The
[written derivation](manuscript/03-complexity/gct.tex) and
[executable check](gct_permanent_fiber.py) give an exact two-dimensional
example and the support-specific upper bound. The three-dimensional
question is recorded as a conjecture. The written Hessian argument gives
an overall upper bound of four in the symmetric order-four problem, with
the rank-nine calculation checked by the executable.

The [three-plane constraints](manuscript/03-complexity/gct-three-plane.tex)
are local written derivations from permanent coefficients, the
rank-two Schur complement, and simultaneous regular Klein four
permutations. The exact executable checks the order-four transverse
coefficient constraints for an arbitrary symmetric extension of the
star plane, the rank-one expansion, and the coefficient identities
in all four character spaces. The general star maximality proof uses
the block permanent identity over $\mathbb C$ for every $n\ge3$.

Chloe van der Vlugt's [Jacobian collision Paper I](https://github.com/what-social-construct/jacobian-collision-geometry/blob/e3b8a200de998e808a61ed2b76bd36db5d0156b8/paper/paper1.tex)
and its [canonical Lean theorem](https://github.com/what-social-construct/jacobian-collision-geometry/blob/e3b8a200de998e808a61ed2b76bd36db5d0156b8/CollisionIdeals/ComplexThree/Cubic/Canonical.lean)
were reviewed at `e3b8a200de998e808a61ed2b76bd36db5d0156b8`.
The theorem takes the three-dimensional Keller condition, generic degree
three, and the explicit Keller–Galois rigidity input. It identifies the
generic collision algebra with $L\times N$, with first projection the
diagonal map and $\operatorname{Gal}(N/K)\cong S_3$. For the permanent problem
we adopt the method of isolating the equations left by an exact
reduction. The Witt charts and the zero-row-sum exclusion are local
derivations from permanent coefficients. The [executable](gct_permanent_fiber.py)
generates the four remaining systems and checks the finite-field rank
certificate used in the zero-row-sum argument.

The [modular obstructions](manuscript/03-complexity/gct-modular.tex) use
the Stacks Project results [projective implies proper, Tag 01WC](https://stacks.math.columbia.edu/tag/01WC)
and [valuative criterion for properness, Tag 0BX5](https://stacks.math.columbia.edu/tag/0BX5).
The two geometric special-fiber exclusions are written reductions to
unit-ideal checks. The [modular executable](gct_permanent_modular.py)
checks the rank obstructions over the algebraic closures at 11 and 23
via explicit chart equations and polynomial operations in the prime
fields. It also checks absence of rational points at 5 and 7 by exact
enumeration and compatibility. The latter two checks supply the local
and global arithmetic restrictions via the valuative criterion.

The [three-cycle calculation](manuscript/03-complexity/gct-three-plane.tex)
uses simultaneous index relabeling. The [permanent checker](gct_permanent_fiber.py)
computes the fixed-sector ideals over $\mathbb Q$, $\mathbb F_5$,
$\mathbb F_7$, and $\mathbb F_{11}$ and the eigencubic by exact expansion. The point count for
the nonnormal cubic case is a written application of commuting relabeling
and arithmetic actions, conditional on the candidate's cubic field of
definition. [Sutherland, Section 2.1](https://math.mit.edu/~drew/ArithmeticEquivalenceLectureNotes.pdf)
supplies the unramified Frobenius cycle interpretation. The JC3 Paper I
result concerns the generic extension of a degree-three Keller map.

The [involution chart checks](gct_permanent_involutions.py) establish
geometric emptiness of the relevant invariant-plane loci in
characteristic 11. The written proof applies the same projective
specialization as the rank exclusions. The [quadratic-field checker](gct_permanent_f25.cpp)
uses an explicit Witt basis over $\mathbb F_{25}$ and exhausts the
three representative charts by necessary column and pair tests.
The ordinary-diagonal classification and its extension kernels
are local derivations verified by [the coefficient checker](gct_permanent_fiber.py).

The [two-plane extension reduction](manuscript/03-complexity/gct-extension.tex)
uses [Stacks Project, Tag 0D4I](https://stacks.math.columbia.edu/tag/0D4I)
for upper semicontinuity of geometric fiber dimension of the proper
rank locus. [Lean](lean/PvsNP/LevelSetExtension.lean) checks linearity
of the first coefficient, the kernel dimension argument, and the
hyperplane reduction for a downward-closed level predicate. The
[executable](gct_permanent_extensions.py) checks all prime-field
two-planes and the residual polynomials modulo 5. The geometric lift
of this check fixes the given rational two-plane before specializing.

[PEqualNP Ideas discussion #37059](https://github.com/open-goat/pequalnp-proofs/discussions/37059)
was posted on 2026-11-26. It asks for a helper step on the hyperplane
section and first-variation bound for `L-gct-231`.
The [public follow-up](https://github.com/open-goat/pequalnp-proofs/discussions/37059#discussioncomment-19935662)
records the two-edge exclusion and its specialization argument.

The [Plücker-cut generator and checks](gct_permanent_plucker.py) use the
same permanent coefficients as the extension checker. The finite-field
counterexample to first-order cut emptiness is verified by direct
expansion and a rank minor. The four one-edge extension systems were
checked using [msolve v0.11.0](https://msolve.lip6.fr/) in exact
prime-field Gröbner mode. The [written specialization and chart proof](manuscript/03-complexity/gct-extension.tex)
then gives the single-edge exclusion over $\mathbb C$ and the 24-system
cover at 5. The generator includes the full extension equations in
those systems.

The local Galois Obstruction Theory repository was reviewed at
`cc62910fc1b817708be644fbe4486d19c710af9b`. The existing
`OrbitMatrices.lean` source is unchanged from `ad5e755`. Its
orbit-coordinate method informs the reduction of pivot triples to
star, triangle, and path representatives. The [path reduction](manuscript/03-complexity/gct-extension.tex)
and the 16 opposite-edge checks are new. The prime-field check replays
unit-ideal membership by row operations and monomial multiplication
through degree seven on the input polynomials. The unrestricted path
system was exported for exact msolve and the run ended before a basis
was produced.

The matching-direction extension uses the same block identity and the
previous single-edge exclusion. The [pencil generator](gct_permanent_plucker.py)
checks the two polar identities over $\mathbb Q$ modulo $h^2-2$. All
three normalized matching systems were checked over $\mathbb F_5$ with
[msolve v0.11.0](https://msolve.lip6.fr/) in exact Gröbner mode
(`-g 2 -l 2`) and return the unit basis. The [written coverage argument](manuscript/03-complexity/gct-extension.tex)
uses projectivity of the rank-drop incidence for the complex conclusion.

The adjacent-edge extension uses the permanent cofactor formula
obtained by expanding along the last row and column. The [written argument](manuscript/03-complexity/gct-extension.tex)
reduces the nonsingular cofactor case to a symmetric order-three
two-plane and the singular case to one fixed adjacent direction.
The order-three chart and ten extensions through that fixed direction
give unit bases over $\mathbb F_5$. The generator checks the identities
over exact coefficients and emits the msolve systems.

The same section derives the path-reversal change of coordinates and
the averaging identity for bounded-degree certificates. A pilot
standard F4 run with those coordinates ended before returning a basis.
The subsequent exact degree-seven search uses the same 31 adapted
generators over $\mathbb F_5$. Sparse row elimination gives rank
130,832 for the 147,622 by 240,460 even matrix. The
[stored functional](gct_permanent_path_degree7.dual.gz) and its
[independent verifier](gct_permanent_plucker.py) certify separation of
the constant from the row span. The verifier checks every original row
and needs only the functional, without the elimination transcript.

The Homotopical Encryption local repository was reviewed at
`1ed8d55b67f266414cb7b1c55858f8b5566d4013`. Its Paper 3
`lean/Proximity/Core/PolynomialAgreement/Boundary.lean` supplies
`coefficientSystem_fiber` and the normalized affine-kernel pattern.
That file last changed at `8dcf71d23e0cbfc8c917f0106b6572efe4ce703c`.
Monic substitutions in the older cut charts were checked locally.
They save variables while raising degrees in some charts. The chosen
path presentation keeps the original coefficient degrees.

## GODEL

Balthasar Grabmayr,
[*On the Invariance of Gödel's Second Theorem with Regard to Numberings*](https://arxiv.org/abs/1803.08392),
and Warren Goldfarb,
[*Notes on Metamathematics*](https://people.math.harvard.edu/~wboney/spring19/Goldfarb_NotesonMetamath.pdf).
Grabmayr supplies the coding conventions used by the local Galois register.
Goldfarb's fixed-point lemma makes the numeral substitution and provable
biconditional explicit. The [Lean tracking statement](lean/PvsNP/Compatibility.lean)
assumes the substitution law for the chosen code. The diagonal lemma is
cited in the [manuscript](manuscript/01-compatibility/section.tex).

The local sequel files `research/sequel/GodelSquares.lean` and
`research/sequel/RealizationChecking.lean` were reviewed at Galois
Obstruction Theory `cc62910`, with their last revision `4d104436d1c9020612cb671aaf4945fdb69befb7`.
They describe the coding comparisons and a proposed checker. The
existing [Lean compatibility lemmas](lean/PvsNP/Compatibility.lean)
check the descent and reflection principles. The path calculation
checks the chart cover and replays its finite-field subsidiary
certificates against the polynomial generators.

## LOGIC

[*The Open Logic Text*](https://builds.openlogicproject.org/open-logic-complete.pdf),
release `2e19d09`. Reviewed the all-model consequence formulation of first-order
completeness and Chapter 37's fixed-point and incompleteness arguments for
computably axiomatized extensions of Robinson arithmetic. The manuscript
uses these results to distinguish the kernel for the standard-model comparison
from the kernel for the comparison over all models.

## CR

Stephen A. Cook and Robert A. Reckhow,
[*The Relative Efficiency of Propositional Proof Systems*](https://doi.org/10.2307/2273702).
Reviewed [the paper](https://www.cs.toronto.edu/~sacook/homepage/cook_reckhow.pdf),
especially the definition of p-simulation and Proposition 1.6. The manuscript
uses the exact identity on the proved formula and the polynomial bound on
the translator as separate hypotheses. The polynomial proof length result
belongs to the `NP = coNP` comparison.

## VV

Leslie G. Valiant and Vijay V. Vazirani,
[*NP is as easy as detecting unique solutions*](https://ics.uci.edu/~vazirani/ValVaz.pdf),
Theoretical Computer Science 47 (1986), 85–93. Theorem 1.1 reduces SAT
in randomized polynomial time to distinguishing formulas with zero or
one satisfying assignment, allowing arbitrary answers on formulas with
multiple assignments. This supports the [witness selection comparison](SEMANTIC-PARITY.md#witness-selection-under-prefix-restrictions)
for the zero-or-one promise.

## ML

Lean 4.35.0 and Mathlib are pinned in the
[toolchain file](lean/lean-toolchain) and [Lake manifest](lean/lake-manifest.json).
The [kernel declarations](https://github.com/leanprover-community/mathlib4/blob/56a005855ea17e0b0958f73ec801ae140b0a1679/Mathlib/Algebra/Module/Submodule/Ker.lean)
support the affine comparison. The
[finite-dimensional lemmas](https://github.com/leanprover-community/mathlib4/blob/56a005855ea17e0b0958f73ec801ae140b0a1679/Mathlib/LinearAlgebra/FiniteDimensional/Lemmas.lean)
include `LinearMap.finrank_range_add_finrank_ker`, used in the written
cardinality derivation.

## ST

The Stacks Project, [Chinese remainder](https://stacks.math.columbia.edu/tag/00DT)
and [open and closed subsets of spectra](https://stacks.math.columbia.edu/tag/04PN).
The reviewed statements concern comaximal factors and the
idempotent–clopen correspondence. In the finite product of copies of
$\mathbb F_2$, every subset has its characteristic idempotent. The
[manuscript](manuscript/02-affine-disclosure/section.tex) obtains that
product directly from the Boolean equations and cites Tag 04PN for the
clopen splitting.

## PEQ

PEqualNP's [circuit-size definitions](https://github.com/open-goat/pequalnp-proofs/blob/main/lean/PEqualNP/Defs/MetaComplexity.lean)
and [contribution rules](https://github.com/open-goat/pequalnp-proofs/blob/main/CONTRIBUTING.md)
were reviewed as the external comparison surface. `HasCircuitSize` supplies
a candidate bounded circuit predicate for comparing the projected agreement
locus with the public repository's definitions. The affine witness square
has its own definitions and proof in this repository.

The [public contribution fork](https://github.com/what-social-construct/pequalnp-proofs)
was set up against [upstream revision `36665a9`](https://github.com/open-goat/pequalnp-proofs/tree/36665a9146d4653d38f068739425e4f50bc52f54)
with Lean 4.36.0 and Mathlib revision `fc4f59e577feb1a4956671bc04ac18aaaf8cd842`.
The reviewed [reduction `R_meta_4211_1`](https://github.com/open-goat/pequalnp-proofs/blob/36665a9146d4653d38f068739425e4f50bc52f54/lean/PEqualNP/Outside/R_meta_4211_1.lean)
separates the construction of an extra OR gate from the lower bound for the
resulting single-output circuit.

The [posted finite covering statement `L-meta-19020`](https://data.pequalnp.com/data/lemma/L-meta-19020.cdb60ec996e9.json)
uses cyclic incidence offsets \(\{0,1,3,9\}\) modulo 13. The Python check
enumerated 560 point sets meeting each line in at most two points and 560
line sets meeting each point in at most two lines. It rejected pairs with an
incidence, then tested containment in the 468 distinct supports obtained by
translating, scaling, and exchanging sides with negation as in the posted
statement.

At [upstream revision `efe70b48`](https://github.com/open-goat/pequalnp-proofs/tree/efe70b48),
the merged reductions `R_meta_17715_1`, `R_meta_17918_2`, and
`R_meta_17920_2` give the exact hypotheses used for three local Lean
checks. The one-gate case uses two disjoint incident inputs. The
primary-output cases use preservation of the initial wire list by
circuit evaluation and a singleton input. These checks used only
`PEqualNP.Defs` from the public fork.
The public records for [`L-meta-17715`](https://data.pequalnp.com/data/lemma/L-meta-17715.f395b591f5b1.json),
[`L-meta-17918`](https://data.pequalnp.com/data/lemma/L-meta-17918.6648ce2ba458.json),
and [`L-meta-17920`](https://data.pequalnp.com/data/lemma/L-meta-17920.c6f1d5548070.json)
record these as surplus reductions.

The [merged reduction for `L-meta-17243`](https://github.com/open-goat/pequalnp-proofs/pull/24293)
uses the two empty-set rejection tests to exclude primary output wires.
It removes missing wires and repeated indices from the selected list,
preserving the OR of its values on every input. A positive incidence
test makes the resulting list nonempty. The lower bound then has two
cases, according to whether the list has one or two distinct generated
wires. The public row allowed reductions, and the desk issued a
prove-only reservation. The desk recorded the reservation as submitted
after the one-file PR opened. It merged on 2026-11-26 as
[`8ecc5c6`](https://github.com/open-goat/pequalnp-proofs/commit/8ecc5c65716ed002115ddf8fb07fc0c9cd43511e).
The [public lemma record](https://data.pequalnp.com/data/lemma/L-meta-17243.2cb64b4c8004.json)
records it as a surplus reduction because a new child would be at depth
3. At depth 1, [`L-meta-1990`](https://pequalnp-desk.pequalnp.workers.dev/desk/row?gap=L-meta-1990)
is already reduced by [PR #21167](https://github.com/open-goat/pequalnp-proofs/pull/21167)
to the AND-last case `L-meta-17243` and the OR-last case
[`L-meta-17245`](https://data.pequalnp.com/data/lemma/L-meta-17245.70e7330d99bd.json).
The separate first-gate split [PR #24564](https://github.com/open-goat/pequalnp-proofs/pull/24564)
passed its checker and was closed because the desk permits one case split
per step. The [intake decision](https://github.com/open-goat/pequalnp-proofs/pull/24564#issuecomment-7193607202)
explicitly leaves cuts from smaller statements eligible.

The [parent-level draft](contributions/pequalnp/R_meta_1990_997.lean)
uses the exact [posted `L-meta-1990` conclusion](https://data.pequalnp.com/data/lemma/L-meta-1990.307c700bb206.json).
The statement text has SHA-256
`2442775baf0d3a6e9b75afaa8ffedbd36889b06870286f38eb1cd61123e03166`.
The proof reuses the output normalization from PR #24293, then takes the
gate-list prefix through the latest selected wire. The prefix preserves
every selected wire's evaluation and weakly decreases the circuit size.
The AND-last branches take the same two hypotheses as PR #24293. The
OR-last branch restricts `L-meta-17245` to normalized output lists that
include the circuit's last wire. The draft imports only `PEqualNP.Defs`
and compiled in the public fork at `df9266f`, with the Lean and Mathlib pins
above.

The [merged sparse-to-full reduction #9384](https://github.com/open-goat/pequalnp-proofs/pull/9384)
uses three hypotheses. Its second hypothesis says that every incidence-free
pair has at most three vertices on one side. The local
[Lean incidence module](lean/PvsNP/IncidenceObservations.lean) proves that
finite implication with kernel-checked `decide` and proves the observation
equivalence for monotone scans. Its cyclic incidence relation and example
rows are those of [`L-meta-1990`](https://data.pequalnp.com/data/lemma/L-meta-1990.307c700bb206.json)
and the full-function target [`L-meta-972`](https://data.pequalnp.com/data/lemma/L-meta-972.9ae53fe249f7.json).

The local [gate-elimination experiment](contributions/pequalnp/incidence_gate_elimination.py)
uses the constant-wire and reader conditions in the upstream
[Lean proof of `L-meta-18649`](https://github.com/open-goat/pequalnp-proofs/blob/da164f9fce46e9d5fdbf7fd03514b202643e82ed/lean/PEqualNP/Outside/L_meta_18649.lean).
It independently builds shortened AND/OR circuits for the two explicit
star factorizations and verifies their semantics by equality of minimal
true sets. The published theorem allows NOT gates in its conclusion.
[`L-meta-9738`](https://data.pequalnp.com/data/lemma/L-meta-9738.7288f9095344.json)
states the conjectural 59-gate AND/OR lower bound for the deletion of line
zero, with the surviving lines relabeled by negation. The local 59- and
48-gate constructions supply upper bounds for
the two restrictions.

For [`L-meta-23645`](https://pequalnp-desk.pequalnp.workers.dev/desk/row?gap=L-meta-23645),
the eight-gate witness uses the posted mask and index convention
$6\min(i,j)+\max(i,j)$. Python independently checked all 36 ordered pairs.
The one-file proof passed the import guard and built in PEqualNP at
[`3e40e23`](https://github.com/open-goat/pequalnp-proofs/tree/3e40e235a483fecb6e978ad624645d8f7ada48be)
with the pinned Lean 4.36.0 and Mathlib `fc4f59e` environment.
The source at [fork commit `43991a8`](https://github.com/what-social-construct/pequalnp-proofs/commit/43991a848dfb227f87792a3576b34217619f02bd)
has SHA-256 `9728dc71a3fed98fbf20a378302114cf21f5c04fa957ac6c2b5b00f4e4a034b6`.
[PR #33168](https://github.com/open-goat/pequalnp-proofs/pull/33168) was
opened on 2026-11-26, and the desk recorded the reservation as submitted.
The desk subsequently marked the step proved after
[PR #32240](https://github.com/open-goat/pequalnp-proofs/pull/32240)
merged the proof file at
[`4211944`](https://github.com/open-goat/pequalnp-proofs/commit/4211944feb4bb0c0ca21f6b62a901dbfbbfc493b).
Intake closed #33168 on the same day because the other proof had already
merged. [Closure notice](https://github.com/open-goat/pequalnp-proofs/pull/33168#issuecomment-7203883959)
