module

public import PvsNP.EdgeDiscriminant
public import Mathlib.Analysis.Real.Sqrt
public import Mathlib.Basic.Complex.Basic
import Mathlib.Algebra.Order.BigOperators.Ring.Finset
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring

/-! # Real orientation sheets of the transverse edge pencil -/

@[expose] public section

namespace PvsNP.RealOrientation

open EdgeDiscriminant

/-- For any finite list of complex equations, their squared norms sum to
zero precisely at the common zeros. This applies pointwise to polynomial values. -/
theorem sum_normSq_eq_zero_iff {ι : Type*} (s : Finset ι) (z : ι → ℂ) :
    (∑ i ∈ s, Complex.normSq (z i)) = 0 ↔ ∀ i ∈ s, z i = 0 := by
  rw [Finset.sum_eq_zero_iff_of_nonneg (fun i _ => Complex.normSq_nonneg (z i))]
  simp only [Complex.normSq_eq_zero]

/-- A positive constant and a square give a uniform positivity certificate. -/
theorem transverse_complete_square (v : ℝ) :
    643 * transverseRadicand v = (643*v - 1450)^2 + 7390752 := by
  rw [transverseRadicand]
  ring

theorem transverse_radicand_pos (v : ℝ) : 0 < transverseRadicand v := by
  linarith [transverse_complete_square v, sq_nonneg (643*v - 1450)]

/-- For the actual Gram determinant the two orientations are the two
explicit square roots. The positive one is strictly positive at every v. -/
theorem transverse_orientations (v D : ℝ) :
    (graphGram (transverseGraph v)).det = 4 * D^2 ↔
      D = Real.sqrt (transverseRadicand v) ∨ D = -Real.sqrt (transverseRadicand v) := by
  rw [transverse_gram_det_integral, ← sq_eq_sq_iff_eq_or_eq_neg,
    Real.sq_sqrt (transverse_radicand_pos v).le]
  constructor <;> intro h <;> linarith

/-- The orientation equation and the strict sign inequality select a single
real point in each orientation fiber. -/
theorem existsUnique_positive_orientation (v : ℝ) :
    ∃! D : ℝ, 0 < D ∧ (graphGram (transverseGraph v)).det = 4 * D^2 := by
  have hs := Real.sqrt_pos.mpr (transverse_radicand_pos v)
  refine ⟨_, ⟨hs, (transverse_orientations _ _).2 (Or.inl rfl)⟩, ?_⟩
  intro D hD
  rcases (transverse_orientations _ _).1 hD.2 with h | h
  · exact h
  · linarith [hD.1]

end PvsNP.RealOrientation
