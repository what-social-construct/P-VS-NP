# Source ledger

Reviewed 2026-11-26. Source IDs refer to a specific text, code revision, or
external definition. The [parity register](SEMANTIC-PARITY.md) records the
local statements and their proof or execution status.

| Source ID | Source and version | Reviewed material | Role here |
| --- | --- | --- | --- |
| [HE-P1-Code](#he-p1-code) | Homotopical Encryption at `e619391` | Fresh-sign and residual Lean import closure | Copied source proofs and fixed-mask cost comparison |
| [HE-P1-Text](#he-p1-text) | Homotopical Encryption Paper 1 at `62f20ff` | Fresh-sign normal form, explicit residual, cost gap, disclosure and oracle scope | Originating cochain and residual data |
| [GOT](#got) | Local Galois Obstruction Theory manuscript, §4 | Agreement pullback and idempotent comparison | Diagram and parity conventions |
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
graph pullback with the equalizer. This repository uses those comparison
conventions with affine witness fibers and finite split schemes.

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
$\mathbb F_2$, every subset has its characteristic idempotent.

## PEQ

PEqualNP's [circuit-size definitions](https://github.com/open-goat/pequalnp-proofs/blob/main/lean/PEqualNP/Defs/MetaComplexity.lean)
and [contribution rules](https://github.com/open-goat/pequalnp-proofs/blob/main/CONTRIBUTING.md)
were reviewed as the external comparison surface. `HasCircuitSize` supplies
a candidate bounded circuit predicate for comparing the projected agreement
locus with the public repository's definitions. The affine witness square
has its own definitions and proof in this repository.
