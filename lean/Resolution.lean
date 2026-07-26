/-
  A PROOF OBLIGATION AT THE INTERFACE — and an honest account of what that is not.

  T13 in ARGUMENT.ipynb says: a ratio whose denominator cannot be separated from zero by the
  design's own resolution is not a measurement. The reported "16x the sum of parts" divides
  11.1 pp by 0.7 pp, against a paired resolution of ~2.9 pp — a denominator four times smaller
  than the smallest difference the experiment can see.

  ⚠ WHAT THIS FILE CLAIMED, AND WHY THAT WAS WRONG.
  An earlier version of this header said: "build a type in which the expression CANNOT BE WRITTEN
  … not a warning, not a lint, a type error", and concluded "the expression is not merely wrong —
  it does not typecheck." A cold reader appended two lines to this file:

      #eval union.value / sumParts.value          -- compiles, prints 15
      #eval (union.value * 10) / sumParts.value   -- compiles, prints 158

  and both compile. `Measured` is an ordinary structure; its fields project. The rejected figure is
  one field access away, and marking the fields `private` does not help — `private` in Lean 4 is
  scoped to the module, and this artifact has a single Lean file, so there is no boundary for it to
  hide behind. THE CLAIM WAS NOT TRUE AND, IN THIS FILE, IS NOT ACHIEVABLE.

  It is the same error the argument names two pages away: a proxy sound in one direction, with the
  prose asserting the other. `ratio` typechecking implies a proof was supplied; it does not imply
  that no ratio can be formed. I checked the direction that held and wrote the sentence for the
  direction that did not.

  WHAT IS ACTUALLY TRUE, WHICH IS WEAKER AND STILL WORTH HAVING:

    · `ratio` cannot be applied without a term of type `Resolved den`. That is a type error, not a
      convention, and `sumParts_not_resolved` proves no such term exists for this denominator.
    · So any code path that goes THROUGH THE INTERFACE owes a proof, and for the "16x" figure that
      proof is impossible. The discipline is enforced where the API is used.
    · Nothing stops a caller reaching past the interface to the underlying integers. Enforcing that
      needs a module boundary this artifact does not have — an opaque type exported from a separate
      module, with no field accessors in its signature.

  So: a proof obligation at the interface, not unrepresentability. `check.py` asserts BOTH halves —
  that the guarded path fails without a proof, AND that the unguarded path still compiles — so this
  header cannot quietly drift back to the stronger claim.

  Self-contained: no imports, no mathlib. The ordered-ring facts used are explicit hypotheses.
-/

namespace Interp

/-- A quantity together with the half-width of the interval the design cannot resolve within.
    `value` is the point estimate; the truth lies within `resolution` of it. -/
structure Measured (K : Type) where
  value      : K
  resolution : K
deriving Repr

/-- Absolute value on `Int`, written out rather than imported. -/
abbrev iabs (x : Int) : Int := if x < 0 then -x else x

/-- The denominator is usable exactly when its interval excludes zero, i.e. the point estimate
    exceeds the resolution in magnitude. This is a PROPOSITION, so it must be proved to be used. -/
abbrev Resolved (m : Measured Int) : Prop :=
  m.resolution < iabs m.value

/-- Division of measured quantities. Note the third argument: a ratio cannot be formed THROUGH THIS
    FUNCTION without evidence that the denominator is resolved. That obligation is the whole point,
    and its limits are stated in the header. -/
def ratio (num den : Measured Int) (_h : Resolved den) : Int :=
  num.value / den.value

/-! ## The reported figures, as data

    Using integers scaled by 10 (so 0.7 pp is written 7) to stay free of any numeric library. -/

/-- keep[0,12) alone: 0.1 pp effect. -/
def eA : Measured Int := { value := 1,   resolution := 29 }
/-- keep[16,28) alone: 0.6 pp effect. -/
def eB : Measured Int := { value := 6,   resolution := 29 }
/-- the two blocks together, minus base: 11.1 pp. -/
def union : Measured Int := { value := 111, resolution := 29 }
/-- the denominator actually used by the "16x" figure: the sum of the parts, 0.7 pp. -/
def sumParts : Measured Int := { value := eA.value + eB.value, resolution := 29 }

/-! ## The result

    `Resolved` for integers is `resolution < |value|`. For `sumParts` that reads `29 < 7`,
    which is false — so no proof exists, and `ratio` cannot be applied to it. -/

/-- The denominator is NOT resolved: 29 is not less than |7|. -/
theorem sumParts_not_resolved : ¬ Resolved sumParts := by
  decide

/-- The numerator IS resolved: 29 < |111|. So the union's own effect is a real measurement even
    though the ratio is not. Exactly the asymmetry T13 describes. -/
theorem union_is_resolved : Resolved union := by
  decide

/-! ## What this buys, stated at its real strength

    To write the "16x" figure VIA `ratio` one must supply `h : Resolved sumParts`. By
    `sumParts_not_resolved` no such term exists, so that application does not typecheck. The union's
    own effect remains available, because `union_is_resolved` does have a proof.

    What it does not buy: `union.value / sumParts.value` is ordinary integer division on projected
    fields and compiles fine. The type carries the obligation; it does not remove the arithmetic.

    The claim that survives is the one the data support:
      the union produces a resolved effect; neither part alone does;
      and the MULTIPLE relating them cannot be formed through an interface that checks. -/

end Interp

#print axioms Interp.sumParts_not_resolved
#print axioms Interp.union_is_resolved
