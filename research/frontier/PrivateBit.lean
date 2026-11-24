import Std

namespace PrivateBit

/-- A table writes one with probability a(i)/N. Its increment is at least s on
    each adjacent pair of cues. The lemma also applies to a subinterval. -/
theorem span (a : Nat → Nat) (start s n : Nat)
    (step : ∀ k, k < n → a (start + k) + s ≤ a (start + k + 1)) :
    a start + n * s ≤ a (start + n) := by
  induction n with
  | zero => simp
  | succ n ih =>
    have prev := ih (fun k hk => step k (by omega))
    have last := step n (by omega)
    rw [Nat.add_assoc start n 1] at last
    rw [Nat.succ_mul]
    omega

/-- A finite grid can afford this many uniformly separated messages exactly
    when their adjacent increments fit in the grid. -/
theorem grid_iff (m N s : Nat) :
    (∃ a : Nat → Nat, (∀ i, i ≤ m → a i ≤ N) ∧
       (∀ i, i < m → a i + s ≤ a (i+1))) ↔ m * s ≤ N := by
  constructor
  · rintro ⟨a, cap, step⟩
    have h := span a 0 s m (by simpa using step)
    have endCap := cap m (by omega)
    simp only [Nat.zero_add] at h
    omega
  · intro fits
    refine ⟨fun i => i * s, ?_, ?_⟩
    · intro i hi
      exact Nat.le_trans (Nat.mul_le_mul_right s hi) fits
    · intro i _
      simp [Nat.succ_mul]

/-- Every pair of symmetrically placed code entries lies in the envelope that,
    after averaging, permits the binary garbling in the minimax proof. -/
theorem pair_envelope (a : Nat → Nat) (i j s N : Nat)
    (endCap : a (i+j) ≤ N)
    (step : ∀ k, k < i+j → a k + s ≤ a (k+1)) :
    (i+j)*s ≤ a i + a j ∧ a i + a j + (i+j)*s ≤ 2*N := by
  have loI := span a 0 s i (by
    intro k hk
    simpa using step k (by omega))
  have loJ := span a 0 s j (by
    intro k hk
    simpa using step k (by omega))
  have hiI := span a i s j (by
    intro k hk
    exact step (i+k) (by omega))
  have hiJ := span a j s i (by
    intro k hk
    exact step (j+k) (by omega))
  simp only [Nat.zero_add] at loI loJ
  rw [Nat.add_comm j i] at hiJ
  rw [Nat.add_mul]
  omega

#print axioms span
#print axioms grid_iff
#print axioms pair_envelope

end PrivateBit
