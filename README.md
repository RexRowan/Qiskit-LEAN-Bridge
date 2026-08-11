# Qiskit LEAN bridge

Bridges Qiskit's `StandardEquivalenceLibrary` (the gate identities the
transpiler relies on) to formally verified proofs in
[inQWIRE/LeanQuantum](https://github.com/inQWIRE/LeanQuantum).

## What's here right now

- `extractor/extract_equivalences.py` — walks Qiskit's equivalence library
  and serializes every registered gate identity to `data/equivalences.json`.
  Verified against Qiskit 2.5.1: **130 equivalences across 50 gates**.
- `extractor/leanquantum_mapping.py` — hand-curated correspondence between
  Qiskit gate names and LeanQuantum matrix definitions, each tagged
  `direct` / `derived` / `needs_convention_check` / `needs_def`.
- `extractor/verify_conventions.py` — numerically re-derives every claim in
  the mapping table from scratch on every CI run, independent of the table
  itself, so convention drift gets caught immediately rather than silently
  producing a false lemma.
- `extractor/generate_lean.py` — emits `lean/QiskitEquiv/Generated.lean`.
  Equivalences with a fully trustworthy mapping become real `sorry`'d lemma
  statements (including the `global_phase` factor — see below); anything
  else is emitted as a comment, never a lemma, so nobody can accidentally
  prove past an unverified assumption.
- `extractor/generate_coverage.py` — emits `notes/coverage.md`, a plain
  status summary.
- `notes/qubit_ordering.md` — the single highest-leverage open question
  (see below).

## Current coverage (Qiskit 2.5.1, 130 equivalences)

| Status | Count | Meaning |
|---|---|---|
| direct | 28 | Ready to attempt proof today |
| derived | 16 | One helper lemma away |
| needs_convention_check | 23 | Blocked on qubit ordering (one open question) |
| needs_def | 63 | Needs a new LeanQuantum primitive first |

Full breakdown in `notes/coverage.md` (regenerated on every extraction).

## Two things worth knowing before touching this

1. **Qiskit's `U(θ,φ,λ)` and LeanQuantum's `rotate θ φ δ` are exactly the
   same matrix, parameter for parameter, with no phase correction.**
   Verified numerically in `verify_conventions.py`. This is the load-bearing
   fact the whole `direct` bucket sits on — most single-qubit gates
   ultimately decompose through U/`rotate`.
2. **`cx` does not match LeanQuantum's `cnot`.** It matches `notc`. This is
   not a typo — it's a genuine qubit-ordering convention mismatch between
   the two systems, confirmed numerically and re-checked in CI. See
   `notes/qubit_ordering.md` for what resolving it actually requires (it's
   the highest-leverage open item: it single-handedly blocks 23 of the 130
   equivalences).

## What's deliberately NOT done yet

- No Lean proofs are actually closed — every emitted lemma is `sorry`.
  The point of this first pass is a trustworthy *map* of what's provable,
  not the proofs themselves.
- `lean/` has never actually been built in this environment (no Lean
  toolchain / Mathlib cache available here) — the lakefile and CI job are
  written and should work, but treat the first real `lake build` as
  something to watch closely rather than assume works.
- Global phase handling is implemented (`generate_lean.py` multiplies the
  RHS by `Complex.exp (global_phase * Complex.I)` when nonzero, with a
  rational-multiple-of-π detector so angles render symbolically rather than
  as decimal literals that would silently state a different, false claim)
  but hasn't been checked against a case with a *symbolic* global phase —
  only numeric ones show up in the current 130.

## Suggested next steps, in order of leverage

1. Resolve `notes/qubit_ordering.md` — unblocks the largest single bucket.
2. Prove the `rz = exp(-iθ/2) • phaseShift(θ)` helper lemma — unblocks most
   of the `derived` bucket in one shot.
3. Actually run `lake build` somewhere with a real Mathlib cache and start
   closing the 28 `direct` sorries — `h_equiv_0` and `h_equiv_1` restate
   LeanQuantum's own `rotate_hadamard`/`rotate` lemmas almost verbatim and
   are probably the fastest wins to confirm the whole pipeline works
   end-to-end.
4. Only then look at `needs_def` — that bucket is really "contribute new
   primitives to LeanQuantum," a bigger and separate effort (multi-control
   wrapper generalizing `controlM`, the Ising-coupling gate family, etc).
