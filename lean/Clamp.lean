/-
  The clamp and the two persona arms, machine-checked.

  NO IMPORTS. NO MATHLIB. Nothing is assumed that is not written as an explicit hypothesis of the
  theorem that uses it — so `#print axioms` at the bottom reports the empty set, and the reader's
  trust base is the Lean kernel alone.

  This is deliberate and it mirrors the paper argument: ARGUMENT.ipynb's proofs of T5 and T7 use
  only bilinearity of the inner product, and ⟨u,u⟩ = 1. They never use completeness, ordering,
  dimension, or the real numbers. So the theorems hold over ANY commutative ring of scalars, and
  the field ℝ is one instance. Stating them this way makes the hypotheses visible in the statement
  instead of hidden in a library.

  Correspondence with the document:
      clamp_hits_target      = T5(a)
      clamp_fixes_orthogonal = T5(b)   ← the property every causal claim in the project rests on
      zremoved_pins          = T7(a)
      zonly_reaches_donor    = T7(b)
      arms_partition         = T7(c)
-/

namespace PersonaForensics

/-! ## T5(a) — the clamp hits its target exactly -/

theorem clamp_hits_target
    {K V : Type}
    (add : V → V → V) (smul : K → V → V) (ip : V → V → K)
    (kadd ksub kmul : K → K → K) (kone : K)
    -- bilinearity in the first argument (D8)
    (ip_add_left  : ∀ x y w, ip (add x y) w = kadd (ip x w) (ip y w))
    (ip_smul_left : ∀ a x w, ip (smul a x) w = kmul a (ip x w))
    -- the two scalar laws used
    (kmul_one  : ∀ a, kmul a kone = a)
    (kadd_ksub : ∀ a b, kadd a (ksub b a) = b)
    -- the data: a state h, a UNIT direction u, a target t
    (h u : V) (t : K) (hu : ip u u = kone) :
    ip (add h (smul (ksub t (ip h u)) u)) u = t := by
  rw [ip_add_left, ip_smul_left, hu, kmul_one, kadd_ksub]

/-! ## T5(b) — the clamp changes nothing orthogonal to `u`

    This is the load-bearing one. It is what licenses attributing a behavioural change to the
    u-coordinate rather than to collateral damage in the other 3583 dimensions. -/

theorem clamp_fixes_orthogonal
    {K V : Type}
    (add : V → V → V) (smul : K → V → V) (ip : V → V → K)
    (kadd ksub kmul : K → K → K) (kzero : K)
    (ip_add_left  : ∀ x y w, ip (add x y) w = kadd (ip x w) (ip y w))
    (ip_smul_left : ∀ a x w, ip (smul a x) w = kmul a (ip x w))
    (kmul_zero : ∀ a, kmul a kzero = kzero)
    (kadd_zero : ∀ a, kadd a kzero = a)
    (h u v : V) (t : K)
    -- v is orthogonal to u
    (huv : ip u v = kzero) :
    ip (add h (smul (ksub t (ip h u)) u)) v = ip h v := by
  rw [ip_add_left, ip_smul_left, huv, kmul_zero, kadd_zero]

/-! ## T7(a) — `z_removed` pins the persona coordinate exactly -/

theorem zremoved_pins
    {K V : Type}
    (add vsub : V → V → V) (smul : K → V → V) (ip : V → V → K)
    (kadd ksub kmul : K → K → K) (kone kzero : K)
    (ip_add_left  : ∀ x y w, ip (add x y) w = kadd (ip x w) (ip y w))
    (ip_sub_left  : ∀ x y w, ip (vsub x y) w = ksub (ip x w) (ip y w))
    (ip_smul_left : ∀ a x w, ip (smul a x) w = kmul a (ip x w))
    (kmul_one  : ∀ a, kmul a kone = a)
    (ksub_self : ∀ a, ksub a a = kzero)
    (kadd_zero : ∀ a, kadd a kzero = a)
    (a delta z : V) (hz : ip z z = kone) :
    ip (add a (vsub delta (smul (ip delta z) z))) z = ip a z := by
  rw [ip_add_left, ip_sub_left, ip_smul_left, hz, kmul_one, ksub_self, kadd_zero]

/-! ## T7(b) — `z_only` moves the persona coordinate all the way to the donor's -/

theorem zonly_reaches_donor
    {K V : Type}
    (add : V → V → V) (smul : K → V → V) (ip : V → V → K)
    (kadd kmul : K → K → K) (kone : K)
    (ip_add_left  : ∀ x y w, ip (add x y) w = kadd (ip x w) (ip y w))
    (ip_smul_left : ∀ a x w, ip (smul a x) w = kmul a (ip x w))
    (kmul_one : ∀ a, kmul a kone = a)
    (a delta z : V) (hz : ip z z = kone) :
    ip (add a (smul (ip delta z) z)) z = kadd (ip a z) (ip delta z) := by
  rw [ip_add_left, ip_smul_left, hz, kmul_one]

/-! ## T7(c) — the two arms partition the donor displacement, with no remainder

    Stated as: the z-component plus the z-complement of `delta` is `delta`. -/

theorem arms_partition
    {V : Type} {K : Type}
    (add vsub : V → V → V) (smul : K → V → V) (ip : V → V → K)
    -- the one vector law used: y + (x - y) = x
    (vadd_vsub : ∀ x y, add y (vsub x y) = x)
    (delta z : V) :
    add (smul (ip delta z) z) (vsub delta (smul (ip delta z) z)) = delta := by
  rw [vadd_vsub]

end PersonaForensics

/-! ## What these proofs depend on

    Lean reports the axioms each theorem rests on. An empty report means the proof is closed under
    the kernel's own rules with nothing else assumed — no classical choice, no propositional
    extensionality, no `sorry`. -/

#print axioms PersonaForensics.clamp_hits_target
#print axioms PersonaForensics.clamp_fixes_orthogonal
#print axioms PersonaForensics.zremoved_pins
#print axioms PersonaForensics.zonly_reaches_donor
#print axioms PersonaForensics.arms_partition
