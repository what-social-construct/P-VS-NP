module

public import PvsNP.EdgeDiscriminant
public import PvsNP.PermanentReadout
public import PvsNP.TransverseRestriction
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.NormNum

/-! # The determinant square on the star edge chart -/

@[expose] public section

namespace PvsNP.OrientationSquare

open Matrix EdgeDiscriminant PermanentReadout

abbrev Frame (R : Type*) := Matrix (Fin 3) (Fin 3) R

/-- A solution of the quadratic equations on the star edge chart. -/
structure GramLift (R : Type*) [CommRing R] where
  frame : Frame R
  readout : Frame R
  gram_eq : graphGram frame = readout.transpose * traceZeroGram R * readout

variable {R : Type*} [CommRing R]

def discriminant (C : Frame R) : R := (graphGram C).det

/-- The pointwise pullback of the Gram discriminant along the scaled square map. -/
abbrev OrientationPoint (R : Type*) [CommRing R] :=
  {p : Frame R × R // discriminant p.1 = 4 * p.2 ^ 2}

/-- The two paths from a quadratic lift to the edge discriminant agree. -/
theorem determinant_square :
    (fun p : GramLift R => discriminant p.frame) =
      fun p => 4 * p.readout.det ^ 2 := by
  funext p
  exact det_edgeGram _ _ p.gram_eq

/-- Factoring the determinant square through its pointwise pullback. -/
noncomputable def orientation (p : GramLift R) : OrientationPoint R :=
  ⟨(p.frame, p.readout.det), congrFun determinant_square p⟩

/-- A compatible pair of arrows into the frame and the square-root line
determines exactly one arrow to the orientation pullback. -/
theorem orientation_pullback {X : Type*} (C : X → Frame R) (d : X → R)
    (h : ∀ x, discriminant (C x) = 4 * (d x)^2) :
    ∃! f : X → OrientationPoint R,
      (∀ x, (f x).val.1 = C x) ∧ (∀ x, (f x).val.2 = d x) := by
  refine ⟨fun x => ⟨(C x, d x), h x⟩, ⟨fun _ => rfl, fun _ => rfl⟩, ?_⟩
  intro f hf
  funext x
  exact Subtype.ext (Prod.ext (hf.1 x) (hf.2 x))

local notation "k₅" => ZMod 5

/-- A corrected readout on the transverse edge frame at parameter zero. -/
def transverseReadout : Frame k₅ := !![1, 0, 0; 2, 0, 4; 3, 3, 0]

theorem transverse_factorization :
    graphGram (transverseGraph (0 : k₅)) =
      transverseReadout.transpose * traceZeroGram k₅ * transverseReadout := by
  simp only [graphGram, transpose_fromRows, fromCols_mul_fromBlocks, fromCols_mul_fromRows,
    transpose_one, one_mul, mul_one]
  ext i j
  fin_cases i <;> fin_cases j <;>
    norm_num [withinEdges, acrossEdges, transverseGraph, traceZeroGram, transverseReadout,
      Matrix.add_apply, Matrix.mul_apply, Fin.sum_univ_three] <;> decide +kernel

def transverseLift : GramLift k₅ :=
  ⟨transverseGraph 0, transverseReadout, transverse_factorization⟩

def oppositeTransverseLift : GramLift k₅ :=
  ⟨transverseGraph 0, -transverseReadout, by
    simpa only [transpose_neg, neg_mul, mul_neg, neg_neg] using transverse_factorization⟩

/-- Both rational roots are realized by actual Gram factorizations at the same
nondegenerate edge frame. -/
theorem transverse_orientations :
    (orientation transverseLift).val = (transverseGraph 0, 3) ∧
    (orientation oppositeTransverseLift).val = (transverseGraph 0, 2) ∧
    discriminant (transverseGraph (0 : k₅)) = 1 := by
  refine ⟨Prod.ext rfl ?_, Prod.ext rfl ?_, ?_⟩
  · change transverseReadout.det = 3
    rw [det_fin_three]
    decide +kernel
  · change (-transverseReadout).det = 2
    rw [det_fin_three]
    decide +kernel
  · rw [discriminant, transverse_gram_det]
    decide +kernel

/-- Cyclic row permutation of the corrected readout. -/
def cyclicReadout : Frame k₅ := !![2, 0, 4; 3, 3, 0; 1, 0, 0]

theorem cyclic_factorization :
    graphGram (transverseGraph (0 : k₅)) =
      cyclicReadout.transpose * traceZeroGram k₅ * cyclicReadout := by
  refine transverse_factorization.trans ?_
  ext i j
  fin_cases i <;> fin_cases j <;>
    norm_num [cyclicReadout, transverseReadout, traceZeroGram, Matrix.mul_apply,
      Fin.sum_univ_three]

def cyclicLift : GramLift k₅ :=
  ⟨transverseGraph 0, cyclicReadout, cyclic_factorization⟩

theorem readout_det_eq : transverseReadout.det = cyclicReadout.det := by
  simp only [det_fin_three]
  decide +kernel

theorem cyclic_orientation_eq : orientation transverseLift = orientation cyclicLift := by
  apply Subtype.ext
  exact congrArg (fun d : k₅ => (transverseGraph (0 : k₅), d)) readout_det_eq

theorem cyclic_lifts_distinct : transverseLift ≠ cyclicLift := by
  intro he
  have h : transverseReadout 0 0 = cyclicReadout 0 0 :=
    congrArg (fun p : GramLift k₅ => p.readout 0 0) he
  exact (by decide : (1 : k₅) ≠ 2) h

/-- The cyclic row permutation gives two Gram realizations of the same
orientation, so the determinant square on Gram lifts fails pullback uniqueness. -/
theorem gram_comparison_not_injective :
    ¬ Function.Injective (orientation : GramLift k₅ → OrientationPoint k₅) :=
  fun hinj => cyclic_lifts_distinct (hinj cyclic_orientation_eq)

/-- At parameter zero both orientations have rational Gram solutions. For either
choice every four-by-four first direction and every choice of the six remaining
diagonals fails the formal permanent level over any characteristic-five field. -/
theorem transverse_orientations_without_completion {K : Type*} [Field K] [CharP K 5]
    (d : k₅) (hd : d = 2 ∨ d = 3) :
    (∃ p : GramLift k₅, (orientation p).val = (transverseGraph 0, d)) ∧
    (∀ (first : Matrix (Fin 4) (Fin 4) K) (x : Fin 6 → K),
      TransversePair.fullPencil first x ≠ 24) := by
  refine ⟨?_, TransversePair.fullPencil_ne_level⟩
  rcases hd with rfl | rfl
  · exact ⟨oppositeTransverseLift, transverse_orientations.2.1⟩
  · exact ⟨transverseLift, transverse_orientations.1⟩

/-- Any family of Gram lifts which supplies an actual level completion at
the fixed transverse frame misses that frame in the orientation pullback. -/
theorem level_comparison_not_surjective {F : Type*} (gram : F → GramLift k₅)
    (restrict : ∀ z, (gram z).frame = transverseGraph 0 →
      ∃ (first : Matrix (Fin 4) (Fin 4) k₅) (x : Fin 6 → k₅),
        TransversePair.fullPencil first x = 24) :
    ¬ Function.Surjective (orientation ∘ gram) := by
  intro surj
  obtain ⟨z, hz⟩ := surj (orientation transverseLift)
  have hframe : (gram z).frame = transverseGraph 0 :=
    congrArg (fun p : OrientationPoint k₅ => p.val.1) hz
  obtain ⟨first, x, h⟩ := restrict z hframe
  let _ : Fact (Nat.Prime 5) := ⟨Nat.prime_five⟩
  exact TransversePair.fullPencil_ne_level first x h

end PvsNP.OrientationSquare
