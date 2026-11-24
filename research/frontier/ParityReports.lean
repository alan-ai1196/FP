import Std

namespace ParityReports

/-- Integer likelihood weights for positive and negative hidden row parity.
    Each coordinate supplies its two likelihoods after all of its reads. -/
def masses : List (Int × Int) → Int × Int
  | [] => (1, 0)
  | p :: ps =>
    let m := masses ps
    (p.1 * m.1 + p.2 * m.2, p.1 * m.2 + p.2 * m.1)

def totals : List (Int × Int) → Int
  | [] => 1
  | p :: ps => (p.1 + p.2) * totals ps

def differences : List (Int × Int) → Int
  | [] => 1
  | p :: ps => (p.1 - p.2) * differences ps

theorem total (ps : List (Int × Int)) :
    (masses ps).1 + (masses ps).2 = totals ps := by
  induction ps with
  | nil => decide
  | cons p ps ih =>
    simp only [masses, totals]
    rw [← ih, Int.add_mul, Int.mul_add, Int.mul_add]
    omega

theorem gap (ps : List (Int × Int)) :
    (masses ps).1 - (masses ps).2 = differences ps := by
  induction ps with
  | nil => decide
  | cons p ps ih =>
    simp only [masses, differences]
    rw [← ih, Int.sub_mul, Int.mul_sub, Int.mul_sub]
    omega

theorem parity_likelihood (ps : List (Int × Int)) :
    2 * (masses ps).1 = totals ps + differences ps ∧
    2 * (masses ps).2 = totals ps - differences ps := by
  have h := total ps
  have d := gap ps
  omega

/-- One uninformative coordinate erases every distinction between parity laws. -/
theorem missing (pre post : List (Int × Int)) (w : Int) :
    (masses (pre ++ (w,w) :: post)).1 = (masses (pre ++ (w,w) :: post)).2 := by
  have zero : differences (pre ++ (w,w) :: post) = 0 := by
    induction pre with
    | nil => simp [differences]
    | cons p ps ih => simp [differences, ih]
  have h := gap (pre ++ (w,w) :: post)
  omega

#print axioms parity_likelihood
#print axioms missing

end ParityReports
