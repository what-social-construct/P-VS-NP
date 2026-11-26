module

public import Mathlib.Algebra.Algebra.Rat
public import Mathlib.Algebra.Group.Action.Prod
public import Mathlib.Data.Matrix.Basic
public import Mathlib.GroupTheory.GroupAction.Defs
public import Mathlib.LinearAlgebra.StdBasis

@[expose] public section

/-!
# Orbit coordinates for invariant matrices

A matrix invariant under simultaneous action on its row and column
indices has one free coefficient per orbit of source–target pairs.
-/

set_option autoImplicit false

namespace HodgeConjecture.OrbitMatrices

variable (G S : Type*) [Group G] [MulAction G S]

/-- Orbits of ordered source–target pairs. -/
abbrev PairOrbits := MulAction.orbitRel.Quotient G (S × S)

/-- The orbit of the pair with source `i` and target `j`. -/
def pairOrbit (i j : S) : PairOrbits G S :=
  Quotient.mk (MulAction.orbitRel G (S × S)) (i, j)

/-- Matrices constant under the simultaneous action on row and column. -/
def InvariantMatrices : Submodule ℚ (Matrix S S ℚ) where
  carrier := {M | ∀ (g : G) (j i : S), M (g • j) (g • i) = M j i}
  zero_mem' := by intro g j i; rfl
  add_mem' := by
    intro A B hA hB g j i
    change A (g • j) (g • i) + B (g • j) (g • i) = A j i + B j i
    rw [hA g j i, hB g j i]
  smul_mem' := by
    intro c A hA g j i
    change c • A (g • j) (g • i) = c • A j i
    rw [hA g j i]

/-- Pullback of orbit coefficients to entries, with targets in the rows
and sources in the columns. -/
def coordinates : (PairOrbits G S → ℚ) ≃ₗ[ℚ] InvariantMatrices G S where
  toFun f := ⟨Matrix.of (fun j i => f (pairOrbit G S i j)), by
    intro g j i
    exact congrArg f (MulAction.orbitRel.Quotient.quotient_smul_eq (g := g) (a := (i, j)))⟩
  invFun M := Quotient.lift (fun p : S × S => (M : Matrix S S ℚ) p.2 p.1) (by
    intro p q hpq
    obtain ⟨g, hg⟩ := MulAction.mem_orbit_iff.mp (MulAction.orbitRel_apply.mp hpq)
    rw [← hg]
    exact M.property g q.2 q.1)
  left_inv f := by
    funext q
    exact Quotient.inductionOn q fun _ => rfl
  right_inv M := by
    apply Subtype.ext
    funext j i
    rfl
  map_add' f h := by
    apply Subtype.ext
    funext j i
    rfl
  map_smul' c f := by
    apply Subtype.ext
    funext j i
    rfl

@[simp]
theorem coordinates_apply (f : PairOrbits G S → ℚ) (j i : S) :
    (coordinates G S f : Matrix S S ℚ) j i = f (pairOrbit G S i j) := rfl

/-- On a finite set, the orbit indicators give a basis of invariant
matrices. -/
noncomputable def orbitBasis [Finite S] : Module.Basis (PairOrbits G S) ℚ (InvariantMatrices G S) := by
  letI := Fintype.ofFinite (PairOrbits G S)
  exact (Pi.basisFun ℚ (PairOrbits G S)).map (coordinates G S)

open Classical in
@[simp]
theorem orbitBasis_apply [Finite S] (q : PairOrbits G S) (j i : S) :
    (orbitBasis G S q : Matrix S S ℚ) j i = if pairOrbit G S i j = q then 1 else 0 := by
  let := Fintype.ofFinite (PairOrbits G S)
  rw [orbitBasis, Module.Basis.map_apply, coordinates_apply, Pi.basisFun_apply]
  simp [Pi.single_apply, eq_comm]

end HodgeConjecture.OrbitMatrices
