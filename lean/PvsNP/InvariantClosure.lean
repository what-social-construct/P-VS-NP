module

public import Mathlib.RingTheory.Adjoin.Basic
public import Mathlib.LinearAlgebra.Dimension.Constructions

@[expose] public section

namespace PvsNP

variable {K A : Type*} [Field K] [Ring A] [Algebra K A]

/-- Stability under multiplication by algebra generators makes a submodule
containing one equal to the whole algebra. -/
theorem submodule_eq_top_of_generator_mul
    {S : Set A} (hS : Algebra.adjoin K S = ⊤) (W : Submodule K A)
    (hone : 1 ∈ W)
    (hmul : ∀ s ∈ S, ∀ w ∈ W, s * w ∈ W) : W = ⊤ := by
  apply top_unique
  intro x _
  have hx : x ∈ Algebra.adjoin K S := by simp [hS]
  have hxmul : ∀ w ∈ W, x * w ∈ W := by
    refine Algebra.adjoin_induction (p := fun x _ => ∀ w ∈ W, x * w ∈ W)
      hmul ?_ ?_ ?_ hx
    · intro a w hw
      rw [← Algebra.smul_def]
      exact W.smul_mem a hw
    · intro a b _ _ ha hb w hw
      rw [add_mul]
      exact W.add_mem (ha w hw) (hb w hw)
    · intro a b _ _ ha hb w hw
      rw [mul_assoc]
      exact ha _ (hb w hw)
  simpa using hxmul 1 hone

/-- A family of (n) vectors gives a dimension upper bound when its
span contains one and is stable under multiplication by the generators. -/
theorem finite_and_finrank_le_of_generator_mul_span
    {S : Set A} (hS : Algebra.adjoin K S = ⊤) {n : ℕ} (basis : Fin n → A)
    (hone : 1 ∈ Submodule.span K (Set.range basis))
    (hmul : ∀ s ∈ S, ∀ j, s * basis j ∈ Submodule.span K (Set.range basis)) :
    Module.Finite K A ∧ Module.finrank K A ≤ n := by
  let W := Submodule.span K (Set.range basis)
  have htop : W = ⊤ := submodule_eq_top_of_generator_mul hS W hone (by
    intro s hs w hw
    refine Submodule.span_induction (p := fun w _ => s * w ∈ W) ?_ ?_ ?_ ?_ hw
    · rintro _ ⟨j, rfl⟩
      exact hmul s hs j
    · rw [mul_zero]
      exact W.zero_mem
    · intro x y _ _ hx hy
      rw [mul_add]
      exact W.add_mem hx hy
    · intro a x _ hx
      rw [mul_smul_comm]
      exact W.smul_mem a hx)
  refine ⟨Module.Finite.of_fg_top ?_, ?_⟩
  · rw [← htop]
    exact Submodule.fg_span (Set.finite_range basis)
  · have hdim := finrank_range_le_card (R := K) basis
    change Module.finrank K W ≤ _ at hdim
    rw [htop, finrank_top] at hdim
    simpa only [Fintype.card_fin] using hdim

end PvsNP
