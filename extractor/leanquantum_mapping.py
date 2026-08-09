"""
leanquantum_mapping.py

Hand-curated (and numerically spot-checked — see verify_conventions.py)
correspondence between Qiskit standard gates and inQWIRE/LeanQuantum
primitives (Quantumlib/Data/Gate/{Basic,Rotate,PhaseShift,Pauli}.lean).

Every entry has a `status`:
  - "direct":   Qiskit gate == LeanQuantum expression, exactly, no phase
                 correction. Verified numerically for concrete parameter
                 values in verify_conventions.py.
  - "derived":  Equal up to a known, simple correction (typically a
                 global phase factor e^{i*expr}) that itself needs a one-
                 line Lean lemma before the identity lemmas can cite it.
  - "needs_def": No LeanQuantum primitive exists yet; the bridge would
                 first need to contribute a new `def` to LeanQuantum
                 (or define it locally in QiskitEquiv/) before any
                 equivalence lemma referencing this gate can be stated.
  - "needs_convention_check": A candidate LeanQuantum expression exists
                 but qubit-ordering / endianness has NOT been verified
                 (the cx/cnot mismatch below is the concrete example of
                 why this category exists — don't assume, check).

`lean_expr` uses `{p0}`, `{p1}`, ... as positional placeholders for the
gate's own parameters (in Qiskit param order) so the generator can
substitute the extracted parameter expressions directly.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GateMapping:
    lean_expr: str | None
    status: str
    note: str = ""


# NOTE: this table is deliberately conservative. Getting a "direct" wrong
# produces a *false* formal proof, which is worse than no proof — so
# anything not spot-checked against qiskit.quantum_info.Operator stays
# at "needs_convention_check" or "needs_def" until it is.
GATE_MAPPING: dict[str, GateMapping] = {
    # --- single-qubit, no params: verified exact matches ---
    "h": GateMapping("hadamard", "direct"),
    "x": GateMapping("σx", "direct"),
    "y": GateMapping("σy", "direct"),
    "z": GateMapping("σz", "direct"),
    "s": GateMapping("sGate", "direct"),
    "t": GateMapping("tGate", "direct"),
    "sx": GateMapping("sqrtx", "direct",
                       "Verified: Qiskit SXGate() == LeanQuantum sqrtx exactly, "
                       "no global phase correction needed (checked numerically)."),
    "id": GateMapping("1", "direct", "Identity matrix, Mathlib's `1 : CSquare 2`."),
    "swap": GateMapping("swap", "needs_convention_check",
                         "Matrix shape matches but qubit-index ordering not yet "
                         "verified the way cx/cnot was — see cx entry below."),

    # --- single-qubit, no params: need a one-line derived lemma ---
    "sdg": GateMapping("phaseShift (-(π / 2))", "derived",
                        "= sGate⁻¹; sGate is unitary so sGate⁻¹ = sGateᴴ. Either "
                        "prove via phaseShift_mul_phaseShift or add sdgGate."),
    "tdg": GateMapping("phaseShift (-(π / 4))", "derived", "Same pattern as sdg."),

    # --- single-qubit, parametrized: verified exact matches ---
    "rx": GateMapping("xRotate {p0}", "direct"),
    "ry": GateMapping("yRotate {p0}", "direct"),
    "p": GateMapping("phaseShift {p0}", "direct",
                      "Verified: Qiskit PhaseGate(lambda) == phaseShift(lambda) exactly."),
    "u": GateMapping("rotate {p0} {p1} {p2}", "direct",
                      "Verified: Qiskit U(theta,phi,lambda) == LeanQuantum "
                      "rotate(theta,phi,delta) exactly, param-for-param, no "
                      "phase correction. This is the load-bearing identity: "
                      "most other single-qubit equivalences bottom out at U."),
    "u2": GateMapping("rotate (π / 2) {p0} {p1}", "direct", "u2(phi,lam) = U(pi/2, phi, lam)."),
    "u1": GateMapping("phaseShift {p0}", "direct", "u1(lambda) = p(lambda), same as p."),

    # --- single-qubit, parametrized: derived (needs a phase-factor lemma first) ---
    "rz": GateMapping("phaseShift {p0}", "derived",
                       "Verified: Qiskit RZGate(theta) == exp(-i*theta/2) * phaseShift(theta) "
                       "exactly. Needs a `rzGate` def (or a scalar-multiple lemma) in "
                       "LeanQuantum before equivalence lemmas can cite it directly."),
    "r": GateMapping(None, "needs_def",
                      "Qiskit's r(theta, phi) has no direct LeanQuantum primitive; "
                      "it's a rotation about an axis in the XY-plane. Expressible via "
                      "`rotate`-family composition but needs a derivation, not a lookup."),
    "sxdg": GateMapping(None, "needs_def", "sqrtx⁻¹ = sqrtxᴴ, no named def yet."),

    # --- two-qubit: THE cautionary example ---
    "cx": GateMapping("notc", "needs_convention_check",
                       "IMPORTANT: numerically, Qiskit's CXGate() (little-endian Operator "
                       "convention, qubit 0 = control) matches LeanQuantum's `notc`, NOT "
                       "`cnot`, because Qiskit's qubit-index-to-tensor-factor ordering is "
                       "the reverse of the naive reading. Do not assume cx -> cnot just "
                       "because the names look aligned. This needs to be re-derived from "
                       "LeanQuantum's own Fin-indexing convention (not just eyeballing the "
                       "matrix) before it's trusted -- see notes/qubit_ordering.md."),
    "cz": GateMapping("controlM σz", "needs_convention_check", "Diagonal, so ordering is probably safe, but verify -- don't assume from cx."),
    "ch": GateMapping("controlM hadamard", "needs_convention_check", "Same ordering caveat as cx."),
    "crx": GateMapping("controlM (xRotate {p0})", "needs_convention_check", "Same ordering caveat as cx."),
    "cry": GateMapping("controlM (yRotate {p0})", "needs_convention_check", "Same ordering caveat as cx."),
    "crz": GateMapping("controlM (phaseShift {p0})", "needs_convention_check",
                        "Compounds the rz derived-phase issue AND the ordering issue -- "
                        "resolve both before attempting a proof."),
    "cp": GateMapping("controlM (phaseShift {p0})", "needs_convention_check", "Diagonal -- likely safe, but verify."),
    "cs": GateMapping("controlM sGate", "needs_convention_check", "Diagonal -- likely safe, but verify."),
    "csdg": GateMapping("controlM (phaseShift (-(π / 2)))", "needs_convention_check", "Diagonal -- likely safe, but verify."),
    "csx": GateMapping("controlM sqrtx", "needs_convention_check", "Same ordering caveat as cx."),
    "cu": GateMapping(None, "needs_def", "4-parameter controlled-U; needs controlM applied to `rotate` plus a global phase factor, not yet composed."),
    "ccx": GateMapping(None, "needs_def", "Toffoli. `controlM` is single-control only; a doubly-controlled wrapper doesn't exist yet in LeanQuantum."),
    "ccz": GateMapping(None, "needs_def", "Same gap as ccx."),
    "cswap": GateMapping(None, "needs_def", "Fredkin; no 3-qubit control primitive yet."),

    # --- two-qubit, no direct control-structure: genuinely new territory ---
    "cy": GateMapping("controlM σy", "needs_convention_check", "Same ordering caveat as cx."),
    "rxx": GateMapping(None, "needs_def", "Ising coupling gate; not expressible via controlM (no single control qubit)."),
    "ryy": GateMapping(None, "needs_def", "Same as rxx."),
    "rzz": GateMapping(None, "needs_def", "Same as rxx."),
    "rzx": GateMapping(None, "needs_def", "Same as rxx."),
    "ecr": GateMapping(None, "needs_def", "Echoed cross-resonance; hardware-native gate, no LeanQuantum analogue."),
    "iswap": GateMapping(None, "needs_def", "No LeanQuantum analogue yet."),
    "dcx": GateMapping(None, "needs_def", "Double-CNOT; expressible as cnot-notc composition once cx ordering is resolved."),
    "ms": GateMapping(None, "needs_def", "Global Mølmer-Sørensen gate; multi-qubit, no analogue."),

    # --- multi-controlled: out of scope for a first pass ---
    "mcx": GateMapping(None, "needs_def", "n-controlled X, arbitrary width -- needs an inductive controlM generalization first."),
    "mcp": GateMapping(None, "needs_def", "Same as mcx."),
    "mcrx": GateMapping(None, "needs_def", "Same as mcx."),
    "mcry": GateMapping(None, "needs_def", "Same as mcx."),
    "mcrz": GateMapping(None, "needs_def", "Same as mcx."),
    "rcccx": GateMapping(None, "needs_def", "Relative-phase Toffoli variant, no analogue."),
    "rccx": GateMapping(None, "needs_def", "Relative-phase Toffoli variant, no analogue."),
    "pauli": GateMapping(None, "needs_def", "Multi-qubit Pauli string gate -- LeanQuantum HAS a `Pauli n` type (Data/Gate/Pauli/Defs.lean) but wiring Qiskit's PauliGate label string into it isn't done."),
    "global_phase": GateMapping(None, "needs_def", "Not a gate in the matrix sense; represented as `Circuit.global_phase` field, needs special-casing rather than a matrix mapping."),
}


def resolve(name: str) -> GateMapping:
    return GATE_MAPPING.get(name, GateMapping(None, "needs_def", "Not yet triaged."))
