import PEqualNP.Defs

open PEqualNP.CircuitLowerBounds in
theorem PEqualNP.Outside.R_meta_1990_997
    (oneGenerated : ∀ (x1 : PEqualNP.CircuitLowerBounds.Circuit) (x2 : List ℕ),   PEqualNP.MetaComplexity.Monotone2 x1 →     x2.length = (1 : ℕ) → (∀ w ∈ x2, (26 : ℕ) ≤ w ∧ w < (26 : ℕ) + x1.size) →       (let x5 : Fin (13 : ℕ) → Fin (13 : ℕ) → Prop := fun (x5 x6 : Fin (13 : ℕ)) => (↑x5 + ↑x6) % (13 : ℕ) ∈ [(0 : ℕ), (1 : ℕ), (3 : ℕ), (9 : ℕ)];         have x6 : Finset (Fin (13 : ℕ)) → Finset (Fin (13 : ℕ)) → Fin (26 : ℕ) → Bool := fun (x6 x7 : Finset (Fin (13 : ℕ))) (x8 : Fin (26 : ℕ)) => if ↑x8 < (13 : ℕ) then Decidable.decide (Fin.ofNat (13 : ℕ) ↑x8 ∈ x6) else Decidable.decide (Fin.ofNat (13 : ℕ) ↑x8 ∈ x7);         have x7 : Finset (Fin (13 : ℕ)) → Finset (Fin (13 : ℕ)) := fun (x7 : Finset (Fin (13 : ℕ))) => {x8 : Fin (13 : ℕ) | ∀ x9 ∈ x7, ¬x5 x9 x8};         have x8 : Finset (Fin (13 : ℕ)) → Finset (Fin (13 : ℕ)) → Bool := fun (x8 x9 : Finset (Fin (13 : ℕ))) => PEqualNP.CircuitLowerBounds.GateOp.or.eval (List.map (fun (x10 : ℕ) => (x1.wires (List.ofFn (x6 x8 x9))).getD x10 Bool.false) x2);         (∀ (x9 x10 : Fin (13 : ℕ)), x5 x9 x10 → x8 {x9} {x10} = Bool.true) ∧ ∀ (x9 : Finset (Fin (13 : ℕ))), x9.card ≤ (3 : ℕ) → x8 x9 (x7 x9) = Bool.false ∧ x8 (x7 x9) x9 = Bool.false) →         (PEqualNP.MetaComplexity.NestedCover.gateAt x1 (x1.size - (1 : ℕ))).op = PEqualNP.CircuitLowerBounds.GateOp.and → (63 : ℕ) ≤ x1.size)
    (twoGenerated : ∀ (x1 : PEqualNP.CircuitLowerBounds.Circuit) (x2 : List ℕ),   PEqualNP.MetaComplexity.Monotone2 x1 →     x2.length = (2 : ℕ) → x2.Nodup → (∀ w ∈ x2, (26 : ℕ) ≤ w ∧ w < (26 : ℕ) + x1.size) →       (let x5 : Fin (13 : ℕ) → Fin (13 : ℕ) → Prop := fun (x5 x6 : Fin (13 : ℕ)) => (↑x5 + ↑x6) % (13 : ℕ) ∈ [(0 : ℕ), (1 : ℕ), (3 : ℕ), (9 : ℕ)];         have x6 : Finset (Fin (13 : ℕ)) → Finset (Fin (13 : ℕ)) → Fin (26 : ℕ) → Bool := fun (x6 x7 : Finset (Fin (13 : ℕ))) (x8 : Fin (26 : ℕ)) => if ↑x8 < (13 : ℕ) then Decidable.decide (Fin.ofNat (13 : ℕ) ↑x8 ∈ x6) else Decidable.decide (Fin.ofNat (13 : ℕ) ↑x8 ∈ x7);         have x7 : Finset (Fin (13 : ℕ)) → Finset (Fin (13 : ℕ)) := fun (x7 : Finset (Fin (13 : ℕ))) => {x8 : Fin (13 : ℕ) | ∀ x9 ∈ x7, ¬x5 x9 x8};         have x8 : Finset (Fin (13 : ℕ)) → Finset (Fin (13 : ℕ)) → Bool := fun (x8 x9 : Finset (Fin (13 : ℕ))) => PEqualNP.CircuitLowerBounds.GateOp.or.eval (List.map (fun (x10 : ℕ) => (x1.wires (List.ofFn (x6 x8 x9))).getD x10 Bool.false) x2);         (∀ (x9 x10 : Fin (13 : ℕ)), x5 x9 x10 → x8 {x9} {x10} = Bool.true) ∧ ∀ (x9 : Finset (Fin (13 : ℕ))), x9.card ≤ (3 : ℕ) → x8 x9 (x7 x9) = Bool.false ∧ x8 (x7 x9) x9 = Bool.false) →         (PEqualNP.MetaComplexity.NestedCover.gateAt x1 (x1.size - (1 : ℕ))).op = PEqualNP.CircuitLowerBounds.GateOp.and → (63 : ℕ) ≤ x1.size)
    (lastOr : ∀ (x1 : PEqualNP.CircuitLowerBounds.Circuit) (x2 : List ℕ),   PEqualNP.MetaComplexity.Monotone2 x1 →     x2.length ≤ (2 : ℕ) → 1 ≤ x2.length → x2.Nodup → (∀ w ∈ x2, (26 : ℕ) ≤ w ∧ w < (26 : ℕ) + x1.size) → (26 : ℕ) + x1.size - 1 ∈ x2 →       (let x5 : Fin (13 : ℕ) → Fin (13 : ℕ) → Prop := fun (x5 x6 : Fin (13 : ℕ)) => (↑x5 + ↑x6) % (13 : ℕ) ∈ [(0 : ℕ), (1 : ℕ), (3 : ℕ), (9 : ℕ)];         have x6 : Finset (Fin (13 : ℕ)) → Finset (Fin (13 : ℕ)) → Fin (26 : ℕ) → Bool := fun (x6 x7 : Finset (Fin (13 : ℕ))) (x8 : Fin (26 : ℕ)) => if ↑x8 < (13 : ℕ) then Decidable.decide (Fin.ofNat (13 : ℕ) ↑x8 ∈ x6) else Decidable.decide (Fin.ofNat (13 : ℕ) ↑x8 ∈ x7);         have x7 : Finset (Fin (13 : ℕ)) → Finset (Fin (13 : ℕ)) := fun (x7 : Finset (Fin (13 : ℕ))) => {x8 : Fin (13 : ℕ) | ∀ x9 ∈ x7, ¬x5 x9 x8};         have x8 : Finset (Fin (13 : ℕ)) → Finset (Fin (13 : ℕ)) → Bool := fun (x8 x9 : Finset (Fin (13 : ℕ))) => PEqualNP.CircuitLowerBounds.GateOp.or.eval (List.map (fun (x10 : ℕ) => (x1.wires (List.ofFn (x6 x8 x9))).getD x10 Bool.false) x2);         (∀ (x9 x10 : Fin (13 : ℕ)), x5 x9 x10 → x8 {x9} {x10} = Bool.true) ∧ ∀ (x9 : Finset (Fin (13 : ℕ))), x9.card ≤ (3 : ℕ) → x8 x9 (x7 x9) = Bool.false ∧ x8 (x7 x9) x9 = Bool.false) →         (PEqualNP.MetaComplexity.NestedCover.gateAt x1 (x1.size - (1 : ℕ))).op = PEqualNP.CircuitLowerBounds.GateOp.or → (63 : ℕ) ≤ x1.size) :
    ∀ (x1 : PEqualNP.CircuitLowerBounds.Circuit) (x2 : List ℕ),   PEqualNP.MetaComplexity.Monotone2 x1 →     x2.length ≤ (2 : ℕ) →       (let x5 : Fin (13 : ℕ) → Fin (13 : ℕ) → Prop := fun (x5 x6 : Fin (13 : ℕ)) => (↑x5 + ↑x6) % (13 : ℕ) ∈ [(0 : ℕ), (1 : ℕ), (3 : ℕ), (9 : ℕ)];         have x6 : Finset (Fin (13 : ℕ)) → Finset (Fin (13 : ℕ)) → Fin (26 : ℕ) → Bool := fun (x6 x7 : Finset (Fin (13 : ℕ))) (x8 : Fin (26 : ℕ)) => if ↑x8 < (13 : ℕ) then Decidable.decide (Fin.ofNat (13 : ℕ) ↑x8 ∈ x6) else Decidable.decide (Fin.ofNat (13 : ℕ) ↑x8 ∈ x7);         have x7 : Finset (Fin (13 : ℕ)) → Finset (Fin (13 : ℕ)) := fun (x7 : Finset (Fin (13 : ℕ))) => {x8 : Fin (13 : ℕ) | ∀ x9 ∈ x7, ¬x5 x9 x8};         have x8 : Finset (Fin (13 : ℕ)) → Finset (Fin (13 : ℕ)) → Bool := fun (x8 x9 : Finset (Fin (13 : ℕ))) => PEqualNP.CircuitLowerBounds.GateOp.or.eval (List.map (fun (x10 : ℕ) => (x1.wires (List.ofFn (x6 x8 x9))).getD x10 Bool.false) x2);         (∀ (x9 x10 : Fin (13 : ℕ)), x5 x9 x10 → x8 {x9} {x10} = Bool.true) ∧ ∀ (x9 : Finset (Fin (13 : ℕ))), x9.card ≤ (3 : ℕ) → x8 x9 (x7 x9) = Bool.false ∧ x8 (x7 x9) x9 = Bool.false) →         (63 : ℕ) ≤ x1.size := by
  intro C outputs hmon hlength hspec
  let edge (p l : Fin 13) : Prop := (p.val + l.val) % 13 ∈ ([0, 1, 3, 9] : List ℕ)
  let input (P L : Finset (Fin 13)) (i : Fin 26) : Bool :=
    if i.val < 13 then decide (Fin.ofNat 13 i.val ∈ P)
    else decide (Fin.ofNat 13 i.val ∈ L)
  let avoid (P : Finset (Fin 13)) : Finset (Fin 13) := {l | ∀ p ∈ P, ¬ edge p l}
  let wire (P L : Finset (Fin 13)) (i : ℕ) : Bool :=
    (C.wires (List.ofFn (input P L))).getD i false
  let scan (rs : List ℕ) (P L : Finset (Fin 13)) : Bool :=
    (rs.map (wire P L)).any id
  have hs : (∀ (p l : Fin 13), edge p l → scan outputs {p} {l} = true) ∧
      ∀ P : Finset (Fin 13), P.card ≤ 3 →
        scan outputs P (avoid P) = false ∧ scan outputs (avoid P) P = false := hspec
  let appendGate (ws : List Bool) (g : Gate) : List Bool :=
    ws ++ [g.op.eval (g.inputs.map fun i => ws.getD i false)]
  have preserveInputs : ∀ (gs : List Gate) (ws : List Bool) (i : ℕ), i < ws.length →
      (gs.foldl appendGate ws).getD i false = ws.getD i false := by
    intro gs
    induction gs with
    | nil => intros; rfl
    | cons g gs ih =>
      intro ws i hi
      rw [List.foldl_cons, ih]
      · exact List.getD_append _ _ _ _ hi
      · simp [appendGate]; omega
  have wire_length : ∀ (gs : List Gate) (ws : List Bool),
      (gs.foldl appendGate ws).length = ws.length + gs.length := by
    intro gs
    induction gs with
    | nil => intros; simp
    | cons g gs ih =>
      intro ws
      rw [List.foldl_cons, ih]
      simp [appendGate]
      omega
  have primary (P L : Finset (Fin 13)) (i : ℕ) (hi : i < 26) :
      wire P L i = input P L ⟨i, hi⟩ := by
    change (C.gates.foldl appendGate (List.ofFn (input P L))).getD i false = _
    rw [preserveInputs _ _ _ (by simpa using hi)]
    rw [List.getD_eq_getElem _ _ (by simpa only [List.length_ofFn] using hi)]
    simp only [List.getElem_ofFn]
  have missing (P L : Finset (Fin 13)) (i : ℕ) (hi : 26 + C.size ≤ i) :
      wire P L i = false := by
    change (C.gates.foldl appendGate (List.ofFn (input P L))).getD i false = false
    apply List.getD_eq_default
    change 26 + C.gates.length ≤ i at hi
    simpa only [wire_length, List.length_ofFn] using hi
  have scan_true (rs : List ℕ) (P L : Finset (Fin 13)) :
      scan rs P L = true ↔ ∃ i ∈ rs, wire P L i = true := by
    simp [scan, List.any_eq_true]
  have zerorows : scan outputs ∅ Finset.univ = false ∧
      scan outputs Finset.univ ∅ = false := by
    simpa [avoid] using hs.2 ∅ (by simp)
  have nonprimary (i : ℕ) (hi : i ∈ outputs) : 26 ≤ i := by
    by_contra h
    have hi26 : i < 26 := Nat.lt_of_not_ge h
    by_cases hp : i < 13
    · have ht : wire Finset.univ ∅ i = true := by
        rw [primary _ _ _ hi26]
        simp [input, hp]
      have hv := (scan_true _ _ _).2 ⟨i, hi, ht⟩
      exact Bool.false_ne_true (zerorows.2.symm.trans hv)
    · have ht : wire ∅ Finset.univ i = true := by
        rw [primary _ _ _ hi26]
        simp [input, hp]
      have hv := (scan_true _ _ _).2 ⟨i, hi, ht⟩
      exact Bool.false_ne_true (zerorows.1.symm.trans hv)
  let filtered := outputs.filter fun i => decide (i < 26 + C.size)
  let selected := filtered.dedup
  have mem_selected (i : ℕ) : i ∈ selected ↔ i ∈ outputs ∧ i < 26 + C.size := by
    simp [selected, filtered]
  have valid (i : ℕ) (hi : i ∈ selected) : 26 ≤ i ∧ i < 26 + C.size := by
    obtain ⟨hm, hv⟩ := (mem_selected i).1 hi
    exact ⟨nonprimary i hm, hv⟩
  have replay (P L : Finset (Fin 13)) : scan selected P L = scan outputs P L := by
    apply Bool.eq_iff_iff.2
    rw [scan_true, scan_true]
    constructor
    · rintro ⟨i, hi, hv⟩
      exact ⟨i, ((mem_selected i).1 hi).1, hv⟩
    · rintro ⟨i, hi, hv⟩
      have hirange : i < 26 + C.size := by
        by_contra h
        exact Bool.false_ne_true ((missing P L i (Nat.le_of_not_gt h)).symm.trans hv)
      exact ⟨i, (mem_selected i).2 ⟨hi, hirange⟩, hv⟩
  have normalized_spec : (∀ (p l : Fin 13), edge p l → scan selected {p} {l} = true) ∧
      ∀ P : Finset (Fin 13), P.card ≤ 3 →
        scan selected P (avoid P) = false ∧ scan selected (avoid P) P = false := by
    constructor
    · intro p l he
      rw [replay]
      exact hs.1 p l he
    · intro P hP
      simp only [replay]
      exact hs.2 P hP
  have hcap : selected.length ≤ 2 :=
    (List.dedup_sublist filtered).length_le.trans ((List.length_filter_le _ _).trans hlength)
  have hnonempty : 1 ≤ selected.length := by
    obtain ⟨i, hi, _⟩ := (scan_true selected _ _).1 (normalized_spec.1 0 0 (by decide))
    exact List.length_pos_of_mem hi
  have selected_nonempty : selected.toFinset.Nonempty := by
    obtain ⟨i, hi, _⟩ := (scan_true selected _ _).1 (normalized_spec.1 0 0 (by decide))
    exact ⟨i, List.mem_toFinset.mpr hi⟩
  let latest := selected.toFinset.max' selected_nonempty
  have latest_mem : latest ∈ selected :=
    List.mem_toFinset.mp (Finset.max'_mem _ _)
  have le_latest (i : ℕ) (hi : i ∈ selected) : i ≤ latest :=
    Finset.le_max' _ _ (List.mem_toFinset.mpr hi)
  obtain ⟨latest_lower, latest_upper⟩ := valid latest latest_mem
  let count := latest + 1 - 26
  let D : Circuit := ⟨C.gates.take count, C.output⟩
  have count_le : count ≤ C.size := by
    dsimp [count]
    omega
  have hDsize : D.size = count := by
    change (C.gates.take count).length = count
    rw [List.length_take, min_eq_left (show count ≤ C.gates.length from count_le)]
  have hDle : D.size ≤ C.size := hDsize.trans_le count_le
  have hend : 26 + D.size = latest + 1 := by
    rw [hDsize]
    dsimp [count]
    omega
  have hDlast : 26 + D.size - 1 ∈ selected := by
    have hindex : 26 + D.size - 1 = latest := by omega
    rwa [hindex]
  have hDmono : PEqualNP.MetaComplexity.Monotone2 D := by
    intro g hg
    exact hmon g (List.mem_of_mem_take hg)
  have hDvalid (i : ℕ) (hi : i ∈ selected) : 26 ≤ i ∧ i < 26 + D.size := by
    refine ⟨(valid i hi).1, ?_⟩
    rw [hend]
    exact Nat.lt_succ_of_le (le_latest i hi)
  have preserve_selected (P L : Finset (Fin 13)) (i : ℕ) (hi : i ∈ selected) :
      (D.wires (List.ofFn (input P L))).getD i false = wire P L i := by
    let ws := List.ofFn (input P L)
    have hprefix : i < (D.gates.foldl appendGate ws).length := by
      rw [wire_length, show ws.length = 26 from List.length_ofFn]
      exact (hDvalid i hi).2
    have hsplit : D.gates ++ C.gates.drop count = C.gates := List.take_append_drop _ _
    change (D.gates.foldl appendGate ws).getD i false =
      (C.gates.foldl appendGate ws).getD i false
    calc
      _ = ((D.gates ++ C.gates.drop count).foldl appendGate ws).getD i false := by
        rw [List.foldl_append, preserveInputs _ _ _ hprefix]
      _ = _ := by rw [hsplit]
  let scanD (P L : Finset (Fin 13)) : Bool :=
    (selected.map (fun i => (D.wires (List.ofFn (input P L))).getD i false)).any id
  have scanD_eq (P L : Finset (Fin 13)) : scanD P L = scan selected P L := by
    unfold scanD scan
    congr 1
    apply List.map_congr_left
    exact preserve_selected P L
  have specD : (∀ (p l : Fin 13), edge p l → scanD {p} {l} = true) ∧
      ∀ P : Finset (Fin 13), P.card ≤ 3 →
        scanD P (avoid P) = false ∧ scanD (avoid P) P = false := by
    simp only [scanD_eq]
    exact normalized_spec
  have hDindex : D.size - 1 < D.gates.length := by
    change D.size - 1 < D.size
    omega
  have hDgate : PEqualNP.MetaComplexity.NestedCover.gateAt D (D.size - 1) =
      D.gates[D.size - 1] := List.getD_eq_getElem _ _ hDindex
  have hDop :
      (PEqualNP.MetaComplexity.NestedCover.gateAt D (D.size - 1)).op = GateOp.and ∨
      (PEqualNP.MetaComplexity.NestedCover.gateAt D (D.size - 1)).op = GateOp.or := by
    rw [hDgate]
    exact (hDmono _ (List.getElem_mem hDindex)).1
  refine Nat.le_trans ?_ hDle
  rcases hDop with hand | hor
  · by_cases hsingle : selected.length = 1
    · exact oneGenerated D selected hDmono hsingle hDvalid specD hand
    · exact twoGenerated D selected hDmono (by omega) (List.nodup_dedup _) hDvalid specD hand
  · exact lastOr D selected hDmono hcap hnonempty (List.nodup_dedup _)
      hDvalid hDlast specD hor
