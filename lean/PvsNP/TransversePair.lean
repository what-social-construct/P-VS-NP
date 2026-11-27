module

public import PvsNP.TransversePairCertificate
public import Mathlib.Data.Nat.Factorization.Defs
public import Mathlib.Data.Fin.VecNotation
public import Mathlib.Algebra.CharP.Basic
public import Mathlib.Algebra.CharP.Lemmas
public import Mathlib.Algebra.BigOperators.Group.Finset.Defs
public import Mathlib.Data.Fintype.BigOperators
import Mathlib.Algebra.BigOperators.Group.List.Lemmas
import Mathlib.Algebra.BigOperators.Group.Finset.Basic
import Mathlib.Algebra.BigOperators.Fin
import Mathlib.Tactic.LinearCombination
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FinCases

@[expose] public section

namespace PvsNP.TransversePair

def decode (p : List (Nat × Nat)) : Terms := p.map fun t => (t.1, primeKey t.2)

def primes : Fin 6 → Nat := ![2,3,5,7,11,13]

/-- A monomial denotes the product of the six coordinates to their encoded powers. -/
noncomputable def monomial {K : Type*} [CommMonoidWithZero K] (x : Fin 6 → K) : Nat →* K where
  toFun k := if k = 0 then 0 else ∏ i, x i ^ (k.factorization (primes i))
  map_one' := by simp
  map_mul' a b := by
    by_cases ha : a = 0
    · simp [ha]
    by_cases hb : b = 0
    · simp [hb]
    simp [ha, hb, Nat.factorization_mul ha hb, pow_add, Finset.prod_mul_distrib]

def eval {K : Type*} [CommRing K] (m : Nat →* K) (p : Terms) : K :=
  (p.map fun t => (t.1 : K) * m t.2).sum

private theorem eval_cons {K : Type*} [CommRing K] (m : Nat →* K)
    (t : Term) (p : Terms) : eval m (t::p) = (t.1 : K)*m t.2 + eval m p := rfl

private theorem eval_merge {K : Type*} [CommRing K] [CharP K 5] (m : Nat →* K)
    (p q : Terms) : eval m (merge p q) = eval m p + eval m q := by
  induction p generalizing q with
  | nil => simp [merge, eval]
  | cons a p ih =>
    induction q with
    | nil => simp [merge, eval]
    | cons b q ihq =>
      change eval m (if a.2 < b.2 then a :: merge p (b :: q) else if b.2 < a.2 then
        b :: merge (a :: p) q else if (a.1 + b.1)%5 == 0 then merge p q
        else ((a.1+b.1)%5,a.2) :: merge p q) = _
      by_cases hab : a.2 < b.2
      · simp [hab, eval_cons, ih, add_assoc]
      by_cases hba : b.2 < a.2
      · simp [hab, hba, eval_cons, ihq, add_assoc, add_comm, add_left_comm]
      rw [ite_eq_right hab, ite_eq_right hba]
      have he : a.2 = b.2 := by omega
      have hc := (CharP.natCast_eq_natCast_mod K 5 (a.1+b.1)).symm
      by_cases hz : (a.1+b.1)%5 = 0
      · simp [hz] at hc
        simp only [hz, beq_self_eq_true, ite_true, ih, eval_cons, he]
        linear_combination m b.2 * hc
      · simp only [beq_iff_eq, hz, ite_false, eval_cons, ih, hc, Nat.cast_add, he]
        ring

private theorem eval_norm {K : Type*} [CommRing K] [CharP K 5] (m : Nat →* K)
    (p : Terms) : eval m (norm p) = eval m (decode p) := by
  induction p with
  | nil => rfl
  | cons a p ih =>
    change eval m (merge [(a.1,primeKey a.2)] (norm p)) = _
    rw [eval_merge, ih]
    simp [eval, decode]

private theorem eval_mul {K : Type*} [CommRing K] [CharP K 5] (m : Nat →* K)
    (p q : Terms) : eval m (mul p q) = eval m p * eval m q := by
  induction p with
  | nil => simp [mul, eval]
  | cons a p ih =>
    obtain ⟨c,k⟩ := a
    have row : eval m (q.map fun (b,j) => ((c*b)%5,k*j)) = (c : K)*m k * eval m q := by
      clear ih
      induction q with
      | nil => simp [eval]
      | cons t q h =>
        obtain ⟨b,j⟩ := t
        simp only [List.map_cons, eval_cons, ← CharP.natCast_eq_natCast_mod K 5,
          Nat.cast_mul, map_mul] at *
        rw [h]
        ring
    change eval m (merge _ (mul p q)) = _
    rw [eval_merge, row, ih, eval_cons, add_mul]

private theorem eval_combination {K : Type*} [CommRing K] [CharP K 5] (m : Nat →* K)
    (ps qs : List Terms) : eval m (certSum ps qs) =
    ((ps.zip qs).map fun (p,q) => eval m (decode p) * eval m (decode q)).sum := by
  induction ps generalizing qs with
  | nil => rfl
  | cons p ps ih =>
    cases qs with
    | nil => rfl
    | cons q qs =>
      rw [certSum, eval_merge, eval_mul, eval_norm, eval_norm, ih]
      rfl

/-- Evaluate the decimal exponents in the generator table directly. -/
def evalTerms {K : Type*} [CommSemiring K] (x : Fin 6 → K)
    (p : List (Nat × Nat)) : K :=
  (p.map fun t => (t.1 : K) * ∏ i : Fin 6, x i ^ (t.2 / 10^i.val % 10)).sum

private theorem monomial_prime {K : Type*} [CommMonoidWithZero K]
    (x : Fin 6 → K) (i : Fin 6) : monomial x (primes i) = x i := by
  have hp : (primes i).Prime := by fin_cases i <;> decide
  have inj (a b : Fin 6) : primes a = primes b ↔ a = b := by
    have h : ∀ a b : Fin 6, primes a = primes b ↔ a = b := by decide
    exact h a b
  simp [monomial, hp.ne_zero, hp.factorization, Finsupp.single_apply, inj,
    apply_ite, Finset.prod_ite_eq]

private theorem eval_decode {K : Type*} [CommRing K] (x : Fin 6 → K)
    (p : List (Nat × Nat)) : eval (monomial x) (decode p) = evalTerms x p := by
  have key (k : Nat) : monomial x (primeKey k) = ∏ i : Fin 6, x i^(k / 10^i.val % 10) := by
    simp only [primeKey, map_mul, map_pow]
    have m0 : monomial x 2 = x 0 := monomial_prime x 0
    have m1 : monomial x 3 = x 1 := monomial_prime x 1
    have m2 : monomial x 5 = x 2 := monomial_prime x 2
    have m3 : monomial x 7 = x 3 := monomial_prime x 3
    have m4 : monomial x 11 = x 4 := monomial_prime x 4
    have m5 : monomial x 13 = x 5 := monomial_prime x 5
    simp [m0, m1, m2, m3, m4, m5, Fin.prod_univ_succ, mul_assoc]
  simp [eval, decode, evalTerms, Function.comp_def, key]


/-- The explicit Bézout identity evaluated at any six coordinates in a
commutative ring of characteristic five. -/
theorem certificate_identity {K : Type*} [CommRing K] [CharP K 5] (x : Fin 6 → K) :
    ((generatorTerms.zip multiplierTerms).map fun (p,q) => evalTerms x p * evalTerms x q).sum = 1 := by
  have h := eval_combination (monomial x) generatorTerms multiplierTerms
  rw [cert_checked] at h
  simp only [eval_decode] at h
  simpa [eval] using h.symm

/-- The twelve coefficient equations exported by the transverse two-column
chart have no common zero in any field of characteristic five. -/
theorem no_common_zero {K : Type*} [Field K] [CharP K 5] (x : Fin 6 → K) :
    ¬ ∀ p ∈ generatorTerms, evalTerms x p = 0 := by
  intro h
  have hz : ((generatorTerms.zip multiplierTerms).map fun (p,q) =>
      evalTerms x p * evalTerms x q).sum = 0 := by
    apply List.sum_eq_zero
    intro z hz
    obtain ⟨⟨p,q⟩, hpq, rfl⟩ := List.mem_map.mp hz
    simp [h p (List.of_mem_zip hpq).1]
  exact (zero_ne_one : (0 : K) ≠ 1) (hz.symm.trans (certificate_identity x))

end PvsNP.TransversePair
