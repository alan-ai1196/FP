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

/-- The successor may incorporate a fixed noise trajectory and the entire prefix. -/
def mistakes (guess : σ → Bool) (next : σ → Bool → σ) (s : σ) : List Bool → List Bool
  | [] => []
  | b :: bs => (b ^^ guess s) :: mistakes guess next (next s b) bs

def reconstruct (guess : σ → Bool) (next : σ → Bool → σ) (s : σ) : List Bool → List Bool
  | [] => []
  | e :: es =>
    let b := e ^^ guess s
    b :: reconstruct guess next (next s b) es

theorem reconstruct_mistakes (guess : σ → Bool) (next : σ → Bool → σ)
    (s : σ) (bits : List Bool) : reconstruct guess next s (mistakes guess next s bits) = bits := by
  induction bits generalizing s with
  | nil => rfl
  | cons b bs ih => simp [mistakes, reconstruct, ih]

theorem mistakes_reconstruct (guess : σ → Bool) (next : σ → Bool → σ)
    (s : σ) (errors : List Bool) : mistakes guess next s (reconstruct guess next s errors) = errors := by
  induction errors generalizing s with
  | nil => rfl
  | cons e es ih => simp [mistakes, reconstruct, ih]

theorem mistakes_length (guess : σ → Bool) (next : σ → Bool → σ)
    (s : σ) (bits : List Bool) : (mistakes guess next s bits).length = bits.length := by
  induction bits generalizing s with
  | nil => rfl
  | cons b bs ih => simp [mistakes, ih]

#print axioms reconstruct_mistakes
#print axioms mistakes_reconstruct
#print axioms mistakes_length

end CausalState
