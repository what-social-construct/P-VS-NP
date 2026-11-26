module

public import Proximity.Core.PolynomialAgreement.Boundary
public import Proximity.Core.PolynomialAgreement.Completeness
public import Proximity.Core.PolynomialAgreement.Sharpness
public import PvsNP.AffineDisclosure

@[expose] public section

namespace PvsNP

set_option autoImplicit false

open ProximityCoding ProximityCoding.ReedSolomon
open ProximityCoding.ReedSolomon.Parameters.PairAgreementCertificate

variable {F ι : Type*} [Field F] [Fintype ι]
  (P : Parameters F ι) (w : VectorWord ι F (Fin 2)) (budget degree : ℕ)

/-- Normalized multiplier and response coefficients at one fixed word,
budget, and response degree. -/
abbrev AgreementCoefficientFiber :=
  AffineFiber (coefficientSystem P w budget degree) (fun i => P.domain.point i ^ degree)

/-- Exact certificate existence is the nonemptiness of the normalized fiber. -/
theorem exists_agreementCertificate_iff_nonempty_coefficientFiber [DecidableEq F]
    (degree_pos : 0 < degree) (separates : P.degreeBound + budget ≤ degree) :
    (∃ cert : P.PairAgreementCertificate w,
      cert.degreeBudget = budget ∧ cert.response.natDegree = degree) ↔
      Nonempty (AgreementCoefficientFiber P w budget degree) := by
  refine (exists_certificate_iff_coefficientSystem (P := P) (w := w)
    budget degree degree_pos separates).trans ?_
  exact ⟨fun ⟨x, hx⟩ => ⟨⟨x, hx⟩⟩, fun ⟨x⟩ => ⟨x.val, x.property⟩⟩

/-- The difference between two normalized certificates is a kernel direction. -/
def agreementCoefficientCollisionEquiv :
    (AgreementCoefficientFiber P w budget degree × AgreementCoefficientFiber P w budget degree) ≃
      (AgreementCoefficientFiber P w budget degree ×
        LinearMap.ker (coefficientSystem P w budget degree)) :=
  collisionEquiv (coefficientSystem P w budget degree) (fun i => P.domain.point i ^ degree)

variable {Z : Type*} [AddCommGroup Z] [Module F Z]
  (disclosure : Coefficients F budget degree →ₗ[F] Z)

/-- Pairs of normalized certificates with equal linear disclosures. -/
abbrev AgreementDisclosureCollision :=
  DisclosureCollision (coefficientSystem P w budget degree)
    (fun i => P.domain.point i ^ degree) disclosure

/-- Equal disclosures restrict the difference direction to both kernels. -/
def agreementDisclosureCollisionEquiv :
    AgreementDisclosureCollision P w budget degree disclosure ≃
      (AgreementCoefficientFiber P w budget degree ×
        (LinearMap.ker (coefficientSystem P w budget degree) ⊓ LinearMap.ker disclosure :
          Submodule F (Coefficients F budget degree))) :=
  disclosureCollisionEquiv (coefficientSystem P w budget degree)
    (fun i => P.domain.point i ^ degree) disclosure

/-- Forgetting equality of disclosures commutes with including its kernel
in the full coefficient kernel. -/
theorem agreementDisclosureCollision_square
    (p : AgreementDisclosureCollision P w budget degree disclosure) :
    agreementCoefficientCollisionEquiv P w budget degree p.val =
      ((agreementDisclosureCollisionEquiv P w budget degree disclosure p).1,
        ⟨(agreementDisclosureCollisionEquiv P w budget degree disclosure p).2.val,
          (agreementDisclosureCollisionEquiv P w budget degree disclosure p).2.property.1⟩) :=
  disclosureCollision_square (coefficientSystem P w budget degree)
    (fun i => P.domain.point i ^ degree) disclosure p

/-- The diagonal of the disclosed collision is the zero direction. -/
theorem agreementDisclosureCollisionEquiv_diagonal
    (p : AgreementDisclosureCollision P w budget degree disclosure) :
    (agreementDisclosureCollisionEquiv P w budget degree disclosure p).2 = 0 ↔
      p.val.1 = p.val.2 :=
  disclosureCollisionEquiv_diagonal (coefficientSystem P w budget degree)
    (fun i => P.domain.point i ^ degree) disclosure p

end PvsNP
