# Source ledger

Local theorem targets reviewed 2026-11-27. Source IDs refer to a specific text, code revision, or
external definition. The [parity register](SEMANTIC-PARITY.md) records the
local statements and their proof or execution status. Full entries for cited
manuscript sources are in the [bibliography](manuscript/references.bib).

| Source ID | Source and version | Reviewed material | Role here |
| --- | --- | --- | --- |
| [HE-P1-Code](#he-p1-code) | Homotopical Encryption at `e619391` | Fresh-sign and residual Lean import closure | Copied source proofs and fixed-mask cost comparison |
| [HE-P1-Text](#he-p1-text) | Homotopical Encryption Paper 1 at `62f20ff` | Fresh-sign normal form, explicit residual, cost gap, disclosure and oracle scope | Originating cochain and residual data |
| [HE-P3](#he-p3) | Homotopical Encryption Paper 3 local §8 draft based on `62f20ff` | Normalized certificate coefficients, degree feasibility, completeness, and sharpness | Finite-field selector and certificate collision square |
| [GOT](#got) | Local Galois Obstruction Theory manuscript, §4 and proof spine | Tagged graph pullback, idempotent comparison, and first-colon quotient | Agreement square and affine residual calculation |
| [GCT](#gct) | Pinned Galois orbit and commutant exports, published geometric complexity results, and PEqualNP GCT rows | Orbit coordinates, polynomial separation, multiplicity comparison, and permanent level spaces | Finite symmetry and geometric complexity in Section 4 |
| [GODEL](#godel) | Grabmayr and Goldfarb | Coding and substitution, fixed-point lemma | Exact tracking and provability comparisons |
| [LOGIC](#logic) | Open Logic Text, release `2e19d09` | First-order completeness and arithmetic incompleteness | Semantic kernel examples |
| [CR](#cr) | Cook and Reckhow, JSL 44 (1979) | Proof systems, p-simulation, polynomial boundedness | Resource-bounded comparison |
| [VV](#vv) | Valiant and Vazirani, TCS 47 (1986) | Randomized reduction to distinguishing zero and one satisfying assignments | Empty off-diagonal residual and witness feasibility |
| [APT](#apt) | Aspvall, Plass and Tarjan, IPL 8 (1979), Theorem 1 | Implication graph and complementary literals in strong components | Correctness of the local 2-CNF prefix compiler |
| [ML](#ml) | Mathlib at `56a0058` | Linear-map kernels, finite-dimensional rank–nullity | Lean algebra and the cardinality derivation |
| [ST](#st) | Stacks Project, Tags 00DT and 04PN | Chinese remainder and idempotents of spectra | Background for the finite split scheme realization |
| [PEQ](#peq) | PEqualNP public `MetaComplexity.lean` | Bounded circuit semantics | External comparison target |

## APT

Aspvall, Plass and Tarjan, “A Linear-Time Algorithm for Testing the Truth
of Certain Quantified Boolean Formulas,” 1979, pp. 121–123. Theorem 1
characterizes satisfiability by complementary literal pairs in the same
strong component. [Original paper](https://mathweb.ucsd.edu/~sbuss/CourseWeb/Math268_2007WS/2SAT.pdf)

The [local prefix construction](manuscript/03-complexity/prefix-collision.tex)
combines component equalities with pins from the prefix's implication
closure. The [compiler](python/two_sat_prefix.py) uses the existing binary
elimination routine. The [Lean module](lean/PvsNP/PrefixCollision.lean)
proves the tagged fiber equivalence, the linear-verifier prefix
specialization and the finite candidate-weight construction. The 2-CNF
graph argument is written and its implementation has executable tests.

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
that base. They are available with the same contents at
the [public source revision `1ed8d55`](https://github.com/what-social-construct/homotopical-encrypt/tree/1ed8d55b67f266414cb7b1c55858f8b5566d4013).
Their content hashes identify the source snapshot.

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
[prime-field executable](python/polynomial_agreement_selector.py) implements
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

For the two reduced permanent sections, the
[pinned decomposition-defect criterion](https://github.com/what-social-construct/galois-obstruction-theory/blob/4d104436d1c9020612cb671aaf4945fdb69befb7/GaloisObstructionTheory/Hodge/Collision/DecompositionDefect.lean)
identifies the idempotent case by the overlap and contact ideals.
The [local derivation](manuscript/03-complexity/collision-pencil-fiber.tex)
takes the self-product of each section over the prime field. The
[checker](python/gct_collision_fiber_slice.py) constructs its diagonal
projector from the squarefree eliminant and verifies the field-factor
projectors by the Chinese remainder theorem. The finite étale
interpretation uses [Stacks, Tag 00U3](https://stacks.math.columbia.edu/tag/00U3).
The rank exclusion comes from the separate permanent net. The
witness-prefix equivalence and its algorithmic conditions are recorded
in the [selector parity entries](SEMANTIC-PARITY.md).

### Handoff to Galois collision

P-vs-NP consumes three reviewed Lean exports from Galois Obstruction Theory
at `4f8a63cd946ab4a99d4fffe2bd42c1043f5c7d4a`. Both checkouts pin
Lean 4.35.0 and Mathlib `56a005855ea17e0b0958f73ec801ae140b0a1679`.
The [export lock](lean/galois-exports.json) records each upstream path,
the selected line range where applicable, the public destination and its
SHA-256. Every exported proof block already appeared in P-vs-NP at
[0f4dac1](https://github.com/what-social-construct/P-VS-NP/tree/0f4dac164889b7b82ec904d363fa61b9fc486a4f).
The public package builds from the tracked sources. The
[export verifier](python/galois_exports.py) also supports replay against
the pinned Git objects.

| Shared result | Source of the implementation | P-vs-NP responsibility |
| --- | --- | --- |
| Orbit coordinates | [Canonical orbit-matrix module](lean/GaloisObstructionTheory/Hodge/LinearAlgebra/OrbitMatrices.lean), complete file | Preserve the [old import](lean/PvsNP/GaloisOrbitMatrices.lean) and the finite-rank specialization. |
| Permutation commutant | [Five declarations](lean/GaloisExport/PermutationCommutant.lean) from `Hodge/LinearAlgebra/InvariantMatrixAlgebra.lean`, originally contributed from P-vs-NP at `96fa380` | Preserve the public [action and commutation API](lean/PvsNP/FiniteSymmetry.lean) and apply it to finite symmetry. The export retains its MIT attribution. |
| Quotient annihilator | [Selected theorem](lean/GaloisExport/QuotientAnnihilator.lean) from `Hodge/Collision/OffDiagonal.lean` for arbitrary ideals in a commutative ring | Apply it to the [readout normal form, base change and punctured image](lean/PvsNP/ReadoutResidual.lean), including nonreduced coefficient rings. |

**For the Galois maintainer.** Please return a stable module path and a
full commit hash for any narrow public export of these declarations.
Three further candidate modules are ready for review in the public
[P-vs-NP revision](https://github.com/what-social-construct/P-VS-NP/tree/0f4dac164889b7b82ec904d363fa61b9fc486a4f/lean/PvsNP):
[BranchCertificate](lean/PvsNP/BranchCertificate.lean) combines two
ideal-membership certificates over a commutative ring,
[InvariantClosure](lean/PvsNP/InvariantClosure.lean) bounds dimension
from a generator-stable span over a field, and
[AffineDisclosure](lean/PvsNP/AffineDisclosure.lean) identifies
equal-disclosure pairs over a ring with a kernel-direction product.
P-vs-NP owns these implementations until an upstream revision adopts them.

The requested realization comparison concerns a positive-dimensional
abelian variety over an algebraically closed field with a symmetric ample
class $H$. Positivity gives $Q_H(u-v)=0$ exactly when $u=v$ on
$\operatorname{End}^0(A)\otimes_{\mathbb Q}\mathbb R$.
For the mixed-degree and spectral comparisons, the complex linear
realization uses a prime $\ell$ different from the characteristic and an
abstract embedding $\overline{\mathbb Q}_\ell\hookrightarrow\mathbb C$.
The later Galois revision `b998bb79107cb1c9ebdc0fc5020287d7452d4ea5`
records the general positive-form equality criterion and its transport
under a nonzero scalar pullback by a linear map. Those Lean declarations
take positivity and the pullback identity as hypotheses. Their geometric
verification for the Rosati and Tate forms is given by the cited written
results. [Upstream comparison](https://github.com/what-social-construct/galois-obstruction-theory/blob/b998bb79107cb1c9ebdc0fc5020287d7452d4ea5/GaloisObstructionTheory/Hodge/LinearAlgebra/PolarizedDegreeComparison.lean)
The [P-vs-NP calculation](manuscript/03-complexity/collision-normalization.tex)
supplies a smooth model of genus 43, the traces of Frobenius and its
square, and the degree form on the span of the identity and Frobenius.
P-vs-NP also owns any proposed link from Jacobian endomorphisms to the
common-line condition. The latter link is open. The reference is the written argument
in the notes prepared for Christopher D. Long, revision
`117cb4e316eb7977ff7144e68ab8fe7c8c1f0f21`.
[Rosati form and its domain](https://github.com/long-mathematics/abelian-degree-polynomials/blob/117cb4e316eb7977ff7144e68ab8fe7c8c1f0f21/papers/abelian_comparison_streamlined.tex#L33-L81)
· [Frobenius on curve Jacobians](https://github.com/long-mathematics/abelian-degree-polynomials/blob/117cb4e316eb7977ff7144e68ab8fe7c8c1f0f21/papers/curve_rh_single_scale.tex#L45-L56)
· [Verification scope](https://github.com/long-mathematics/abelian-degree-polynomials/tree/117cb4e316eb7977ff7144e68ab8fe7c8c1f0f21#current-papers--choose-by-mathematical-scope)

## GCT

The orbit-coordinate proof first reviewed at `ad5e755` has SHA-256
`07349c8b74bdba9a3d305561e79d79719c5aaa1a8fa959bba096a6a0d1347619`.
The [shared Lean exports](#handoff-to-galois-collision) provide the orbit
basis and commutant at the current pin. [FiniteSymmetry](lean/PvsNP/FiniteSymmetry.lean)
deduces the dimension formula from that basis. The separate [closure criterion](lean/PvsNP/OrbitClosureSeparation.lean)
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
[executable check](python/gct_permanent_fiber.py) give an exact two-dimensional
example and the support-specific upper bound. The three-dimensional
question is recorded as a conjecture. The written Hessian argument gives
an overall upper bound of four in the symmetric order-four problem, with
the rank-nine calculation checked by the executable.
The desk's [negated twin `L-gct-232`](https://pequalnp-desk.pequalnp.workers.dev/desk/row?gap=L-gct-232)
is the matching outside theorem for a nonexistence result. It asks for
the full Lean statement in `PEqualNP.Outside.L_gct_232`. The
[public contribution rules](https://github.com/open-goat/pequalnp-proofs/blob/aecf602ea3c8da01533a13d2ca03b633689f3033/CONTRIBUTING.md)
require an exact statement and a single-file proof.
The posted proposition elaborates against `PEqualNP.Defs` at that
revision with Lean 4.36.0 and Mathlib `fc4f59e`. The same revision's
[submission script](https://github.com/open-goat/pequalnp-proofs/blob/aecf602ea3c8da01533a13d2ca03b633689f3033/tools/pnp.sh)
supports taking an exact eligible row with `next --unit`, checking
the proof, and submitting the checked file. The full proof remains open.

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
derivations from permanent coefficients. The [executable](python/gct_permanent_fiber.py)
generates the four remaining systems and checks the finite-field rank
certificate used in the zero-row-sum argument.

The [modular obstructions](manuscript/03-complexity/gct-modular.tex) use
the Stacks Project results [projective implies proper, Tag 01WC](https://stacks.math.columbia.edu/tag/01WC)
and [valuative criterion for properness, Tag 0BX5](https://stacks.math.columbia.edu/tag/0BX5).
The two geometric special-fiber exclusions are written reductions to
unit-ideal checks. The [modular executable](python/gct_permanent_modular.py)
checks the rank obstructions over the algebraic closures at 11 and 23
via explicit chart equations and polynomial operations in the prime
fields. It also checks absence of rational points at 5 and 7 by exact
enumeration and compatibility. The latter two checks supply the local
and global arithmetic restrictions via the valuative criterion.

The [three-cycle calculation](manuscript/03-complexity/gct-three-plane.tex)
uses simultaneous index relabeling. The [permanent checker](python/gct_permanent_fiber.py)
computes the fixed-sector ideals over $\mathbb Q$, $\mathbb F_5$,
$\mathbb F_7$, and $\mathbb F_{11}$ and the eigencubic by exact expansion. The point count for
the nonnormal cubic case is a written application of commuting relabeling
and arithmetic actions, conditional on the candidate's cubic field of
definition. [Sutherland, Section 2.1](https://math.mit.edu/~drew/ArithmeticEquivalenceLectureNotes.pdf)
supplies the unramified Frobenius cycle interpretation. The JC3 Paper I
result concerns the generic extension of a degree-three Keller map.

The [involution chart checks](python/gct_permanent_involutions.py) establish
geometric emptiness of the relevant invariant-plane loci in
characteristic 11. The written proof applies the same projective
specialization as the rank exclusions. The [quadratic-field checker](gct_permanent_f25.cpp)
uses an explicit Witt basis over $\mathbb F_{25}$ and exhausts the
three representative charts by necessary column and pair tests.
The ordinary-diagonal classification and its extension kernels
are local derivations verified by [the coefficient checker](python/gct_permanent_fiber.py).

The [two-plane extension reduction](manuscript/03-complexity/gct-extension.tex)
uses [Stacks Project, Tag 0D4I](https://stacks.math.columbia.edu/tag/0D4I)
for upper semicontinuity of geometric fiber dimension of the proper
rank locus. [Lean](lean/PvsNP/LevelSetExtension.lean) checks linearity
of the first coefficient, the kernel dimension argument, and the
hyperplane reduction for a downward-closed level predicate. The
[executable](python/gct_permanent_extensions.py) checks all prime-field
two-planes and the residual polynomials modulo 5. The geometric lift
of this check fixes the given rational two-plane before specializing.

[PEqualNP Ideas discussion #37059](https://github.com/open-goat/pequalnp-proofs/discussions/37059)
was posted on 2026-11-26. It asks for a helper step on the hyperplane
section and first-variation bound for `L-gct-231`.
The [public follow-up](https://github.com/open-goat/pequalnp-proofs/discussions/37059#discussioncomment-19935662)
records the two-edge exclusion and its specialization argument.

The [Plücker-cut generator and checks](python/gct_permanent_plucker.py) use the
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
previous single-edge exclusion. The [pencil generator](python/gct_permanent_plucker.py)
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

For triangle support, the same cofactor argument reduces to a
rank-two radical pencil. The [generator and checker](python/gct_permanent_plucker.py)
check the five-variable rank exclusion by exact Gröbner basis and
emit a 12-variable pencil with reduced msolve basis `[1]` modulo five.
The [written incidence argument](manuscript/03-complexity/gct-extension.tex)
uses [Stacks Project, Tag 01WN](https://stacks.math.columbia.edu/tag/01WN)
to deduce finiteness from projectivity and containment in the fixed
affine star chart. The same executable separately checks a three-plane
in the special fiber at three of the integral tangent model.
[Lean](lean/PvsNP/LevelSetExtension.lean) checks the coordinate restriction
from four injective coordinates to an isomorphism onto three using
Mathlib's standard coordinate basis.

The same section derives the path-reversal change of coordinates and
the averaging identity for bounded-degree certificates. A pilot
standard F4 run with those coordinates ended before returning a basis.
The subsequent exact degree-seven search uses the same 31 adapted
generators over $\mathbb F_5$. Sparse row elimination gives rank
130,832 for the 147,622 by 240,460 even matrix. The
[stored functional](gct_permanent_path_degree7.dual.gz) and its
[independent verifier](python/gct_permanent_plucker.py) certify separation of
the constant from the row span. The verifier checks every original row
and needs only the functional, without the elimination transcript.

The four-cycle Fourier charts use the matching exclusion to ensure
that projection has rank three. The rotation action and averaging
are derived in the manuscript. The 313,629 by 390,755 weight-zero
matrix for omitted frequency two was reduced exactly by sparse
elimination grouped by the three column degrees. Its rank was
260,865. The [degree-eight functional](gct_permanent_cycle_omit2_degree8.dual.gz)
has 97,877 nonzero entries and was checked against all original rows
by the [independent verifier](python/gct_permanent_plucker.py).

The star Fourier coordinates use the $S_3$ action on the three leaves.
The [generator](python/gct_permanent_plucker.py) verifies descent from
$\mathbb F_{25}$, rotation weights, and reflection over exact
coefficients. Degree-seven invariant elimination gives rank 43,913 in
the matrix of 49,527 row orbits and 80,588 column orbits. Its
[functional](gct_permanent_star_degree7.dual.gz) is checked before
reflection against all 98,336 weight-zero products. The degree-eight
run ended after 155,700 of 209,809 rows without deciding the bound.

The center-diagonal change of coordinates uses the isolated-row
identity for the leading equations. [Python](python/gct_permanent_plucker.py)
checks that the 15 replacement quartics have the stated monic center
terms and verifies the order-three quadratic Hessian. The
[written boundary argument](manuscript/03-complexity/gct-extension.tex)
uses the existing order-three two-plane exclusion. A bounded native
degree-seven comparison reproduced the rank 43,913 with the rewritten
input and fewer modular coefficient updates.

The [Hodge decomposition](manuscript/03-complexity/gct-extension.tex)
uses the equal-disclosure pullback and residual convention recorded
under [GOT](#got). The corrected diagonal projection is derived from
the quadratic permanent coefficient. The exterior star pairing
uses the restricted edge form, and the orientation factors come from
adjoining a square root of its Gram determinant divided by four.
The [star generator](python/gct_permanent_plucker.py) verifies the
quadratic identity over the rationals and in the normalized frame
at five. It checks the discriminant on the scalar edge-graph line
and emits the collision and injective branch systems.

The 2026-11-26 field-extension review drew on the following working copies.
The JC3 checkout at `e3b8a20` contains a local
`CollisionIdeals/General/Normalization/QuadraticDVRParity.lean`
proving that a fraction-field square cannot have odd valuation
in a discrete valuation ring. The reviewed file has SHA-256
`679cf6af206561bc2b23c0d23e4bc6fa4c5b65e2382fdc3d1353b23ec938aa14`.
The Galois checkout at `ed50f62` extends the first-colon comparison
in `ResidualBaseChange.lean`, reviewed working-copy SHA-256
`ef4a15d4bf8346e28da1cb771003f56db59c0707ef966749d9cc4d06b0d20436`.
Both working files passed Lean in their respective checkouts.
The Hodge checkout at `7ace84b` has a working comparison of the
length-two square-map fiber with its reduced support in
`research/working/0065-projective-line-ramification-comparison.md`,
reviewed SHA-256
`2cee6a8928e18c8b72210d9a1d3e0797ad4f200d378c9a13b5ab87b4f9063f55`.
The committed [Hodge coefficient-descent theorem](https://github.com/what-social-construct/HodgeConjecture/blob/7ace84b545cb027f4dfceedb214bcdc9ac0835b4/HodgeConjecture/LinearAlgebra/GaloisDescent.lean#L111)
characterizes fixed tensors. Homotopical Encryption Paper 3 at
`1ed8d55` supplies the previously reviewed linear certificate
comparison in [`Boundary.lean`](https://github.com/what-social-construct/homotopical-encrypt/blob/1ed8d55b67f266414cb7b1c55858f8b5566d4013/lean/Proximity/Core/PolynomialAgreement/Boundary.lean#L94).

The [permanent manuscript](manuscript/03-complexity/gct-extension.tex)
derives its own first-colon ideal from the unit-minor charts and normalizes
its explicit orientation curve over the field of five elements. It uses
the elementary quadratic field inclusion to bound the residue degree
of a surviving lift. The general finite étale field decomposition is
recorded in [Stacks, Tag 00U3](https://stacks.math.columbia.edu/tag/00U3).
The [edge-family exporter](python/gct_permanent_hodge.py) checks the
transverse pencil and emits its full and fixed-pair systems. The same
tool emits the cyclic edge chart and the open transposition pair chart.
All four inputs give reduced Gröbner basis `[1]` in msolve 0.11.0
with `-t 1 -g 2 -l 2`. The transposition exclusion also uses the
previous adjacent-edge result at `a=b`. These permanent results have
written and executable evidence.

The [Lean umbrella](lean/PvsNP.lean) now exports the field-extension
and residual proofs. [QuadraticDVRParity.lean](lean/PvsNP/QuadraticDVRParity.lean)
ports the JC3 source identified above from Lean 4.28.0 to this project's
4.35.0. The port adds module-system imports and updates the simplification
of the valuation equality. The [upstream MIT notice](lean/PvsNP/LICENSE-JC3)
accompanies it. [ScalarOrientation.lean](lean/PvsNP/ScalarOrientation.lean)
uses that theorem on the scalar orientation equation and verifies the two
normalized roots explicitly as $\pm2(c-1)$.

[ReadoutResidual.lean](lean/PvsNP/ReadoutResidual.lean) delegates to the pinned export of
`comap_annihilator_map_quotient_eq_colon` from the Galois repo's
[OffDiagonal.lean](https://github.com/what-social-construct/galois-obstruction-theory/blob/4d104436d1c9020612cb671aaf4945fdb69befb7/GaloisObstructionTheory/Hodge/Collision/OffDiagonal.lean#L41).
The source file has SHA-256
`6417b50f17ce23dcbad0d0b8f689ede672e2b09c99a68e91152dee429823c599`.
The shared theorem identifies the diagonal annihilator with the first
colon. The local proofs compute the colon, the punctured-family image
kernel and the base-change identity over arbitrary commutative rings.
[ReadoutPivotIdeal.lean](lean/PvsNP/ReadoutPivotIdeal.lean) computes the
first colon directly from the three rows of a matrix on a unit-minor chart.
[PermanentReadout.lean](lean/PvsNP/PermanentReadout.lean) verifies
the cofactor parameter on a unit pivot and transfers the Gram determinant
identity to a field-degree bound. [OrientationDescent.lean](lean/PvsNP/OrientationDescent.lean)
constructs the Frobenius action on the coefficient extension of a lift
algebra. The absence of a degree-two full lift is supplied by the
existing extension-field enumeration.

[EdgeDiscriminant.lean](lean/PvsNP/EdgeDiscriminant.lean) computes the
Gram matrix of the explicit six-edge form in both test families.
[EdgeStabilizer.lean](lean/PvsNP/EdgeStabilizer.lean) identifies the
simultaneous relabeling equations and derives the orbit sizes from
the two geometric exclusions. The cyclic and transposition emptiness
results still use the external Gröbner calculations above.

For the fixed pair of transverse edge columns, the twelve generators in
[TransversePairData.lean](lean/PvsNP/TransversePairData.lean) come from
the six-variable `--emit-edge-family transverse-pair` system, whose
SHA-256 is `9f8b87c79b4c5b2aff3be155595dc277237f13478a1fa20b593a0fc5d552a0e4`.
Bounded polynomial elimination over
$\mathbb F_5$ supplied the twelve multipliers, with 755 nonzero terms
in total. [TransversePairChart.lean](lean/PvsNP/TransversePairChart.lean)
independently forms the four-by-four permanent from its permutations
and checks the declared coefficient expansion modulo five. Its
`sparseExpr_eval` lemma identifies each reflected coefficient with
ordinary polynomial evaluation on the six free diagonal entries.
[TransversePairCertificate.lean](lean/PvsNP/TransversePairCertificate.lean)
checks that the 14,018 term products combine to the constant one modulo
five. [TransversePair.lean](lean/PvsNP/TransversePair.lean) proves that
this computation preserves polynomial evaluation and derives absence of
a common zero over every field of characteristic five.
[TransversePairLevel.lean](lean/PvsNP/TransversePairLevel.lean) takes
the coefficients in the two polynomial parameters and applies this
identity to the permanent of the fixed pair.

The gluing square specializes the overlap and contact ideals in
[Galois Obstruction Theory, DecompositionDefect.lean](https://github.com/what-social-construct/galois-obstruction-theory/blob/4d104436d1c9020612cb671aaf4945fdb69befb7/GaloisObstructionTheory/Hodge/Collision/DecompositionDefect.lean),
reviewed at checkout `234b30818b07f690240ebef4006413ced73e1329`.
The file was last changed at `4d104436`. The [Gödel squares register](https://github.com/what-social-construct/galois-obstruction-theory/blob/234b30818b07f690240ebef4006413ced73e1329/research/sequel/README.md)
supplies the distinction between commuting maps and faithful realization.
[ReadoutGluing.lean](lean/PvsNP/ReadoutGluing.lean) gives a local proof of
the pullback for the determinant normal form.
[DiscriminantIdeal.lean](lean/PvsNP/DiscriminantIdeal.lean) compares its
image ideal with the pulled-back Gram discriminant over nonreduced rings.
[OrientationSquare.lean](lean/PvsNP/OrientationSquare.lean) checks the
two explicit rational Gram factorizations at the transverse frame and
two distinct factorizations with the same orientation.
[TransverseRestriction.lean](lean/PvsNP/TransverseRestriction.lean)
identifies the reflected permanent with Mathlib's matrix permanent and
specializes the three-parameter polynomial to the certified pair.

The same Galois checkout contained an untracked working file
`GaloisObstructionTheory/Hodge/Boundary/Examples/SquareCover.lean`,
reviewed SHA-256 `63f91d1cf54113a269561b466a7d203d202cf9019cb6da7efe5a2f72c5ba6367`.
It derives the branch contact ideal from the diagonal and residual
evaluations of the square cover. [OrientationContact.lean](lean/PvsNP/OrientationContact.lean)
computes the polynomial first colon locally and identifies the evaluated
ideal with the previously checked punctured-readout image.

Michel Coste's [*An Introduction to Semialgebraic Geometry*](https://arxiv.org/abs/2611.31550v1)
is dated October 2002 (arXiv v1 posted 2026-11-23). Theorem 2.3 gives
closure under real coordinate projection. Applied to the real and
imaginary components of the integer star equations, it places the
complex lift image in the semialgebraic category. Theorem 4.1 states
Hardt's triviality theorem. A point of each nonempty model fiber gives
a section in its product coordinates. The manuscript cites both
theorems and leaves the partition and full-lift selector uncomputed.
[RealOrientation.lean](lean/PvsNP/RealOrientation.lean) checks the
explicit positive-root section for the transverse orientation pencil and the
finite sum-of-squared-norms test used to encode complex common zeros.

The [kernel chart](python/gct_permanent_hodge.py) uses the Hadamard
coordinates from the [permanent fiber computation](python/gct_permanent_fiber.py)
and the written Witt chart coverage. [msolve v0.11.0](https://msolve.lip6.fr/)
returns the reduced basis [1] over $\mathbb F_5$ in exact sparse mode
on the six-variable system, including the field equation for $h$.
The emitted input has SHA-256
`4f2ac126324d02602f4e06ee96b9c14c68c28d90b420a25bbd41beed03b35e38`.
The same Python module checks the Gram matrix on all 156 rational
level two-planes at five. The proper specialization argument for the
closed rank locus and the orbit bound on each branch are written
derivations. The 17-variable collision chart fixes the first star
coordinate of the kernel line and uses leaf symmetry for coverage.
The executable verifies its kernel and quadratic pairing identities.
A bounded msolve run on this larger system reached degree seven without
deciding the ideal.

The [collision chart reduction](python/gct_collision_kernel_reduction.py)
uses those same 17 coordinates and the three polars of the permanent
at the kernel direction. The local [derivation](manuscript/03-complexity/collision-kernel-reduction.tex)
uses exact row operations capped at working degree seven for the rank test
and a five-variable reduced-basis comparison to obtain three chart opens for all possible completions.
The [kernel direction checker](python/gct_collision_direction.py)
uses the original permanent, the star normalization, and simultaneous
vertex permutations to define the degree-507 minor and its orbit sum.
It verifies the nonzero specialization, a degree-four identity for one,
and the enumeration of eligible prime-field lines. The argument over
the algebraic closure uses the evaluated monomial vector. The conclusion
over the rationals uses the properness results cited above.

The [quadratic-field census](python/gct_collision_f25.py) uses the
same pure kernel equations and the finite-field arithmetic from the
Frobenius checker, with \(\mathbb F_{25}=\mathbb F_5[\omega]/(\omega^2-2)\).
The [companion checker](python/gct_collision_f25_companion.py)
recovers and verifies the coefficients of an identity for one at each
orbit representative. The [quadratic-net checker](python/gct_collision_quadrics.py)
uses the three quadratic terms on the polar quotient. The
[rank bound and specialization proof](manuscript/03-complexity/collision-kernel-quadrics.tex)
are local written derivations. The calculation uses exact reduced
Gröbner bases from msolve v0.11.0 for the four exceptional rank cases.
The [projective slice](python/gct_collision_slice.py) restricts the
original permanent to the two stated hyperplanes and computes its
Hilbert function. The 24 distinct census points account for the
whole geometric slice. The local dimension argument uses the
[projective intersection theorem, Tag 0B2R](https://stacks.math.columbia.edu/tag/0B2R).
The complex conclusion applies proper specialization to the projective
flag incidence. These dimension bounds apply to directions satisfying
the quadratic completion conditions alone.

D'Andrea and Dickenstein, *Explicit formulas for the multivariate
resultant*, introduction and Lemma 3.4, give the projective
resultant criterion and its degree in each block of coefficients.
The [local specialization](python/gct_collision_eliminant.py) gives
kernel degree 180 and verifies that the polynomial is nonzero by a
rank calculation at five. [Primary source](https://arxiv.org/pdf/math/0007036)

The [pencil-fiber derivation](manuscript/03-complexity/collision-pencil-fiber.tex)
uses the same characteristic-five permanent and full polar-rank calculation.
The [curve checker](python/gct_collision_fiber_slice.py) reconstructs the
two hyperplane sections, their Jacobian ranks over their residue fields
and the singular scheme. The disjoint sections certify geometric
integrality by the component-degree argument in the manuscript.
The [local normalization calculation](python/gct_collision_normalization.py)
works over the quadratic residue field at the two geometric singularities.
It uses the original permanent equations to determine a square tangent
cone and a critical value of order six. The [smooth-model proof](manuscript/03-complexity/collision-normalization.tex)
derives the branch contact and genus and describes the smooth model by
three blowups at the successive reduced singular loci. Completion preserves the local
normalization defect. The Jacobian of the smooth projective model has
dimension equal to the genus and Tate-module rank twice that dimension.
[Stacks, delta and completion](https://stacks.math.columbia.edu/tag/0C3W)
· [Stacks, Picard groups of curves](https://stacks.math.columbia.edu/tag/03RN)

The point counts give traces of Frobenius and its square. Applying
the cited trace identity on the span of Frobenius and the identity gives
$Q_H(F-1)=270/43$. This comparison is a written derivation for the
normalized curve and its polarized Jacobian. The general degree form
and its source are recorded in the [Galois handoff](#handoff-to-galois-collision).

The [edge-face checker](python/gct_collision_fiber_net.py) excludes the
geometric support of both edge-orbit sections using polar sextic unit
identities. The [original slice](python/gct_collision_fiber_slice.py) and
[its four translates](python/gct_collision_translated_sections.py) apply
this test to every closed point of the five sections $d=a+rm$. They
construct the inverse of the reduced sextic in each residue-field
calculation and verify its product reduces to one. The section lengths
and multiplicities come from the original permanent equations by
elimination. Together with the earlier exclusion at $m=0$, these give
the prime-field pencil restriction in the manuscript.

The [pencil overlap calculation](python/gct_collision_pencil_orbits.py)
restricts the original permanent to the possible prime-field triples of
normalized edge differences. The [vertex fixed-point calculation](python/gct_collision_vertex_orbits.py)
restricts it to the projective eigenspaces of a transposition and a
three-cycle. These finite computations supply the overlaps and fixed
directions. The [quotient proof](manuscript/03-complexity/collision-vertex-orbits.tex)
uses the two branches at each singularity, the quartic with constant
leading coefficient in the invariant elimination, and its first
subresultant. Over the algebraic closure the stabilizers give the inertia
groups. Characteristic five makes the degree-six quotient tame, so each
ramified point contributes its ramification index minus one.
[Stacks, Galois extensions and ramification](https://stacks.math.columbia.edu/tag/09E3)
· [Stacks, Riemann–Hurwitz](https://stacks.math.columbia.edu/tag/0C1B)

The equivariant map in this application sends a pair consisting of a
direction and a line to its direction. Its commuting squares under
relabeling and Frobenius give the return-map test in the quotient proof.
The general orbit-fiber identity appears in
[OrbitFiberCard](https://github.com/what-social-construct/galois-obstruction-theory/blob/4f8a63cd946ab4a99d4fffe2bd42c1043f5c7d4a/GaloisObstructionTheory/Hodge/Correspondence/OrbitFiberCard.lean#L23).
The quotient genus, overlap counts, and concrete transport argument are
established here by the written derivations and executable checks.

The [witness search](python/gct_common_line_witness.py) uses the existing
[ten row-echelon charts](python/gct_collision_quadrics.py) and verifies
each returned frame against the input Gram matrices after embedding
the coefficients. The positive control is the explicit net
$(x_1^2-2x_0^2,x_3^2-2x_2^2,x_4^2)$ over $\mathbb F_5$.
The certificates, field searches and control are exact Python computations.
The geometric termination argument is written in the
[pencil calculation](manuscript/03-complexity/collision-pencil-fiber.tex).

The [vertex-symmetry calculation](python/gct_collision_face.py)
interpolates opposite edges, excludes boundary strata, and descends the
permanent polars to the invariant coordinates. Excluding the $u=0$ and
$v=3$ sections permits the plane resultant in two variables. Two factorizations
and a smooth rational point certify absolute irreducibility, and the first
subresultant gives generic recovery of the other invariants. The
[exceptional lift](python/gct_collision_subresultant.py) takes polynomial
gcds in each projection residue field and checks the remaining quadratic
discriminant. The [degree-88 rank replay](python/gct_collision_exceptional_rank.py)
expresses the lift in the power basis generated by $p$ and checks
Jacobian rank 54 there, so rational recovery applies at every surviving
point. The plane-curve checker also factors all remaining
prime-field slope sections and excludes their geometric points by rank. The
[frame checker](python/gct_collision_pencil_fiber.py) uses the original
permanent for all six exact msolve boundary ideals and for the remaining
16-variable chart. The chart equivalence holds up to relabeling on the face.

The degree-755 section uses the determinant of the rank-five quotient
bundle and a nonzero specialized minor. The local degree-180 check
uses the companion resultant. The zero-divisor lengths use the degree
of an invertible sheaf on a proper integral curve. The binary norm
uses the determinant of multiplication for the degree-24 finite flat
projection. The coefficient expansion and factorization of the norm
remain open. [Stacks, degrees on curves (Tag 0AYQ)](https://stacks.math.columbia.edu/tag/0AYQ)
· [Stacks, norms (Tag 0BCX)](https://stacks.math.columbia.edu/tag/0BCX)

The [quotient divisor and incidence decomposition](manuscript/03-complexity/common-line-decomposition.tex)
use the projective resultant criterion and coefficient multidegrees from
D'Andrea and Dickenstein above. The invariant incident and diagonal
covectors, the sextic obtained from the polar cofactors, and its
[nonzero specialization](python/gct_collision_line_divisor.py) are
specific to this face. The [interpolation and frame replay](python/gct_collision_incidence_descent.py)
uses the permanent and the full-rank polar kernel, and the
[quadratic-slope check](python/gct_collision_quadratic_slopes.py) uses
the plane resultant and first subresultant already recorded here.
The [ordering calculation](python/gct_collision_ordering_fibers.py) computes
Frobenius in each separable cubic algebra. The field decomposition uses
the finite étale classification, and the lifting statement applies over
the henselian local Artin rings of the scheme-theoretic image.
[Stacks, schemes étale over a field](https://stacks.math.columbia.edu/tag/03QR)
· [Stacks, finite étale extensions of henselian local rings](https://stacks.math.columbia.edu/tag/04GK)

The residual proposition uses irreducibility and multidegrees of the
universal homogeneous resultant. On a transverse section its eight
evaluation factors give the auxiliary square. Specialization in the
polynomial ring of framed nets containing a line proves that the remaining
degree-336 equation vanishes on the full incidence scheme. The degree
bound 1,344 is a written consequence of its twist and the quotient degree.
The local subtraction of multiplicities uses the discrete valuation rings
of the smooth quotient. [Jouanolou, *Le formalisme du résultant*](https://doi.org/10.1016/0001-8708(91)90031-2) · [Stacks, effective divisors on smooth curves](https://stacks.math.columbia.edu/tag/0B9D)

The [local colon identities](lean/PvsNP/ReadoutResidual.lean) are proved
in Lean for regular principal factors. The [eight-point control](python/gct_collision_resultant_square.py)
computes the polar cofactors for a split transverse section over the prime
field and checks the double zero as the auxiliary form varies.
The [slope check](python/gct_collision_line_divisor_slopes.py)
tests the original resultant itself at all eligible closed points above
$v^{25}-v=0$, including four points on excluded pencils. Each unit
certificate uses the two vertex-invariant covectors in the descended frame.

The [Frobenius checker](python/gct_permanent_frobenius.py) constructs the
fixed tangent spaces for all five conjugacy classes modulo five.
It uses the existing [Witt chart enumeration](python/gct_permanent_modular.py)
with exact extension-field arithmetic for the twisted classes.
The double-transposition positive sector uses four
[involution charts](python/gct_permanent_involutions.py) at five. These
exclusions and the earlier support and three-cycle arguments give
the 48-point lower bounds in the manuscript. The complex statement
uses the finite free closure of the reduced generic fiber.
The invariant-algebra criterion uses
[Cziszter and Domokos, Theorem 10.3](https://arxiv.org/abs/1205.3011)
for the degree-four generating bound. The [orbit-sum generator](python/gct_permanent_plucker.py)
uses decomposables and leading parts of averaged equation multiples
to choose 127 generators for the quotient by exact row reduction.
The dimension-seven upper bound is a proof target.

The [theorem targets](manuscript/03-complexity/theorem-targets.tex)
use the star equations, corrected diagonal determinant and orbit bound from
the [local reduction at 9c8b588](https://github.com/what-social-construct/P-VS-NP/blob/9c8b58844113c8ae7e43e389349eb7d5104b272f/manuscript/03-complexity/gct-extension.tex).
[PermanentLevelTarget](lean/PvsNP/PermanentLevelTarget.lean) derives its
coefficient criterion from Mathlib's permanent and multivariate polynomials.
[BranchCertificate](lean/PvsNP/BranchCertificate.lean) applies the finite
geometric sum identity to the two proposed ideal memberships. Both are
local proofs. The chart-specific identities are open hypotheses.
The [selector interface](lean/PvsNP/StratumSelector.lean) makes the model
representative and transport hypotheses explicit. Its correctness proof
is local. The geometric existence input is Coste's Theorem 4.1 above,
and the decoded affine example uses [HE-P1-Text](#he-p1-text). Uniform
bit bounds for a new succinct verifier require an independent proof.

[Lean](lean/PvsNP/InvariantClosure.lean) proves the finite dimension
criterion for stability under algebra generators. The
[closure checker](python/gct_permanent_closure.py) replays supplied
polynomial identities against the original star equations.
The [degree-seven obstruction data](gct_permanent_star_span_degree7.dual.gz)
stores 20 low-degree pairings obtained by exact invariant elimination.
The checker independently verifies the identity pairing matrix and all
98,336 weight-zero row products of the original Fourier generators.
The written rank argument uses the 27-dimensional span of one and the
selected degree-at-most-two orbit sums inside the 39-dimensional
low-degree invariant space.

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

The local [gate-elimination experiment](python/incidence_gate_elimination.py)
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
