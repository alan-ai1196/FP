import Std

namespace PredictiveMixture

/-- Two selected-token masses in a common denominator. The mixture may vary by event. -/
structure Row where
  left : Nat
  right : Nat
  weight : Nat
  grid : Nat
  feasible : weight ≤ grid

def measured (r : Row) : Nat :=
  (r.grid - r.weight) * r.left + r.weight * r.right

def envelope (r : Row) : Nat := r.grid * max r.left r.right

theorem measured_le_envelope (r : Row) : measured r ≤ envelope r := by
  unfold measured envelope
  calc
    _ ≤ (r.grid - r.weight) * max r.left r.right + r.weight * max r.left r.right :=
      Nat.add_le_add (Nat.mul_le_mul_left _ (Nat.le_max_left ..))
        (Nat.mul_le_mul_left _ (Nat.le_max_right ..))
    _ = _ := by rw [← Nat.add_mul, Nat.sub_add_cancel r.feasible]

/-- Multiplying probabilities preserves the bound after clearing each row's denominator. -/
theorem any_trajectory (rows : List Row) :
    (rows.map measured).prod ≤ (rows.map envelope).prod := by
  induction rows with
  | nil => simp
  | cons row rest ih =>
    simpa only [List.map_cons, List.prod_cons] using
      Nat.mul_le_mul (measured_le_envelope row) ih

#print axioms measured_le_envelope
#print axioms any_trajectory

end PredictiveMixture
