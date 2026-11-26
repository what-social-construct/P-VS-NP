module

public import Mathlib.Logic.Function.Basic

@[expose] public section

namespace PvsNP

set_option autoImplicit false

variable {A Q Y : Type*}

/-- A map on presentations descends uniquely through a surjective comparison
exactly when it is constant on the fibers of that comparison. -/
theorem existsUnique_descend_iff (q : A → Q) (surj : Function.Surjective q) (f : A → Y) :
    (∃! g : Q → Y, ∀ a, g (q a) = f a) ↔
      ∀ a a', q a = q a' → f a = f a' := by
  constructor
  · rintro ⟨g, commutes, _⟩ a a' same
    rw [← commutes a, ← commutes a', same]
  · intro same
    let sectionMap : Q → A := fun x => Classical.choose (surj x)
    have undo (x : Q) : q (sectionMap x) = x := Classical.choose_spec (surj x)
    refine ⟨f ∘ sectionMap, ?_, ?_⟩
    · intro a
      exact same _ _ (undo (q a))
    · intro g commutes
      funext x
      change g x = f (sectionMap x)
      exact (congrArg g (undo x).symm).trans (commutes (sectionMap x))

/-- The endomorphism square for an operation that preserves collisions. -/
theorem endomorphism_descends_iff (q : A → Q) (surj : Function.Surjective q) (D : A → A) :
    (∃! Dbar : Q → Q, ∀ a, Dbar (q a) = q (D a)) ↔
      ∀ a a', q a = q a' → q (D a) = q (D a') :=
  existsUnique_descend_iff q surj (q ∘ D)

/-- Interpreting the realized value back into the original space reflects
equality whenever interpretation is a left inverse. -/
theorem evaluation_eq_iff_of_leftInverse (E : A → Y) (J : Y → A)
    (leftInverse : Function.LeftInverse J E) (a a' : A) :
    E a = E a' ↔ a = a' :=
  ⟨fun h => leftInverse.injective h, congrArg E⟩

/-- Specializing a tracked substitution to the formula's own code gives the
self-substitution square. The code and its tracking law are supplied inputs. -/
theorem selfSubstitution_square {F S : Type*} (g₁ : F → Nat) (g₀ : S → Nat)
    (substitute : F → Nat → S) (subCode : Nat → Nat → Nat)
    (track : ∀ φ n, subCode (g₁ φ) n = g₀ (substitute φ n)) :
    (fun n => subCode n n) ∘ g₁ = g₀ ∘ (fun φ => substitute φ (g₁ φ)) := by
  funext φ
  exact track φ (g₁ φ)

end PvsNP
