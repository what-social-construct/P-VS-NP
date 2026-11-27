module

public import HCP.CoupledSignResidual
public import PvsNP.AffineDisclosure
public import PvsNP.AgreementCertificate
public import PvsNP.Compatibility
public import PvsNP.EdgeDiscriminant
public import PvsNP.EdgeStabilizer
public import PvsNP.FiniteSymmetry
public import PvsNP.IncidenceObservations
public import PvsNP.InvariantClosure
public import PvsNP.LevelSetExtension
public import PvsNP.OrbitClosureSeparation
public import PvsNP.OrientationDescent
public import PvsNP.PermanentReadout
public import PvsNP.ReadoutPivotIdeal
public import PvsNP.ReadoutResidual
public import PvsNP.ScalarOrientation
public import PvsNP.TransversePair
public import PvsNP.TransversePairChart
public import PvsNP.TransversePairLevel

@[expose] public section

/-!
The Paper 1 import closure is copied from homotopical-encrypt at revision
e619391ec7d40c5349ebe31846e24461e0b49649 under the accompanying MIT license.
The Paper 3 polynomial agreement sources come from the working tree at
62f20ffd0dc8bf643fe72511dc80c04b8825883f under the same license. See the
source ledger for the files and hashes.
The bridge below uses the original fresh-sign objective and mask equivalence.
-/

namespace PvsNP

set_option autoImplicit false

open HomotopicalEncryption.HCP.CoupledSignResidual
open HomotopicalEncryption.Protocol.Transfer.PathSignature.NativeSignSampler

/-- On a fixed public mask, distinct compatible keys give different messages
while their respective supplied lattices give the same minimum cost. -/
theorem distinct_messages_same_minimum
    {rows cols : ℕ} (A : Matrix (Fin rows) (Fin cols) ℤ) (d a : ℤ)
    (orthogonal : A.transpose * A = d • (1 : Matrix (Fin cols) (Fin cols) ℤ))
    (masked key other : Fin cols → Bool) (different : key ≠ other) :
    mask key masked ≠ mask other masked ∧
      fixedMaskCost A d a key masked (coefficients d (mask key masked)) =
        fixedMaskCost A d a other masked (coefficients d (mask other masked)) := by
  exact ⟨(maskEquiv masked).injective.ne different,
    (cost_at_message A d a orthogonal key masked).trans
      (cost_at_message A d a orthogonal other masked).symm⟩

end PvsNP
