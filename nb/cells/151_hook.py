# ⟨needs⟩ 011 (np)

def toy_model(x, hooks=None):
    # A three-layer residual "model" in numpy, so a hook is a thing you have written.
    # `hooks=None` is a DEFAULT argument: call toy_model(x) and hooks arrives as None.

    hooks = hooks or {}
    # `a or b` returns b when a is falsy — the standard idiom for "default to an empty dict".
    # (Writing `hooks={}` in the signature would be a bug: Python creates that dict once and
    #  shares it across every call.)

    h = x.copy()
    # `.copy()` so the caller's input array is never modified in place.

    trace = {}
    # Somewhere to record the state after each layer, for inspection.

    for layer in range(3):
        # Three pretend layers.

        f = np.sin(h) * 0.3                       # stand-in for the layer's computation
        h = h + f                                 # residual update
        if layer in hooks:
            # THE MECHANISM: if a function was registered for this layer, call it on the state.

            h = hooks[layer](h)                   # <- the hook may REPLACE the state
        trace[layer] = h.copy()
        # Snapshot after the (possibly hooked) update.

    return h, trace
    # Returning two values makes a tuple; the caller can unpack it into two names.

x = np.array([0.5, -1.0, 2.0])
# A tiny 3-dimensional input, so every printed vector is readable at a glance.

clean, _ = toy_model(x)
# Run with NO hooks — the reference output. `_` discards the trace we do not need here.

seen = {}
# an observing hook: records, changes nothing
# A dict the hook writes into, so the captured state survives after the call returns.

def observe(h):
    # A hook is just a function taking the state and returning a state. Nothing more.

    seen["L1"] = h.copy()
    # Store a copy of what passed through.

    return h
    # And hand the state back UNCHANGED — that is what makes it an observation, not an edit.

obs_out, _ = toy_model(x, {1: observe})
# `{1: observe}` registers the function at layer 1. This is exactly what "hooking layer 16" means
# in the real experiments: a function attached at one layer, called with that layer's state.

assert np.allclose(obs_out, clean), "an observing hook must not change the output"
# The defining property of a read-only hook: the model's output is bit-for-bit what it was.

print(f"observed state at layer 1: {np.round(seen['L1'], 4)}")
# What the hook captured — a real intermediate state, extracted without disturbing the run.

print(f"output unchanged by observation: {np.allclose(obs_out, clean)}")
# And the proof that nothing was disturbed, printed rather than asserted out of sight.

inter_out, _ = toy_model(x, {1: lambda h: h * 2.0})
# an intervening hook: doubles layer 1's state
# `lambda h: h * 2.0` is an anonymous one-expression function — same shape as `observe`, except it
# returns something different from what it received, which is what makes it an INTERVENTION.

print(f"\nclean output      {np.round(clean, 4)}")
# The two outputs side by side, so the effect of the edit is visible before it is asserted.

print(f"intervened output {np.round(inter_out, 4)}")
assert not np.allclose(inter_out, clean), "the intervening hook had no effect"
# `not np.allclose(…)`: this time the output MUST differ, otherwise the hook was never called
# and every causal claim built on this machinery would be measuring nothing. A positive control.

print("\nThat is the whole mechanism. Everything causal in this project is a hook plus a choice")
# The generalisation: every causal experiment in this project is those two lines, at scale.

print("of what to write at that point -- and the CHOICE is where chapter 9's correction lives.")
