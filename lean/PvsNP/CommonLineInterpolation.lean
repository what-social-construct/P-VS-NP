module

public import Mathlib.Algebra.Field.ZMod
public import Mathlib.LinearAlgebra.Matrix.NonsingularInverse
public import Mathlib.LinearAlgebra.Vandermonde
public import Mathlib.RingTheory.Ideal.Span

/-! # Interpolating the three residual binary forms on a common-line frame -/

@[expose] public section

namespace PvsNP.CommonLineInterpolation

open Matrix

variable {R : Type*} [CommRing R] [Algebra (ZMod 5) R]

/-- Values at $(1,0),\ldots,(1,n-1)$ in increasing order of the exponent of
the second coordinate. -/
def samples {n : ℕ} (c : Fin n → R) : Fin n → R :=
  vandermonde (fun i : Fin n ↦ (i.val : R)) *ᵥ c

private theorem sampleMatrix_unit {n : ℕ} (hn : n ≤ 5) :
    IsUnit (vandermonde (fun i : Fin n ↦ (i.val : R))).det := by
  let nodes (i : Fin n) : ZMod 5 := i.val
  let _ : Fact (Nat.Prime 5) := ⟨by decide⟩
  have hinj : Function.Injective nodes := by
    intro i j hij
    apply Fin.ext
    simpa only [nodes, ZMod.val_natCast_of_lt (i.isLt.trans_le hn),
      ZMod.val_natCast_of_lt (j.isLt.trans_le hn)] using congrArg ZMod.val hij
  have hu : IsUnit (vandermonde nodes).det :=
    isUnit_iff_ne_zero.mpr (det_vandermonde_ne_zero_iff.mpr hinj)
  have hmap : (vandermonde nodes).map (algebraMap (ZMod 5) R) =
      vandermonde (fun i : Fin n ↦ (i.val : R)) := by
    ext i j
    simp [vandermonde_apply, nodes]
  rw [← hmap]
  change IsUnit (((algebraMap (ZMod 5) R).mapMatrix (vandermonde nodes)).det)
  rw [← RingHom.map_det]
  exact hu.map (algebraMap (ZMod 5) R)

/-- The same ideal is obtained from the coefficient functions or the samples,
including over nonreduced base algebras. -/
theorem sampleIdeal_eq {n : ℕ} (hn : n ≤ 5) (c : Fin n → R) :
    Ideal.span (Set.range (samples c)) = Ideal.span (Set.range c) := by
  let V := vandermonde (fun i : Fin n ↦ (i.val : R))
  have le_span (M : Matrix (Fin n) (Fin n) R) (v : Fin n → R) :
      Ideal.span (Set.range (M *ᵥ v)) ≤ Ideal.span (Set.range v) := by
    apply Ideal.span_le.mpr
    rintro _ ⟨i, rfl⟩
    change (∑ j, M i j * v j) ∈ Ideal.span (Set.range v)
    exact Submodule.sum_mem _ fun j _ ↦
      (Ideal.span (Set.range v)).mul_mem_left _ (Ideal.subset_span (Set.mem_range_self j))
  have hrecover : V⁻¹ *ᵥ (V *ᵥ c) = c := by
    rw [mulVec_mulVec, nonsing_inv_mul V (sampleMatrix_unit hn), one_mulVec]
  apply le_antisymm (le_span V c)
  simpa only [hrecover] using le_span V⁻¹ (V *ᵥ c)

/-- The two cubics and the quartic jointly define the same closed subscheme
with their thirteen scalar evaluations as with their thirteen coefficients. -/
theorem residual_sample_ideals (c d : Fin 4 → R) (q : Fin 5 → R) :
    Ideal.span (Set.range (samples c)) ⊔ Ideal.span (Set.range (samples d)) ⊔
        Ideal.span (Set.range (samples q)) =
      Ideal.span (Set.range c) ⊔ Ideal.span (Set.range d) ⊔ Ideal.span (Set.range q) := by
  rw [sampleIdeal_eq (by decide) c, sampleIdeal_eq (by decide) d, sampleIdeal_eq (by decide) q]

end PvsNP.CommonLineInterpolation
