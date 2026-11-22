import Std

namespace HammingSeven

/-- A bit at position `i` selects coordinate `i` of a seven-coordinate parity probe.
    The least significant bit is coordinate 0. -/
abbrev Mask := Fin 128

/-- The parity of the selected coordinates of `word`, i.e. the binary dot product. -/
def parityProbe (selected word : Mask) : Bool :=
  (List.range 7).foldl (fun parity i =>
    parity.xor (selected.val.testBit i && word.val.testBit i)) false

/-- Each column of the parity-check matrix is the three-bit representation of `i + 1`.
    The three row masks below read the low, middle, and high bit respectively. -/
def syndrome (word : Mask) : Nat :=
  (parityProbe 0b1010101 word).toNat +
    2 * (parityProbe 0b1100110 word).toNat +
    4 * (parityProbe 0b1111000 word).toNat

def hammingDistance (a b : Mask) : Nat :=
  ((List.range 7).filter (fun i => a.val.testBit i != b.val.testBit i)).length

/-- The code contains exactly the masks on which all three checks have even parity. -/
def codewords : List Mask :=
  (List.finRange 128).filter (fun w => syndrome w == 0)

theorem mem_codewords (w : Mask) : w ∈ codewords ↔ syndrome w = 0 := by
  simp [codewords, List.mem_finRange]

/-- A nonzero syndrome `i + 1` identifies the coordinate to flip. -/
def decode (query : Mask) : Mask :=
  match syndrome query with
  | 0 => query
  | i + 1 => Fin.ofNat 128 (query.val ^^^ (2 ^ i))

set_option maxRecDepth 4096

theorem codewords_cardinality : codewords.length = 16 ∧ codewords.Nodup := by
  decide

theorem decode_valid : ∀ q : Mask,
    syndrome (decode q) = 0 ∧ hammingDistance q (decode q) ≤ 1 := by
  decide

theorem decode_unique : ∀ c : Mask, syndrome c = 0 →
    ∀ q : Mask, hammingDistance q c ≤ 1 → c = decode q := by
  decide

/-- For each of the 128 parity-probe masks, exactly one code mask agrees at all
    but at most one coordinate. The witness is the single-syndrome decoder. -/
theorem unique_codeword_within_one (q : Mask) :
    ∃ c : Mask, c ∈ codewords ∧ hammingDistance q c ≤ 1 ∧
      ∀ d : Mask, d ∈ codewords → hammingDistance q d ≤ 1 → d = c := by
  obtain ⟨hc, hd⟩ := decode_valid q
  exact ⟨decode q, (mem_codewords _).2 hc, hd,
    fun d hmem hdist => decode_unique d ((mem_codewords d).1 hmem) q hdist⟩

/-- The independent data coordinates are bits 2, 4, 5 and 6 (numbered from zero).
    Each of these bits selects one of the four generator masks 7, 25, 42 and 75. -/
def generatorSum (c : Mask) : Nat :=
  (if c.val.testBit 2 then 7 else 0) ^^^ (if c.val.testBit 4 then 25 else 0) ^^^
  (if c.val.testBit 5 then 42 else 0) ^^^ (if c.val.testBit 6 then 75 else 0)

theorem systematic_basis : ∀ c : Mask, syndrome c = 0 ↔ generatorSum c = c.val := by
  decide

theorem minimum_distance_three :
    (∀ a : Mask, syndrome a = 0 → ∀ b : Mask, syndrome b = 0 → a ≠ b →
      3 ≤ hammingDistance a b) ∧
    (syndrome 0 = 0 ∧ syndrome 7 = 0 ∧ hammingDistance 0 7 = 3) := by
  decide

structure BasisParities where
  p7 : Bool
  p25 : Bool
  p42 : Bool
  p75 : Bool

/-- These four parity bits are stored once for the hidden vector `x`. -/
def cache (x : Mask) : BasisParities :=
  ⟨parityProbe 7 x, parityProbe 25 x, parityProbe 42 x, parityProbe 75 x⟩

def combine (c : Mask) (stored : BasisParities) : Bool :=
  (c.val.testBit 2 && stored.p7) ^^ (c.val.testBit 4 && stored.p25) ^^
  (c.val.testBit 5 && stored.p42) ^^ (c.val.testBit 6 && stored.p75)

/-- The query is public. An answer uses its decoded generator coefficients, the four
    stored bits, and only in the nonzero-syndrome branch a single raw-coordinate read. -/
def answer (q : Mask) (stored : BasisParities) (readCoordinate : Fin 7 → Bool) : Bool :=
  let fromCache := combine (decode q) stored
  match syndrome q with
  | 0 => fromCache
  | i + 1 => fromCache ^^ readCoordinate (Fin.ofNat 7 i)

set_option maxHeartbeats 3000000 in
theorem answer_eq_parity : ∀ q x : Mask,
    answer q (cache x) (fun i => x.val.testBit i.val) = parityProbe q x := by
  decide

#print axioms codewords_cardinality
#print axioms unique_codeword_within_one
#print axioms systematic_basis
#print axioms minimum_distance_three
#print axioms answer_eq_parity

end HammingSeven
