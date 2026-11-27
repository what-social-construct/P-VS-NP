module

public import Mathlib.Algebra.Ring.Idempotent
public import Mathlib.FieldTheory.Finite.Basic
public import Mathlib.FieldTheory.IntermediateField.Adjoin.Basic
public import Mathlib.FieldTheory.KummerPolynomial
public import Mathlib.RingTheory.Flat.Basic
public import Mathlib.RingTheory.TensorProduct.Maps
import Mathlib.Tactic.LinearCombination
import Mathlib.Tactic.Ring

@[expose] public section

namespace PvsNP.OrientationDescent

open Polynomial
open scoped TensorProduct

/-- A square root of a base-field nonsquare forces an even extension degree.
Excluding a degree-two lift then forces degree at least four. -/
theorem even_degree_ge_four {K L : Type*} [Field K] [Field L] [Algebra K L]
    [FiniteDimensional K L] {a : K} {d : L} (ha : ∀ b : K, b ^ 2 ≠ a)
    (hd : d ^ 2 = algebraMap K L a) (h₂ : Module.finrank K L ≠ 2) :
    2 ∣ Module.finrank K L ∧ 4 ≤ Module.finrank K L := by
  have hm : X ^ 2 - C a = minpoly K d := minpoly.eq_of_irreducible_of_monic
    (X_pow_sub_C_irreducible_of_prime Nat.prime_two ha) (by simp [hd])
    (monic_X_pow_sub_C a (by decide))
  have hdiv := minpoly.degree_dvd (Algebra.IsIntegral.isIntegral (R := K) d)
  rw [← hm, natDegree_X_pow_sub_C] at hdiv
  have hpos := Module.finrank_pos (R := K) (M := L)
  exact ⟨hdiv, by omega⟩

local notation "k₅" => ZMod 5
scoped instance primeFive : Fact (Nat.Prime 5) := ⟨Nat.prime_five⟩

variable {L B : Type*} [Field L] [Algebra k₅ L] [CommRing B] [Algebra k₅ B]

/-- The square root of a nonsquare of F₅ is sent to its negative by Frobenius. -/
theorem frobenius_sqrt {a : k₅} {d : L} (ha : ∀ b : k₅, b ^ 2 ≠ a)
    (hd : d ^ 2 = algebraMap k₅ L a) : FiniteField.frobeniusAlgHom k₅ L d = -d := by
  have ha₂ : a ^ 2 = -1 := (by decide : ∀ x : k₅, (∀ b : k₅, b ^ 2 ≠ x) → x ^ 2 = -1) a ha
  rw [FiniteField.frobeniusAlgHom_apply, ZMod.card]
  calc
    d ^ 5 = (d ^ 2) ^ 2 * d := by ring
    _ = -d := by rw [hd, ← map_pow, ha₂, map_neg, map_one, neg_one_mul]

/-- In the scalar extension of the lift algebra, the positive orientation is
(1 + D/d)/2. The scalar 3 is the inverse of 2 in characteristic five. -/
noncomputable def orientationProjector (d : L) (D : B) : L ⊗[k₅] B :=
  3 * (1 + d⁻¹ ⊗ₜ[k₅] D)

private theorem twice_three (T : Type*) [CommRing T] [Algebra k₅ T] : (2 : T) * 3 = 1 := by
  simpa only [map_mul, map_ofNat, map_one] using
    congrArg (algebraMap k₅ T) (show (2 : k₅) * 3 = 1 by decide)

/-- The two complementary orientation projectors are orthogonal idempotents
as soon as the readout determinant and splitting scalar have the same nonzero square. -/
theorem complementary_projectors {a : k₅} {d : L} {D : B} (ha : a ≠ 0)
    (hd : d ^ 2 = algebraMap k₅ L a) (hD : D ^ 2 = algebraMap k₅ B a) :
    IsIdempotentElem (orientationProjector d D) ∧
      IsIdempotentElem (1 - orientationProjector d D) ∧
      orientationProjector d D * (1 - orientationProjector d D) = 0 := by
  have hsign : (d⁻¹ ⊗ₜ[k₅] D : L ⊗[k₅] B) ^ 2 = 1 := by
    rw [Algebra.TensorProduct.tmul_pow, inv_pow, hd, hD, Algebra.algebraMap_eq_smul_one (R := k₅) (A := B),
      ← TensorProduct.smul_tmul, Algebra.smul_def, mul_inv_cancel₀ ((map_ne_zero_iff _ (algebraMap k₅ L).injective).2 ha)]
    rfl
  have h : IsIdempotentElem (orientationProjector d D) := by
    unfold IsIdempotentElem orientationProjector
    linear_combination (3 : L ⊗[k₅] B)^2 * hsign +
      3 * (1 + d⁻¹ ⊗ₜ[k₅] D) * twice_three (L ⊗[k₅] B)
  exact ⟨h, h.one_sub, h.mul_one_sub_self⟩

/-- Frobenius acts only on the coefficients added by scalar extension and
exchanges the positive and negative orientations. -/
theorem frobenius_projector {a : k₅} {d : L} (D : B) (ha : ∀ b : k₅, b ^ 2 ≠ a)
    (hd : d ^ 2 = algebraMap k₅ L a) :
    Algebra.TensorProduct.map (FiniteField.frobeniusAlgHom k₅ L) (AlgHom.id k₅ B)
      (orientationProjector d D) = 1 - orientationProjector d D := by
  simp only [orientationProjector, map_mul, map_ofNat, map_add, map_one,
    Algebra.TensorProduct.map_tmul, map_inv₀, frobenius_sqrt ha hd, AlgHom.id_apply,
    inv_neg, TensorProduct.neg_tmul]
  linear_combination twice_three (L ⊗[k₅] B)

/-- If one orientation projector vanishes after splitting a nonsquare at five,
coefficientwise Frobenius and faithful scalar extension force the original lift algebra to vanish. -/
theorem subsingleton_of_projector_zero {a : k₅} {d : L} {D : B}
    (ha : ∀ b : k₅, b ^ 2 ≠ a) (hd : d ^ 2 = algebraMap k₅ L a)
    (he : orientationProjector d D = 0) : Subsingleton B := by
  by_contra! h
  have := Algebra.TensorProduct.nontrivial_of_algebraMap_injective_of_flat_left
    k₅ L B (algebraMap k₅ B).injective
  have hs := frobenius_projector D ha hd
  rw [he, map_zero, sub_zero] at hs
  exact zero_ne_one hs

end PvsNP.OrientationDescent
