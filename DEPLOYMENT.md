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

## Final Studionet deployment — provenance source

- Network: Studionet, chain ID `61999`
- RPC: `https://studio.genlayer.com/api`
- Source commit: `577d52f0a13b09cf3ac0b055fd409678678d377a`
- Source SHA-256: `0dc05e635ae64e9a0d77c35e2393e9b9a34a06836f248e1822cfda4fca38fee2`
- Source bytes: `57197`
- Contract: `0xcb211f72AecB476c1366102cFD6F4fFa6786be41`
- Deployment transaction: `0x3d0767d7d38ade906f70528fe700d8c59563cd5d0a650f3913c82acb54858e78`
- Explorer: `https://explorer-studio.genlayer.com/address/0xcb211f72AecB476c1366102cFD6F4fFa6786be41`
- Deployment result: `FINALIZED / MAJORITY_AGREE / SUCCESS`

### Frozen-admission live evidence

The live task setup used the new high-assurance mode and finalized successfully:

- Provider profile creation: `0x4ac2616c673049296b5d98f7ae3dd4e8b144c46c9be527dac808d75a89bd9f6f`
- Provider evidence: `0x0bb7d66d794f891ae470630d365d38f663150b0f8b13eea60a2cf780b2f9f903`
- Provider sealing: `0x44f3bdbc297dcd05f25a1628f20f2229efb42ec31bf840fce5ccb5de331dc308`
- Task creation: `0xe8dcb6ea6bf5aa2ec790050969eaaaabedf57d51cebe54483c5984732af14`
- Requirement: `0xc992334dda24430204a024c549838ab2dfaac3c5207df8f028357019340b90e9`
- Admission mode `FROZEN_PROFILES`: `0x4ee24b37bc0038344fdf78109f6a31a2c186c6b6629121d6670bcc5ab2fa91e1`
- Admitted profile: `0x0a30c26494b038066c5e71483fd89759e65a7425f4d5f0a9f1a9b46b70b98271`
- Task sealing: `0xaa4c84d759bd7b2b450c522fd0ebc0e52f1dd67ac795f204e0412e6ae227f215`
- Task ID: `1`
- Definition hash: `8567a76058778f31d2a0b7d7d326850d85d2af1dac1c554eb9e0e65988a8acfb`
- Readback: `BIDDING`, admission mode `1`, admitted profile IDs `[1]`, matrix/solution hashes empty before bidding.

A second short-window task was also created and sealed, but its bid reached the
chain after the deadline and finalized with `EXPECTED: task is not accepting
bids`. It is retained as an honest deadline-boundary diagnostic, not as a
successful coalition lifecycle:

- Task creation: `0x9363f1b242fb555efebfbc302668a4490635d7941cc140cc9084336b28ef60c4`
- Requirement: `0xfa33b679b771ef975df06aefd83e105a090d64c8c440a8b083a91f47592b5de3`
- Admission mode: `0x17b9c754ff817c93cb421f9b929f87716b6e31a31225eb529e5b06264dbb1def`
- Admission: `0xe9e43b5042ab6ec0b721916e88c0c5e08347fbc01ec4fabcd49d41d928fd8258`
- Seal: `0x3a8aeeb656a96169ee7b4b6a456ad7e0a76742d8cdec4afb71d8ad60d8e1ecc8`
- Late bid diagnostic: `0x9676818cbe188eef095783863cc13a24905cae9601f0a22a1f4bf8655170c59b`
