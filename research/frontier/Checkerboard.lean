import Std

namespace Checkerboard

def miss (forecast target : Rat) : Nat := if forecast = target then 0 else 1

/-- One pair of opposite-bit rows and one pair of opposite-bit columns. -/
def block (a : Rat) (r c : Rat × Rat) : Nat :=
  miss (r.1 + c.1) a + miss (r.1 + c.2) (-a)
    + miss (r.2 + c.1) (-a) + miss (r.2 + c.2) a

theorem block_lower {a : Rat} (ha : 0 < a) (r c : Rat × Rat) : 1 ≤ block a r c := by
  unfold block miss
  split <;> split <;> split <;> split <;> grind

def rowMiss (a : Rat) (r : Rat × Rat) (cols : List (Rat × Rat)) : Nat :=
  (cols.map (block a r)).sum

theorem row_lower {a : Rat} (ha : 0 < a) (r : Rat × Rat) (cols : List (Rat × Rat)) :
    cols.length ≤ rowMiss a r cols := by
  induction cols with
  | nil => simp [rowMiss]
  | cons c cs ih =>
    have h := block_lower ha r c
    simp only [rowMiss, List.map_cons, List.sum_cons, List.length_cons] at ih ⊢
    omega

def misses (a : Rat) (rows cols : List (Rat × Rat)) : Nat :=
  (rows.map (fun r => rowMiss a r cols)).sum

theorem grid_lower {a : Rat} (ha : 0 < a) (rows cols : List (Rat × Rat)) :
    rows.length * cols.length ≤ misses a rows cols := by
  induction rows with
  | nil => simp [misses]
  | cons r rs ih =>
    have h := row_lower ha r cols
    simp only [misses, List.map_cons, List.sum_cons, List.length_cons, Nat.succ_mul] at ih ⊢
    omega

theorem template_attains {a : Rat} (ha : 0 < a) :
    block a (0,-(a+a)) (a,-a) = 1 := by
  unfold block miss
  split <;> split <;> split <;> split <;> grind

theorem grid_attains {a : Rat} (ha : 0 < a) (n m : Nat) :
    misses a (List.replicate n (0,-(a+a))) (List.replicate m (a,-a)) = n*m := by
  simp [misses, rowMiss, List.map_replicate, template_attains ha, List.sum_replicate_nat]

#print axioms grid_lower
#print axioms grid_attains

end Checkerboard
