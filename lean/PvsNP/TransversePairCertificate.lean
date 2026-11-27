module

public import PvsNP.TransversePairData

@[expose] public section

namespace PvsNP.TransversePair

/-- Encoding the powers of the six variables as the valuations at six
different primes makes multiplication of monomial keys ordinary multiplication. -/
def primeKey (k : Nat) : Nat :=
  2^(k%10) * 3^(k/10%10) * 5^(k/100%10) *
  7^(k/1000%10) * 11^(k/10000%10) * 13^(k/100000%10)

abbrev Term := Nat × Nat
abbrev Terms := List Term

/-- Merge polynomial rows in monomial order, adding matching coefficients modulo five.
The two structural recursors make reduction of the closed certificate practical in the kernel. -/
noncomputable def merge (p : Terms) : Terms → Terms := p.rec id fun a tail outer q =>
  q.rec (a::tail) fun b rest inner =>
    if a.2 < b.2 then a::outer (b::rest)
    else if b.2 < a.2 then b::inner
    else if (a.1+b.1)%5 == 0 then outer rest else ((a.1+b.1)%5,a.2)::outer rest

/-- Encode input exponents and insert terms into monomial order. -/
noncomputable def norm (p : Terms) : Terms := p.foldr (fun t q => merge [(t.1,primeKey t.2)] q) []

/-- Multiply the polynomial rows using their multiplicative monomial keys. -/
noncomputable def mul : Terms → Terms → Terms
  | [], _ => []
  | (a,k)::p, q => merge (q.map fun (b,j) => ((a*b)%5,k*j)) (mul p q)

/-- Sum the pairwise products of the generator and multiplier rows. -/
noncomputable def certSum : List Terms → List Terms → Terms
  | p::ps,q::qs => merge (mul (norm p) (norm q)) (certSum ps qs)
  | _,_ => []

set_option maxRecDepth 100000 in
set_option maxHeartbeats 4000000 in
/-- The stored multipliers combine the twelve generators to the constant one modulo five. -/
theorem cert_checked : certSum generatorTerms multiplierTerms = [(1,1)] := by decide +kernel

end PvsNP.TransversePair
