module

public import PvsNP.TransversePairLevel
public import Mathlib.Algebra.Polynomial.Eval.Defs
public import Mathlib.LinearAlgebra.Matrix.Permanent

@[expose] public section

namespace PvsNP.TransversePair

open Polynomial Lean.Grind.CommRing

noncomputable section

private theorem prodExpr_denote {R : Type*} [CommRing R] (ctx : Context R) (es : List Expr) :
    (prodExpr es).denote ctx = (es.map (Expr.denote ctx)).prod := by
  induction es with
  | nil => rfl
  | cons e es ih =>
    simp only [List.map_cons, List.prod_cons]
    exact congrArg (e.denote ctx * ·) ih

/-- The matrix J₄+sB+tC, with s and t the two independent polynomial variables. -/
def pairMatrix {K : Type*} [CommRing K] (x : Fin 6 → K) : Matrix (Fin 4) (Fin 4) K[X][X] :=
  fun i j => (pairEntry i j).denote (pencilCtx x)

/-- The certificate's reflected permanent agrees with the matrix permanent. -/
theorem pairMatrix_permanent {K : Type*} [CommRing K] (x : Fin 6 → K) :
    (pairMatrix x).permanent = transversePermanent.denote (pencilCtx x) := by
  classical
  let rows : List (Fin 4) := [0, 1, 2, 3]
  have complete : (permsOfList rows).toFinset = Finset.univ := by
    apply Finset.eq_univ_of_forall
    intro σ
    apply List.mem_toFinset.mpr
    apply mem_permsOfList_of_mem
    intro i _
    fin_cases i <;> decide
  have unique : (permsOfList rows).Nodup := nodup_permsOfList (by decide : rows.Nodup)
  rw [Matrix.permanent, ← complete, List.sum_toFinset _ unique, transversePermanent,
    sumExpr_denote, List.map_map]
  apply congrArg List.sum
  apply List.map_congr_left
  intro σ _
  simp [pairMatrix, prodExpr_denote, Fin.prod_univ_succ]

/-- Adjoin a third parameter for an arbitrary first direction of the four-by-four pencil. -/
def fullPencil {K : Type*} [CommRing K] (first : Matrix (Fin 4) (Fin 4) K)
    (x : Fin 6 → K) : K[X][X][X] :=
  Matrix.permanent fun i j => C (pairMatrix x i j) + X * C (C (C (first i j)))

/-- Restriction to the plane where the first parameter vanishes commutes with the permanent. -/
theorem fullPencil_restrict {K : Type*} [CommRing K] (first : Matrix (Fin 4) (Fin 4) K)
    (x : Fin 6 → K) :
    (evalRingHom 0) (fullPencil first x) = transversePermanent.denote (pencilCtx x) := by
  rw [← pairMatrix_permanent]
  simp [fullPencil, Matrix.permanent, map_sum, map_prod]

/-- Every third direction restricts to the excluded transverse pair in characteristic five. -/
theorem fullPencil_ne_level {K : Type*} [Field K] [CharP K 5]
    (first : Matrix (Fin 4) (Fin 4) K) (x : Fin 6 → K) : fullPencil first x ≠ 24 := by
  intro h
  apply transversePermanent_ne_level x
  rw [← fullPencil_restrict first x, h, map_ofNat]

end

end PvsNP.TransversePair
