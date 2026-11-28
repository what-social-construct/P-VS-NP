module

public import Mathlib.Algebra.Field.ZMod
public import Mathlib.LinearAlgebra.Matrix.NonsingularInverse
public import Mathlib.LinearAlgebra.Vandermonde
public import Mathlib.RingTheory.Polynomial.ContentIdeal

/-! # Interpolating the residual binary forms and the hyperplane pencil -/

@[expose] public section

namespace PvsNP.CommonLineInterpolation

open Matrix

variable {R : Type*} [CommRing R]

/-- Values at $(1,0),\ldots,(1,n-1)$ in increasing order of the exponent of
the second coordinate. -/
def samples {n : ℕ} (c : Fin n → R) : Fin n → R :=
  vandermonde (fun i : Fin n ↦ (i.val : R)) *ᵥ c

private theorem vandermonde_unit {k : Type*} [Field k] [Algebra k R]
    {n : ℕ} (nodes : Fin n → k) (h : Function.Injective nodes) :
    IsUnit (vandermonde (fun i ↦ algebraMap k R (nodes i))).det := by
  have hu : IsUnit (vandermonde nodes).det :=
    isUnit_iff_ne_zero.mpr (det_vandermonde_ne_zero_iff.mpr h)
  have hmap : (vandermonde nodes).map (algebraMap k R) =
      vandermonde (fun i ↦ algebraMap k R (nodes i)) := by
    ext i j
    simp [vandermonde_apply]
  rw [← hmap]
  change IsUnit (((algebraMap k R).mapMatrix (vandermonde nodes)).det)
  rw [← RingHom.map_det]
  exact hu.map (algebraMap k R)

private theorem mulVec_span_eq {n : ℕ} (V : Matrix (Fin n) (Fin n) R)
    (hV : IsUnit V.det) (c : Fin n → R) :
    Ideal.span (Set.range (V *ᵥ c)) = Ideal.span (Set.range c) := by
  have le_span (M : Matrix (Fin n) (Fin n) R) (v : Fin n → R) :
      Ideal.span (Set.range (M *ᵥ v)) ≤ Ideal.span (Set.range v) := by
    apply Ideal.span_le.mpr
    rintro _ ⟨i, rfl⟩
    change (∑ j, M i j * v j) ∈ Ideal.span (Set.range v)
    exact Submodule.sum_mem _ fun j _ ↦
      (Ideal.span (Set.range v)).mul_mem_left _ (Ideal.subset_span (Set.mem_range_self j))
  have hrecover : V⁻¹ *ᵥ (V *ᵥ c) = c := by
    rw [mulVec_mulVec, nonsing_inv_mul V hV, one_mulVec]
  apply le_antisymm (le_span V c)
  simpa only [hrecover] using le_span V⁻¹ (V *ᵥ c)

section

variable [Algebra (ZMod 5) R]

/-- The same ideal is obtained from the coefficient functions or the samples,
including over nonreduced base algebras. -/
theorem sampleIdeal_eq {n : ℕ} (hn : n ≤ 5) (c : Fin n → R) :
    Ideal.span (Set.range (samples c)) = Ideal.span (Set.range c) := by
  let nodes (i : Fin n) : ZMod 5 := i.val
  let _ : Fact (Nat.Prime 5) := ⟨by decide⟩
  have hinj : Function.Injective nodes := by
    intro i j hij
    apply Fin.ext
    simpa only [nodes, ZMod.val_natCast_of_lt (i.isLt.trans_le hn),
      ZMod.val_natCast_of_lt (j.isLt.trans_le hn)] using congrArg ZMod.val hij
  apply mulVec_span_eq
  simpa [nodes] using vandermonde_unit (R := R) nodes hinj

/-- The two cubics and the quartic jointly define the same closed subscheme
with their thirteen scalar evaluations as with their thirteen coefficients. -/
theorem residual_sample_ideals (c d : Fin 4 → R) (q : Fin 5 → R) :
    Ideal.span (Set.range (samples c)) ⊔ Ideal.span (Set.range (samples d)) ⊔
        Ideal.span (Set.range (samples q)) =
      Ideal.span (Set.range c) ⊔ Ideal.span (Set.range d) ⊔ Ideal.span (Set.range q) := by
  rw [sampleIdeal_eq (by decide) c, sampleIdeal_eq (by decide) d, sampleIdeal_eq (by decide) q]

end

/-- Sampling a polynomial of degree less than the number of distinct scalar
nodes recovers its full content ideal, including infinitesimal structure. -/
theorem sampleIdeal_eq_contentIdeal {k : Type*} [Field k] [Algebra k R]
    {n : ℕ} (nodes : Fin n → k) (hinj : Function.Injective nodes)
    (p : Polynomial R) (hdeg : p.natDegree < n) :
    Ideal.span (Set.range (fun i ↦ p.eval (algebraMap k R (nodes i)))) = p.contentIdeal := by
  let V := vandermonde (fun i ↦ algebraMap k R (nodes i))
  let c (i : Fin n) := p.coeff i.val
  have heval : (fun i ↦ p.eval (algebraMap k R (nodes i))) = V *ᵥ c := by
    funext i
    rw [Polynomial.eval_eq_sum_range' hdeg, ← Fin.sum_univ_eq_sum_range]
    simp [V, c, Matrix.mulVec, dotProduct, vandermonde_apply, mul_comm]
  rw [heval, mulVec_span_eq V (vandermonde_unit nodes hinj)]
  apply le_antisymm
  · apply Ideal.span_le.mpr
    rintro _ ⟨i, rfl⟩
    exact p.coeff_mem_contentIdeal i.val
  · apply Ideal.span_le.mpr
    intro a ha
    obtain ⟨i, hi, rfl⟩ := Polynomial.mem_coeffs_iff.mp ha
    exact Ideal.subset_span ⟨⟨i, (Polynomial.le_natDegree_of_mem_supp i hi).trans_lt hdeg⟩, rfl⟩

/-- A degree-24 pencil can be sampled at all scalars of a field of size 25. -/
theorem pencil_contentIdeal {k : Type*} [Field k] [Fintype k] [Algebra k R]
    (hk : Fintype.card k = 25) (p : Polynomial R) (hdeg : p.natDegree ≤ 24) :
    Ideal.span (Set.range (fun t : k ↦ p.eval (algebraMap k R t))) = p.contentIdeal := by
  let e := (Fintype.equivFinOfCardEq hk).symm
  rw [← e.surjective.range_comp (fun t : k ↦ p.eval (algebraMap k R t))]
  exact sampleIdeal_eq_contentIdeal e e.injective p (by omega)

/-- The content scheme represents base changes killing the entire pencil. -/
theorem map_eq_zero_iff_contentIdeal_le_ker {S : Type*} [CommRing S]
    (p : Polynomial R) (f : R →+* S) : p.map f = 0 ↔ p.contentIdeal ≤ RingHom.ker f := by
  rw [← Polynomial.contentIdeal_eq_bot_iff, Polynomial.contentIdeal_map_eq_map_contentIdeal,
    Ideal.map_eq_bot_iff_le_ker]

end PvsNP.CommonLineInterpolation
