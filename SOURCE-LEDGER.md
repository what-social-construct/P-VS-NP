# Source ledger

Reviewed 2026-11-26. Source IDs refer to a specific text, code revision, or
external definition. The [parity register](SEMANTIC-PARITY.md) records the
local statements and their proof or execution status. Full entries for cited
manuscript sources are in the [bibliography](manuscript/references.bib).

| Source ID | Source and version | Reviewed material | Role here |
| --- | --- | --- | --- |
| [HE-P1-Code](#he-p1-code) | Homotopical Encryption at `e619391` | Fresh-sign and residual Lean import closure | Copied source proofs and fixed-mask cost comparison |
| [HE-P1-Text](#he-p1-text) | Homotopical Encryption Paper 1 at `62f20ff` | Fresh-sign normal form, explicit residual, cost gap, disclosure and oracle scope | Originating cochain and residual data |
| [GOT](#got) | Local Galois Obstruction Theory manuscript, §4 and proof spine | Tagged graph pullback, idempotent comparison, and first-colon quotient | Agreement square and affine residual calculation |
| [GODEL](#godel) | Grabmayr and Goldfarb | Coding and substitution, fixed-point lemma | Exact tracking and provability comparisons |
| [LOGIC](#logic) | Open Logic Text, release `2e19d09` | First-order completeness and arithmetic incompleteness | Semantic kernel examples |
| [CR](#cr) | Cook and Reckhow, JSL 44 (1979) | Proof systems, p-simulation, polynomial boundedness | Resource-bounded comparison |
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
