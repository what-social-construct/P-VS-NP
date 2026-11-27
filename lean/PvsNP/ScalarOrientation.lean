module

public import PvsNP.QuadraticDVRParity
public import Mathlib.Algebra.CharP.Defs
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.LinearCombination
import Mathlib.Tactic.Ring

@[expose] public section

namespace PvsNP.ScalarOrientation

/-- Removing a square factor from the scalar-line discriminant preserves
the odd-valuation obstruction at a DVR of its function field. -/
theorem no_orientation_of_odd_order
    {R K : Type*} [CommRing R] [IsDomain R] [IsDiscreteValuationRing R]
    [Field K] [Algebra R K] [IsFractionRing R K]
    (π : R) (hπ : Irreducible π) (u : Rˣ) (m : ℕ)
    (c : K) (hh : c^2 - c + 1 ≠ 0)
    (hodd : 3 * (c^2 + c + 1) = algebraMap R K (π^(2*m+1) * (u : R))) :
    ¬∃ D : K, D^2 = 3 * (c^2 - c + 1)^2 * (c^2 + c + 1) := by
  rintro ⟨D, hD⟩
  apply CollisionIdeals.no_square_eq_odd_uniformizer_mul_unit π hπ u m
    (D / (c^2 - c + 1))
  rw [← hodd, div_pow, div_eq_iff (pow_ne_zero _ hh), hD]
  ring

/-- At a root of the discarded factor in characteristic five the normalized
equation has exactly the two distinct roots ±2(c−1), already over the
field of definition of c. -/
theorem normalized_roots_at_double_zero {K : Type*} [Field K] [CharP K 5]
    (c : K) (hc : c^2 - c + 1 = 0) :
    2*(c-1) ≠ -(2*(c-1)) ∧
      ∀ v : K, v^2 = 3*(c^2 + c + 1) ↔ v = 2*(c-1) ∨ v = -(2*(c-1)) := by
  have h5 : (5 : K) = 0 := CharP.cast_eq_zero K 5
  have hroot : (2*(c-1))^2 = 3*(c^2+c+1) := by
    linear_combination hc - 2*c*h5
  constructor
  · intro heq
    have hc1 : 4*(c-1) = 0 := by linear_combination heq
    have hc4 : (4 : K) ≠ 0 := fun h => by
      have : (1 : K) = 0 := by linear_combination h5 - h
      exact one_ne_zero this
    have h1 : c = 1 := sub_eq_zero.mp ((mul_eq_zero.mp hc1).resolve_left hc4)
    simp [h1] at hc
  · intro v
    rw [← hroot, sq_eq_sq_iff_eq_or_eq_neg]

end PvsNP.ScalarOrientation
