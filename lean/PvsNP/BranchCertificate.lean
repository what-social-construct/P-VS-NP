module

public import Mathlib.Algebra.Ring.GeomSum
public import Mathlib.RingTheory.Ideal.Operations

/-! # Combining certificates on a divisor and its open complement -/

@[expose] public section

namespace PvsNP.BranchCertificate

variable {R : Type*} [CommRing R]

/-- Multipliers for `1 - a * d` and `d ^ n` that give an identity for one. -/
theorem combine (a d : R) (n : ℕ) :
    (∑ i ∈ Finset.range n, (a * d) ^ i) * (1 - a * d) + a ^ n * d ^ n = 1 := by
  rw [geom_sum_mul_neg, ← mul_pow, sub_add_cancel]

/-- The closed branch is empty when `d` is invertible modulo the ideal.
The open branch is empty when a positive power of `d` belongs to the ideal. -/
theorem one_mem_iff_branch_certificates (I : Ideal R) (d : R) :
    (1 : R) ∈ I ↔ (∃ a : R, 1 - a * d ∈ I) ∧ ∃ n : ℕ, 0 < n ∧ d ^ n ∈ I := by
  constructor
  · intro h
    exact ⟨⟨0, by simpa using h⟩, ⟨1, by decide, by simpa using I.mul_mem_left d h⟩⟩
  · rintro ⟨⟨a, hclosed⟩, ⟨n, _, hopen⟩⟩
    rw [← combine a d n]
    exact I.add_mem (I.mul_mem_left _ hclosed) (I.mul_mem_left _ hopen)

end PvsNP.BranchCertificate
