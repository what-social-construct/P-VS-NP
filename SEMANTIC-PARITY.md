# Semantic parity

This register follows the [manuscript](manuscript/main.tex) from compatibility
of presentations through affine disclosure and finite Boolean agreement. The
[source ledger](SOURCE-LEDGER.md) tracks reviewed revisions and the scope of
each transfer.

**Lean** marks a checked declaration with its stated hypotheses. **Executable**
marks the Python realization at the decoded cochain boundary. **Derived**
marks a written mathematical consequence. **Cited** marks an external
theorem. **Target** marks a comparison still to be established here.

## Compatibility, descent, and faithful realization

| Realization | Notation | Semantic role | Declaration or source | Status and scope |
| --- | --- | --- | --- | --- |
| Descent of a map | $\bar f q=f$, $A\times_Q A$ | A map descends uniquely along a surjection when it is constant on its fibers. For an operation $D$, apply the criterion to $qD$. | [`existsUnique_descend_iff`, `endomorphism_descends_iff`](lean/PvsNP/Compatibility.lean) | Lean proves the set-level criterion. The construction uses choice of representatives. An effective or polynomial-time descent needs additional data. |
| Faithful evaluation | $JE=\mathrm{id}$ | A left inverse recovers the original element and therefore reflects equality. | [`evaluation_eq_iff_of_leftInverse`](lean/PvsNP/Compatibility.lean) | Lean proves the implication from a supplied left inverse. The full Hodge residual supplies a left inverse on its image by reading the message block. |
| Gödel coding | $d_g g_1=g_0\delta_g$ | The exact syntax-to-code identity specializes tracked numeral substitution to the formula's own code. | [`selfSubstitution_square`](lean/PvsNP/Compatibility.lean), [coding sources](SOURCE-LEDGER.md#godel) | Lean proves the tracked-operation interface from a supplied coding and tracking law. Concrete arithmetization and descent through provable equivalence are separate targets. |
| Provable fixed point | $q_T(G)=[\theta(\overline{g_0(G)})]_T$ | A proved biconditional becomes equality in the Lindenbaum algebra at the constructed sentence. | [Manuscript section](manuscript/01-compatibility/section.tex), [diagonal lemma sources](SOURCE-LEDGER.md#godel) | Cited. The literal coding square holds throughout its domain. The provability equality concerns the fixed point. |
| Selected semantics | $c_{\mathcal M}:H_T\twoheadrightarrow Q_{\mathcal M}$, $\ker c_{\mathcal M}$ | The residual records distinct provability classes with equal selected semantics. The difference of the two classes lies in the kernel ideal. | [Manuscript section](manuscript/01-compatibility/section.tex), [logic sources](SOURCE-LEDGER.md#logic) | Derived from soundness and the cited logical theorems. The standard-model collision uses a sound, computably axiomatized extension of Robinson arithmetic. All models give injectivity by completeness. |
| Propositional proof translation | $f_2\tau=f_1$, $\mathrm{TAUT}$ | A polynomial-time translator preserves the formula proved and transfers polynomial bounds on proof length. | [Cook–Reckhow](SOURCE-LEDGER.md#cr), [manuscript section](manuscript/03-complexity/section.tex) | Cited. Polynomially bounded proof systems for tautologies characterize $\mathsf{NP}=\mathsf{coNP}$. A bound on proof search is a separate condition. |
| Polynomial-time predicates | $R\hookrightarrow B$, $B/R$ | The class of an NP predicate vanishes exactly when the language has a polynomial-time decider. | [Manuscript section](manuscript/03-complexity/section.tex) | Defined and derived as a module cokernel in the manuscript. A comparison with the logical kernel or a uniform complexity result is a target. |

## Originating object

Fix a generated cochain $b=(a,0,(d+1)A\tau)$ from Paper 1, with
$A^{\mathsf T}A=dI$ and $d>0$. In Boolean coordinates, the mask imposes
$u+v=m$, where $u$ is the key, $v$ the message, and $m_j=1$ for a negative
mask sign. An affine constraint on the key and message becomes $Qv=c$ after
substituting $u=m+v$. Thus each point of the affine fiber
$W=\{v : Qv=c\}$ determines one compatible key–message pair. Write
$K=\ker Q$.

The message signs are $s_j=2v_j-1$. Paper 1 gives the residual
$r_v=(a,-ds,A\tau)$. For an index set $J$, the disclosed information
coordinates $r_{v,j}=d(1-2v_j)$ recover $v_j$ by exact arithmetic over the
integers. In the Boolean realization the disclosure map is therefore
$D=\operatorname{pr}_J$ restricted to $W$.

## Disclosure collision square

Let $C_J=W\times_D W$ be the ordered witness pairs with equal disclosures,
and let $K_J=K\cap\ker D$. The horizontal arrows take a pair to its first
witness and the difference of its message coordinates.

$$
\begin{array}{ccc}
C_J & \xrightarrow{\;\Psi_J\;\cong\;}& W\times K_J\\
\big\downarrow && \big\downarrow\\
W\times W & \xrightarrow{\;\Psi\;\cong\;}& W\times K .
\end{array}
$$

The left arrow forgets the equality condition. The right arrow includes
$K_J$ in $K$. Since $D(v'-v)=D(v')-D(v)$, the equality condition is precisely
membership in $K_J$. This gives the Cartesian square of sets, including
the empty-fiber case. The diagonal corresponds to the zero direction. Its
complement corresponds to $W\times(K_J\setminus\{0\})$.

For each finite set $T$ here, write $A(T)=\mathbb F_2^T$ for its function
algebra. Transport by $\Psi_J$ gives
$\theta_J(f)=f\circ\Psi_J^{-1}$ and the diagonal projector square

$$
\begin{array}{ccc}
A(C_J) & \xrightarrow{\;\theta_J\;\cong\;}& A(W\times K_J)\\
\big\downarrow {e_\Delta\cdot(-)} &&
\big\downarrow {\mathbf 1_{W\times\{0\}}\cdot(-)}\\
A(C_J) & \xrightarrow{\;\theta_J\;\cong\;}& A(W\times K_J).
\end{array}
$$

The indicator transforms pointwise because $\Psi_J$ carries equal pairs to
the zero direction. In the finite split scheme realization
$T\mapsto\operatorname{Spec}A(T)$, these are the diagonal and its clopen
complement.

For every attained disclosure $y$, the surviving fiber $W_y$ is a translate
of $K_J$. Rank–nullity gives

$$
|W_y|=2^{\dim K-\operatorname{rank}(D|_K)}.
$$

Consequently an attained disclosure determines the message exactly when
$K_J=0$. With a uniform choice from $W$, conditioning on a disclosure is
uniform on $W_y$, so optimal recovery has probability $1/|W_y|$. The full
ordered collision residual has $|W|(|K_J|-1)$ points, since each witness
has one matching partner for each nonzero direction in $K_J$.

## Parity table

| Realization | Notation | Semantic role | Declaration or implementation | Status and scope |
| --- | --- | --- | --- | --- |
| Hodge/CVP | $r_v=(a,-ds,A\tau)$, $\lVert r_v\rVert^2$ | The vector determines the message, while its squared norm is common to the public mask. | [Paper 1 formula](SOURCE-LEDGER.md#he-p1-text); [copied cost and gap](lean/HCP/CoupledSignResidual.lean); [residual computation](hcp_cvp_residual.py) | Lean verifies the cost and gap. Python computes the full rational vector for a supplied lattice. The displayed vector formula follows from Paper 1's harmonic projection. |
| Affine witnesses | $W=\{v:Qv=c\}$ | A particular solution and a kernel basis encode the whole witness family. | [Selector](affine_witness_selector.py); [affine fiber](lean/PvsNP/AffineDisclosure.lean) | Executable Gaussian elimination uses explicitly supplied binary affine constraints and decoded cochains. |
| Disclosure collision | $C_J\cong W\times K_J$ | Equal disclosures correspond to unobserved homogeneous directions. | [`disclosureCollisionEquiv`, `disclosureCollision_square`](lean/PvsNP/AffineDisclosure.lean) | Lean proves the equivalence and commuting square for linear maps over a ring. The fresh-sign specialization uses the bit decoding above. |
| Marked diagonal | $\Delta_W\subset C_J$, $W\times\{0\}$ | Equality of witnesses corresponds to a zero direction. | [`disclosureCollisionEquiv_diagonal`](lean/PvsNP/AffineDisclosure.lean) | Lean proves the pointwise comparison. The complementary subset follows by taking complements. |
| Function algebra and finite split scheme | $A(C_J)$, $e_\Delta$, $1-e_\Delta$ | The change of coordinates $w=v'-v$ gives equations $Qw=Dw=0$ and takes the diagonal to $w=0$. The complementary idempotents give a product decomposition. | [Boolean coordinate derivation](manuscript/02-affine-disclosure/section.tex); [projector square](#disclosure-collision-square) | Derived in the finite split realization. The Lean square is at the level of points. |
| First-colon residual | $S/(I_C:I_\Delta)$ | The diagonal ideal in $S/I_C$ is generated by $1-e_\Delta$. Its annihilator is the diagonal factor, so the quotient is the residual factor. | [Colon computation](manuscript/02-affine-disclosure/section.tex); [Galois source](SOURCE-LEDGER.md#got) | Derived for the Boolean collision ring. |
| Cardinality and selector | $\lvert W_y\rvert=2^{\dim K-\operatorname{rank}(D\vert_K)}$ | Counts the candidates after a specified disclosure. A one-point fiber gives exact recovery. | [Rank–nullity derivation](#disclosure-collision-square); [`residual_coordinates`, `cardinality`](affine_witness_selector.py) | Derived for attained disclosures. Executable selection supports inconsistent constraints and disclosures by returning an empty fiber. |
| Minimum coordinate disclosure | $k=\dim K$ | A nonempty witness fiber needs at least $k$ coordinates for exact recovery. Independent rows of a kernel basis select $k$ sufficient coordinates. | [Row-rank argument](manuscript/02-affine-disclosure/section.tex) | Derived. The Python selector consumes supplied coordinates. |
| Bounded circuit agreement | $I_E=([x^\alpha](P_a-N_b))_\alpha$ | Coefficient equations cut out exact Boolean agreement. Contracting the ideal to target parameters gives the represented targets. | [Projection and example](manuscript/03-complexity/section.tex); [symbolic check](agreement_scheme.py) | Derived for finite Boolean families. Executable for constant and affine one-bit candidates. A comparison to the site’s general circuit predicate and a uniform complexity transfer are targets. |
| Tagged graphs of evaluations | $E=\operatorname{Eq}(a,b)$ on $Z=U\times V$ | Keeping the parameter pair in the graph forces agreement to be a cross component of a tagged self-collision. Its two ordered cross components are the off-diagonal residual. | [Graph square](manuscript/03-complexity/section.tex); [Galois source](SOURCE-LEDGER.md#got) | Derived for the finite Boolean families. The target complement is computed by the separate projection in the preceding row. |

## PEqualNP contribution status

| Step | Exact scope | Evidence and status |
| --- | --- | --- |
| `L-meta-4211` | A monotone circuit with at most 62 gates cannot realize the posted incidence examples by OR-ing two selected wires. | Reviewed and returned to the desk. The [public reduction](SOURCE-LEDGER.md#peq) isolates the remaining lower bound for a circuit with at most 63 gates and a single output. |
| `L-meta-19020` | Every pair of sparse point and line sets with no incidences in the order-three plane is covered by a relabeling of one of eight sample masks. | An independent Python enumeration covered all 12,234 eligible pairs. Another contributor's [Lean proof #23821](https://github.com/open-goat/pequalnp-proofs/pull/23821) merged. |
| `R-meta-17715-1`, second hypothesis | An order-two incidence circuit with the specified first AND gate needs a second gate. | Lean checked the exact hypothesis in the public fork's pinned environment. Awaiting a child step ID for the [merged reduction #23858](https://github.com/open-goat/pequalnp-proofs/pull/23858). |
| `R-meta-17918-2` and `R-meta-17920-2`, first hypotheses | An order-three incidence circuit cannot use a primary input as its output. A singleton input would make that output true without any incidence. | Lean checked both exact hypotheses in the public fork's pinned environment. Awaiting child step IDs for the [merged reductions #23852](https://github.com/open-goat/pequalnp-proofs/pull/23852) and [#23853](https://github.com/open-goat/pequalnp-proofs/pull/23853). |

Run `python3 affine_witness_selector.py` to see the common squared CVP cost
on two distinct witnesses and then reduce the fiber to one witness with a
residual coordinate. Run `lake build` from `lean/` for the Lean declarations.
Run `latexmk -pdf -outdir=.build main.tex` from `manuscript/` to build the draft.
