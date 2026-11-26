module

public import HCP.CoupledSignResidual

@[expose] public section

/-!
The Paper 1 import closure is copied from homotopical-encrypt at revision
e619391ec7d40c5349ebe31846e24461e0b49649 under the accompanying MIT license.
The bridge below uses the original fresh-sign objective and mask equivalence.
-/

namespace PvsNP

set_option autoImplicit false

open HomotopicalEncryption.HCP.CoupledSignResidual
open HomotopicalEncryption.Protocol.Transfer.PathSignature.NativeSignSampler

/-- On a fixed public mask, distinct compatible keys give different messages
while their respective supplied lattices give the same minimum cost. -/
theorem distinct_messages_same_minimum
    {rows cols : ℕ} (A : Matrix (Fin rows) (Fin cols) ℤ) (d a : ℤ)
    (orthogonal : A.transpose * A = d • (1 : Matrix (Fin cols) (Fin cols) ℤ))
    (masked key other : Fin cols → Bool) (different : key ≠ other) :
    mask key masked ≠ mask other masked ∧
      fixedMaskCost A d a key masked (coefficients d (mask key masked)) =
        fixedMaskCost A d a other masked (coefficients d (mask other masked)) := by
  exact ⟨(maskEquiv masked).injective.ne different,
    (cost_at_message A d a orthogonal key masked).trans
      (cost_at_message A d a orthogonal other masked).symm⟩

section Affine

variable {R M N : Type*} [Ring R] [AddCommGroup M] [Module R M]
  [AddCommGroup N] [Module R N] (Q : M →ₗ[R] N) (c : N)

/-- A pair in one affine fiber is its first point and a homogeneous
direction. This also applies when the fiber is empty. -/
def collisionEquiv :
    ({v : M // Q v = c} × {v : M // Q v = c}) ≃
      ({v : M // Q v = c} × LinearMap.ker Q) where
  toFun p := (p.1, ⟨p.2.val - p.1.val, by
    simp [p.1.property, p.2.property]⟩)
  invFun p := (p.1, ⟨p.1.val + p.2.val, by
    simp [p.1.property, (LinearMap.mem_ker.mp p.2.property)]⟩)
  left_inv p := by
    refine Prod.ext ?_ ?_
    · rfl
    · apply Subtype.ext
      change p.1.val + (p.2.val - p.1.val) = p.2.val
      abel
  right_inv p := by
    refine Prod.ext ?_ ?_
    · rfl
    · apply Subtype.ext
      change p.1.val + p.2.val - p.1.val = p.2.val
      abel

/-- The diagonal consists exactly of the pairs with zero direction. -/
theorem collisionEquiv_diagonal (left right : {v : M // Q v = c}) :
    (collisionEquiv Q c (left, right)).2 = 0 ↔ left = right := by
  constructor
  · intro h
    have hzero : right.val - left.val = 0 := congrArg (fun v : LinearMap.ker Q ↦ v.val) h
    exact Subtype.ext (sub_eq_zero.mp hzero).symm
  · rintro rfl
    apply Subtype.ext
    exact sub_self _

end Affine
end PvsNP
