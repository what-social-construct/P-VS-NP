module

public import Mathlib.Logic.Equiv.Defs

/-! # Witness selection from a representative of each model fiber -/

@[expose] public section

namespace PvsNP.StratumSelector

/-- Data for one selector. The representative depends only on the stratum.
Transport takes that model point back to a witness over the given instance. -/
structure Charts (X C W : Type*) (S : C → Type*) where
  locate : X → C
  seed : (c : C) → Option (S c)
  transport : (x : X) → S (locate x) → W

variable {X C W : Type*} {S : C → Type*}

def select (a : Charts X C W S) (x : X) : Option W :=
  (a.seed (a.locate x)).map (a.transport x)

variable (a : Charts X C W S) (V : X → W → Prop) (M : (c : C) → S c → Prop)

/-- The seed is checked in its model fiber, and transport preserves validity.
Together these give soundness in the original witness relation. -/
theorem select_sound
    (seed_valid : ∀ c s, a.seed c = some s → M c s)
    (transport_valid : ∀ x s, M (a.locate x) s → V x (a.transport x s))
    {x : X} {w : W} (h : select a x = some w) : V x w := by
  unfold select at h
  cases hs : a.seed (a.locate x) with
  | none => simp [hs] at h
  | some s =>
    have hw : a.transport x s = w := by simpa [hs] using h
    exact hw ▸ transport_valid x s (seed_valid _ _ hs)

/-- A representative for each nonempty model fiber suffices if an original
witness implies that the model fiber is inhabited. The latter implication
is purely a proof obligation and is not evaluated by the selector. -/
theorem select_some_iff
    (seed_valid : ∀ c s, a.seed c = some s → M c s)
    (transport_valid : ∀ x s, M (a.locate x) s → V x (a.transport x s))
    (seed_complete : ∀ c, (∃ s, M c s) → ∃ s, a.seed c = some s)
    (covers : ∀ x, (∃ w, V x w) → ∃ s, M (a.locate x) s)
    (x : X) : (∃ w, select a x = some w) ↔ ∃ w, V x w := by
  constructor
  · rintro ⟨w, hw⟩
    exact ⟨w, select_sound a V M seed_valid transport_valid hw⟩
  · intro hx
    obtain ⟨s, hs⟩ := seed_complete (a.locate x) (covers x hx)
    exact ⟨a.transport x s, by simp [select, hs]⟩

/-- A trivialization on each stratum supplies the coverage implication of
`select_some_iff` by mapping a witness to its model point. -/
theorem covers_of_fiberEquiv
    (chart : ∀ x, {w // V x w} ≃ {s // M (a.locate x) s}) (x : X) :
    (∃ w, V x w) → ∃ s, M (a.locate x) s := by
  rintro ⟨w, hw⟩
  exact ⟨(chart x ⟨w, hw⟩).val, (chart x ⟨w, hw⟩).property⟩

end PvsNP.StratumSelector
