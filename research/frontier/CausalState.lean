import Std

namespace CausalState

abbrev Word (I : Type) := I → Bool
def zero : Word I := fun _ => false
def add (u v : Word I) : Word I := fun i => u i ^^ v i

theorem add_self (u : Word I) : add u u = zero := by
  funext i
  simp [add, zero]

theorem add_comm (u v : Word I) : add u v = add v u := by
  funext i
  exact Bool.xor_comm _ _

/-- The names of cells may change under a translation. Only equality is preserved. -/
def Invariant (f : Word I → A) : Prop :=
  ∀ u v t, f u = f v ↔ f (add u t) = f (add v t)

theorem cell_is_coset (f : Word I → A) (h : Invariant f) (u v : Word I) :
    f u = f v ↔ f zero = f (add u v) := by
  rw [← add_comm v u, ← add_self u]
  exact h u v u

theorem kernel_closed (f : Word I → A) (h : Invariant f) (u v : Word I)
    (hu : f zero = f u) (hv : f zero = f v) : f zero = f (add u v) :=
  (cell_is_coset f h u v).mp (hu.symm.trans hv)

#print axioms cell_is_coset
#print axioms kernel_closed

end CausalState
