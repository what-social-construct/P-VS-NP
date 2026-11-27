module

public import PvsNP.PermanentReadout
public import PvsNP.ReadoutResidual
public import Mathlib.Algebra.DualNumber
public import Mathlib.RingTheory.Ideal.Operations

/-! # The Gram discriminant and the collision image on a readout minor chart -/

@[expose] public section

namespace PvsNP.PermanentReadout

open Matrix Polynomial

variable {R : Type*} [CommRing R]

/-- Pulling back the Gram discriminant gives the square of the determinant
ideal. On a unit-minor chart the latter ideal defines the collision image. -/
theorem gram_discriminant_ideal (G A : Matrix (Fin 3) (Fin 3) R)
    (hG : G = A.transpose * traceZeroGram R * A) (h₄ : IsUnit (4 : R)) :
    Ideal.span {G.det} = (Ideal.span {A.det}) ^ 2 := by
  rw [det_edgeGram G A hG, Ideal.span_singleton_mul_left_unit h₄, Ideal.span_singleton_pow]

/-- In the unit-minor normal form the kernel of the base map to distinct
pairs is the collision image ideal, with any free first-direction variables σ. -/
theorem gram_discriminant_eq_punctured_image_sq (σ : Type*) (G A : Matrix (Fin 3) (Fin 3) R)
    (hG : G = A.transpose * traceZeroGram R * A) (h₄ : IsUnit (4 : R)) :
    Ideal.span {G.det} = (RingHom.ker (toLaurent.comp (C.comp ((MvPolynomial.C (σ := σ)).comp
      (Ideal.Quotient.mk (Ideal.span {A.det})))))) ^ 2 := by
  rw [ReadoutResidual.puncturedPairs_base_ker, gram_discriminant_ideal G A hG h₄]

/-- The two zero loci therefore agree on reduced support. -/
theorem gram_discriminant_radical (G A : Matrix (Fin 3) (Fin 3) R)
    (hG : G = A.transpose * traceZeroGram R * A) (h₄ : IsUnit (4 : R)) :
    (Ideal.span {G.det}).radical = (Ideal.span {A.det}).radical := by
  rw [gram_discriminant_ideal G A hG h₄, Ideal.radical_pow _ (by decide : 2 ≠ 0)]

/-- The diagonal matrix over the dual numbers tests the local Gram identity
on a nonreduced base. Its leading two-by-two minor is one. -/
def infinitesimalReadout : Matrix (Fin 3) (Fin 3) (DualNumber (ZMod 5)) :=
  !![1, 0, 0; 0, 1, 0; 0, 0, DualNumber.eps]

/-- In this local Gram example the discriminant vanishes, while the first-colon
image equation generates the nonzero ideal (ε). -/
theorem infinitesimal_discriminant_ideals :
    let A := infinitesimalReadout
    let G := A.transpose * traceZeroGram _ * A
    Ideal.span {G.det} = ⊥ ∧ Ideal.span {A.det} ≠ ⊥ := by
  dsimp only
  have hA : infinitesimalReadout.det = DualNumber.eps := by
    simp [infinitesimalReadout, Matrix.det_fin_three]
  rw [det_edgeGram _ infinitesimalReadout rfl, hA]
  constructor
  · simp
  · intro h
    have he : (DualNumber.eps : DualNumber (ZMod 5)) = 0 := Ideal.span_singleton_eq_bot.mp h
    exact (by decide : (1 : ZMod 5) ≠ 0) (congrArg TrivSqZeroExt.snd he)

end PvsNP.PermanentReadout
