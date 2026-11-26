import Std

namespace DelayChannel

/-- Index the leaves of a depth-`n` binary mass tree by their input words. -/
def Word : Nat → Type
  | 0 => Unit
  | n + 1 => Bool × Word n

abbrev Mass (n : Nat) := Word n → Rat

/-- The binary symmetric channel on two signed masses. Its probability
    interpretation uses strengths in [-1,1]. -/
def pairChannel (a x y : Rat) : Rat × Rat :=
  (((1 + a) / 2) * x + ((1 - a) / 2) * y,
   ((1 - a) / 2) * x + ((1 + a) / 2) * y)

theorem pair_inverse (a x y : Rat) (ha : a ≠ 0) :
    pairChannel (1 / a) (pairChannel a x y).1 (pairChannel a x y).2 = (x, y) := by
  apply Prod.ext <;> dsimp [pairChannel] <;> grind [Rat.inv_mul_cancel a ha]

def firstBit {n : Nat} (a : Rat) (v : Mass (n + 1)) : Mass (n + 1) :=
  fun (b, w) =>
    let both := pairChannel a (v (false, w)) (v (true, w))
    if b then both.2 else both.1

theorem firstBit_inverse {n : Nat} (a : Rat) (ha : a ≠ 0) (v : Mass (n + 1)) :
    firstBit (1 / a) (firstBit a v) = v := by
  funext p
  obtain ⟨b, w⟩ := p
  have h := pair_inverse a (v (false, w)) (v (true, w)) ha
  cases b
  · exact congrArg Prod.fst h
  · exact congrArg Prod.snd h

def onChildren {n : Nat} (g : Mass n → Mass n) (v : Mass (n + 1)) : Mass (n + 1) :=
  fun (b, w) => g (fun tail => v (b, tail)) w

/-- Apply the binary channel once on each bit. -/
def blockChannel (a : Rat) : (n : Nat) → Mass n → Mass n
  | 0 => id
  | n + 1 => fun v => firstBit a (onChildren (blockChannel a n) v)

/-- A unit mass on a fixed input word. -/
def pointMass : (n : Nat) → Word n → Mass n
  | 0, _, _ => 1
  | n + 1, (b, u), (c, w) => if b == c then pointMass n u w else 0

/-- Product of the individual probabilities of agreement or disagreement. -/
def blockEntry (a : Rat) : (n : Nat) → Word n → Word n → Rat
  | 0, _, _ => 1
  | n + 1, (b, u), (c, w) =>
    (if b == c then (1 + a) / 2 else (1 - a) / 2) * blockEntry a n u w

private theorem block_zero (a : Rat) (n : Nat) :
    blockChannel a n (fun _ => 0) = (fun _ => 0) := by
  induction n with
  | zero => rfl
  | succ n ih =>
    funext p
    obtain ⟨b, w⟩ := p
    cases b <;> simp [blockChannel, firstBit, onChildren, pairChannel, ih, Rat.zero_add]

theorem block_on_pointMass (a : Rat) (n : Nat) (s t : Word n) :
    blockChannel a n (pointMass n s) t = blockEntry a n s t := by
  induction n with
  | zero => rfl
  | succ n ih =>
    obtain ⟨b, u⟩ := s
    obtain ⟨c, w⟩ := t
    cases b <;> cases c <;>
      simp [blockChannel, firstBit, onChildren, pointMass, blockEntry, pairChannel,
        block_zero, ih, Rat.add_zero, Rat.zero_add]

/-- Reverse the coordinate operations using the signed inverse of each channel. -/
def recover (a : Rat) : (n : Nat) → Mass n → Mass n
  | 0 => id
  | n + 1 => fun v => onChildren (recover a n) (firstBit (1 / a) v)

theorem recover_block (a : Rat) (ha : a ≠ 0) (n : Nat) (v : Mass n) :
    recover a n (blockChannel a n v) = v := by
  induction n with
  | zero => rfl
  | succ n ih =>
    simp only [recover, blockChannel, firstBit_inverse a ha]
    funext p
    obtain ⟨b, w⟩ := p
    exact congrFun (ih (fun tail => v (b, tail))) w

theorem block_injective (a : Rat) (ha : a ≠ 0) (n : Nat) :
    Function.Injective (blockChannel a n) := by
  intro x y h
  have recovered := congrArg (recover a n) h
  simpa only [recover_block a ha] using recovered

#print axioms block_on_pointMass
#print axioms pair_inverse
#print axioms recover_block
#print axioms block_injective

end DelayChannel
