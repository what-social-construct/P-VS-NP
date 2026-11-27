/-
Copyright (c) 2026 what-social-construct. Released under the MIT license in ../LICENSE.
The permutation action and commutation criterion originated in PvsNP.FiniteSymmetry.
-/
module

public import GaloisObstructionTheory.Hodge.LinearAlgebra.OrbitMatrices
public import Mathlib.Algebra.Group.Action.Basic
public import Mathlib.Data.Matrix.Mul

@[expose] public section

namespace HodgeConjecture.OrbitMatrices

open scoped BigOperators

variable {G S : Type*} [Group G] [MulAction G S]

-- BEGIN GALOIS EXPORT
/-- Inverse pullback is the left permutation action on coefficient functions. -/
def permutationMap (g : G) : (S → ℚ) →ₗ[ℚ] (S → ℚ) where
  toFun v := fun j => v (g⁻¹ • j)
  map_add' _ _ := rfl
  map_smul' _ _ := rfl

@[simp]
theorem permutationMap_apply (g : G) (v : S → ℚ) (j : S) :
    permutationMap g v j = v (g⁻¹ • j) := rfl

theorem permutationMap_one :
    permutationMap (1 : G) = LinearMap.id (R := ℚ) (M := S → ℚ) := by
  apply LinearMap.ext
  intro v
  funext j
  simp

theorem permutationMap_mul (g h : G) :
    permutationMap (S := S) (g * h) = (permutationMap g).comp (permutationMap h) := by
  apply LinearMap.ext
  intro v
  funext j
  simp [mul_inv_rev, mul_smul]

/-- Rows are targets and columns are sources. Simultaneous invariance of
the entries is equivalent to commuting with the permutation action. -/
theorem invariant_iff_mulVec_commutes [Fintype S] (A : Matrix S S ℚ) :
    A ∈ InvariantMatrices G S ↔
      ∀ (g : G) (v : S → ℚ),
        A.mulVec (permutationMap g v) = permutationMap g (A.mulVec v) := by
  constructor
  · intro invariant g v
    funext j
    change (∑ i : S, A j i * v (g⁻¹ • i)) = ∑ i : S, A (g⁻¹ • j) i * v i
    calc
      _ = ∑ i : S, A j (g • i) * v (g⁻¹ • (g • i)) :=
        (Equiv.sum_comp (MulAction.toPerm (β := S) g)
          (fun i => A j i * v (g⁻¹ • i))).symm
      _ = _ := by
        apply Finset.sum_congr rfl
        intro i _
        have h := invariant g (g⁻¹ • j) i
        rw [smul_inv_smul] at h
        rw [inv_smul_smul, h]
  · intro commutes
    change ∀ (g : G) (j i : S), A (g • j) (g • i) = A j i
    intro g j i
    classical
    have basisMoved : permutationMap g (Pi.single i (1 : ℚ)) = Pi.single (g • i) 1 := by
      funext k
      have h : (g⁻¹ • k = i) ↔ k = g • i := by
        constructor
        · intro hk
          rw [← hk, smul_inv_smul]
        · intro hk
          rw [hk, inv_smul_smul]
      simp [Pi.single_apply, h]
    have h := congrFun (commutes g (Pi.single i 1)) (g • j)
    rw [basisMoved, Matrix.mulVec_single_one, Matrix.mulVec_single_one] at h
    simpa using h
-- END GALOIS EXPORT

end HodgeConjecture.OrbitMatrices
