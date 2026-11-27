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
| Hodge/CVP | $r_v=(a,-ds,A\tau)$, $\lVert r_v\rVert^2$ | The vector determines the message, while its squared norm is common to the public mask. | [Paper 1 formula](SOURCE-LEDGER.md#he-p1-text); [copied cost and gap](lean/HCP/CoupledSignResidual.lean); [residual computation](python/hcp_cvp_residual.py) | Lean verifies the cost and gap. Python computes the full rational vector for a supplied lattice. The displayed vector formula follows from Paper 1's harmonic projection. |
| Affine witnesses | $W=\{v:Qv=c\}$ | A particular solution and a kernel basis encode the whole witness family. | [Selector](python/affine_witness_selector.py); [affine fiber](lean/PvsNP/AffineDisclosure.lean) | Executable Gaussian elimination uses explicitly supplied binary affine constraints and decoded cochains. |
| Disclosure collision | $C_J\cong W\times K_J$ | Equal disclosures correspond to unobserved homogeneous directions. | [`disclosureCollisionEquiv`, `disclosureCollision_square`](lean/PvsNP/AffineDisclosure.lean) | Lean proves the equivalence and commuting square for linear maps over a ring. The fresh-sign specialization uses the bit decoding above. |
| Marked diagonal | $\Delta_W\subset C_J$, $W\times\{0\}$ | Equality of witnesses corresponds to a zero direction. | [`disclosureCollisionEquiv_diagonal`](lean/PvsNP/AffineDisclosure.lean) | Lean proves the pointwise comparison. The complementary subset follows by taking complements. |
| Function algebra and finite split scheme | $A(C_J)$, $e_\Delta$, $1-e_\Delta$ | The change of coordinates $w=v'-v$ gives equations $Qw=Dw=0$ and takes the diagonal to $w=0$. The complementary idempotents give a product decomposition. | [Boolean coordinate derivation](manuscript/02-affine-disclosure/section.tex); [projector square](#disclosure-collision-square) | Derived in the finite split realization. The Lean square is at the level of points. |
| First-colon residual | $S/(I_C:I_\Delta)$ | The diagonal ideal in $S/I_C$ is generated by $1-e_\Delta$. Its annihilator is the diagonal factor, so the quotient is the residual factor. | [Colon computation](manuscript/02-affine-disclosure/section.tex); [Galois source](SOURCE-LEDGER.md#got) | Derived for the Boolean collision ring. |
| Cardinality and selector | $\lvert W_y\rvert=2^{\dim K-\operatorname{rank}(D\vert_K)}$ | Counts the candidates after a specified disclosure. A one-point fiber gives exact recovery. | [Rank–nullity derivation](#disclosure-collision-square); [`residual_coordinates`, `cardinality`](python/affine_witness_selector.py) | Derived for attained disclosures. Executable selection supports inconsistent constraints and disclosures by returning an empty fiber. |
| Minimum coordinate disclosure | $k=\dim K$ | A nonempty witness fiber needs at least $k$ coordinates for exact recovery. Independent rows of a kernel basis select $k$ sufficient coordinates. | [Row-rank argument](manuscript/02-affine-disclosure/section.tex) | Derived. The Python selector consumes supplied coordinates. |
| Bounded circuit agreement | $I_E=([x^\alpha](P_a-N_b))_\alpha$ | Coefficient equations cut out exact Boolean agreement. Contracting the ideal to target parameters gives the represented targets. | [Projection and example](manuscript/03-complexity/section.tex); [symbolic check](python/agreement_scheme.py) | Derived for finite Boolean families. Executable for constant and affine one-bit candidates. A comparison to the site’s general circuit predicate and a uniform complexity transfer are targets. |
| Tagged graphs of evaluations | $E=\operatorname{Eq}(a,b)$ on $Z=U\times V$ | Keeping the parameter pair in the graph forces agreement to be a cross component of a tagged self-collision. Its two ordered cross components are the off-diagonal residual. | [Graph square](manuscript/03-complexity/section.tex); [Galois source](SOURCE-LEDGER.md#got) | Derived for the finite Boolean families. The target complement is computed by the separate projection in the preceding row. |

## Witness selection under prefix restrictions

For a polynomial-time verifier $V(x,w)$ with a known polynomial bound on
the witness length, write $W_x$ for its witness fiber. Fix a witness
encoding of that length and define

$$
F(x,u)\quad\Longleftrightarrow\quad
\text{some witness in } W_x \text{ starts with }u .
$$

A polynomial-time test for $F$ gives a selector. Test the empty prefix
for feasibility, then extend a feasible prefix $u$ by testing $u0$.
Choose $u0$ when it is feasible and $u1$ otherwise. At most one test per
witness bit suffices after the initial feasibility check. For the
explicit affine family, each prefix adds coordinate equations and
Gaussian elimination tests their consistency.

Adding $k$ free bits replaces a fiber of size $m$ by one of size
$m2^k$, with $m2^k(m2^k-1)$ off-diagonal ordered pairs. A selector
extends the original witness by $k$ zeros. An executable check with
the fresh-sign affine selector and four extra bits increased the fiber
from 2 to 32 and the residual from 2 to 992 pairs, preserving the first two
selected bits. At the other extreme, fibers of size zero and one both have
empty off-diagonal residual. The promised satisfiability comparison between
these two cases has a [randomized hardness result](SOURCE-LEDGER.md#vv).

## Polynomial agreement certificates

Fix the received Reed–Solomon pair $w$, the distinct evaluation sites
$a_i$, the code degree bound $k$, a multiplier budget $t$, and a
response degree $D$ with $k+t\le D<n$. Making the response monic
gives an affine coefficient system $M_w c=b$, where the rows are

$$
\sum_{j=0}^1 w_{ij}\sum_{s=0}^t a_i^s h_{js}
  - \sum_{s=0}^{D-1}a_i^s r_s = a_i^D .
$$

The selected witness is a certificate for an error-count lower bound.
Write $e$ for the true whole-pair error count and $b(w)$ for the best
certified count.
For given $w$, solving the linear system gives the actual fiber,
including inconsistency. With $w$ varying, consistency is the rank
condition $\operatorname{rank} M_w=\operatorname{rank}[M_w\mid b]$.
Eliminating the coefficients gives the Zariski closure of the projection.
The zero specialization in the four-site example is in that closure
and has an empty actual fiber.

On the four nonzero sites of $\mathbb F_5$ with $k=1$, the received pair
$(a,2a)$ gives five degree-one certificates. The first coefficient
restriction $h_{00}=0$ leaves one certificate. The received pair
$(1-1/a,0)$ has true error count three and strongest certified count
one. These cases are checked by the executable example.

| Realization | Notation | Semantic role | Evidence and scope |
| --- | --- | --- | --- |
| Normalized coefficients | $W_{w,t,D}=\{c:M_wc=b\}$ | A nonempty fiber is a translate of $\ker M_w$. A prefix adds coordinate equations. | [Paper 3 Lean boundary](lean/Proximity/Core/PolynomialAgreement/Boundary.lean) proves the coefficient equivalence and kernel description. The [Python selector](python/polynomial_agreement_selector.py) computes a particular solution and basis over an explicitly supplied prime field. |
| Certificate disclosure | $W_{w,t,D}\times_\Lambda W_{w,t,D}$ | Two certificates with the same linear disclosure differ by a direction in $\ker M_w\cap\ker\Lambda$. The diagonal corresponds to zero direction. | [Lean bridge](lean/PvsNP/AgreementCertificate.lean) specializes the equivalence, square, and diagonal theorem over a field. |
| Degree frontier | $D_{\min}$, $n-D_{\min}$ | At maximal budget $t=D-k$, feasible degrees form an upper interval. Binary search gives the strongest certified count. | Lean proves [upward closure](lean/Proximity/Core/PolynomialAgreement/Boundary.lean). The Python search uses unrestricted coefficient fibers at each candidate degree. |
| Certificate strength | $\min(e,n-k+1-e)\le b(w)\le e$ | The best certificate is exact through the closed half-distance boundary. | [Soundness](lean/Proximity/Core/PolynomialAgreement.lean), [completeness](lean/Proximity/Core/PolynomialAgreement/Completeness.lean), and [sharpness on nonzero domains](lean/Proximity/Core/PolynomialAgreement/Sharpness.lean) are imported Lean results. |
| Projection across inputs | $\operatorname{rank} M_w=\operatorname{rank}[M_w\mid b]$ | Equality of ranks characterizes actual feasibility. The Zariski closure also contains the zero specialization in the example. | Written derivation and [Paper 3 provenance](SOURCE-LEDGER.md#he-p3). |

## Geometric complexity and orbit closures

| Realization | Exact scope | Evidence |
| --- | --- | --- |
| Polynomial orbit-closure separation | A polynomial that vanishes on the source and has nonzero value at a target excludes that target from the zero locus of the source's vanishing ideal. The two-by-two determinant excludes the identity from the closure of the rank-one orbit. | [Lean](lean/PvsNP/OrbitClosureSeparation.lean) checks the criterion, the determinant evaluation, and inclusion of all left-right transforms of $E_{00}$ in the outer-product family. |
| Finite permutation symmetry | Simultaneous invariance of matrix entries is exactly commutation with the permutation action on coefficient functions. The dimension is the number of ordered-pair orbits. | [Copied orbit coordinates](lean/PvsNP/GaloisOrbitMatrices.lean) and [Lean bridge](lean/PvsNP/FiniteSymmetry.lean). |
| Graded multiplicity comparison | Containment of the padded permanent orbit closure in the determinant orbit closure gives surjective equivariant restriction in each degree. A larger multiplicity on the padded permanent side certifies noncontainment. | [Written argument and cited occurrence barrier](manuscript/03-complexity/gct.tex). The finite permutation calculation concerns a different group action. |
| Constant permanent level | The nonconstant coefficients of the permanent pencil cut out the level fiber inside the independent-frame locus. For $n\ge2$ and symmetric perturbations supported on one row and its column, the dimension at $J_n$ is $n-2$. | [Written coefficient formula](manuscript/03-complexity/gct.tex) and [exact SymPy check at $J_4$](python/gct_permanent_fiber.py). The desk's dimension-three question concerns unrestricted symmetric directions. |
| Symmetric tangent Hessian | The Hessian at $J_n$ is nondegenerate on the symmetric tangent space. Its rank at $J_4$ is nine, so a symmetric constant-level subspace has dimension at most four. | [Written Hessian argument](manuscript/03-complexity/gct.tex) and [exact rank check](python/gct_permanent_fiber.py). |
| Star-plane maximality | For $n\ge3$, a symmetric constant-level space containing the first-row-and-column $(n-2)$-plane equals that plane, even when extension directions may use all entries. | [Written block-permanent proof](manuscript/03-complexity/gct-three-plane.tex). [Python](python/gct_permanent_fiber.py) checks the six independent first-order constraints and the remaining equations at $J_4$. |
| Rank and finite symmetry at $J_4$ | A symmetric level three-plane must have a direction of matrix rank at least three. A level subspace stable under the simultaneous regular Klein four action is zero. | [Written rank and character proofs](manuscript/03-complexity/gct-three-plane.tex). [Python](python/gct_permanent_fiber.py) checks the rank-one coefficient identity and the four character cases. The unrestricted three-plane question remains open. |
| Three-cycle symmetry | No level three-plane is invariant under a simultaneous index 3-cycle over $\mathbb C$ or the algebraic closures at 5, 7, and 11. The only two-plane invariant under the vertex stabilizer $S_3$ over $\mathbb C$ is the star. | [Written eigenspace argument](manuscript/03-complexity/gct-three-plane.tex). [Python](python/gct_permanent_fiber.py) checks the fixed-sector ideals and the coefficient identities. |
| Ordinary diagonal rank | Every complex level three-plane projects with rank at least two to the diagonals modulo constant vectors. The zero-diagonal slice has 24 level two-planes, each maximal in the full symmetric fiber. | [Written classification and extension argument](manuscript/03-complexity/gct-three-plane.tex) and [exact coefficient and kernel checks](python/gct_permanent_fiber.py). |
| Witt charts for level three-planes | The quadratic coefficient vanishes on the isotropic Grassmannian of the rank-nine tangent form. Its 32 projection charts give four representative systems for the complex-point existence question. Each uses 12 variables and the 25 cubic and quartic pencil coefficients. | [Written chart parametrization, coverage, and symmetry argument](manuscript/03-complexity/gct-three-plane.tex). [Python](python/gct_permanent_fiber.py) checks the Witt Gram matrix and chart orbits, generates the systems, and compares their coefficients with direct permanent expansions at exact sample parameters. The four systems have yet to be decided. |
| Zero-row-sum slice | A symmetric level three-plane at $J_4$ must contain a direction $B$ with $B\mathbf 1\ne0$. On the zero-row-sum slice, the ten cubic coefficients already generate the unit ideal on every quadratic chart. | [Written coefficient identities, chart argument, and rank lift](manuscript/03-complexity/gct-three-plane.tex). [Python](python/gct_permanent_fiber.py) checks the coefficient identities and the full column rank of the $46\times35$ coefficient matrix modulo 11. |
| Modular rational-point obstruction | The three-plane locus has no $\mathbb F_5$- or $\mathbb F_7$-points. It has no points over a characteristic-zero local field with either of those residue fields, excluding rational and Gaussian-rational three-planes. | [Exact chart enumeration and pair-compatibility check](python/gct_permanent_modular.py). [Written projective specialization argument](manuscript/03-complexity/gct-modular.tex) uses the valuative criterion. The prime-field point check leaves geometric existence open. |
| Quadratic fields of definition | No level three-plane is defined over a quadratic number field. Any field of definition has all residue degrees above 5 at least three. | [C++ extension-field search](gct_permanent_f25.cpp) checks three representative charts over $\mathbb F_{25}$. [Written coverage and specialization](manuscript/03-complexity/gct-modular.tex). |
| Free simultaneous relabeling | Every level three-plane over $\mathbb C$ or $\overline{\mathbb F}_{11}$ has 24 distinct $S_4$ relabelings. | [Written involution cases and specialization](manuscript/03-complexity/gct-modular.tex) and [finite-field chart ideal checks](python/gct_permanent_involutions.py), combined with the three-cycle exclusion. |
| Nonnormal cubic field of definition | A candidate over a cubic field forces 5 and 7 to be inert. If the field is nonnormal, the arithmetic $S_3$ action and the relabeling action force at least 72 distinct geometric points. | [Written residue-degree and commuting-action arguments](manuscript/03-complexity/gct-modular.tex). The 72-point bound assumes a candidate defined over a nonnormal cubic field. |
| Row-sum rank | Every complex level three-plane has $\operatorname{rank}(B\mapsto B\mathbf1)\ge2$. | [Executable unit-ideal calculation modulo 11](python/gct_permanent_modular.py) after [written symmetry reduction and projective specialization](manuscript/03-complexity/gct-modular.tex). The unit ideal excludes points over the algebraic closure of the residue field. |
| Hadamard diagonal rank | Every complex level three-plane has diagonal map of rank at least two on the lower $3\times3$ block in Hadamard coordinates. | [Exact coefficient identities, Gröbner bases and polynomial gcd checks modulo 23](python/gct_permanent_modular.py). [Written case coverage and specialization](manuscript/03-complexity/gct-modular.tex) lift geometric emptiness for two-planes on which that diagonal vanishes. |
| First variation and hyperplane section | The first coefficient is linear in the extension direction. A larger level space lies in the first-variation kernel. If every level two-plane inside a fixed hyperplane is maximal, no level three-plane exists. | [Lean](lean/PvsNP/LevelSetExtension.lean) proves the abstract statements over coordinate spaces or submodules under their stated field hypotheses. The [written permanent specialization](manuscript/03-complexity/gct-extension.tex) identifies the nine linear and ten higher equations. |
| Dimension of the extension rank locus | Every complex level three-plane places a copy of $\mathbb P^2$ inside the rank-at-most-six locus of level two-planes. A geometric special fiber of dimension at most one would exclude it. | [Written Grassmannian argument and cited semicontinuity](manuscript/03-complexity/gct-extension.tex). This dimension bound for the whole locus remains a target. |
| Extending a rational two-plane | None of the 156 level two-planes defined over $\mathbb F_5$ extends over $\overline{\mathbb F}_5$. Consequently no complex level three-plane contains a rational two-plane. | [Exact enumeration, linear kernels, and residual checks](python/gct_permanent_extensions.py) and [written specialization of the fixed-plane incidence](manuscript/03-complexity/gct-extension.tex). |
| Two Plücker cuts | The cuts avoid all 112 rational rank-deficient two-planes over $\mathbb F_5$. A level two-plane over $\mathbb F_{25}$ satisfies both cuts and has rank six. Its unique first-order extension fails the quadratic coefficient. | [Exact prime-field check, extension-field expansion, and rank minor](python/gct_permanent_plucker.py). [Written argument](manuscript/03-complexity/gct-extension.tex) explains why the higher extension equations are needed. |
| One off-diagonal pair | No complex or $\overline{\mathbb F}_5$ level three-plane contains a direction with exactly one nonzero off-diagonal pair. | [Exact generated systems](python/gct_permanent_plucker.py) give unit Gröbner bases in the four representative charts using msolve. [Written coverage and proper specialization](manuscript/03-complexity/gct-extension.tex). |
| Full equations with the cuts | The 24 affine systems cover every geometric three-plane in characteristic five. Geometric emptiness of all systems would exclude complex three-planes. | [Written cut and normalization argument](manuscript/03-complexity/gct-extension.tex) and [generator for exact solver input](python/gct_permanent_plucker.py). Unrestricted nonexistence remains open. |
| Unrestricted path chart | Every complex or $\overline{\mathbb F}_5$ level three-plane has a path minor. The normalized path chart has 18 variables and 31 equations of degree at most four. | [Written orbit and block argument](manuscript/03-complexity/gct-extension.tex). [Python](python/gct_permanent_plucker.py) checks the orbit cover, all 16 opposite-edge cases over $\mathbb Q$ and $\mathbb F_5$, and emits the path system. The path ideal remains undecided. |
| One matching-supported direction | No level three-plane over $\mathbb C$ or $\overline{\mathbb F}_5$ has a nonzero direction whose off-diagonal support is contained in a perfect matching. Projection onto each four-cycle is injective. | [Written chart coverage and proper specialization](manuscript/03-complexity/gct-extension.tex). [Python](python/gct_permanent_plucker.py) checks the polar identities and emits three systems of 24 generators in 11 variables. Exact msolve bases over $\mathbb F_5$ are all $[1]$. |
| Adjacent-edge direction | No level three-plane over $\mathbb C$ or $\overline{\mathbb F}_5$ contains a direction on two adjacent edges. Together with the matching case, projection onto any four off-diagonal entries is injective. | [Written cofactor and specialization arguments](manuscript/03-complexity/gct-extension.tex). [Python](python/gct_permanent_plucker.py) checks the coefficient identities, the order-three two-plane ideal, and exports the ten eight-variable residual systems. Exact msolve bases modulo 5 for those ten systems are $[1]$. |
| Triangle support and finiteness | No candidate contains a nonzero direction on the three edges of a triangle. A fixed star chart covers the full level three-plane scheme, which is finite over $\mathbb Z_{(5)}$. | [Written radical, chart coverage, and proper-affine argument](manuscript/03-complexity/gct-extension.tex). [Python](python/gct_permanent_plucker.py) checks cofactor rank and generates the 12-variable pencil whose exact msolve basis is $[1]$ modulo five. The star ideal remains undecided. |
| Four-coordinate normalization | An injective linear map from a three-dimensional space into four coordinates restricts to an isomorphism onto some choice of three coordinates. | [Lean](lean/PvsNP/LevelSetExtension.lean) proves the dimension and coordinate statement. Its use in the four-cycle chart assumes injectivity from the written support exclusion. |
| Special fiber at three | The entry-sum-zero integral model has a level three-plane over $\mathbb F_3$. | [Python](python/gct_permanent_plucker.py) checks explicit symmetric directions, independence, and all pencil coefficients by integer expansion modulo three. |
| Path-reversal certificates | The path equations have definite reversal parity in adapted coordinates. A degree-bounded identity for one can use only even products of multipliers and generators. | [Written symmetry and averaging](manuscript/03-complexity/gct-extension.tex). [Python](python/gct_permanent_plucker.py) checks the sign of each monomial and emits the adapted equations over $\mathbb F_5$. No unrestricted unit-ideal certificate has been obtained. |
| Degree-seven path bound | The 31 path generators over $\mathbb F_5$ admit no identity for one with every product of total degree at most seven. The same statement holds after extending the field. | [Stored functional](gct_permanent_path_degree7.dual.gz) takes one to one. [Python](python/gct_permanent_plucker.py) checks its vanishing on all 147,622 even generator multiples. [Written averaging argument](manuscript/03-complexity/gct-extension.tex) makes the bound exhaustive. Higher-degree identities remain open. |
| Four-cycle degree-eight bound | The Fourier chart over $\mathbb F_5$ omitting frequency two admits no identity for one with every product of total degree at most eight, even after extending the field. | [Written rotation and averaging argument](manuscript/03-complexity/gct-extension.tex). [Python](python/gct_permanent_plucker.py) checks the [stored functional](gct_permanent_cycle_omit2_degree8.dual.gz) on all 313,629 invariant products. The unrestricted problem remains open. |
| Star-chart degree-seven bound | All candidates are covered by the fixed star chart. In its Fourier coordinates, the descended coefficient equations admit no degree-seven unit-ideal identity over $\overline{\mathbb F}_5$. | [Written star coverage and Fourier averaging](manuscript/03-complexity/gct-extension.tex). [Python](python/gct_permanent_plucker.py) checks descent, rotation, reflection, and the [functional](gct_permanent_star_degree7.dual.gz) on all 98,336 weight-zero products. The star ideal remains undecided. |
| Center-diagonal rewrites and leading support | The alternative Fourier generators reduce every degree-four center-diagonal monomial to degree at most three. The block identity extends to order $N$ when $N!$ is invertible. In order four the projective leading zero set is the Segre product of the order-three level-direction locus and $\mathbb P^2$. | [Written block and rank-one argument](manuscript/03-complexity/gct-extension.tex). [Python](python/gct_permanent_plucker.py) generates the 15 order-four rewrites and checks the leaf quadratic Hessian. |
| Hodge collision and orientation | The corrected diagonal readout has off-diagonal collisions exactly at $D=\det A=0$. The Hodge pairing is $4D^2$ in the normalized frame. Over the function field of the unrestricted edge chart, the quadratic orientation cover is nonsplit and has equation $D^2=\det G_U/4$. Over an odd-degree extension of $\mathbb F_5$, at most one of $U,U^\perp$ admits a rational quadratic lift. The higher equations restrict each orientation factor. | [Python](python/gct_permanent_plucker.py) checks the quadratic identity and exports both branch ideals. [Lean](lean/PvsNP/PermanentReadout.lean) derives the determinant square from the Gram factorization. The [discriminant computation](lean/PvsNP/EdgeDiscriminant.lean) verifies the scalar specialization, and the [written proof](manuscript/03-complexity/gct-extension.tex) derives generic nonsplitting. |
| Collision kernel | Every geometric level three-plane has corrected diagonal rank at least two at five and over $\mathbb C$. The collision branch has exactly one kernel line per plane and a 17-variable chart up to leaf permutations. | The [Lean cofactor theorem](lean/PvsNP/PermanentReadout.lean) gives a unique kernel parameter at a unit minor. The [Witt chart cover and specialization](manuscript/03-complexity/gct-extension.tex) give the geometric rank bound. [Python](python/gct_permanent_hodge.py) generates the two-plane chart whose exact reduced msolve basis at five is $[1]$, checks the Gram form on rational two-planes, and emits the 17-variable collision chart. The last ideal remains open. |
| First-colon residual under field extension | The scheme-theoretic image of distinct equal-readout pairs is $V(D)$. Locally the residual has algebra $(R/(D))[u_1,u_2,u_3,\lambda]$. This presentation commutes with arbitrary base change. | Lean computes the [first colon of the three matrix rows](lean/PvsNP/ReadoutPivotIdeal.lean) at a unit pivot and the [residual quotient, base change and punctured-family image kernel](lean/PvsNP/ReadoutResidual.lean). The [matrix theorem](lean/PvsNP/PermanentReadout.lean) gives the unique kernel parameter. [Coverage](manuscript/03-complexity/gct-extension.tex) uses the geometric rank exclusion above. |
| Orientation fields and ramification | At a rational edge plane of nonsquare discriminant a full lift would have even residue degree at least four. On the scalar test line the normalized cover ramifies at the roots of $c^2+c+1$ and splits over the roots of $c^2-c+1$ in $\mathbb F_{25}$. | [Lean](lean/PvsNP/OrientationDescent.lean) proves that coefficientwise Frobenius exchanges the idempotents and that a zero projector implies a zero base algebra. [The degree theorem](lean/PvsNP/PermanentReadout.lean) takes the Gram identity, nonsquare and degree-two exclusion as inputs. [Scalar-line proofs](lean/PvsNP/ScalarOrientation.lean) check the odd-valuation obstruction and the two explicit normalized roots. The [written normalization argument](manuscript/03-complexity/gct-extension.tex) identifies the branch points. |
| Edge families and stabilizers | A transverse pencil has two conjugate ramification points with all 20 edge minors nonzero. Its last two columns forbid any full lift in characteristic five. No transposition or three-cycle stabilizes an occurring edge plane at five or over $\mathbb C$. Its vertex orbit size is 6, 12, or 24. | Lean checks the [Gram determinant](lean/PvsNP/EdgeDiscriminant.lean), the [fixed-pair permanent expansion](lean/PvsNP/TransversePairChart.lean), the [unit-ideal certificate](lean/PvsNP/TransversePair.lean), the resulting [nonconstant permanent over every field of characteristic five](lean/PvsNP/TransversePairLevel.lean), and the [orbit bound given the symmetry exclusions](lean/PvsNP/EdgeStabilizer.lean). [Python](python/gct_permanent_hodge.py) checks all 20 minors and exports the cyclic and transposition systems for msolve. The [manuscript](manuscript/03-complexity/gct-extension.tex) gives chart coverage, the adjacent-edge argument and specialization. |
| Frobenius orbit lower bound | The geometric special fiber at five is empty or has at least 48 points. The same dichotomy holds for the complex fiber. | [Written freeness, descent, and finite flat closure arguments](manuscript/03-complexity/gct-extension.tex). [Python](python/gct_permanent_frobenius.py) verifies the five conjugacy-class searches and the positive double-transposition charts. |
| Invariant quotient criterion | A dimension bound of seven for the star invariant algebra at five proves complex nonexistence. The same bound can be checked separately on the collision and injective branches. For the full algebra a span of at most seven classes containing one and closed under multiplication by 127 known orbit sums suffices. | [Written quotient argument and Noether bound](manuscript/03-complexity/gct-extension.tex). [Lean](lean/PvsNP/InvariantClosure.lean) proves the general finite dimension bound. [Python](python/gct_permanent_plucker.py) computes the orbit sums and the [checker](python/gct_permanent_closure.py) verifies supplied full-chart identities. The dimension bounds remain open. |
| Degree-seven closure obstruction | A seven-element closure certificate starting with one must use an ideal multiple of degree at least eight in at least one identity expressing a generator in the span. In general a degree cap $d$ fails for an $n$-element span when the generators and one have rank above $n$ modulo the permitted degree-$d$ ideal multiples. | [Stored functionals](gct_permanent_star_span_degree7.dual.gz) have rank 20 in low degree. [Python](python/gct_permanent_closure.py) checks the pairings and 98,336 weight-zero products. The [written dimension argument](manuscript/03-complexity/gct-extension.tex) gives rank at least eight on one and the low-degree generators. |

## PEqualNP contribution status

| Step | Exact scope | Evidence and status |
| --- | --- | --- |
| `L-meta-4211` | A monotone circuit with at most 62 gates cannot realize the posted incidence examples by OR-ing two selected wires. | Reviewed and returned to the desk. The [public reduction](SOURCE-LEDGER.md#peq) isolates the remaining lower bound for a circuit with at most 63 gates and a single output. |
| `L-meta-19020` | Every pair of sparse point and line sets with no incidences in the order-three plane is covered by a relabeling of one of eight sample masks. | An independent Python enumeration covered all 12,234 eligible pairs. Another contributor's [Lean proof #23821](https://github.com/open-goat/pequalnp-proofs/pull/23821) merged. |
| `R-meta-17715-1`, second hypothesis | An order-two incidence circuit with the specified first AND gate needs a second gate. | Lean checked the exact hypothesis in the public fork's pinned environment. The desk recorded [merged PR #23858](https://github.com/open-goat/pequalnp-proofs/pull/23858) as a surplus reduction. |
| `R-meta-17918-2` and `R-meta-17920-2`, first hypotheses | An order-three incidence circuit cannot use a primary input as its output. A singleton input would make that output true without any incidence. | Lean checked both exact hypotheses in the public fork's pinned environment. The desk recorded [merged PR #23852](https://github.com/open-goat/pequalnp-proofs/pull/23852) and [#23853](https://github.com/open-goat/pequalnp-proofs/pull/23853) as surplus reductions. |
| `R-meta-17243-1` | Reduces the AND-last case under `L-meta-1990` to one generated output wire or two distinct generated output wires. | The Lean build, import guards, and compiled declaration check passed locally. [PR #24293](https://github.com/open-goat/pequalnp-proofs/pull/24293) merged on 2026-11-26. The desk recorded it as surplus because the new cases would be at depth 3. |
| `L-meta-1990`, parent-level draft | Trim the circuit after its latest selected generated wire. The 63-gate lower bound follows from the two existing AND-last obligations and an OR-last obligation with a nonempty list of distinct generated outputs that includes the last wire. | The [Lean draft](contributions/pequalnp/R_meta_1990_997.lean) compiled in the public project's pinned environment. The parent is at depth 1. The [intake decision on a separate contribution](https://github.com/open-goat/pequalnp-proofs/pull/24564#issuecomment-7193607202) confirms that the existing case split fills the case-split slot. |
| `L-meta-23645` | An eight-gate circuit computes the posted mask 34612 on six shared inputs, with the input marking an ordered pair and allowing repeated indices. | The concrete AND/OR witness passed all 36 ordered pairs independently and in the pinned Lean build. Intake [closed our PR #33168](https://github.com/open-goat/pequalnp-proofs/pull/33168#issuecomment-7203883959) after [PR #32240](https://github.com/open-goat/pequalnp-proofs/pull/32240) merged the same step. |

### Restricting the order-three incidence circuit

| Step | Exact scope | Evidence |
| --- | --- | --- |
| Sparse observations determine the full function | An incidence-free pair has at most three vertices on one side. A monotone scan satisfying the posted singleton positives and sparse negatives computes the entire incidence function. | [Lean](lean/PvsNP/IncidenceObservations.lean) checks all 715 four-point subsets and proves the observation equivalence. Appending an OR gate to the scan gives the comparison between the parent budget of 63 and the full-function budget of 64. |
| Restriction to zero | Delete the fixed vertex. The remaining graph has 48 edges and a 59-gate vertex-cover construction. On either 64-gate star circuit, fixing a vertex on the side used for factoring saves five gates, including three private gates. Fixing on the other side saves four. | The [Python experiment](python/incidence_gate_elimination.py) constructs and checks the restricted circuits exactly. The 59-gate lower bound is the open [L-meta-9738](https://data.pequalnp.com/data/lemma/L-meta-9738.7288f9095344.json). |
| Restriction to one | The four neighbors contribute singleton terms. The graph outside the closed neighborhood has 36 edges. Together they admit a 48-gate construction. On either 64-gate star circuit, fixing a vertex on the opposite side saves sixteen gates, and fixing on the factored side saves one. | [Lean](lean/PvsNP/IncidenceObservations.lean) proves the decomposition. The Python experiment checks all 104 restrictions of the two explicit circuits and verifies the 48-gate construction. |

There is a sufficient condition for a five-gate saving in a smallest
AND/OR circuit for the full incidence function. Suppose a point input $p$
has just one reader $g=p\land w$, and the gate cone for $w$ has consumers
only within that cone or at $g$. The wire $w$ is independent of $p$ and
must accept each of the four neighboring line singletons. Comparing the
positive input $(p,\ell)$ with the negative input $\ell$ forces this
because only $g$ reads $p$. At the empty input $w$ must be false, since an
always-true $w$ would make $g$ a removable copy of $p$. Thus $w$ depends on
at least four inputs and needs at least three gates, since a cone with $s$
fan-in-two gates depends on at most $s+1$ input wires. Setting $p=0$ makes
$g$ constant and deletes its private cone. The restricted output remains
nonconstant, so $g$ is an interior gate, and minimality gives it a later
reader. That reader also simplifies, saving at least five gates in total.
This is a written argument using the
deletion pattern certified in [L-meta-18649](SOURCE-LEDGER.md#peq).

An induction through these restrictions would need a five- or sixteen-gate
saving for some vertex of every candidate smallest circuit, together with
the corresponding restricted lower bound. The 48-gate target can in turn
be reduced to a 44-gate lower bound on the 36-edge graph. Each of the four
essential singleton inputs can be fixed to zero in turn, simplifying at
least one direct reader while leaving the graph term nonconstant. These
size claims concern AND/OR circuits. The published pruning theorem is stated
with AND/OR/NOT outputs, so a general use of its construction in this
induction would need a proof that it preserves the monotone gate set.

Run `python3 python/affine_witness_selector.py` to see the common squared CVP cost
on two distinct witnesses and then reduce the fiber to one witness with a
residual coordinate. Run `lake build` from `lean/` for the Lean declarations.
Run `python3 python/polynomial_agreement_selector.py` for the four-site
certificate and prefix examples.
Run `python3 python/incidence_gate_elimination.py` for the
incidence restriction and pruning experiment.
Run `python3 python/gct_permanent_fiber.py` for the symmetric permanent level
plane and the exact coefficient check at order four.
Run `latexmk -pdf -outdir=.build main.tex` from `manuscript/` to build the draft.
