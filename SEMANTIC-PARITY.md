# Semantic parity

This register compares the Paper 1 residual vector, the affine witness fiber,
and its collision decomposition. [Source ledger](SOURCE-LEDGER.md) tracks
origin, reviewed revisions, and the scope of each transfer.

**Lean** marks a checked declaration with its stated hypotheses. **Executable**
marks the Python realization at the decoded cochain boundary. **Derived**
marks a mathematical consequence explained here. **Target** marks a comparison
still to be established in this repository.

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
| Function algebra and finite split scheme | $A(C_J)$, $e_\Delta$, $1-e_\Delta$ | Transport preserves the two complementary idempotents and hence the product decomposition. | [Projector square above](#disclosure-collision-square); [source convention](SOURCE-LEDGER.md#got) | Derived in the finite split realization. The Lean square is presently at the level of points. |
| Cardinality and selector | $|W_y|=2^{\dim K-\operatorname{rank}(D\vert_K)}$ | Counts the candidates after a specified disclosure. A one-point fiber gives exact recovery. | [Rank–nullity derivation](#disclosure-collision-square); [`residual_coordinates`, `cardinality`](affine_witness_selector.py) | Derived for attained disclosures. Executable selection supports inconsistent constraints and disclosures by returning an empty fiber. |
| Bounded circuit agreement | $I_E=([x^\alpha](P_a-N_b))_\alpha$ | Coefficient equalities cut out agreement between candidate descriptions. Projection tests whether a target has any candidate. | [Symbolic example](agreement_scheme.py); [circuit-size definitions](SOURCE-LEDGER.md#peq) | Executable toy model. A comparison to the site’s general circuit predicate and a uniform complexity transfer are targets. |

Run `python3 affine_witness_selector.py` to see the common squared CVP cost
on two distinct witnesses and then reduce the fiber to one witness with a
residual coordinate. Run `lake build` from `lean/` for the Lean declarations.
