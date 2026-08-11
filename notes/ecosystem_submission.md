# Qiskit Ecosystem submission checklist

Working notes for submitting this repo to the Qiskit Ecosystem, based on
what actually blocked previous submissions (`qiskit-qkd-lab`).

## Known validator gotcha: `member.website`

The Ecosystem submission validator rejects an entry where
`member.website` points at a GitHub URL -- it needs to resolve somewhere
else. This blocked `qiskit-qkd-lab` previously. For this project, point
it at the QPortfolio page for `qiskit-lean-bridge` rather than the repo's
GitHub URL:

```json
"website": "https://<qportfolio-domain>/projects/qiskit-lean-bridge"
```

(`html_url`/`repository` fields elsewhere in the submission metadata are
fine as GitHub links -- it's specifically the `website` field that can't
be one.)

## Before submitting

- [ ] `LICENSE` present at repo root (done -- MIT)
- [ ] `README.md` has a clear one-line description near the top (used
      for the Ecosystem listing's summary text)
- [ ] Repo builds/runs cleanly from a fresh clone -- the Python side via
      `pip install -e .`, the Lean side via `lake exe cache get && lake build`
- [ ] CI is green on `main` (`.github/workflows/bridge-ci.yml`)
- [ ] QPortfolio entry for this project exists and is live *before*
      submitting, since the `website` field needs a working URL at
      submission time, not a placeholder

## What to say this project *is*, for the listing description

Given the Ecosystem lists a mix of applications, tutorials, and plugins,
this project is closest to the "tooling / verification" category rather
than a runnable application -- worth checking which category the
submission form expects and framing the one-line description around
"formal verification of the transpiler's gate-equivalence library" rather
than a user-facing feature, since that's the actual value proposition and
differentiator (per the earlier project-ideas discussion, no other
Ecosystem member does formally-verified gate identities).

## Honest state to disclose at submission time

Per `notes/coverage.md` as of this writing: 130 equivalences extracted,
33 with a fully trustworthy mapping (`direct`), 11 needing one helper
lemma (`derived`), and the rest blocked on either the qubit-ordering
question or missing LeanQuantum primitives. Of the addressable ones,
roughly two dozen `sorry`s are actually closed with real proofs. This is
early-stage, working tooling with a real (if partial) verification
result -- not a finished verification of the whole transpiler. Worth
being upfront about that scope in the submission description, same as
the README already is, rather than overstating completeness.
