import Std

namespace CategoricalMasses

/-- Integer mass of a target label. The first input name has weight one. -/
def mass [DecidableEq α] (y : α) : List α → Nat
  | [] => 0
  | x :: xs => (if x = y then 1 else 0) + 2 * mass y xs

/-- The row of target masses determines the unknown assignment at every input. -/
theorem recover [DecidableEq α] (xs ys : List α)
    (hlen : xs.length = ys.length) (heq : ∀ y, mass y xs = mass y ys) :
    xs = ys := by
  induction xs generalizing ys with
  | nil =>
    cases ys <;> simp_all
  | cons a xs ih =>
    cases ys with
    | nil => simp at hlen
    | cons b ys =>
      have hab : a = b := by
        by_cases h : a = b
        · exact h
        · have hba : b ≠ a := Ne.symm h
          have ha : 1 + 2 * mass a xs = 2 * mass a ys := by
            simpa [mass, hba] using heq a
          omega
      subst b
      have hrest : ∀ y, mass y xs = mass y ys := by
        intro y
        have h := heq y
        simp only [mass] at h
        omega
      exact congrArg (List.cons a) (ih ys (by simpa using hlen) hrest)

end CategoricalMasses
