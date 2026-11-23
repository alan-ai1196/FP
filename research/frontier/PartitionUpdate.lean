import Std

namespace PartitionUpdate

/-- The first row has label zero; the three free bits enumerate the eight partitions. -/
def label (p u : Nat) : Bool := if u = 0 then false else p.testBit (u-1)

def eqClass (p i j : Nat) : Nat := if label p i = label p j then 1 else 0

def weight (p : Nat) (cross : Bool) : Nat :=
  let together := if cross then eqClass p 0 2 + eqClass p 1 3
                  else eqClass p 0 1 + eqClass p 2 3
  6 ^ together * 5 ^ (2 - together)

def total (cross : Bool) : Nat := ((List.range 8).map (fun p => weight p cross)).sum
def same (cross : Bool) : Nat :=
  ((List.range 8).map (fun p => eqClass p 0 1 * weight p cross)).sum

/-- Before the new success, the queried rows co-cluster with chances 6/11 and 1/2. -/
theorem co_membership :
    11 * same false = 6 * total false ∧ 2 * same true = total true ∧
    0 < total false ∧ 0 < total true := by decide

/-- Posterior predictive numerator with denominator six times the total weight. -/
def nextNumer (cross : Bool) : Nat := 3 * total cross + same cross

theorem next_forecasts :
    22 * nextNumer false = 13 * (6 * total false) ∧
    12 * nextNumer true = 7 * (6 * total true) ∧
    13 * 12 - 7 * 22 = 2 := by decide

#print axioms co_membership
#print axioms next_forecasts

end PartitionUpdate
