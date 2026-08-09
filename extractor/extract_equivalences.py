"""
extract_equivalences.py

Walks Qiskit's StandardEquivalenceLibrary and serializes every registered
gate identity (source gate -> equivalent circuit) into a structured JSON
schema. This JSON is the interface contract between Qiskit and the Lean 4
side: `lean/generate_lemmas.py` consumes it to emit `.lean` lemma stubs,
and CI diffs it release-over-release to detect newly added equivalences
that don't yet have a formal proof.

Design notes
------------
- Qiskit's EquivalenceLibrary keys are (gate_name, num_qubits) pairs; a
  single key can map to *multiple* equivalent circuits (e.g. 'h' currently
  has 6 known decompositions). We keep all of them — the Lean side proves
  each one, since a transpiler pass could legally emit any of them.
- Parametrized gates (rx, ry, crz, ...) carry `Parameter` objects rather
  than floats. We preserve the parameter *names* and the symbolic
  expression each equivalent circuit uses for them, rather than binding
  to numeric values, since the Lean lemma needs to be proved for all
  theta, not a sampled point.
- We do NOT attempt to resolve global phase drift here beyond recording
  it; equivalence-up-to-global-phase vs strict equivalence is a choice
  the Lean formalization has to make explicitly per LeanQuantum's
  conventions, so we surface the number rather than deciding for it.
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from qiskit import __version__ as qiskit_version
from qiskit.circuit import Parameter
from qiskit.circuit.library.standard_gates import get_standard_gate_name_mapping
from qiskit.circuit.library.standard_gates.equivalence_library import (
    StandardEquivalenceLibrary,
)


def _param_expr_to_str(expr) -> str:
    """Render a ParameterExpression (or plain float) as a stable string."""
    try:
        return str(expr)
    except Exception:  # pragma: no cover - defensive
        return repr(expr)


@dataclass
class GateInstruction:
    name: str
    qubits: list[int]
    params: list[str]  # stringified ParameterExpressions or numeric literals


@dataclass
class Equivalence:
    index: int  # position among multiple equivalences for this key
    global_phase: str
    instructions: list[GateInstruction]


@dataclass
class GateEntry:
    name: str
    num_qubits: int
    source_params: list[str]  # symbolic parameter names of the LHS gate
    equivalences: list[Equivalence]


@dataclass
class ExtractionManifest:
    qiskit_version: str
    extracted_at: str
    gate_count: int
    equivalence_count: int
    gates: list[GateEntry] = field(default_factory=list)


def extract() -> ExtractionManifest:
    lib = StandardEquivalenceLibrary
    name_mapping = get_standard_gate_name_mapping()

    gates: list[GateEntry] = []
    total_equivalences = 0

    for key in sorted(lib.keys(), key=lambda k: (k.name, k.num_qubits)):
        proto = name_mapping.get(key.name)
        if proto is None:
            # Should not happen for the standard library, but don't let
            # an unknown gate silently vanish from the manifest.
            print(f"WARNING: no prototype found for gate '{key.name}'", file=sys.stderr)
            continue

        source_params = [str(p) for p in getattr(proto, "params", []) if isinstance(p, Parameter)]

        circuits = lib.get_entry(proto)
        equivalences: list[Equivalence] = []
        for idx, circ in enumerate(circuits):
            instrs = [
                GateInstruction(
                    name=ci.operation.name,
                    qubits=[circ.find_bit(q).index for q in ci.qubits],
                    params=[_param_expr_to_str(p) for p in ci.operation.params],
                )
                for ci in circ.data
            ]
            equivalences.append(
                Equivalence(
                    index=idx,
                    global_phase=_param_expr_to_str(circ.global_phase),
                    instructions=instrs,
                )
            )
        total_equivalences += len(equivalences)

        gates.append(
            GateEntry(
                name=key.name,
                num_qubits=key.num_qubits,
                source_params=source_params,
                equivalences=equivalences,
            )
        )

    return ExtractionManifest(
        qiskit_version=qiskit_version,
        extracted_at=datetime.now(timezone.utc).isoformat(),
        gate_count=len(gates),
        equivalence_count=total_equivalences,
        gates=gates,
    )


def main() -> None:
    out_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/equivalences.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    manifest = extract()
    out_path.write_text(json.dumps(asdict(manifest), indent=2, sort_keys=False))

    print(
        f"Extracted {manifest.equivalence_count} equivalences across "
        f"{manifest.gate_count} gates (qiskit {manifest.qiskit_version}) -> {out_path}"
    )


if __name__ == "__main__":
    main()
