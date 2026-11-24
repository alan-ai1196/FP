import Std

namespace GroupedReset

/-- The two mixture rows have common weight denominator 60, coin denominator 8. -/
def leftWeight (e : Bool) : Nat := if e then 28 else 35
def leftCoin (e : Bool) : Nat := if e then 4 else 1
def likelihood (coin : Nat) (bit : Bool) : Nat := if bit then coin else 8 - coin

def initial (e bit : Bool) : Nat :=
  leftWeight e * likelihood (leftCoin e) bit +
  (60 - leftWeight e) * likelihood 7 bit

def sameCoin (e x y : Bool) : Nat :=
  leftWeight e * likelihood (leftCoin e) x * likelihood (leftCoin e) y +
  (60 - leftWeight e) * likelihood 7 x * likelihood 7 y

theorem new_coin_means :
    16 * initial false true = 7 * 480 ∧ 10 * initial true true = 7 * 480 := by decide

theorem continuing_after_one :
    ∀ e : Bool, 4 * sameCoin e true true = 3 * 8 * initial e true := by decide

theorem continuing_after_zero :
    36 * sameCoin false false true = 7 * 8 * initial false false ∧
    12 * sameCoin true false true = 7 * 8 * initial true false := by decide

/-- A strictly positive binary channel produces the reset observation from
    the kept observation after zero in both environments. -/
theorem garbling_after_zero :
    0 < 49 ∧ 49 < 157 ∧ 157 < 160 ∧
    ∀ e : Bool, 160 * 8 * initial e false * initial e true =
      480 * (49 * 8 * initial e false + (157 - 49) * sameCoin e false true) := by decide

#print axioms new_coin_means
#print axioms continuing_after_one
#print axioms continuing_after_zero
#print axioms garbling_after_zero

end GroupedReset
