import Std

namespace PairCalibration

/-- An ordered n-bit path with k ones under one coin, denominator 20^n. -/
def component (x n k : Nat) : Nat := x ^ k * (20 - x) ^ (n - k)

/-- Four equiprobable biases (10 ± a)/20, (10 ± b)/20. -/
def numerator (a b n k : Nat) : Nat :=
  component (10 + a) n k + component (10 - a) n k +
  component (10 + b) n k + component (10 - b) n k

theorem through_three :
    ∀ n : Fin 4, ∀ k : Fin (n.val + 1),
      numerator 1 8 n.val k.val = numerator 4 7 n.val k.val := by decide

theorem four_draw_gap :
    ∀ k : Fin 5,
      numerator 1 8 4 k.val + 2880 = numerator 4 7 4 k.val ∨
      numerator 4 7 4 k.val + 2880 = numerator 1 8 4 k.val := by decide

theorem gap_in_probability : 2880 * 2000 = 9 * (4 * 20^4) := by decide

#print axioms through_three
#print axioms four_draw_gap
#print axioms gap_in_probability

end PairCalibration
