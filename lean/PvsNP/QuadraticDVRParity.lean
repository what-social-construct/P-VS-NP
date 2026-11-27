module

public import Mathlib.RingTheory.DiscreteValuationRing.Basic
public import Mathlib.Data.ENat.Basic
public import Mathlib.RingTheory.Localization.FractionRing
import Mathlib.Tactic.Ring

@[expose] public section

/-!
# Odd uniformizer order cannot be a square

The local parity calculation needed for the quadratic generic-degree test.
It is independent of polynomial maps and of a chosen normal closure.
-/

set_option autoImplicit false

namespace CollisionIdeals

noncomputable section

/-- In a DVR, a unit times a uniformizer cannot be a square in the fraction
field. The displayed cross-multiplied form avoids choosing a fraction-field
valuation. -/
theorem no_square_eq_uniformizer_mul_unit_square
    {R : Type*} [CommRing R] [IsDomain R] [IsDiscreteValuationRing R]
    (ϖ : R) (hϖ : Irreducible ϖ) (u : Rˣ)
    (a b : R) (hb : b ≠ 0)
    (h : a ^ 2 = ϖ * (u : R) * b ^ 2) : False := by
  have ha : a ≠ 0 := by
    intro ha
    rw [ha, zero_pow (by omega : 2 ≠ 0)] at h
    have hϖ0 := hϖ.ne_zero
    have hu0 := u.ne_zero
    have hb20 : b ^ 2 ≠ 0 := pow_ne_zero _ hb
    exact (mul_ne_zero (mul_ne_zero hϖ0 hu0) hb20) h.symm
  have hva : IsDiscreteValuationRing.addVal R a ≠ ⊤ := by
    exact mt IsDiscreteValuationRing.addVal_eq_top_iff.mp ha
  have hvb : IsDiscreteValuationRing.addVal R b ≠ ⊤ := by
    exact mt IsDiscreteValuationRing.addVal_eq_top_iff.mp hb
  obtain ⟨na, hna⟩ := ENat.ne_top_iff_exists.mp hva
  obtain ⟨nb, hnb⟩ := ENat.ne_top_iff_exists.mp hvb
  have hv := congrArg (IsDiscreteValuationRing.addVal R) h
  simp only [IsDiscreteValuationRing.addVal_pow,
    IsDiscreteValuationRing.addVal_mul,
    IsDiscreteValuationRing.addVal_uniformizer hϖ,
    IsDiscreteValuationRing.addVal_eq_zero_of_unit u] at hv
  rw [← hna, ← hnb] at hv
  have hnat : 2 * na = 1 + 2 * nb := by
    exact_mod_cast (show (2 * na : ENat) = 1 + 2 * nb by
      simpa only [nsmul_eq_mul, Nat.cast_ofNat, zero_add, add_zero] using hv)
  omega

/-- A fraction-field square cannot have odd order at a DVR uniformizer.
The factor away from the uniformizer is represented by a unit of the DVR. -/
theorem no_square_eq_odd_uniformizer_mul_unit
    {R S : Type*} [CommRing R] [IsDomain R] [IsDiscreteValuationRing R]
    [Field S] [Algebra R S] [IsFractionRing R S]
    (ϖ : R) (hϖ : Irreducible ϖ) (u : Rˣ) (m : ℕ)
    (z : S)
    (h : z ^ 2 =
      algebraMap R S (ϖ ^ (2 * m + 1) * (u : R))) : False := by
  obtain ⟨a, b, hb, hab⟩ := IsFractionRing.div_surjective (A := R) z
  have hb0 : b ≠ 0 := mem_nonZeroDivisors_iff_ne_zero.mp hb
  have hbF : algebraMap R S b ≠ 0 :=
    by simpa only [map_zero] using
      (IsFractionRing.injective R S).ne hb0
  have hcross :
      (algebraMap R S a) ^ 2 =
        algebraMap R S (ϖ ^ (2 * m + 1) * (u : R)) *
          (algebraMap R S b) ^ 2 := by
    rw [← hab, div_pow] at h
    exact (div_eq_iff (pow_ne_zero _ hbF)).mp h
  have hR : a ^ 2 = ϖ ^ (2 * m + 1) * (u : R) * b ^ 2 := by
    apply IsFractionRing.injective R S
    simpa only [map_pow, map_mul] using hcross
  apply no_square_eq_uniformizer_mul_unit_square ϖ hϖ u a (ϖ ^ m * b)
    (mul_ne_zero (pow_ne_zero _ hϖ.ne_zero) hb0)
  calc
    a ^ 2 = ϖ ^ (2 * m + 1) * (u : R) * b ^ 2 := hR
    _ = ϖ ^ (m * 2 + 1) * (u : R) * b ^ 2 := by rw [Nat.mul_comm 2 m]
    _ = ϖ * (u : R) * (ϖ ^ m * b) ^ 2 := by
      rw [pow_add, pow_mul, pow_one, mul_pow]
      ring

end

end CollisionIdeals
