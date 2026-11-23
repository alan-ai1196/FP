import Std

namespace TicketBudget

inductive Requirements (unit : Nat) : List Nat → List Nat → Prop where
  | nil : Requirements unit [] []
  | cons {x y : Nat} {xs ys : List Nat} :
      unit + unit ≤ x + y → Requirements unit xs ys →
      Requirements unit (x :: xs) (y :: ys)

/-- Each name is paired with a distinct competitor by the caller; this lemma
    uses the resulting two-name inequalities in common integer units. -/
theorem sum_pair_requirements (unit : Nat) {left right : List Nat}
    (pairs : Requirements unit left right) :
    left.length * unit * 2 ≤ left.sum + right.sum := by
  induction pairs with
  | nil => simp
  | cons bound rest ih =>
    simp only [List.length_cons, List.sum_cons, Nat.succ_mul, Nat.add_mul]
    omega

theorem sum_permutation {xs ys : List Nat} (h : xs.Perm ys) : xs.sum = ys.sum := by
  induction h with
  | nil => rfl
  | cons a h ih => simp [ih]
  | swap a b tail =>
    simp only [List.sum_cons]
    omega
  | trans h₁ h₂ ih₁ ih₂ => exact ih₁.trans ih₂

/-- Pair with a permutation (for example a cycle on at least two names).
    Fixed exploration consumes part of the same single-offer budget. -/
theorem single_offer_budget (unit exploration budget : Nat) {left right : List Nat}
    (pairs : Requirements unit left right)
    (reorder : left.Perm right) (cap : left.sum + exploration ≤ budget) :
    left.length * unit + exploration ≤ budget := by
  have twice := sum_pair_requirements unit pairs
  have equal : left.sum = right.sum := sum_permutation reorder
  omega

#print axioms single_offer_budget

end TicketBudget
