module

public import PvsNP.ReadoutResidual

@[expose] public section

namespace PvsNP.ReadoutGluing

open Polynomial

variable {R : Type*} [CommRing R]

/-- Coefficients on the determinant divisor, where the two pieces meet. -/
abbrev ContactRing (d : R) := R ⧸ Ideal.span {d}

/-- Restrict a function to the diagonal and to the first-colon residual. -/
noncomputable def restrictions (d : R) : R[X] →+* R × (ContactRing d)[X] :=
  constantCoeff.prod (mapRingHom (Ideal.Quotient.mk (Ideal.span {d})))

/-- The ring pullback imposing agreement at the residual zero section. -/
noncomputable def compatiblePairs (d : R) : Subring (R × (ContactRing d)[X]) :=
  ((Ideal.Quotient.mk (Ideal.span {d})).comp (RingHom.fst _ _)).eqLocus
    (constantCoeff.comp (RingHom.snd _ _))

theorem mem_compatiblePairs (d : R) (r : R) (p : (ContactRing d)[X]) :
    (r, p) ∈ compatiblePairs d ↔ Ideal.Quotient.mk (Ideal.span {d}) r = p.coeff 0 :=
  Iff.rfl

private theorem ker_residual (d : R) :
    RingHom.ker (mapRingHom (Ideal.Quotient.mk (Ideal.span {d}))) =
      Ideal.span {C d} := by
  simp [Polynomial.ker_mapRingHom, Ideal.map_span]

/-- The two restrictions jointly detect a function modulo the readout equation. -/
theorem ker_restrictions (d : R) :
    RingHom.ker (restrictions d) = Ideal.span {C d * X} := by
  let π := Ideal.Quotient.mk (Ideal.span {d})
  apply le_antisymm
  · intro p hp
    have he : (p.coeff 0, p.map π) = 0 := hp
    obtain ⟨q, rfl⟩ := X_dvd_iff.mpr (congrArg Prod.fst he)
    have hmap : X * q.map π = 0 := by simpa using congrArg Prod.snd he
    have hq : q ∈ RingHom.ker (mapRingHom π) := by
      change q.map π = 0
      exact isRegular_X.left (hmap.trans (mul_zero X).symm)
    rw [ker_residual d, Ideal.mem_span_singleton] at hq
    obtain ⟨u, rfl⟩ := hq
    exact Ideal.mem_span_singleton.mpr ⟨u, by ac_rfl⟩
  · refine Ideal.span_le.mpr (Set.singleton_subset_iff.mpr ?_)
    change (constantCoeff (C d * X), (C d * X).map π) = 0
    have hd : π d = 0 := Ideal.Quotient.eq_zero_iff_mem.mpr (Ideal.mem_span_singleton_self d)
    simp [hd]

/-- The scheme-theoretic union of the diagonal and its first-colon residual
recovers the full collision equation, even over a nonreduced base. -/
theorem diagonal_inf_firstColon (d : R) :
    Ideal.span {(X : R[X])} ⊓ (Ideal.span {C d * X}).colon (Ideal.span {(X : R[X])}) =
      Ideal.span {C d * X} := by
  rw [ReadoutResidual.normalForm_colon d, ← ker_residual d, ← ker_restrictions d]
  ext p
  rw [Submodule.mem_inf, Ideal.mem_span_singleton, X_dvd_iff]
  let π := Ideal.Quotient.mk (Ideal.span {d})
  change (p.coeff 0 = 0 ∧ p.map π = 0) ↔ (p.coeff 0, p.map π) = (0, 0)
  exact Prod.mk_inj.symm

/-- Every pair with the same value on the contact ring glues. The correction
to a lifted residual polynomial changes only its constant coefficient. -/
theorem range_restrictions (d : R) : (restrictions d).range = compatiblePairs d := by
  let π := Ideal.Quotient.mk (Ideal.span {d})
  ext ⟨r, p⟩
  rw [mem_compatiblePairs]
  constructor
  · rintro ⟨q, hq⟩
    obtain ⟨rfl, rfl⟩ := Prod.mk.inj hq
    exact (coeff_map _ _).symm
  · intro h
    obtain ⟨q, rfl⟩ := Polynomial.map_surjective π Ideal.Quotient.mk_surjective p
    have hc : π (r - q.coeff 0) = 0 := by simpa [map_sub, coeff_map, π, sub_eq_zero] using h
    refine ⟨q + C (r - q.coeff 0), Prod.ext ?_ ?_⟩
    · change (q + C (r - q.coeff 0)).coeff 0 = r
      simp
    · change (q + C (r - q.coeff 0)).map π = q.map π
      rw [Polynomial.map_add, map_C, hc, map_zero, add_zero]

/-- The equal-readout ring is the fiber product of the diagonal ring and
the residual polynomial ring over the determinant quotient. -/
noncomputable def gluingEquiv (d : R) :
    (R[X] ⧸ Ideal.span {C d * X}) ≃+* compatiblePairs d :=
  (Ideal.quotEquivOfEq (ker_restrictions d).symm).trans
    (((restrictions d).quotientKerEquivRange).trans (RingEquiv.subringCongr (range_restrictions d)))

@[simp] theorem gluingEquiv_mk (d : R) (p : R[X]) :
    (gluingEquiv d (Ideal.Quotient.mk _ p)).val =
      (p.coeff 0, p.map (Ideal.Quotient.mk (Ideal.span {d}))) :=
  rfl

/-- Two ring maps agreeing on the contact divisor lift uniquely to the
equal-readout ring with the specified restrictions. -/
theorem gluing_universal {T : Type*} [CommRing T] (d : R)
    (u : T →+* R) (v : T →+* (ContactRing d)[X])
    (agree : ∀ t, Ideal.Quotient.mk (Ideal.span {d}) (u t) = (v t).coeff 0) :
    ∃! l : T →+* (R[X] ⧸ Ideal.span {C d * X}),
      ∀ t, (gluingEquiv d (l t)).val = (u t, v t) := by
  let paired := (u.prod v).codRestrict (compatiblePairs d) agree
  let l := (gluingEquiv d).symm.toRingHom.comp paired
  have hl (t : T) : (gluingEquiv d (l t)).val = (u t, v t) := by
    change (gluingEquiv d ((gluingEquiv d).symm (paired t))).val = _
    rw [RingEquiv.apply_symm_apply]
    rfl
  refine ⟨l, hl, ?_⟩
  intro other ho
  ext t
  exact (gluingEquiv d).injective (Subtype.ext ((ho t).trans (hl t).symm))

/-- The unrestricted product of these two factors is attained exactly
when the determinant is a unit, equivalently the contact divisor is empty. -/
theorem compatiblePairs_eq_top_iff (d : R) : compatiblePairs d = ⊤ ↔ IsUnit d := by
  constructor
  · intro he
    have h : ((1 : R), (0 : (ContactRing d)[X])) ∈ compatiblePairs d := he ▸ trivial
    rw [mem_compatiblePairs] at h
    have h1 : (1 : R) ∈ Ideal.span {d} := Ideal.Quotient.eq_zero_iff_mem.mp (by simpa using h)
    rwa [← Ideal.span_singleton_eq_top, Ideal.eq_top_iff_one]
  · intro hd
    have : Subsingleton (ContactRing d) :=
      Ideal.Quotient.subsingleton_iff.mpr (Ideal.span_singleton_eq_top.mpr hd)
    apply top_unique
    intro p _
    exact Subsingleton.elim _ _

end PvsNP.ReadoutGluing
