module

public import Mathlib.LinearAlgebra.CrossProduct
public import PvsNP.OrientationDescent
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.LinearCombination
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Ring

@[expose] public section

namespace PvsNP.PermanentReadout

open Matrix

variable {R : Type*} [CommRing R]

/-- Dot product on traceless diagonals in the first three coordinates. -/
def traceZeroGram (R : Type*) [CommRing R] : Matrix (Fin 3) (Fin 3) R :=
  !![2, 1, 1; 1, 2, 1; 1, 1, 2]

/-- The quadratic permanent equations give the displayed Gram factorization.
Taking determinants gives the square detected by the Hodge pairing. -/
theorem det_edgeGram (G A : Matrix (Fin 3) (Fin 3) R)
    (hG : G = A.transpose * traceZeroGram R * A) : G.det = 4 * A.det^2 := by
  have hT : (traceZeroGram R).det = 4 := by
    norm_num [traceZeroGram, det_fin_three]
  rw [hG, det_mul, det_mul, det_transpose, hT]
  ring

/-- For a lifted edge Gram matrix, a nonsquare base discriminant forces
even degree. The exclusion of degree two is a separate geometric input. -/
theorem degree_of_edge_lift {K L : Type*} [Field K] [Field L] [Algebra K L]
    [FiniteDimensional K L] (G : Matrix (Fin 3) (Fin 3) K)
    (A : Matrix (Fin 3) (Fin 3) L) {a : K} (h₄ : (4 : K) ≠ 0)
    (hdisc : G.det = 4 * a) (ha : ∀ b : K, b^2 ≠ a)
    (hG : (algebraMap K L).mapMatrix G = A.transpose * traceZeroGram L * A)
    (h₂ : Module.finrank K L ≠ 2) :
    2 ∣ Module.finrank K L ∧ 4 ≤ Module.finrank K L := by
  have h := det_edgeGram _ A hG
  rw [← RingHom.map_det, hdisc, map_mul, map_ofNat] at h
  have h₄' : (4 : L) ≠ 0 := by
    simpa only [map_ofNat, map_zero] using (algebraMap K L).injective.ne h₄
  apply OrientationDescent.even_degree_ge_four ha (d := A.det) _ h₂
  exact mul_left_cancel₀ h₄' h.symm

/-- On the chart with the first two rows and columns as pivot, the last
component of this cross product is the pivot minor. -/
abbrev cofactorDirection (A : Matrix (Fin 3) (Fin 3) R) :=
  crossProduct (A 0) (A 1)

theorem mulVec_cofactorDirection (A : Matrix (Fin 3) (Fin 3) R) :
    A *ᵥ cofactorDirection A = ![0, 0, A.det] := by
  funext i
  fin_cases i
  · exact dot_self_cross _ _
  · exact dot_cross_self _ _
  · change A 2 ⬝ᵥ cofactorDirection A = A.det
    simp only [cofactorDirection, cross_apply, vec3_dotProduct,
      Matrix.cons_val, det_fin_three]
    ring

/-- Over any commutative ring, a unit pivot identifies zero-readout
differences with scalar multiples of the cofactor direction annihilated by
the readout determinant. The scalar is unique even over a nonreduced ring. -/
theorem kernel_iff_unique_parameter (A : Matrix (Fin 3) (Fin 3) R)
    (pivot : IsUnit (cofactorDirection A 2)) (w : Fin 3 → R) :
    A *ᵥ w = 0 ↔ ∃! t : R, t • cofactorDirection A = w ∧ t * A.det = 0 := by
  obtain ⟨u, hu⟩ := pivot
  constructor
  · intro hw
    have row (i : Fin 3) : A i 0 * w 0 + A i 1 * w 1 + A i 2 * w 2 = 0 := by
      simpa only [mulVec, vec3_dotProduct, Pi.zero_apply] using congrFun hw i
    have minors (i : Fin 3) :
        w 2 * cofactorDirection A i = (u : R) * w i := by
      rw [hu]
      fin_cases i
      · change w 2 * (A 0 1 * A 1 2 - A 0 2 * A 1 1) =
          (A 0 0 * A 1 1 - A 0 1 * A 1 0) * w 0
        linear_combination A 0 1 * row 1 - A 1 1 * row 0
      · change w 2 * (A 0 2 * A 1 0 - A 0 0 * A 1 2) =
          (A 0 0 * A 1 1 - A 0 1 * A 1 0) * w 1
        linear_combination A 1 0 * row 0 - A 0 0 * row 1
      · exact mul_comm _ _
    let t := (↑u⁻¹ : R) * w 2
    have htw : t • cofactorDirection A = w := by
      funext i
      change ((↑u⁻¹ : R) * w 2) * _ = _
      rw [mul_assoc, minors, ← mul_assoc, Units.inv_mul, one_mul]
    have ht : t * A.det = 0 := by
      rw [← htw, mulVec_smul, mulVec_cofactorDirection] at hw
      exact congrFun hw 2
    refine ⟨t, ⟨htw, ht⟩, ?_⟩
    rintro s ⟨hs, _⟩
    have heq := congrFun (hs.trans htw.symm) 2
    change s * cofactorDirection A 2 = t * cofactorDirection A 2 at heq
    rw [← hu] at heq
    exact u.isUnit.mul_left_inj.mp heq
  · rintro ⟨t, ⟨rfl, ht⟩, _⟩
    rw [mulVec_smul, mulVec_cofactorDirection]
    funext i
    fin_cases i <;> simp [Pi.smul_apply, ht]

end PvsNP.PermanentReadout
