module

public import PvsNP.ReadoutResidual

/-!
# Contact of the two orientations

After a root d is chosen, the orientation equation is Y² = d². Its residual
branch along Y = d has equation Y + d = 0. The two branches meet on 2d = 0.
The square-cover calculation in Galois Obstruction Theory motivates this
comparison with the equal-readout image.
-/

@[expose] public section

namespace PvsNP.OrientationContact

open Polynomial

variable {R : Type*} [CommRing R]

/-- The first colon by the positive branch cuts out the negative branch
over every commutative coefficient ring. -/
theorem orientation_colon (d : R) :
    (Ideal.span {X ^ 2 - C (d ^ 2)}).colon (Ideal.span {X - C d}) =
      Ideal.span {(X + C d : R[X])} := by
  have factor : (X ^ 2 - C (d ^ 2) : R[X]) = (X + C d) * (X - C d) := by
    rw [map_pow, sq_sub_sq]
  rw [factor]
  ext p
  rw [Ideal.mem_colon_span_singleton, Ideal.mem_span_singleton', Ideal.mem_span_singleton']
  constructor
  · rintro ⟨q, hq⟩
    exact ⟨q, (monic_X_sub_C d).isRegular.right (by simpa only [mul_assoc] using hq)⟩
  · rintro ⟨q, rfl⟩
    exact ⟨q, (mul_assoc _ _ _).symm⟩

/-- On the positive branch the residual ideal restricts to the derivative 2d. -/
theorem orientation_contact (d : R) :
    ((Ideal.span {X ^ 2 - C (d ^ 2)}).colon (Ideal.span {X - C d})).map (evalRingHom d) =
      Ideal.span {2 * d} := by
  rw [orientation_colon, Ideal.map_span, Set.image_singleton]
  simp [two_mul]

/-- When 2 is invertible, the contact of the two orientations is exactly the
scheme-theoretic image of punctured equal-readout pairs on the minor chart. -/
theorem orientation_contact_eq_punctured_image (σ : Type*) (d : R) (h₂ : IsUnit (2 : R)) :
    ((Ideal.span {X ^ 2 - C (d ^ 2)}).colon (Ideal.span {X - C d})).map (evalRingHom d) =
      RingHom.ker (toLaurent.comp (C.comp ((MvPolynomial.C (σ := σ)).comp
        (Ideal.Quotient.mk (Ideal.span {d}))))) := by
  rw [orientation_contact, Ideal.span_singleton_mul_left_unit h₂,
    ReadoutResidual.puncturedPairs_base_ker]

end PvsNP.OrientationContact
