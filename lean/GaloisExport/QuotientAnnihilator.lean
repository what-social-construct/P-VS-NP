module

public import Mathlib.RingTheory.Ideal.Colon
public import Mathlib.RingTheory.Ideal.Quotient.Operations

@[expose] public section

namespace HodgeConjecture.CollisionFoundations

variable {A : Type*} [CommRing A]

-- BEGIN GALOIS EXPORT
/--
The pullback of the annihilator of `J/I` is the colon ideal `I : J`.
-/
theorem comap_annihilator_map_quotient_eq_colon
    (I J : Ideal A) :
    ((J.map (Ideal.Quotient.mk I)).annihilator).comap
        (Ideal.Quotient.mk I) =
      I.colon J := by
  ext x
  constructor
  · intro hx
    rw [Submodule.mem_colon]
    intro j hj
    have hzero :
        Ideal.Quotient.mk I x *
            Ideal.Quotient.mk I j = 0 := by
      exact
        Submodule.mem_annihilator.mp hx _
          (Ideal.mem_map_of_mem (Ideal.Quotient.mk I) hj)
    rw [← map_mul, Ideal.Quotient.eq_zero_iff_mem] at hzero
    exact hzero
  · intro hx
    apply Submodule.mem_annihilator.mpr
    intro z hz
    obtain ⟨j, hj, rfl⟩ :=
      (Ideal.mem_map_iff_of_surjective
        (Ideal.Quotient.mk I)
        Ideal.Quotient.mk_surjective).mp hz
    change
      Ideal.Quotient.mk I x *
          Ideal.Quotient.mk I j = 0
    rw [← map_mul, Ideal.Quotient.eq_zero_iff_mem]
    exact Submodule.mem_colon.mp hx j hj
-- END GALOIS EXPORT

end HodgeConjecture.CollisionFoundations
