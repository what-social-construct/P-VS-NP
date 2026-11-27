module

public import Init.Grind.Ring.CommSolver
public import Mathlib.Algebra.Ring.GrindInstances
public import Mathlib.Algebra.BigOperators.Fin
public import Mathlib.Data.Fintype.Perm
public import PvsNP.TransversePairData

@[expose] public section

namespace PvsNP.TransversePair

open Lean.Grind.CommRing

def sumExpr (xs : List Expr) := xs.foldr Expr.add (.num 0)
def prodExpr (xs : List Expr) := xs.foldr Expr.mul (.num 1)

/-- The last two columns of the transverse edge frame, in the order
01,02,03,23,13,12. The three free diagonals in each column are variables. -/
def direction (second : Bool) (i j : Nat) : Expr := Id.run do
  let start := if second then 3 else 0
  let v := fun k => Expr.var (start + k)
  if i == j then
    if i == 0 then
      -- Each off-diagonal occurs twice in the zero entry-sum constraint.
      return .sub (.num (if second then -16 else -18)) (sumExpr [v 0, v 1, v 2])
    return v (i - 1)
  let entry := match min i j, max i j with
    | 0, 2 => if second then 0 else 1
    | 0, 3 => if second then 1 else 0
    | 2, 3 => if second then 3 else 2
    | 1, 3 => if second then 1 else 2
    | 1, 2 => if second then 3 else 4
    | _, _ => 0
  return .num entry

/-- One entry of the pencil J₄+sB+tC in the six free diagonal coordinates. -/
def pairEntry (i j : Fin 4) : Expr :=
  .add (.num 1) (.add (.mul (.var 6) (direction false i j))
                     (.mul (.var 7) (direction true i j)))

/-- Permanent of J₄+sB+tC as a ring expression. The first six variables
are the free diagonal entries, and variables 6 and 7 are s and t. -/
def transversePermanent : Expr :=
  sumExpr ((permsOfList ([0, 1, 2, 3] : List (Fin 4))).map fun σ =>
    prodExpr (List.ofFn fun j => pairEntry (σ j) j))

def sparseExpr (p : List (Nat × Nat)) : Expr :=
  sumExpr (p.map fun (a,k) =>
    .mul (.natCast a) (prodExpr ((List.range 6).map fun i =>
      .pow (.var i) (k / 10^i % 10))))

/-- The bidegrees of the nonconstant coefficients, ordered first by the power of s. -/
def transversePowers : List (Nat × Nat) :=
  (List.range 5).flatMap fun i =>
    ((List.range (5-i)).filter fun j => 2 ≤ i+j).map fun j => (i,j)

/-- The twelve nonconstant coefficients and the permanent of the all-ones matrix. -/
def transverseExpansion : Expr :=
  .add (.num 24) (sumExpr ((transversePowers.zip generatorTerms).map fun ((i,j),p) =>
    .mul (.mul (.pow (.var 6) i) (.pow (.var 7) j)) (sparseExpr p)))

set_option maxRecDepth 16000 in
set_option maxHeartbeats 4000000 in
/-- Kernel replay of the entire symbolic permanent expansion modulo five.
No finite sampling or assumption on the diagonal entries is involved. -/
theorem transverse_expansion_checked :
    (transversePermanent.toPolyC 5).beq' (transverseExpansion.toPolyC 5) = true := by
  decide +kernel

theorem transverse_expansion {K : Type*} [Lean.Grind.CommRing K] [Lean.Grind.IsCharP K 5]
    (coordinates : Context K) :
    transversePermanent.denote coordinates = transverseExpansion.denote coordinates :=
  Expr.eq_of_toPolyC_eq (c := 5) coordinates _ _ (by
    apply beq_iff_eq.mpr
    simpa only [Poly.beq'_eq] using transverse_expansion_checked)

theorem sumExpr_denote {K : Type*} [CommRing K] (ctx : Context K) (es : List Expr) :
    (sumExpr es).denote ctx = (es.map (Expr.denote ctx)).sum := by
  induction es with
  | nil => rfl
  | cons e es ih =>
    simp only [List.map_cons, List.sum_cons]
    exact congrArg (e.denote ctx + ·) ih

/-- Evaluation of the reflected coefficient is ordinary evaluation of its six decimal exponents. -/
theorem sparseExpr_eval {K : Type*} [CommRing K] (ctx : Context K) (p : List (Nat × Nat)) :
    (sparseExpr p).denote ctx = (p.map fun t => (t.1 : K) * ∏ i : Fin 6, ctx.get i.val ^ (t.2 / 10^i.val % 10)).sum := by
  rw [sparseExpr, sumExpr_denote, List.map_map]
  congr 1

end PvsNP.TransversePair
