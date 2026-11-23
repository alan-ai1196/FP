import Std

namespace ResponseProfiles

variable {Row Col Value State : Type}

def Fits (observed : Row → Col → Option Value) (encode : Row → State)
    (decode : State → Col → Value) : Prop :=
  ∀ u v p, observed u v = some p → decode (encode u) v = p

/-- One extra state permits replacing any single missing law while preserving every other law. -/
theorem spare_state [DecidableEq Row] [DecidableEq Col]
    (observed : Row → Col → Option Value) (encode : Row → State)
    (decode : State → Col → Value) (fits : Fits observed encode decode)
    (u₀ : Row) (v₀ : Col) (missing : observed u₀ v₀ = none) (value : Value) :
    ∃ (encode' : Row → Option State) (decode' : Option State → Col → Value),
      Fits observed encode' decode' ∧ decode' (encode' u₀) v₀ = value ∧
      ∀ u v, u ≠ u₀ ∨ v ≠ v₀ → decode' (encode' u) v = decode (encode u) v := by
  let enc (u : Row) := if u = u₀ then none else some (encode u)
  let dec (s : Option State) (v : Col) := match s with
    | some a => decode a v
    | none => if v = v₀ then value else decode (encode u₀) v
  have same (u : Row) (v : Col) (ne : u ≠ u₀ ∨ v ≠ v₀) :
      dec (enc u) v = decode (encode u) v := by
    by_cases h : u = u₀
    · subst u
      have hv : v ≠ v₀ := by simpa using ne
      simp [enc, dec, hv]
    · simp [enc, dec, h]
  refine ⟨enc, dec, ?_, ?_, same⟩
  · intro u v p h
    have ne : u ≠ u₀ ∨ v ≠ v₀ := by
      by_cases hu : u = u₀
      · subst u
        right
        intro hv
        subst v
        simp [missing] at h
      · exact Or.inl hu
    exact (same u v ne).trans (fits u v p h)
  · simp [enc, dec]

#print axioms spare_state

end ResponseProfiles
