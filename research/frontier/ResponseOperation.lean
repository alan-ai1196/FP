import Std

namespace ResponseOperation

/-- Positions 0,1,2,3 represent the outputs for 00,01,10,11. -/
abbrev Gate := Fin 16

def evalGate (g : Gate) (a b : Bool) : Bool :=
  g.val.testBit (2 * a.toNat + b.toNat)

def usesBoth (g : Gate) : Prop :=
  (∃ b : Bool, evalGate g false b ≠ evalGate g true b) ∧
  (∃ a : Bool, evalGate g a false ≠ evalGate g a true)

instance (g : Gate) : Decidable (usesBoth g) := by unfold usesBoth; infer_instance

/-- Applying g to two rows must respect their additional h-observation. -/
def commutes (g h : Gate) : Prop :=
  ∀ a b c e : Bool, evalGate g (evalGate h a b) (evalGate h c e) =
    evalGate h (evalGate g a c) (evalGate g b e)

instance (g h : Gate) : Decidable (commutes g h) := by unfold commutes; infer_instance

theorem xor_truth_table : ∀ a b : Bool, evalGate 6 a b = (a ^^ b) := by decide
theorem or_truth_table : ∀ a b : Bool, evalGate 14 a b = (a || b) := by decide

theorem xor_essential : ∀ g : Gate, (commutes g 6 ∧ usesBoth g) ↔ g = 6 := by decide
theorem or_essential : ∀ g : Gate, (commutes g 14 ∧ usesBoth g) ↔ g = 14 := by decide

/-- Each row has arbitrary d pilot bits and one additional bit h(row i,row j).
    The coordinatewise g of any two rows must again have this form. -/
def closed {d : Nat} (g h : Gate) (i j : Fin d) : Prop :=
  ∀ x y : Fin d → Bool,
    evalGate g (evalGate h (x i) (x j)) (evalGate h (y i) (y j)) =
      evalGate h (evalGate g (x i) (y i)) (evalGate g (x j) (y j))

theorem graph_test_iff {d : Nat} (g h : Gate) (i j : Fin d) (ne : i ≠ j) :
    closed g h i j ↔ commutes g h := by
  constructor
  · intro hc a b c e
    let x : Fin d → Bool := fun k => if k = i then a else b
    let y : Fin d → Bool := fun k => if k = i then c else e
    simpa [x, y, Ne.symm ne] using hc x y
  · intro hc x y
    exact hc (x i) (x j) (y i) (y j)

theorem unique_on_xor_rows {d : Nat} (g : Gate) (i j : Fin d) (ne : i ≠ j) :
    (closed g 6 i j ∧ usesBoth g) ↔ g = 6 := by
  rw [graph_test_iff g 6 i j ne]
  exact xor_essential g

theorem unique_on_or_rows {d : Nat} (g : Gate) (i j : Fin d) (ne : i ≠ j) :
    (closed g 14 i j ∧ usesBoth g) ↔ g = 14 := by
  rw [graph_test_iff g 14 i j ne]
  exact or_essential g

#print axioms xor_truth_table
#print axioms or_truth_table
#print axioms unique_on_xor_rows
#print axioms unique_on_or_rows

end ResponseOperation
