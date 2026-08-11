# Contributing

There are two genuinely different kinds of work here, and contributors
generally come from one side or the other:

## Python side (`extractor/`)

Extends what Qiskit equivalences get captured, mapped, and correctly
rendered as Lean statements. No Lean toolchain needed.

```bash
pip install -e .
python3 extractor/extract_equivalences.py data/equivalences.json
python3 extractor/verify_conventions.py
python3 extractor/verify_true_statements.py   # run this after ANY change
                                               # to leanquantum_mapping.py
python3 extractor/generate_lean.py
python3 extractor/generate_coverage.py
```

**Before adding or changing a `GateMapping` entry** in
`leanquantum_mapping.py`: run `verify_true_statements.py`. It numerically
checks the exact expression the generator will write against a
LeanQuantum-primitive-matching numpy reimplementation, independent of
Qiskit's own gate matrices. This project has already shipped one real bug
this way (an incomplete `rz` mapping that was individually plausible but
produced a false statement wherever `rz` appeared as a component
instruction inside another gate's equivalence) -- this check exists
specifically to catch that class of error before it reaches Lean.

A `GateMapping.status` is a claim about trustworthiness, not just
existence:
- `"direct"`: the LeanQuantum expression is the *complete, phase-accurate*
  value of the Qiskit gate, safe to substitute anywhere.
- `"derived"`: correct in principle but needs a helper lemma that doesn't
  exist in LeanQuantum yet before it can be cited directly.
- `"needs_convention_check"`: a candidate mapping exists but a
  qubit-ordering or similar convention hasn't been independently derived
  (not just numerically spot-checked) -- see `notes/qubit_ordering.md`.
- `"needs_def"`: no LeanQuantum primitive exists for this gate at all.

Don't mark something `"direct"` on the strength of a single numeric
check against one set of gates -- check whether it's also correct
wherever it might appear as a *component* of another equivalence.

## Lean side (`lean/QiskitEquiv/`)

Closes the `sorry`s in `Generated.lean`. Requires a Lean 4 + Mathlib
toolchain (see `lean/lean-toolchain` for the pinned version) and the
LeanQuantum dependency, pulled automatically by `lake`.

```bash
cd lean
lake exe cache get   # pulls prebuilt Mathlib .oleans -- do this before
                      # `lake build`, or expect a very long first build
lake build
```

**Do not run the Python generator and hand-edit `Generated.lean` in the
same session without care** -- `generate_lean.py` rebuilds the entire
file from the template on every run, which will silently overwrite any
proof you've written by hand. If you're actively closing `sorry`s, treat
`Generated.lean` as the file you edit directly; don't regenerate it
until you're ready to reconcile.

See `notes/coverage.md` for what's currently open, and
`notes/qubit_ordering.md` for the single highest-leverage unresolved
question (it blocks the largest bucket of equivalences by itself).

## Both sides

Any change to the generator or the mapping table that affects an
already-open `sorry` needs the corresponding statement in
`Generated.lean` checked against what `generate_lean.py` would now
produce -- diff the specific lemma, don't assume it's unaffected.
