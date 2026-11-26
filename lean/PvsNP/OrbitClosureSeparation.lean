module

public import Mathlib.Algebra.BigOperators.Fin
public import Mathlib.Data.Matrix.Mul
public import Mathlib.RingTheory.Nullstellensatz

@[expose] public section

namespace PvsNP.OrbitClosureSeparation

open MvPolynomial

/-- A polynomial that vanishes on the source and is nonzero at the target
excludes the target from the algebraic closure of the source. -/
theorem not_mem_closure_of_separator
    {k K σ : Type*} [Field k] [Field K] [Algebra k K]
    {source : Set (σ → K)} {target : σ → K} (p : MvPolynomial σ k)
    (vanishes : ∀ x ∈ source, aeval x p = 0) (nonzero : aeval target p ≠ 0) :
    target ∉ zeroLocus K (vanishingIdeal k source) := by
  intro member
  exact nonzero (mem_zeroLocus_iff.mp member p (mem_vanishingIdeal_iff.mpr vanishes))

/-- The determinant of the generic two-by-two matrix. -/
noncomputable def minor (k : Type*) [Field k] : MvPolynomial (Fin 2 × Fin 2) k :=
  X (0, 0) * X (1, 1) - X (0, 1) * X (1, 0)

def outerProduct {k : Type*} [Field k] (u v : Fin 2 → k) : Fin 2 × Fin 2 → k :=
  fun ij => u ij.1 * v ij.2

def outerProductFamily (k : Type*) [Field k] : Set (Fin 2 × Fin 2 → k) :=
  Set.range (fun uv : (Fin 2 → k) × (Fin 2 → k) => outerProduct uv.1 uv.2)

def identityPoint (k : Type*) [Field k] : Fin 2 × Fin 2 → k :=
  fun ij => if ij.1 = ij.2 then 1 else 0

theorem minor_at_outerProduct {k : Type*} [Field k] (u v : Fin 2 → k) :
    aeval (outerProduct u v) (minor k) = 0 := by
  simp only [minor, map_sub, map_mul, aeval_X, outerProduct]
  apply sub_eq_zero.mpr
  ac_rfl

theorem minor_at_identityPoint (k : Type*) [Field k] :
    aeval (identityPoint k) (minor k) = 1 := by
  simp [minor, identityPoint, show (0 : Fin 2) ≠ 1 by decide,
    show (1 : Fin 2) ≠ 0 by decide]

/-- The identity matrix is excluded from the algebraic closure of the
outer-product family by the generic determinant. -/
theorem identity_not_mem_outerProduct_closure (k : Type*) [Field k] :
    identityPoint k ∉ zeroLocus k (vanishingIdeal k (outerProductFamily k)) := by
  apply not_mem_closure_of_separator (minor k)
  · rintro _ ⟨⟨u, v⟩, rfl⟩
    exact minor_at_outerProduct u v
  · rw [minor_at_identityPoint]
    exact one_ne_zero

def elementary00 (k : Type*) [Field k] : Matrix (Fin 2) (Fin 2) k :=
  fun i j => if i = 0 ∧ j = 0 then 1 else 0

/-- Every left-right transform of the elementary matrix is an outer product.
Taking arbitrary matrices here includes the orbit under invertible ones. -/
theorem leftRightProduct_mem_outerProductFamily {k : Type*} [Field k]
    (L R : Matrix (Fin 2) (Fin 2) k) :
    (fun ij => ((L * elementary00 k) * R) ij.1 ij.2) ∈ outerProductFamily k := by
  refine ⟨(fun i => L i 0, fun j => R 0 j), ?_⟩
  funext ij
  simp [outerProduct, Matrix.mul_apply, Fin.sum_univ_two, elementary00,
    show (1 : Fin 2) ≠ 0 by decide]

/-- Left and right invertible matrices give the rank-one orbit of `E₀₀`.
Using the inverse on the right gives the same set of matrices. -/
def leftRightOrbit (k : Type*) [Field k] : Set (Fin 2 × Fin 2 → k) :=
  Set.range (fun lr : (Matrix (Fin 2) (Fin 2) k)ˣ × (Matrix (Fin 2) (Fin 2) k)ˣ =>
    fun ij => ((lr.1.val * elementary00 k) * lr.2.val) ij.1 ij.2)

theorem identity_not_mem_leftRightOrbit_closure (k : Type*) [Field k] :
    identityPoint k ∉ zeroLocus k (vanishingIdeal k (leftRightOrbit k)) := by
  apply not_mem_closure_of_separator (minor k)
  · rintro _ ⟨⟨L, R⟩, rfl⟩
    obtain ⟨⟨u, v⟩, product⟩ := leftRightProduct_mem_outerProductFamily L.val R.val
    exact (congrArg (fun x : Fin 2 × Fin 2 → k => aeval x (minor k)) product.symm).trans
      (minor_at_outerProduct u v)
  · rw [minor_at_identityPoint]
    exact one_ne_zero

end PvsNP.OrbitClosureSeparation
