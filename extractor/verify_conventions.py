"""
verify_conventions.py

Every "direct" or "derived" status in leanquantum_mapping.py is a claim
about numerical equality between a Qiskit gate and a LeanQuantum matrix
expression. This script re-derives those claims from scratch using
qiskit.quantum_info.Operator, independent of the mapping table, and
fails loudly if any of them stop holding (e.g. after a Qiskit version
bump changes a gate's phase convention).

This is intentionally NOT a proof — it's a numeric sanity check over a
handful of parameter values, run in CI on every extraction. It exists to
catch the class of error where someone (or a future Qiskit release)
silently changes a convention and a "direct" mapping quietly becomes
wrong. The actual proof obligation lives in Lean.
"""

from __future__ import annotations

import sys

import numpy as np
from qiskit.circuit.library import (
    CXGate,
    HGate,
    PhaseGate,
    RXGate,
    RYGate,
    RZGate,
    SGate,
    SXGate,
    TGate,
    UGate,
    XGate,
    YGate,
    ZGate,
)
from qiskit.quantum_info import Operator

TEST_PARAMS = [0.3, 0.7, 1.1, -0.4, 2.9]


def lq_rotate(theta, phi, delta):
    return np.array(
        [
            [np.cos(theta / 2), -np.exp(1j * delta) * np.sin(theta / 2)],
            [np.exp(1j * phi) * np.sin(theta / 2), np.exp(1j * (phi + delta)) * np.cos(theta / 2)],
        ]
    )


def lq_phase_shift(phi):
    return np.array([[1, 0], [0, np.exp(1j * phi)]])


def lq_sqrtx():
    return np.array([[(1 + 1j) / 2, (1 - 1j) / 2], [(1 - 1j) / 2, (1 + 1j) / 2]])


def lq_hadamard():
    return (1 / np.sqrt(2)) * np.array([[1, 1], [1, -1]])


def lq_notc():
    return np.array([[1, 0, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0], [0, 1, 0, 0]])


def lq_cnot():
    return np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]])


CHECKS = []


def check(name):
    def deco(fn):
        CHECKS.append((name, fn))
        return fn

    return deco


@check("u == rotate (exact, no phase correction)")
def _():
    for t, p, l in zip(TEST_PARAMS, TEST_PARAMS[1:] + [0.1], TEST_PARAMS[2:] + [0.2, 0.3]):
        if not np.allclose(Operator(UGate(t, p, l)).data, lq_rotate(t, p, l)):
            return False
    return True


@check("p == phaseShift (exact)")
def _():
    return all(np.allclose(Operator(PhaseGate(x)).data, lq_phase_shift(x)) for x in TEST_PARAMS)


@check("rz == exp(-i*theta/2) * phaseShift(theta)")
def _():
    return all(
        np.allclose(Operator(RZGate(x)).data, np.exp(-1j * x / 2) * lq_phase_shift(x))
        for x in TEST_PARAMS
    )


@check("sx == sqrtx (exact, no phase correction)")
def _():
    return np.allclose(Operator(SXGate()).data, lq_sqrtx())


@check("h == hadamard (exact)")
def _():
    return np.allclose(Operator(HGate()).data, lq_hadamard())


@check("rx == xRotate (exact)")
def _():
    return all(
        np.allclose(
            Operator(RXGate(x)).data,
            np.array(
                [[np.cos(x / 2), -1j * np.sin(x / 2)], [-1j * np.sin(x / 2), np.cos(x / 2)]]
            ),
        )
        for x in TEST_PARAMS
    )


@check("ry == yRotate (exact)")
def _():
    return all(
        np.allclose(
            Operator(RYGate(x)).data,
            np.array([[np.cos(x / 2), -np.sin(x / 2)], [np.sin(x / 2), np.cos(x / 2)]]),
        )
        for x in TEST_PARAMS
    )


@check("s == sGate (exact)")
def _():
    return np.allclose(Operator(SGate()).data, lq_phase_shift(np.pi / 2))


@check("t == tGate (exact)")
def _():
    return np.allclose(Operator(TGate()).data, lq_phase_shift(np.pi / 4))


@check("x == sigma_x, y == sigma_y, z == sigma_z (exact)")
def _():
    sx = np.array([[0, 1], [1, 0]])
    sy = np.array([[0, -1j], [1j, 0]])
    sz = np.array([[1, 0], [0, -1]])
    return (
        np.allclose(Operator(XGate()).data, sx)
        and np.allclose(Operator(YGate()).data, sy)
        and np.allclose(Operator(ZGate()).data, sz)
    )


@check("cx matches LeanQuantum's notc, NOT cnot (documents the ordering gotcha)")
def _():
    cx = Operator(CXGate()).data
    matches_notc = np.allclose(cx, lq_notc())
    matches_cnot = np.allclose(cx, lq_cnot())
    # This check exists to FAIL LOUDLY if this ever flips, since the whole
    # point is that the mapping table's warning depends on it.
    return matches_notc and not matches_cnot


def main() -> int:
    failures = []
    for name, fn in CHECKS:
        ok = fn()
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {name}")
        if not ok:
            failures.append(name)

    if failures:
        print(f"\n{len(failures)} convention check(s) failed:", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1

    print(f"\nAll {len(CHECKS)} convention checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
