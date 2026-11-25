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

theorem undo_shift (u t : Word I) : add (add u t) t = u := by
  funext i
  simp [add]

/-- A homogeneous state update on every reachable translation forces its cells to be cosets. -/
theorem cosets_of_updates (j : Word I → A) (push : Word I → A → A)
    (commutes : ∀ u t, j (add u t) = push t (j u)) (u v : Word I) :
    j u = j v ↔ j zero = j (add u v) := by
  apply cell_is_coset
  intro x y t
  constructor
  · intro h
    rw [commutes, commutes, h]
  · intro h
    have h' := congrArg (push t) h
    simpa only [← commutes, undo_shift] using h'

/-- Seeing whether every future translation hits one target separates all syndrome states. -/
theorem agreement_on_future_hits (u v a : Word I) :
    (∀ t, add u t = a ↔ add v t = a) ↔ u = v := by
  constructor
  · intro agree
    have hit : add u (add a u) = a := by
      rw [add_comm u, undo_shift]
    have eq := hit.trans ((agree (add a u)).mp hit).symm
    have back := congrArg (fun x => add x (add a u)) eq
    simpa only [undo_shift] using back
  · rintro rfl
    exact fun _ => Iff.rfl

#print axioms cell_is_coset
#print axioms kernel_closed
#print axioms cosets_of_updates
#print axioms agreement_on_future_hits

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
