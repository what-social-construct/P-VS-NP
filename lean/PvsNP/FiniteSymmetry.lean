module

public import PvsNP.GaloisOrbitMatrices
public import GaloisExport.PermutationCommutant
public import Mathlib.Algebra.Group.Action.Basic
public import Mathlib.Data.Matrix.Mul
public import Mathlib.LinearAlgebra.Dimension.StrongRankCondition

@[expose] public section

namespace PvsNP.FiniteSymmetry

open HodgeConjecture.OrbitMatrices (InvariantMatrices PairOrbits orbitBasis)

variable {G S : Type*} [Group G] [MulAction G S]

/-- Inverse pullback is the left permutation action on coefficient functions. -/
def permutationMap (g : G) : (S → ℚ) →ₗ[ℚ] (S → ℚ) :=
  HodgeConjecture.OrbitMatrices.permutationMap g

@[simp]
theorem permutationMap_apply (g : G) (v : S → ℚ) (j : S) :
    permutationMap g v j = v (g⁻¹ • j) :=
  HodgeConjecture.OrbitMatrices.permutationMap_apply g v j

theorem permutationMap_one :
    permutationMap (1 : G) = LinearMap.id (R := ℚ) (M := S → ℚ) :=
  HodgeConjecture.OrbitMatrices.permutationMap_one

theorem permutationMap_mul (g h : G) :
    permutationMap (S := S) (g * h) = (permutationMap g).comp (permutationMap h) :=
  HodgeConjecture.OrbitMatrices.permutationMap_mul g h

/-- Rows are targets and columns are sources. Simultaneous invariance of
the entries is equivalent to commuting with the permutation action. -/
theorem invariant_iff_mulVec_commutes [Fintype S] (A : Matrix S S ℚ) :
    A ∈ InvariantMatrices G S ↔
      ∀ (g : G) (v : S → ℚ),
        A.mulVec (permutationMap g v) = permutationMap g (A.mulVec v) :=
  HodgeConjecture.OrbitMatrices.invariant_iff_mulVec_commutes A

/-- There is one independent invariant matrix coordinate per ordered-pair orbit. -/
theorem invariant_finrank [Finite S] :
    Module.finrank ℚ (InvariantMatrices G S) = Nat.card (PairOrbits G S) :=
  Module.finrank_eq_nat_card_basis (orbitBasis G S)

end PvsNP.FiniteSymmetry
