module

public import PvsNP.TransversePair
public import PvsNP.TransversePairChart
public import Mathlib.Algebra.Polynomial.Coeff
import Mathlib.RingTheory.Polynomial.Basic
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Ring

/-! # The formal permanent level on the transverse pair chart -/

@[expose] public section

namespace PvsNP.TransversePair
open Polynomial Lean.Grind.CommRing

noncomputable section

private def atTerm {K : Type*} [CommRing K] (q : Nat × Nat) (a : K) : K[X][X] :=
  Polynomial.monomial q.1 (Polynomial.monomial q.2 a)

private theorem extract_atTerm {K : Type*} [CommRing K] (r q : Nat × Nat) (a : K) :
    ((atTerm q a).coeff r.1).coeff r.2 = if q = r then a else 0 := by
  rcases q with ⟨i,j⟩
  rcases r with ⟨k,l⟩
  by_cases hi : i = k <;> by_cases hj : j = l <;> simp [atTerm, coeff_monomial, *, Prod.ext_iff]

private theorem ifSum_absent {K α : Type*} [CommRing K] (q : Nat × Nat)
    (idx : α → Nat × Nat) (v : α → K) (xs : List α) (h : q ∉ xs.map idx) :
    (xs.map (fun z => if idx z = q then v z else 0)).sum = 0 := by
  induction xs with
  | nil => rfl
  | cons x xs ih =>
    have hp : idx x ≠ q := fun e => h (by simp [e])
    have ht : q ∉ xs.map idx := fun hh => h (by simp [hh])
    simp [hp, ih ht]

private theorem all_zero_of_poly_sum {K α : Type*} [CommRing K] (idx : α → Nat × Nat)
    (v : α → K) (xs : List α) (hd : (xs.map idx).Nodup)
    (he : (xs.map (fun z => atTerm (idx z) (v z))).sum = 0) :
    ∀ z ∈ xs, v z = 0 := by
  induction xs with
  | nil => simp
  | cons x xs ih =>
    simp only [List.map_cons, List.nodup_cons] at hd
    have h := congrArg (fun p : K[X][X] => (p.coeff (idx x).1).coeff (idx x).2) he
    simp only [List.map_cons, List.sum_cons, coeff_add, coeff_zero, coeff_list_sum_map,
      extract_atTerm, ifSum_absent (idx x) idx v xs hd.1, add_zero] at h
    have hx : v x = 0 := by simpa using h
    have ht : (xs.map (fun z => atTerm (idx z) (v z))).sum = 0 := by
      simp only [List.map_cons, List.sum_cons] at he
      rw [hx] at he
      simpa [atTerm] using he
    intro z hz
    rcases List.mem_cons.mp hz with rfl | hm
    · exact hx
    · exact ih hd.2 ht z hm

/-- Equality with the prescribed level would force every coefficient to vanish. -/
private theorem expansion_ne_level_of_no_common_zero {K : Type*} [CommRing K] (x : Fin 6 → K)
    (h : ¬ ∀ p ∈ generatorTerms, evalTerms x p = 0) :
    (24 : K[X][X]) + ((transversePowers.zip generatorTerms).map (fun z => atTerm z.1 (evalTerms x z.2))).sum ≠ 24 := by
  intro he
  have hz : ((transversePowers.zip generatorTerms).map (fun z => atTerm z.1 (evalTerms x z.2))).sum = 0 :=
    add_left_cancel (he.trans (add_zero _).symm)
  have hd : ((transversePowers.zip generatorTerms).map Prod.fst).Nodup := by decide +kernel
  have hzero := all_zero_of_poly_sum Prod.fst (fun z => evalTerms x z.2) _ hd hz
  apply h
  intro p hp
  have hm : p ∈ (transversePowers.zip generatorTerms).map Prod.snd := by
    rw [List.map_snd_zip (by decide : generatorTerms.length ≤ transversePowers.length)]
    exact hp
  obtain ⟨z,hz,hp'⟩ := List.mem_map.mp hm
  exact hp' ▸ hzero z hz

/-- Set the first six inputs to the diagonal parameters and the last two inputs to
the independent outer and inner polynomial variables. -/
def pencilCtx {K : Type*} [CommRing K] (x : Fin 6 → K) : Context K[X][X] :=
  let c := fun i => C (C (x i))
  .branch 4
    (.branch 2 (.branch 1 (.leaf (c 0)) (.leaf (c 1))) (.branch 3 (.leaf (c 2)) (.leaf (c 3))))
    (.branch 6 (.branch 5 (.leaf (c 4)) (.leaf (c 5))) (.branch 7 (.leaf X) (.leaf (C X))))

private theorem pencil_get {K : Type*} [CommRing K] (x : Fin 6 → K) (i : Fin 6) :
    (pencilCtx x).get i.val = C (C (x i)) := by fin_cases i <;> rfl

private theorem eval_sparse_in_pencil {K : Type*} [CommRing K] (x : Fin 6 → K)
    (p : List (Nat × Nat)) : (sparseExpr p).denote (pencilCtx x) = C (C (evalTerms x p)) := by
  let B : K →+* K[X][X] := C.comp C
  change _ = B _
  simp only [sparseExpr_eval, evalTerms, map_list_sum, List.map_map, Function.comp_def,
    map_mul, map_natCast, map_prod, map_pow, pencil_get, B, RingHom.comp_apply]

private def expansionExpr (xs : List ((Nat × Nat) × List (Nat × Nat))) : Expr :=
  .add (.num 24) (sumExpr (xs.map fun ((i,j),p) =>
    .mul (.mul (.pow (.var 6) i) (.pow (.var 7) j)) (sparseExpr p)))

private theorem expansionExpr_in_pencil {K : Type*} [CommRing K] (x : Fin 6 → K)
    (xs : List ((Nat × Nat) × List (Nat × Nat))) :
    (expansionExpr xs).denote (pencilCtx x) =
    (24 : K[X][X]) + (xs.map (fun z => atTerm z.1 (evalTerms x z.2))).sum := by
  change (24 : K[X][X]) + (sumExpr _).denote (pencilCtx x) = _
  apply congrArg ((24 : K[X][X]) + ·)
  rw [sumExpr_denote, List.map_map]
  apply congrArg List.sum
  apply List.map_congr_left
  rintro ⟨⟨i,j⟩,p⟩ _
  change ((X:K[X][X])^i * (C X)^j) * (sparseExpr p).denote (pencilCtx x) =
    Polynomial.monomial i (Polynomial.monomial j (evalTerms x p))
  rw [eval_sparse_in_pencil, ← C_mul_X_pow_eq_monomial, ← C_mul_X_pow_eq_monomial]
  simp only [map_mul, map_pow]
  ring

private theorem expansion_in_pencil {K : Type*} [CommRing K] (x : Fin 6 → K) :
    transverseExpansion.denote (pencilCtx x) =
    (24 : K[X][X]) + ((transversePowers.zip generatorTerms).map (fun z => atTerm z.1 (evalTerms x z.2))).sum :=
  expansionExpr_in_pencil x (transversePowers.zip generatorTerms)

private theorem pencil_ne_level_of_no_common_zero {K : Type*} [Field K] [CharP K 5] (x : Fin 6 → K)
    (h : ¬ ∀ p ∈ generatorTerms, evalTerms x p = 0) :
    transversePermanent.denote (pencilCtx x) ≠ (24 : K[X][X]) := by
  rw [transverse_expansion, expansion_in_pencil]
  exact expansion_ne_level_of_no_common_zero x h

/-- On the fixed transverse pair chart the formal permanent pencil differs from its
constant value at the origin over every field of characteristic five. -/
theorem transversePermanent_ne_level {K : Type*} [Field K] [CharP K 5] (x : Fin 6 → K) :
    transversePermanent.denote (pencilCtx x) ≠ (24 : K[X][X]) :=
  pencil_ne_level_of_no_common_zero x (no_common_zero x)

end

end PvsNP.TransversePair
