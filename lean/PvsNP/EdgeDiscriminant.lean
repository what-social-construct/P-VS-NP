module

public import Mathlib.Data.Matrix.ColumnRowPartitioned
public import Mathlib.LinearAlgebra.Matrix.Determinant.Basic
public import Mathlib.Algebra.CharP.Defs
public import PvsNP.ScalarOrientation
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.LinearCombination
import Mathlib.Tactic.ReduceModChar
import Mathlib.Tactic.Ring

@[expose] public section

namespace PvsNP.EdgeDiscriminant

open Matrix

variable {R : Type*} [CommRing R]

/-- The six edges are ordered as 01,02,03 followed by their opposites 23,13,12.
Within either triple, the quadratic edge metric has diagonal five and off-diagonal one. -/
def withinEdges (R : Type*) [CommRing R] : Matrix (Fin 3) (Fin 3) R :=
  !![5, 1, 1; 1, 5, 1; 1, 1, 5]

/-- From a star edge to its opposite the pairing is −1, and to another edge it is 1. -/
def acrossEdges (R : Type*) [CommRing R] : Matrix (Fin 3) (Fin 3) R :=
  !![-1, 1, 1; 1, -1, 1; 1, 1, -1]

/-- Pull back the actual six-edge pairing by the star frame with blocks I and C. -/
def graphGram (C : Matrix (Fin 3) (Fin 3) R) : Matrix (Fin 3) (Fin 3) R :=
  let X := fromRows 1 C
  X.transpose * fromBlocks (withinEdges R) (acrossEdges R) (acrossEdges R) (withinEdges R) * X

private theorem graphGram_blocks (C : Matrix (Fin 3) (Fin 3) R) :
    graphGram C = (withinEdges R + C.transpose * acrossEdges R) +
      (acrossEdges R + C.transpose * withinEdges R) * C := by
  simp [graphGram, transpose_fromRows, fromCols_mul_fromBlocks, fromCols_mul_fromRows]

def scalarGraph (c : R) : Matrix (Fin 3) (Fin 3) R :=
  !![c, 0, 0; 0, c, 0; 0, 0, c]

def transverseGraph (v : R) : Matrix (Fin 3) (Fin 3) R :=
  !![1+v, 2, 3; 3, 2, 1; 3, 4, 3]

private theorem scalar_gram (c : R) :
    graphGram (scalarGraph c) =
      let a := 5*c^2 - 2*c + 5
      let b := (1+c)^2
      !![a, b, b; b, a, b; b, b, a] := by
  rw [graphGram_blocks]
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [scalarGraph, acrossEdges, withinEdges, Matrix.add_apply, Matrix.mul_apply, Fin.sum_univ_three] <;> ring

private theorem transverse_gram (v : R) :
    graphGram (transverseGraph v) =
      !![5*v^2+20*v+140, 17*v+142, 20*v+112;
         17*v+142, 173, 142; 20*v+112, 142, 132] := by
  rw [graphGram_blocks]
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [transverseGraph, acrossEdges, withinEdges, Matrix.add_apply, Matrix.mul_apply, Fin.sum_univ_three] <;> ring

/-- Four times the square-root radicand on the scalar edge line. -/
theorem scalar_gram_det [CharP R 5] (c : R) :
    (graphGram (scalarGraph c)).det = 4 * (3 * (c^2-c+1)^2 * (c^2+c+1)) := by
  rw [scalar_gram, det_fin_three]
  simp only [cons_val, of_apply]
  ring_nf
  reduce_mod_char!

/-- Odd order of the normalized radicand rules out an orientation of the actual
scalar edge Gram matrix in the fraction field. -/
theorem scalar_gram_no_orientation_of_odd_order
    {V K : Type*} [CommRing V] [IsDomain V] [IsDiscreteValuationRing V]
    [Field K] [CharP K 5] [Algebra V K] [IsFractionRing V K]
    (π : V) (hπ : Irreducible π) (u : Vˣ) (m : ℕ)
    (c : K) (hh : c^2-c+1 ≠ 0)
    (hodd : 3*(c^2+c+1) = algebraMap V K (π^(2*m+1) * (u : V))) :
    ¬∃ D : K, (graphGram (scalarGraph c)).det = 4 * D^2 := by
  rintro ⟨D, hD⟩
  rw [scalar_gram_det] at hD
  have h₄ : (4 : K) ≠ 0 := by
    intro h
    have h₅ : (5 : K) = 0 := CharP.cast_eq_zero K 5
    exact one_ne_zero (show (1 : K) = 0 by linear_combination h₅ - h)
  exact ScalarOrientation.no_orientation_of_odd_order π hπ u m c hh hodd
    ⟨D, mul_left_cancel₀ h₄ hD.symm⟩

/-- The transverse orientation radicand in integer coefficients. -/
def transverseRadicand (v : R) : R := 643*v^2 - 2900*v + 14764

/-- The determinant identity before reduction modulo five. -/
theorem transverse_gram_det_integral (v : R) :
    (graphGram (transverseGraph v)).det = 4 * transverseRadicand v := by
  rw [transverse_gram, det_fin_three]
  simp only [cons_val, of_apply, transverseRadicand]
  ring

/-- Two conjugate roots of v²=2 are zeros of the transverse discriminant. -/
theorem transverse_gram_det [CharP R 5] (v : R) :
    (graphGram (transverseGraph v)).det = 4 * (3 * (v^2-2)) := by
  rw [transverse_gram_det_integral, transverseRadicand]
  ring_nf
  reduce_mod_char!

/-- The fixed two-column Gram minor is a unit at five, including at v²=2. -/
theorem transverse_gram_minor [CharP R 5] (v : R) :
    let G := graphGram (transverseGraph v)
    G 1 1 * G 2 2 - G 1 2 * G 2 1 = 2 := by
  simp only [transverse_gram, cons_val, of_apply]
  reduce_mod_char!

end PvsNP.EdgeDiscriminant
