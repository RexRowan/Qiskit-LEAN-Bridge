# Open question: qubit ordering (cx vs. cnot/notc)

## The observation

`qiskit.quantum_info.Operator(CXGate()).data` produces:

```
[[1, 0, 0, 0],
 [0, 0, 0, 1],
 [0, 0, 1, 0],
 [0, 1, 0, 0]]
```

which is numerically identical to LeanQuantum's `notc` (`Quantumlib/Data/Gate/Basic.lean`),
**not** `cnot`, despite `cx` being "the" CNOT gate in both systems' vocabulary.

This is reproduced in `extractor/verify_conventions.py::cx matches notc, NOT cnot`
and re-checked on every CI run, so it will be caught immediately if a Qiskit
release changes it.

## Why this happens (working hypothesis, not yet proven)

Both systems index a 2-qubit basis state as a single 4-dimensional index, but
they very likely disagree on which physical qubit contributes the
most-significant bit of that index:

- Qiskit's `Statevector`/`Operator` little-endian convention puts **qubit 0
  in the least-significant position** of the combined index. For `cx(0, 1)`
  (control=0, target=1), that ordering happens to make control the *high*
  bit of the 2-qubit index.
- LeanQuantum's `kron`/`⊗` (`Matrix/Kron.lean`) combines indices via
  `divNat`/`modNat` on a `Fin (a*c)`, and `cnot` is written down as a fixed
  4x4 literal — so "which physical qubit is the control" is whatever
  convention was used when `cnot` was written, not something derived from
  `kron`'s own indexing.

These are two independently-reasonable but different conventions, and
nothing forces them to agree. **This needs to be settled by deriving it from
LeanQuantum's own `Fin`-indexing rules, not by more numerical spot-checks.**
Spot-checks can confirm cx==notc for the identity case, but a wrong mental
model of *why* would produce wrong predictions for every other multi-qubit
gate (ch, crx, cry, crz, cp, cs, csx, cy — the whole `needs_convention_check`
bucket, 23 equivalences as of this writing).

## What "resolving" this actually requires

1. Pick one physical-qubit-to-tensor-factor convention and state it as an
   explicit Lean definition or lemma — e.g. a `qiskitOrder : CSquare (2^n) →
   CSquare (2^n)` reindexing function, or a proof that Qiskit's circuit
   composition order corresponds to `kron`'s `divNat`/`modNat` split in a
   specific, named way.
2. Prove `cx_eq_notc : <qiskit-cx-as-built-from-controlM-or-otherwise> = notc`
   from that definition, rather than asserting it from the numpy check.
3. Once that one lemma exists, `ch`, `crx`, `cry`, `crz`, `cp`, `cs`, `csx`,
   `cy` (and by extension every equivalence built on `controlM` applied to a
   single control qubit) can cite it directly instead of each needing its
   own from-scratch ordering argument.

## Why this is worth doing first

Per `notes/coverage.md`, `needs_convention_check` is the second-largest
bucket (23 of 130 equivalences, 18%) and every single one of them reduces to
the *same* underlying question. Resolving this once has more leverage than
proving any individual `direct`-status lemma.
