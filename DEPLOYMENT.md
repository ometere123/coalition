# Deployment — stable Studionet only

COALITION targets **Studionet, chain ID 61999**.

RPC: `https://studio.genlayer.com/api`

This repository is intentionally **not** configured for Studio-dev / 61997.

## 1. Clone

`git clone https://github.com/ometere123/coalition.git`

`cd coalition`

## 2. Install the repository-local stable CLI

Ignore any globally installed GenLayer CLI for this repo.

`npm install`

`npx genlayer --version`

Expected: **0.39.1**.

## 3. Run Direct Mode before deployment

Under Linux/macOS/WSL:

`python -m venv .venv`

`source .venv/bin/activate`

`pip install -r requirements-test.txt`

`pytest tests/direct -q`

Do not deploy while the suite is red.

## 4. Select and verify Studionet

`npx genlayer network set studionet`

`npx genlayer network info`

Verify the output corresponds to:

- RPC: `https://studio.genlayer.com/api`
- chain ID: `61999`

If you see `61997`, `studio-dev`, or `studio-dev.genlayer.com`, stop.

## 5. Confirm signer and test GEN

Use the stable CLI account commands to confirm the intended signer and enough test GEN. Never commit private keys or a populated `.env`.

## 6. Deploy

`npx genlayer deploy --contract contracts/coalition.py`

Wait for the expected finalized state, then record the contract address, deployment transaction hash, deployed Git commit and signer.

## 7. Execute the reviewer lifecycle

Follow `LIVE_DEMO.md`, then fill `REVIEW_EVIDENCE.md` with real transaction hashes and observed results only.

## 8. Latest live compatibility deployment

The liveness-hardening source was deployed to Studionet 61999 after the full
Direct Mode suite, preflight, compile and lint gates passed.

- Contract: `0x19b6bB183859b4418c6347C24Fa15d09316e432f`
- Deployment transaction: `0x6a057cf8f50d3dc48ec3e4ded57bf295defc7a3c581875f97983a5341a970e81`
- Explorer: `https://explorer-studio.genlayer.com/address/0x19b6bB183859b4418c6347C24Fa15d09316e432f`
- Deployment result: `FINALIZED / ACCEPTED / SUCCESS`
- Deployed source snapshot: `48619` bytes, SHA-256 `40642726e20b04c6a58952294b52f182a0e77da50566934bd0222c061659e85d`

The deployed changes are narrowly scoped to two liveness protections:

1. withdrawn bids no longer consume the task's active bid-admission capacity;
2. retained bid history is capped at 20 records per task, while the solver
   remains capped at 10 active bids;
3. a qualification that resolves `UNAVAILABLE` can be retried in place, while
   all other terminal qualification verdicts remain immutable.

Live proof on this deployment included a provider-specific public-evidence
qualification (`0xcb76dd9a7d0ed0c20dbc291a9723200ad6f3bf59697a175bde2b0689ce0cdf70`)
and a deterministic solved selection (`0x982c194675b4ae9842b2d103d49325d1cf6febcdbe26b68b78f19a20d1dbdf87`).
Task 3 selected bid 5 at total cost 20; `is_solution` returned true for the
exact definition/solution hashes and false after changing the definition hash.

The first qualification on the same deployment also demonstrates conservative
semantic handling: generic public pages that did not substantiate the named
provider returned `AMBIGUOUS`, and the resulting complete task was
`UNSATISFIABLE` rather than being treated as qualified.

## Final provenance migration

The next deployment must use the current source after the admission/provenance
upgrade. Its exact live values are intentionally left blank until a finalized
Studionet deployment is observed. Do not treat this section as evidence.

- Admission modes: `OPEN` (permissionless bounded) and `FROZEN_PROFILES` (exact
  sealed profile set frozen before bidding).
- Definition binding: mode, admitted profile IDs, profile hashes and owners.
- Qualification binding: canonical receipt hash, including verdict and
  source-grounded evidence.
- Solution binding: complete active matrix hash, including losing bids.
- Consumer views: `is_qualification` and `is_solution_bundle`.
