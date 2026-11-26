module

public import Mathlib.Data.Finset.Powerset
public import Mathlib.Data.Fintype.Order

@[expose] public section

namespace PvsNP.ProjectivePlaneOrderThree

/-- The cyclic point-line incidence relation used in PEqualNP's order-three rows. -/
abbrev incident (point line : Fin 13) : Prop :=
  (point.val + line.val) % 13 ∈ ([0, 1, 3, 9] : List ℕ)

def hasIncidence (points lines : Finset (Fin 13)) : Prop :=
  ∃ point ∈ points, ∃ line ∈ lines, incident point line

def avoiding (points : Finset (Fin 13)) : Finset (Fin 13) :=
  Finset.univ.filter fun line => ∀ point ∈ points, ¬ incident point line

theorem subset_avoiding {points lines : Finset (Fin 13)}
    (disjoint : ¬ hasIncidence points lines) : lines ⊆ avoiding points := by
  intro line hl
  refine Finset.mem_filter.mpr ⟨Finset.mem_univ _, ?_⟩
  intro point hp edge
  exact disjoint ⟨point, hp, line, hl, edge⟩

set_option maxRecDepth 10000 in
set_option maxHeartbeats 2000000 in
private theorem four_points_check :
    ∀ points ∈ (Finset.univ : Finset (Fin 13)).powersetCard 4,
      (avoiding points).card ≤ 3 := by
  decide

/-- Any four points are met by at least ten lines. -/
theorem card_avoiding_four (points : Finset (Fin 13)) (four : points.card = 4) :
    (avoiding points).card ≤ 3 :=
  four_points_check points (Finset.mem_powersetCard.mpr ⟨Finset.subset_univ _, four⟩)

theorem small_side_of_no_incidence {points lines : Finset (Fin 13)}
    (disjoint : ¬ hasIncidence points lines) : points.card ≤ 3 ∨ lines.card ≤ 3 := by
  by_cases small : points.card ≤ 3
  · exact Or.inl small
  · obtain ⟨fourPoints, sub, four⟩ :=
      Finset.exists_subset_card_eq (show 4 ≤ points.card by omega)
    have disjointFour : ¬ hasIncidence fourPoints lines := by
      rintro ⟨point, hp, line, hl, edge⟩
      exact disjoint ⟨point, sub hp, line, hl, edge⟩
    exact Or.inr ((Finset.card_le_card (subset_avoiding disjointFour)).trans
      (card_avoiding_four fourPoints four))

/-- With a point active, its neighboring line variables contribute singleton
terms. The remaining edges are those outside the point's closed neighborhood. -/
theorem restrict_point_true (point : Fin 13) (points lines : Finset (Fin 13)) :
    hasIncidence (insert point points) lines ↔
      (∃ line ∈ lines, incident point line) ∨
        hasIncidence (points.erase point) (lines ∩ avoiding {point}) := by
  constructor
  · rintro ⟨other, hp, line, hl, edge⟩
    by_cases meets : incident point line
    · exact Or.inl ⟨line, hl, meets⟩
    · have different : other ≠ point := by
        intro same
        exact meets (same ▸ edge)
      have remaining : other ∈ points := (Finset.mem_insert.mp hp).resolve_left different
      have avoids : line ∈ avoiding {point} := by
        exact Finset.mem_filter.mpr ⟨Finset.mem_univ _, by simpa using meets⟩
      exact Or.inr ⟨other, Finset.mem_erase.mpr ⟨different, remaining⟩, line,
        Finset.mem_inter.mpr ⟨hl, avoids⟩, edge⟩
  · rintro (⟨line, hl, edge⟩ | ⟨other, hp, line, hl, edge⟩)
    · exact ⟨point, Finset.mem_insert_self _ _, line, hl, edge⟩
    · exact ⟨other, Finset.mem_insert_of_mem (Finset.mem_of_mem_erase hp), line,
        (Finset.mem_inter.mp hl).1, edge⟩

/-- The posted singleton positives and sparse negatives determine the entire
incidence function for a scan that preserves acceptance under input enlargement. -/
theorem correct_of_sparse_observations
    (scan : Finset (Fin 13) → Finset (Fin 13) → Bool)
    (monotone : ∀ {points largerPoints lines largerLines},
      points ⊆ largerPoints → lines ⊆ largerLines →
      scan points lines = true → scan largerPoints largerLines = true)
    (positive : ∀ point line, incident point line → scan {point} {line} = true)
    (negative : ∀ side : Finset (Fin 13), side.card ≤ 3 →
      scan side (avoiding side) = false ∧ scan (avoiding side) side = false) :
    ∀ points lines, scan points lines = true ↔ hasIncidence points lines := by
  intro points lines
  constructor
  · intro accepts
    by_contra disjoint
    rcases small_side_of_no_incidence disjoint with small | small
    · have h := monotone (Finset.Subset.refl points) (subset_avoiding disjoint) accepts
      rw [(negative points small).1] at h
      exact Bool.false_ne_true h
    · have swapped : ¬ hasIncidence lines points := by
        rintro ⟨line, hl, point, hp, edge⟩
        exact disjoint ⟨point, hp, line, hl, by simpa [incident, Nat.add_comm] using edge⟩
      have h := monotone (subset_avoiding swapped) (Finset.Subset.refl lines) accepts
      rw [(negative lines small).2] at h
      exact Bool.false_ne_true h
  · rintro ⟨point, hp, line, hl, edge⟩
    exact monotone (Finset.singleton_subset_iff.mpr hp) (Finset.singleton_subset_iff.mpr hl)
      (positive point line edge)

end PvsNP.ProjectivePlaneOrderThree
