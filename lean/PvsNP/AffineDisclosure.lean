module

public import Mathlib.Algebra.Module.Submodule.Ker
import Mathlib.Tactic.Abel

@[expose] public section

namespace PvsNP

set_option autoImplicit false

variable {R M N Z : Type*} [Ring R] [AddCommGroup M] [Module R M]
  [AddCommGroup N] [Module R N] (Q : M →ₗ[R] N) (c : N)

abbrev AffineFiber := {v : M // Q v = c}

/-- A pair in one affine fiber is its first point and a homogeneous
direction. This also applies when the fiber is empty. -/
def collisionEquiv :
    (AffineFiber Q c × AffineFiber Q c) ≃ (AffineFiber Q c × LinearMap.ker Q) where
  toFun p := (p.1, ⟨p.2.val - p.1.val, by
    simp [p.1.property, p.2.property]⟩)
  invFun p := (p.1, ⟨p.1.val + p.2.val, by
    simp [p.1.property, (LinearMap.mem_ker.mp p.2.property)]⟩)
  left_inv p := by
    refine Prod.ext rfl (Subtype.ext ?_)
    change p.1.val + (p.2.val - p.1.val) = p.2.val
    abel
  right_inv p := by
    refine Prod.ext rfl (Subtype.ext ?_)
    change p.1.val + p.2.val - p.1.val = p.2.val
    abel

/-- The diagonal consists exactly of the pairs with zero direction. -/
theorem collisionEquiv_diagonal (left right : AffineFiber Q c) :
    (collisionEquiv Q c (left, right)).2 = 0 ↔ left = right := by
  constructor
  · intro h
    have hzero : right.val - left.val = 0 := congrArg (fun v : LinearMap.ker Q ↦ v.val) h
    exact Subtype.ext (sub_eq_zero.mp hzero).symm
  · rintro rfl
    exact Subtype.ext (sub_self _)

variable [AddCommGroup Z] [Module R Z] (D : M →ₗ[R] Z)

/-- Pairs in an affine fiber whose disclosures agree. -/
abbrev DisclosureCollision :=
  {p : AffineFiber Q c × AffineFiber Q c // D p.1.val = D p.2.val}

/-- The difference of the observations is the observation of the direction. -/
theorem collisionEquiv_disclosure (p : AffineFiber Q c × AffineFiber Q c) :
    D (collisionEquiv Q c p).2.val = D p.2.val - D p.1.val :=
  map_sub D _ _

/-- The pullback condition expressed on the homogeneous direction. -/
theorem disclosure_eq_iff_direction_in_ker (p : AffineFiber Q c × AffineFiber Q c) :
    D p.1.val = D p.2.val ↔ (collisionEquiv Q c p).2.val ∈ LinearMap.ker D := by
  rw [LinearMap.mem_ker, collisionEquiv_disclosure, sub_eq_zero, eq_comm]

/-- Comparing equal disclosures restricts the direction to the intersection
of the original kernel and the kernel of the disclosure map. -/
def disclosureCollisionEquiv :
    DisclosureCollision Q c D ≃
      (AffineFiber Q c × (LinearMap.ker Q ⊓ LinearMap.ker D : Submodule R M)) where
  toFun p :=
    let q := collisionEquiv Q c p.val
    (q.1, ⟨q.2.val, q.2.property, (disclosure_eq_iff_direction_in_ker Q c D p.val).mp p.property⟩)
  invFun q :=
    let direction : LinearMap.ker Q := ⟨q.2.val, q.2.property.1⟩
    let pair := (collisionEquiv Q c).symm (q.1, direction)
    ⟨pair, (disclosure_eq_iff_direction_in_ker Q c D pair).mpr (by
      dsimp [pair]
      rw [(collisionEquiv Q c).apply_symm_apply]
      exact q.2.property.2)⟩
  left_inv p := by
    apply Subtype.ext
    exact (collisionEquiv Q c).left_inv p.val
  right_inv q := by
    refine Prod.ext ?_ ?_
    · rfl
    · apply Subtype.ext
      change q.1.val + q.2.val - q.1.val = q.2.val
      abel

/-- The horizontal equivalences commute with forgetting the disclosure
constraint and including its kernel in the original direction space. -/
theorem disclosureCollision_square (p : DisclosureCollision Q c D) :
    collisionEquiv Q c p.val =
      ((disclosureCollisionEquiv Q c D p).1,
        ⟨(disclosureCollisionEquiv Q c D p).2.val,
          (disclosureCollisionEquiv Q c D p).2.property.1⟩) :=
  rfl

/-- The square preserves the diagonal and therefore also its complement. -/
theorem disclosureCollisionEquiv_diagonal (p : DisclosureCollision Q c D) :
    (disclosureCollisionEquiv Q c D p).2 = 0 ↔ p.val.1 = p.val.2 := by
  change (⟨p.val.2.val - p.val.1.val, _⟩ : (LinearMap.ker Q ⊓ LinearMap.ker D : Submodule R M)) = 0 ↔ _
  constructor
  · intro h
    exact Subtype.ext (sub_eq_zero.mp
      (congrArg (fun v : (LinearMap.ker Q ⊓ LinearMap.ker D : Submodule R M) => v.val) h)).symm
  · intro h
    exact Subtype.ext (sub_eq_zero.mpr (congrArg Subtype.val h.symm))

end PvsNP
