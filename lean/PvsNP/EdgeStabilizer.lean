module

public import Mathlib.GroupTheory.GroupAction.Quotient
public import Mathlib.GroupTheory.Perm.Cycle.Type
public import Mathlib.Data.Matrix.Mul
public import Mathlib.Data.Finite.Perm
import Mathlib.Tactic.FinCases

@[expose] public section

namespace PvsNP.EdgeStabilizer

open Equiv MulAction

/-- In the normalized star frame a relabeling preserves the edge graph exactly
when it preserves the entries under simultaneous row and column relabeling. -/
theorem graph_stability_iff {K I : Type*} [CommSemiring K] [Fintype I]
    (C : Matrix I I K) (g : Perm I) :
    (∀ x : I → K, (C.mulVec x) ∘ g = C.mulVec (x ∘ g)) ↔
      ∀ i j, C (g i) (g j) = C i j := by
  classical
  constructor
  · intro h i j
    have he : Pi.single (g j) (1 : K) ∘ g = Pi.single j 1 := by
      funext k
      by_cases hj : j = k
      · subst k
        simp
      · simp [Function.comp_apply, hj]
    have hv := congrFun (h (Pi.single (g j) 1)) i
    simpa only [he, Matrix.mulVec_single_one, Matrix.col, Matrix.transpose_apply, Function.comp_apply] using hv
  · intro h x
    funext i
    change (∑ k, C (g i) k * x k) = ∑ k, C i k * x (g k)
    rw [← Equiv.sum_comp g (fun k => C (g i) k * x k)]
    simp only [h]

/-- Simultaneous cyclic shifts give the three-parameter circulant chart. -/
theorem cyclic_entries_iff {K : Type*} (C : Matrix (Fin 3) (Fin 3) K) :
    (∀ i j, C (i + 1) (j + 1) = C i j) ↔ ∀ i j, C i j = C 0 (j - i) := by
  constructor
  · intro h i j
    have shifts (a b k : Fin 3) : C (a + k) (b + k) = C a b := by
      fin_cases k
      · simp
      · exact h a b
      · change C (a + 2) (b + 2) = _
        simpa only [add_assoc, show (1 : Fin 3) + 1 = 2 by decide] using
          (h (a + 1) (b + 1)).trans (h a b)
    simpa only [add_neg_cancel, sub_eq_add_neg] using (shifts i j (-i)).symm
  · intro h i j
    rw [h (i + 1) (j + 1), h i j, add_sub_add_right_eq_sub]

/-- A transposition determines the second edge column from the first. -/
theorem swapped_column_entries {K : Type*} (C : Matrix (Fin 3) (Fin 3) K)
    (h : ∀ i j, C (swap 0 1 i) (swap 0 1 j) = C i j) :
    C 0 1 = C 1 0 ∧ C 1 1 = C 0 0 ∧ C 2 1 = C 2 0 := by
  have h2 : swap 0 1 (2 : Fin 3) = 2 := by decide
  exact ⟨by simpa using h 1 0, by simpa using h 0 0, by simpa [h2] using h 2 0⟩

/-- The two geometric exclusions imply that the edge stabilizer acts freely
on the four vertices. The geometric hypotheses are supplied separately. -/
theorem eq_one_of_fixed_vertex {X : Type*} [MulAction (Perm (Fin 4)) X] (U : X)
    (noSwap : ∀ g : Perm (Fin 4), g.IsSwap → g • U ≠ U)
    (noThreeCycle : ∀ g : Perm (Fin 4), g.IsThreeCycle → g • U ≠ U)
    {g : Perm (Fin 4)} (hU : g • U = U) {i : Fin 4} (hi : g i = i) : g = 1 := by
  by_contra hne
  have h2 := Perm.two_le_card_support_of_ne_one hne
  have h4 : g.support.card < 4 := by
    simpa using Finset.card_lt_univ_of_notMem (g.notMem_support.mpr hi)
  rcases (show g.support.card = 2 ∨ g.support.card = 3 by omega) with h | h
  · exact noSwap g (Perm.card_support_eq_two.mp h) hU
  · exact noThreeCycle g (card_support_eq_three_iff.mp h) hU

/-- An edge image satisfying the two symmetry exclusions has an S4 orbit of
size 6, 12, or 24, even when the ambient space of edge images is infinite. -/
theorem orbit_card_of_edge_exclusions {X : Type*} [MulAction (Perm (Fin 4)) X] (U : X)
    (noSwap : ∀ g : Perm (Fin 4), g.IsSwap → g • U ≠ U)
    (noThreeCycle : ∀ g : Perm (Fin 4), g.IsThreeCycle → g • U ≠ U) :
    Nat.card (orbit (Perm (Fin 4)) U) = 6 ∨
      Nat.card (orbit (Perm (Fin 4)) U) = 12 ∨
      Nat.card (orbit (Perm (Fin 4)) U) = 24 := by
  classical
  let H := stabilizer (Perm (Fin 4)) U
  have hv (i : Fin 4) : stabilizer H i = ⊥ := by
    apply le_antisymm _ bot_le
    intro g hg
    apply Subgroup.mem_bot.mpr
    exact Subtype.ext (eq_one_of_fixed_vertex U noSwap noThreeCycle g.property hg)
  have h4 := Nat.card_congr (selfEquivOrbitsQuotientProd hv)
  rw [Nat.card_fin, Nat.card_prod] at h4
  have hd : Nat.card H ∣ 4 :=
    ⟨_, h4.trans (Nat.mul_comm _ _)⟩
  have h24 := Nat.card_congr (orbitProdStabilizerEquivGroup (Perm (Fin 4)) U)
  rw [Nat.card_prod, Nat.card_perm, Nat.card_fin] at h24
  change Nat.card (orbit (Perm (Fin 4)) U) * Nat.card H = 24 at h24
  have hle := Nat.le_of_dvd (by decide : 0 < 4) hd
  have h0 : Nat.card H ≠ 0 := fun h => (by decide : ¬ 0 ∣ 4) (h ▸ hd)
  have h3 : Nat.card H ≠ 3 := fun h => (by decide : ¬ 3 ∣ 4) (h ▸ hd)
  rcases (show Nat.card H = 1 ∨ Nat.card H = 2 ∨ Nat.card H = 4 by omega) with h | h | h <;>
    rw [h] at h24 <;> omega

end PvsNP.EdgeStabilizer
