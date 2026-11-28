module

public import Mathlib.AlgebraicGeometry.Fiber
public import Mathlib.AlgebraicGeometry.IdealSheaf.Basic
public import Mathlib.AlgebraicGeometry.Morphisms.UniversallyClosed
public import Mathlib.RingTheory.Nullstellensatz

/-! # Geometric existence from affine chart equations -/

@[expose] public section

namespace PvsNP.GeometricExistence

open AlgebraicGeometry CategoryTheory MvPolynomial

/-- The points with nonempty scheme fiber form the support of the image ideal
for any universally closed morphism, in particular for a projective incidence. -/
theorem locus_eq_image_support {X S : Scheme} (f : X ⟶ S) [UniversallyClosed f] :
    {s : S | Nonempty (f.fiber s)} = (f.ker.support : Set S) := by
  rw [Scheme.Hom.support_ker, f.isClosedMap.isClosed_range.closure_eq]
  ext s
  change Nonempty (f.fiber s) ↔ ∃ x, f x = s
  rw [(f.fiberHomeo s).nonempty_congr, Set.nonempty_coe_sort]
  rfl

/-- A chart over the coefficient field has a point in an algebraically closed
extension exactly when its equations do not generate the unit ideal. -/
theorem exists_common_zero_iff {k K σ : Type*} [Field k] [Field K] [Algebra k K]
    [IsAlgClosed K] [Finite σ] (equations : Set (MvPolynomial σ k)) :
    (∃ x : σ → K, ∀ p ∈ equations, aeval x p = 0) ↔ 1 ∉ Ideal.span equations := by
  let I := Ideal.span equations
  change (Set.Nonempty {x : σ → K | ∀ p ∈ equations, aeval x p = 0}) ↔ 1 ∉ I
  rw [← zeroLocus_span]
  constructor
  · rintro ⟨x, hx⟩ h
    exact one_ne_zero (α := K) (by simpa using hx 1 h)
  · intro h
    obtain ⟨M, maximal, le⟩ := I.exists_le_maximal (I.ne_top_iff_one.mpr h)
    obtain ⟨x, hM⟩ := eq_vanishingIdeal_singleton_of_isMaximal K maximal
    refine ⟨x, fun p hp ↦ ?_⟩
    exact (mem_vanishingIdeal_singleton_iff x p).mp (hM ▸ le hp)

/-- For a family described by affine charts, eliminate the witness coordinates
fiber by fiber. The coefficient field can be the residue field of each base
point, and the points of the chart are taken in an algebraically closed extension. -/
theorem locus_eq_nonunit_charts {S Chart : Type*} {σ : Chart → Type*}
    [∀ j, Finite (σ j)] {k K : S → Type*} [∀ s, Field (k s)] [∀ s, Field (K s)]
    [∀ s, Algebra (k s) (K s)] [∀ s, IsAlgClosed (K s)]
    (equations : (s : S) → (j : Chart) → Set (MvPolynomial (σ j) (k s))) :
    {s : S | ∃ (j : Chart) (x : σ j → K s), ∀ p ∈ equations s j, aeval x p = 0} =
      {s : S | ∃ j : Chart, 1 ∉ Ideal.span (equations s j)} := by
  ext s
  exact exists_congr fun j ↦ exists_common_zero_iff (K := K s) (equations s j)

end PvsNP.GeometricExistence
