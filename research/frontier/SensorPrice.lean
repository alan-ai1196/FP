import Std

namespace SensorPrice

/-- Counts among the eight raw three-bit words at a fixed final bit and query. -/
def count (mask j : Nat) (state route : Bool) : Nat :=
  ((List.range 8).filter (fun x => mask.testBit x == state && x.testBit j == route)).length

def cell (mask j ticks : Nat) (state : Bool) : Nat :=
  let a := count mask j state false
  let b := count mask j state true
  8 * max a b - ticks * (a+b)

def gain (mask ticks : Nat) : Nat :=
  ((List.range 3).map (fun j => cell mask j ticks false + cell mask j ticks true)).sum

set_option maxRecDepth 16384
set_option maxHeartbeats 10000000

/-- The finite upper certificates use units of 1/192 of sensor advantage. -/
theorem price_corners : ∀ m : Fin 256,
    gain m.val 0 ≤ 144 ∧ gain m.val 4 ≤ 48 ∧ gain m.val 5 ≤ 24 ∧ gain m.val 8 = 0 := by
  decide +kernel

theorem majority_corners :
    gain 232 0 = 144 ∧ gain 232 4 = 48 ∧ gain 232 5 = 24 := by decide

theorem coordinate_corners :
    gain 170 5 = 24 ∧ gain 170 8 = 0 := by decide

#print axioms price_corners

end SensorPrice
