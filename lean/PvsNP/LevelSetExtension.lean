module

public import Mathlib.Algebra.MvPolynomial.Eval
public import Mathlib.Algebra.Polynomial.Roots
public import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas
public import Mathlib.LinearAlgebra.Pi
import Mathlib.Tactic.Ring

@[expose] public section

namespace PvsNP.LevelSetExtension

variable {K σ ι : Type*} [Field K]

/-- Substitute the affine line through `x` in direction `v` into `p`. -/
noncomputable def line (p : MvPolynomial σ K) (x v : σ → K) : Polynomial K :=
  MvPolynomial.eval₂ Polynomial.C (fun i => Polynomial.C (x i) + Polynomial.X * Polynomial.C (v i)) p

theorem eval_line (p : MvPolynomial σ K) (x v : σ → K) (t : K) :
    (line p x v).eval t = MvPolynomial.eval (x + t • v) p := by
  change Polynomial.evalRingHom t (line p x v) = _
  rw [line, MvPolynomial.eval₂_comp_left]
  have hC : (Polynomial.evalRingHom t).comp Polynomial.C = RingHom.id K :=
    Polynomial.eval₂RingHom_comp_C _ _
  have hX : Polynomial.evalRingHom t ∘
      (fun i => Polynomial.C (x i) + Polynomial.X * Polynomial.C (v i)) = x + t • v := by
    funext i
    simp
    exact mul_comm _ _
  rw [hC, hX]
  rfl

private theorem coeff_zero_line (p : MvPolynomial σ K) (x v : σ → K) :
    (line p x v).coeff 0 = MvPolynomial.eval x p := by
  simpa [Polynomial.coeff_zero_eq_eval_zero] using (eval_line p x v 0)

private theorem coeff_one_mul (p q : Polynomial K) :
    (p * q).coeff 1 = p.coeff 0 * q.coeff 1 + p.coeff 1 * q.coeff 0 := by
  rw [Polynomial.coeff_mul]
  have h : Finset.antidiagonal 1 = {(0, 1), (1, 0)} := by decide
  rw [h]
  simp

private theorem coeff_one_line_combination (p : MvPolynomial σ K) (x u v : σ → K) (a : K) :
    (line p x (a • u + v)).coeff 1 =
      a * (line p x u).coeff 1 + (line p x v).coeff 1 := by
  induction p using MvPolynomial.induction_on with
  | C b => simp [line]
  | add p q hp hq =>
    simp only [line, MvPolynomial.eval₂_add, Polynomial.coeff_add] at hp hq ⊢
    rw [hp, hq]
    ring
  | mul_X p i hp =>
    have hm (w : σ → K) :
        (line (p * MvPolynomial.X i) x w).coeff 1 =
        MvPolynomial.eval x p * w i + (line p x w).coeff 1 * x i := by
      have eqn : line (p * MvPolynomial.X i) x w =
          line p x w * (Polynomial.C (x i) + Polynomial.X * Polynomial.C (w i)) := by
        simp [line]
      rw [eqn, coeff_one_mul, coeff_zero_line]
      simp
    rw [hm, hm, hm, hp]
    simp
    ring

/-- The coefficient of the first power of the line parameter is linear in the direction. -/
noncomputable def firstVariation (p : MvPolynomial σ K) (x : σ → K) : (σ → K) →ₗ[K] K where
  toFun v := (line p x v).coeff 1
  map_add' u v := by simpa using coeff_one_line_combination p x u v 1
  map_smul' a u := by
    have h : (line p x (0 : σ → K)).coeff 1 =
        (line p x (0 : σ → K)).coeff 1 + (line p x (0 : σ → K)).coeff 1 := by
      simpa using coeff_one_line_combination p x (0 : σ → K) 0 1
    have hz : (line p x (0 : σ → K)).coeff 1 = 0 :=
      add_left_cancel (h.symm.trans (add_zero _).symm)
    simpa [hz, smul_eq_mul] using coeff_one_line_combination p x u (0 : σ → K) a

/-- Simultaneous first variations of the supplied polynomials along the subspace `W`. -/
noncomputable def variationOn (polynomials : ι → MvPolynomial σ K) (W : Submodule K (σ → K)) :
    (σ → K) →ₗ[K] (ι → W → K) :=
  LinearMap.pi fun i => LinearMap.pi fun x : W => firstVariation (polynomials i) x

/-- Every direction in a larger level space lies in the first-variation kernel. -/
theorem le_ker_variationOn [Infinite K] (polynomials : ι → MvPolynomial σ K)
    {W L : Submodule K (σ → K)} (inclusion : W ≤ L)
    (level : ∀ i, ∀ x ∈ L, MvPolynomial.eval x (polynomials i) = 0) :
    L ≤ LinearMap.ker (variationOn polynomials W) := by
  intro v hv
  rw [LinearMap.mem_ker]
  funext i x
  change (line (polynomials i) (x : σ → K) v).coeff 1 = 0
  have hline : line (polynomials i) (x : σ → K) v = 0 := by
    apply Polynomial.funext
    intro t
    rw [eval_line, Polynomial.eval_zero]
    exact level i _ (L.add_mem (inclusion x.property) (L.smul_mem t hv))
  simp [hline]

/-- Rank-nullity bounds the dimension of any level space containing `W`. -/
theorem rank_add_level_le [Infinite K] [Finite σ] (polynomials : ι → MvPolynomial σ K)
    {W L : Submodule K (σ → K)} (inclusion : W ≤ L)
    (level : ∀ i, ∀ x ∈ L, MvPolynomial.eval x (polynomials i) = 0) :
    Module.finrank K (LinearMap.range (variationOn polynomials W)) + Module.finrank K L ≤
      Module.finrank K (σ → K) := by
  classical
  let _ : Fintype σ := Fintype.ofFinite σ
  rw [← (variationOn polynomials W).finrank_range_add_finrank_ker]
  exact Nat.add_le_add_left
    (Submodule.finrank_mono (le_ker_variationOn polynomials inclusion level)) _

/-- A hyperplane meets a level space of dimension at least `n+1` in an `n`-plane. -/
theorem exists_finrank_submodule_inf_ker
    {K V : Type*} [Field K] [AddCommGroup V] [Module K V]
    (L : Submodule K V) [Module.Finite K L] (f : V →ₗ[K] K)
    {n : ℕ} (hn : n + 1 ≤ Module.finrank K L) :
    ∃ W : Submodule K V, W ≤ L ⊓ LinearMap.ker f ∧ Module.finrank K W = n := by
  let g : L →ₗ[K] K := f.comp L.subtype
  have hrange : Module.finrank K (LinearMap.range g) ≤ 1 := by
    simpa using (LinearMap.range g).finrank_le
  have hdim := g.finrank_range_add_finrank_ker
  have hker : n ≤ Module.finrank K (LinearMap.ker g) := by omega
  obtain ⟨v, hv⟩ := exists_linearIndependent_of_le_finrank hker
  let i : LinearMap.ker g →ₗ[K] V := L.subtype.comp (LinearMap.ker g).subtype
  have hi : Function.Injective i :=
    L.subtype_injective.comp (LinearMap.ker g).subtype_injective
  have hli : LinearIndependent K (i ∘ v) := hv.map' i (LinearMap.ker_eq_bot.mpr hi)
  refine ⟨Submodule.span K (Set.range (i ∘ v)), Submodule.span_le.mpr ?_, ?_⟩
  · rintro _ ⟨j, rfl⟩
    change ((v j : L) : V) ∈ L ⊓ LinearMap.ker f
    exact ⟨(v j : L).property, (v j).property⟩
  · simpa using finrank_span_eq_card hli

/-- Maximality of the level two-planes in a hyperplane excludes a level three-plane. -/
theorem no_threePlane_of_hyperplane_maximal
    {K V : Type*} [Field K] [AddCommGroup V] [Module K V] [Module.Finite K V]
    (f : V →ₗ[K] K) (P : Submodule K V → Prop)
    (hmono : ∀ {W L : Submodule K V}, W ≤ L → P L → P W)
    (hmax : ∀ W : Submodule K V, W ≤ LinearMap.ker f →
      Module.finrank K W = 2 → P W →
      ∀ L : Submodule K V, W ≤ L → P L → L = W) :
    ¬ ∃ L : Submodule K V, Module.finrank K L = 3 ∧ P L := by
  rintro ⟨L, hLdim, hL⟩
  obtain ⟨W, hW, hWdim⟩ :=
    exists_finrank_submodule_inf_ker L f (n := 2) (by omega)
  have hWL : W ≤ L := hW.trans inf_le_left
  have hWf : W ≤ LinearMap.ker f := hW.trans inf_le_right
  have hLW := hmax W hWf hWdim (hmono hWL hL) L hWL hL
  rw [hLW, hWdim] at hLdim
  omega

end PvsNP.LevelSetExtension
