module

public import Mathlib.Algebra.CharZero.Infinite
public import Mathlib.Algebra.MvPolynomial.Degrees
public import Mathlib.Algebra.MvPolynomial.Funext
import Mathlib.Algebra.MvPolynomial.PDeriv
public import Mathlib.Algebra.Order.Antidiag.FinsuppEquiv
public import Mathlib.Basic.Complex.Basic
public import Mathlib.Data.Finsupp.Weight
import Mathlib.GroupTheory.Perm.Fin
public import Mathlib.LinearAlgebra.LinearIndependent.Defs
public import Mathlib.LinearAlgebra.Matrix.Permanent
public import Mathlib.LinearAlgebra.Matrix.Symmetric

@[expose] public section

namespace PvsNP.PermanentLevelTarget

open MvPolynomial
open scoped BigOperators

abbrev Frame := Fin 3 → Matrix (Fin 4) (Fin 4) ℂ
abbrev Exponent := Fin 3 →₀ ℕ

/-- The affine family through the all-ones matrix, with ordered directions `B`. -/
def pencil (B : Frame) (t : Fin 3 → ℂ) : Matrix (Fin 4) (Fin 4) ℂ :=
  fun r c => 1 + ∑ i, t i * B i r c

/-- The permanent restricted to the formal three-parameter pencil. -/
noncomputable def restrictedPermanent (B : Frame) : MvPolynomial (Fin 3) ℂ :=
  Matrix.permanent (fun r c : Fin 4 => 1 + ∑ i, X i * C (B i r c))

def IsLevel (B : Frame) : Prop := ∀ t, (pencil B t).permanent = 24

/-- Open target: the complex permanent level through the all-ones matrix contains
no affine three-plane of symmetric matrices passing through that matrix. -/
def noComplexLevelThreePlane : Prop :=
  ¬ ∃ B : Frame, LinearIndependent ℂ B ∧ (∀ i, (B i).IsSymm) ∧ IsLevel B

theorem eval_restrictedPermanent (B : Frame) (t : Fin 3 → ℂ) :
    eval t (restrictedPermanent B) = (pencil B t).permanent := by
  simp [restrictedPermanent, Matrix.permanent, pencil]

theorem isLevel_iff_polynomial (B : Frame) :
    IsLevel B ↔ restrictedPermanent B = C 24 := by
  rw [MvPolynomial.funext_iff]
  simp only [eval_restrictedPermanent, eval_C]
  rfl

theorem coeff_zero_restrictedPermanent (B : Frame) :
    (restrictedPermanent B).coeff 0 = 24 := by
  rw [← constantCoeff_eq, ← eval_zero, eval_restrictedPermanent]
  simp [pencil, Matrix.permanent, Fintype.card_perm, Nat.factorial]

theorem totalDegree_restrictedPermanent (B : Frame) :
    (restrictedPermanent B).totalDegree ≤ 4 := by
  unfold restrictedPermanent Matrix.permanent
  apply (totalDegree_finsetSum _ _).trans
  apply Finset.sup_le
  intro σ _
  apply (totalDegree_finsetProd _ _).trans
  calc
    _ ≤ ∑ _i : Fin 4, 1 := by
      apply Finset.sum_le_sum
      intro i _
      apply (totalDegree_add _ _).trans
      apply max_le
      · simp
      · apply (totalDegree_finsetSum _ _).trans
        apply Finset.sup_le
        intro j _
        exact (totalDegree_mul _ _).trans (by simp)
    _ = 4 := by simp

/-- The three degree-one equations in the pencil parameters. -/
def FirstOrderVanishes (B : Frame) : Prop :=
  ∀ d : Exponent, d.degree = 1 → (restrictedPermanent B).coeff d = 0

private noncomputable def entry (B : Frame) (r c : Fin 4) : MvPolynomial (Fin 3) ℂ :=
  1 + ∑ j, X j * C (B j r c)

private lemma entry_zero (B : Frame) (r c : Fin 4) : constantCoeff (entry B r c) = 1 := by
  simp [entry]

private lemma entry_first (B : Frame) (r c : Fin 4) (i : Fin 3) :
    constantCoeff (pderiv i (entry B r c)) = B i r c := by
  classical
  simp [entry, Pi.single_apply]

private lemma prod_first (B : Frame) (i : Fin 3) (σ : Equiv.Perm (Fin 4)) (s : Finset (Fin 4)) :
    constantCoeff (pderiv i (∏ c ∈ s, entry B (σ c) c)) = ∑ c ∈ s, B i (σ c) c := by
  induction s using Finset.induction_on with
  | empty => simp
  | insert c s hc ih => simp [hc, entry_zero, entry_first, ih, add_comm]

private lemma sum_perm_entry (A : Matrix (Fin 4) (Fin 4) ℂ) (c : Fin 4) :
    ∑ σ : Equiv.Perm (Fin 4), A (σ c) c = ∑ r : Fin 4, 6 * A r c := by
  calc
    _ = ∑ σ : Equiv.Perm (Fin 4), A (σ 0) c := by
      simpa [Equiv.Perm.mul_apply] using Equiv.sum_comp (Equiv.mulRight (Equiv.swap (0 : Fin 4) c))
        (fun σ : Equiv.Perm (Fin 4) => A (σ 0) c)
    _ = ∑ q : Fin 4 × Equiv.Perm (Fin 3), A (Equiv.Perm.decomposeFin.symm q 0) c :=
      (Equiv.Perm.decomposeFin.symm.sum_comp (fun σ : Equiv.Perm (Fin 4) => A (σ 0) c)).symm
    _ = _ := by simp [Fintype.sum_prod_type, Fintype.card_perm, Nat.factorial, nsmul_eq_mul]

/-- Each fixed matrix entry occurs in six of the 24 permutations. -/
theorem coeff_linear_restrictedPermanent (B : Frame) (i : Fin 3) :
    (restrictedPermanent B).coeff (Finsupp.single i 1) = 6 * ∑ r, ∑ c, B i r c := by
  have hcoeff := coeff_pderiv (i := i) (restrictedPermanent B) 0
  simp only [zero_add, Finsupp.coe_zero, Pi.zero_apply, Nat.cast_zero, mul_one] at hcoeff
  rw [← hcoeff, ← constantCoeff_eq]
  change constantCoeff (pderiv i (∑ σ : Equiv.Perm (Fin 4), ∏ c, entry B (σ c) c)) = _
  simp only [map_sum, prod_first]
  rw [Finset.sum_comm]
  simp_rw [sum_perm_entry]
  rw [Finset.sum_comm]
  simp [Finset.mul_sum]

/-- The first-order equations cut out the entry-sum-zero tangent space. -/
theorem firstOrderVanishes_iff_entry_sums (B : Frame) :
    FirstOrderVanishes B ↔ ∀ i, ∑ r, ∑ c, B i r c = 0 := by
  constructor
  · intro h i
    have hi := h (Finsupp.single i 1) (by simp)
    simpa [coeff_linear_restrictedPermanent] using hi
  · intro h d hd
    obtain ⟨i, rfl⟩ := (Finsupp.sum_eq_one_iff d).mp hd
    simp [coeff_linear_restrictedPermanent, h]

/-- A nonzero quadratic, cubic, or quartic coefficient on the same frame. -/
def HasHigherObstruction (B : Frame) : Prop :=
  ∃ d : Exponent, 2 ≤ d.degree ∧ d.degree ≤ 4 ∧ (restrictedPermanent B).coeff d ≠ 0

theorem isLevel_iff_coefficients (B : Frame) :
    IsLevel B ↔ FirstOrderVanishes B ∧ ¬ HasHigherObstruction B := by
  rw [isLevel_iff_polynomial]
  constructor
  · intro h
    have vanish (d : Exponent) (hd : d.degree ≠ 0) : (restrictedPermanent B).coeff d = 0 := by
      rw [h]
      exact coeff_C_of_ne_zero (fun e => hd ((Finsupp.degree_eq_zero_iff d).mpr e)) _
    constructor
    · intro d hd
      exact vanish d (by omega)
    · rintro ⟨d, h₂, _, hne⟩
      exact hne (vanish d (by omega))
  · rintro ⟨hfirst, hhigher⟩
    ext d
    by_cases hzero : d = 0
    · simp [hzero, coeff_zero_restrictedPermanent]
    rw [coeff_C_of_ne_zero hzero]
    by_contra hne
    have hpos := (Finsupp.degree_eq_zero_iff d).not.mpr hzero
    have hle : d.degree ≤ 4 := (le_totalDegree (mem_support_iff.mpr hne)).trans
      (totalDegree_restrictedPermanent B)
    by_cases h₁ : d.degree = 1
    · exact hne (hfirst d h₁)
    · exact hhigher ⟨d, by omega, hle, hne⟩

/-- Indices of all quadratic, cubic, and quartic terms in the three parameters. -/
def higherIndices : Finset Exponent :=
  (Finset.Icc 2 4).biUnion fun n => (Finset.univ : Finset (Fin 3)).finsuppAntidiag n

@[simp] theorem mem_higherIndices (d : Exponent) : d ∈ higherIndices ↔ 2 ≤ d.degree ∧ d.degree ≤ 4 := by
  simp [higherIndices, Finsupp.degree_eq_sum]

/-- The higher coefficient test has exactly 31 indices. -/
theorem card_higherIndices : higherIndices.card = 31 := by
  unfold higherIndices
  rw [Finset.card_biUnion]
  · have h : Finset.Icc 2 4 = ({2, 3, 4} : Finset ℕ) := by decide
    rw [h]
    simp [Finset.card_finsuppAntidiag_nat_eq_choose, Nat.choose]
  · intro n _ m _ hne
    apply Finset.disjoint_left.mpr
    intro d hn hm
    exact hne ((Finset.mem_finsuppAntidiag.mp hn).1.symm.trans (Finset.mem_finsuppAntidiag.mp hm).1)

/-- Work backward from the unrestricted target: for every independent symmetric frame
passing its first-order equations, exhibit one nonzero higher coefficient. -/
theorem noComplexLevelThreePlane_iff :
    noComplexLevelThreePlane ↔
      ∀ B : Frame, LinearIndependent ℂ B → (∀ i, (B i).IsSymm) →
        FirstOrderVanishes B → HasHigherObstruction B := by
  classical
  constructor
  · intro h B hind hsym hfirst
    by_contra hnone
    exact h ⟨B, hind, hsym, (isLevel_iff_coefficients B).mpr ⟨hfirst, hnone⟩⟩
  · intro h
    rintro ⟨B, hind, hsym, hlevel⟩
    obtain ⟨hfirst, hnone⟩ := (isLevel_iff_coefficients B).mp hlevel
    exact hnone (h B hind hsym hfirst)

/-- The exact open task for the 31 higher coefficients on the tangent space. -/
theorem noComplexLevelThreePlane_iff_tangent :
    noComplexLevelThreePlane ↔
      ∀ B : Frame, LinearIndependent ℂ B → (∀ i, (B i).IsSymm) →
        (∀ i, ∑ r, ∑ c, B i r c = 0) →
        ∃ d ∈ higherIndices, (restrictedPermanent B).coeff d ≠ 0 := by
  simp only [noComplexLevelThreePlane_iff, firstOrderVanishes_iff_entry_sums,
    HasHigherObstruction, mem_higherIndices, and_assoc]

end PvsNP.PermanentLevelTarget
