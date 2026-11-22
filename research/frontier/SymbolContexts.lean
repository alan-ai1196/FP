import Std

namespace SymbolContexts

/-- A word weight is constant on each fiber of the encoded word. -/
def Preserves (f : List A → W) (g : A → C) : Prop :=
  ∀ x y : List A, x.map g = y.map g → f x = f y

/-- Substitutions keep the weight with the same arbitrary left and right flanks. -/
def SameContexts (f : List A → W) (a b : A) : Prop :=
  ∀ u v : List A, f (u ++ a :: v) = f (u ++ b :: v)

theorem substitution_criterion (f : List A → W) (g : A → C) :
    Preserves f g ↔ ∀ a b, g a = g b → SameContexts f a b := by
  constructor
  · intro preserved a b hab u v
    exact preserved _ _ (by simp [hab])
  · intro localEq
    have extend (x : List A) : ∀ y : List A, x.map g = y.map g →
        ∀ p : List A, f (p ++ x) = f (p ++ y) := by
      induction x with
      | nil =>
        intro y h p
        cases y <;> simp_all
      | cons a xs ih =>
        intro y h p
        cases y with
        | nil => simp at h
        | cons b ys =>
          have split : g a = g b ∧ xs.map g = ys.map g := by simpa using h
          calc
            f (p ++ a :: xs) = f (p ++ b :: xs) := localEq a b split.1 p xs
            _ = f ((p ++ [b]) ++ xs) := by simp
            _ = f ((p ++ [b]) ++ ys) := ih ys split.2 (p ++ [b])
            _ = f (p ++ b :: ys) := by simp
    intro x y h
    simpa using extend x y h []

def contextSetoid (f : List A → W) : Setoid A where
  r := SameContexts f
  iseqv := {
    refl := fun _ _ _ => rfl
    symm := fun h u v => (h u v).symm
    trans := fun h k u v => (h u v).trans (k u v)
  }

def classOf (f : List A → W) (a : A) : Quotient (contextSetoid f) :=
  Quotient.mk _ a

/-- This encoding preserves every word and merges every pair merged by any
    other preserving encoding. No probability, topology or rank axiom is needed. -/
theorem coarsest (f : List A → W) :
    Preserves f (classOf f) ∧
    ∀ {D : Type} (g : A → D), Preserves f g → ∀ a b, g a = g b → classOf f a = classOf f b := by
  constructor
  · apply (substitution_criterion f (classOf f)).2
    intro a b h
    exact Quotient.exact h
  · intro D g h a b hab
    exact Quotient.sound ((substitution_criterion f g).1 h a b hab)

#print axioms substitution_criterion
#print axioms coarsest

end SymbolContexts
