module

public import PvsNP.AffineDisclosure
public import Mathlib.Algebra.BigOperators.Ring.Finset
public import Mathlib.Data.ZMod.Basic
public import Mathlib.LinearAlgebra.Prod

/-! # Prefix extension as an off-diagonal collision of two tagged graphs -/

@[expose] public section

namespace PvsNP.PrefixCollision

variable {W Y : Type*}

/-- The first coordinate retains the candidate on both tagged graphs. -/
def readout (f : W → Y) (target : Y) (p : Bool × W) : W × Y :=
  (p.2, if p.1 then f p.2 else target)

/-- Ordered off-diagonal pairs in the self-pullback of the tagged readout. -/
abbrev OffDiagonal (f : W → Y) (target : Y) :=
  {p : (Bool × W) × (Bool × W) //
    p.1 ≠ p.2 ∧ readout f target p.1 = readout f target p.2}

theorem offDiagonal_iff (f : W → Y) (target : Y) (b c : Bool) (w v : W) :
    ((b, w) ≠ (c, v) ∧ readout f target (b, w) = readout f target (c, v)) ↔
      c = !b ∧ v = w ∧ f w = target := by
  cases b <;> cases c <;> simp [readout] <;> grind

/-- A solution contributes both ordered cross-tag pairs, even if it is unique. -/
def collisionEquiv (f : W → Y) (target : Y) :
    OffDiagonal f target ≃ Bool × {w : W // f w = target} where
  toFun p := (p.val.1.1, ⟨p.val.1.2, ((offDiagonal_iff f target _ _ _ _).mp p.property).2.2⟩)
  invFun p := ⟨((p.1, p.2.val), (!p.1, p.2.val)),
    (offDiagonal_iff f target _ _ _ _).mpr ⟨rfl, rfl, p.2.property⟩⟩
  left_inv p := by
    rcases p with ⟨⟨⟨b, w⟩, ⟨c, v⟩⟩, h⟩
    obtain ⟨rfl, rfl, _⟩ := (offDiagonal_iff f target b c w v).mp h
    rfl
  right_inv _ := rfl

theorem nonempty_offDiagonal_iff (f : W → Y) (target : Y) :
    Nonempty (OffDiagonal f target) ↔ ∃ w : W, f w = target := by
  constructor
  · rintro ⟨p⟩
    exact ⟨_, ((collisionEquiv f target p).2).property⟩
  · rintro ⟨w, hw⟩
    exact ⟨(collisionEquiv f target).symm (false, ⟨w, hw⟩)⟩

variable {n k : ℕ}

/-- With any Boolean verifier, the tagged collision exactly detects extending
the prefix. The acceptance function here can be nonlinear. -/
theorem verifier_prefix_iff_collision (accept : (Fin n → Bool) → Bool)
    (hk : k ≤ n) (u : Fin k → Bool) :
    (∃ w, accept w = true ∧ w ∘ Fin.castLE hk = u) ↔
      Nonempty (OffDiagonal (fun w => (accept w, w ∘ Fin.castLE hk)) (true, u)) := by
  rw [nonempty_offDiagonal_iff]
  simp only [Prod.mk.injEq]

/-- A feasibility-preserving compiler can use a different space of auxiliary
variables. Its output preserves existence of collisions. -/
theorem verifier_collision_iff_compiled_collision
    (accept : (Fin n → Bool) → Bool) (hk : k ≤ n) (u : Fin k → Bool)
    (f : W → Y) (target : Y)
    (correct : (∃ w, accept w = true ∧ w ∘ Fin.castLE hk = u) ↔ ∃ v, f v = target) :
    Nonempty (OffDiagonal (fun w => (accept w, w ∘ Fin.castLE hk)) (true, u)) ↔
      Nonempty (OffDiagonal f target) :=
  (verifier_prefix_iff_collision accept hk u).symm.trans
    (correct.trans (nonempty_offDiagonal_iff f target).symm)

section FiniteCandidates

variable [Fintype W]

/-- One parity row and a zero-coordinate row for each rejected candidate. -/
def candidateSystem (P : W → Prop) :
    (W → ZMod 2) →ₗ[ZMod 2] ZMod 2 × ({w // ¬ P w} → ZMod 2) :=
  let total : (W → ZMod 2) →ₗ[ZMod 2] ZMod 2 :=
    { toFun := fun a => ∑ w, a w
      map_add' := fun _ _ => Finset.sum_add_distrib
      map_smul' := fun r a => (Finset.mul_sum Finset.univ a r).symm }
  total.prod (LinearMap.funLeft (ZMod 2) (ZMod 2) Subtype.val)

theorem candidateSystem_spec (P : W → Prop) (a : W → ZMod 2) :
    candidateSystem P a = (1, 0) ↔ (∑ w, a w) = 1 ∧ ∀ w, ¬ P w → a w = 0 := by
  change (∑ w, a w, fun w : {w // ¬ P w} => a w.val) = (1, 0) ↔ _
  rw [Prod.mk.injEq]
  exact and_congr_right fun _ =>
    ⟨fun h w hw => congrFun h ⟨w, hw⟩, fun h => funext fun w => h w.val w.property⟩

/-- This exact affine fallback has one unknown per candidate. An indicator
gives a solution; an odd sum of accepted weights forces an accepted point. -/
theorem exists_iff_candidate_weights (P : W → Prop) :
    (∃ w, P w) ↔ ∃ a : W → ZMod 2, (∑ w, a w) = 1 ∧ ∀ w, ¬ P w → a w = 0 := by
  classical
  constructor
  · rintro ⟨w, hw⟩
    refine ⟨fun v => if v = w then 1 else 0, by simp, ?_⟩
    intro v hv
    have hne : v ≠ w := by rintro rfl; exact hv hw
    simp [hne]
  · rintro ⟨a, hsum, hreject⟩
    by_contra! h
    have hz : (∑ w, a w) = 0 := Finset.sum_eq_zero fun w _ => hreject w (h w)
    exact zero_ne_one (hz.symm.trans hsum)

theorem exists_iff_candidate_collision (P : W → Prop) :
    (∃ w, P w) ↔ Nonempty (OffDiagonal (candidateSystem P) (1, 0)) := by
  rw [exists_iff_candidate_weights, nonempty_offDiagonal_iff]
  exact exists_congr fun a => (candidateSystem_spec P a).symm

end FiniteCandidates

/-- Every finite Boolean verifier has an exact affine encoding of prefix
extension by allocating one unknown per word. -/
theorem verifier_prefix_iff_candidate_collision (accept : (Fin n → Bool) → Bool)
    (hk : k ≤ n) (u : Fin k → Bool) :
    (∃ w, accept w = true ∧ w ∘ Fin.castLE hk = u) ↔ Nonempty (OffDiagonal
      (candidateSystem (fun w => accept w = true ∧ w ∘ Fin.castLE hk = u)) (1, 0)) :=
  exists_iff_candidate_collision _

variable {R N : Type*} [Ring R] [AddCommGroup N] [Module R N]

/-- Stack a linear verifier's equations and the coordinate rows for the prefix.
Specializing the coefficient ring to the binary field gives the binary system. -/
def prefixSystem (Q : (Fin n → R) →ₗ[R] N) (hk : k ≤ n) :
    (Fin n → R) →ₗ[R] N × (Fin k → R) :=
  Q.prod (LinearMap.funLeft R R (Fin.castLE hk))

theorem prefixSystem_spec (Q : (Fin n → R) →ₗ[R] N) (c : N)
    (hk : k ≤ n) (u : Fin k → R) (w : Fin n → R) :
    prefixSystem Q hk w = (c, u) ↔ Q w = c ∧ w ∘ Fin.castLE hk = u := by
  change (Q w, w ∘ Fin.castLE hk) = (c, u) ↔ _
  simp only [Prod.mk.injEq]

/-- Consistency of the stacked affine equations is equivalent to existence of
a verifier witness extending the prefix. The solution is the original witness. -/
theorem prefix_extends_iff_consistent (Q : (Fin n → R) →ₗ[R] N) (c : N)
    (hk : k ≤ n) (u : Fin k → R) :
    (∃ w, Q w = c ∧ w ∘ Fin.castLE hk = u) ↔
      Nonempty (AffineFiber (prefixSystem Q hk) (c, u)) := by
  constructor
  · rintro ⟨w, hw⟩
    exact ⟨⟨w, (prefixSystem_spec Q c hk u w).mpr hw⟩⟩
  · rintro ⟨w⟩
    exact ⟨w.val, (prefixSystem_spec Q c hk u w.val).mp w.property⟩

/-- The entire ordered off-diagonal is two copies of the stacked affine fiber. -/
def prefixCollisionEquiv (Q : (Fin n → R) →ₗ[R] N) (c : N)
    (hk : k ≤ n) (u : Fin k → R) :
    OffDiagonal (prefixSystem Q hk) (c, u) ≃ Bool × AffineFiber (prefixSystem Q hk) (c, u) :=
  collisionEquiv _ _

end PvsNP.PrefixCollision
