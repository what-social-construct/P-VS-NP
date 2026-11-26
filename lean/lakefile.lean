import Lake
open Lake DSL

package PvsNP

require mathlib from git
  "https://github.com/leanprover-community/mathlib4" @ "56a005855ea17e0b0958f73ec801ae140b0a1679"

@[default_target]
lean_lib PvsNP where
  roots := #[`PvsNP, `Axioms, `CVP, `HCP, `Hardness, `Helfer, `Laplacian,
    `Protocol, `Sheaf, `TCB]
  globs := #[.one `PvsNP, .submodules `Axioms, .one `CVP,
    .andSubmodules `HCP, .one `Hardness, .andSubmodules `Helfer,
    .submodules `Laplacian, .submodules `Protocol, .submodules `Sheaf, .submodules `TCB]
