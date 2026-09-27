# Review evidence

Verified live evidence for COALITION on **Studionet chain 61999**.

## Deployment

- repository commit used: `d1b4d7b7d0983b9f741067cc218895a51b98f1ea`
- local CLI version: `0.39.1`
- network: Studionet
- RPC: `https://studio.genlayer.com/api`
- chain ID: `61999`
- contract address: `0x19b6bB183859b4418c6347C24Fa15d09316e432f`
- deployment transaction: `0x6a057cf8f50d3dc48ec3e4ded57bf295defc7a3c581875f97983a5341a970e81`
- finality evidence: `FINALIZED / ACCEPTED / SUCCESS`

## Direct Mode

- CI run: https://github.com/ometere123/coalition/actions/runs/36350211635
- tested commit: `d1b4d7b7d0983b9f741067cc218895a51b98f1ea`
- runner OS: Ubuntu 24.04 GitHub-hosted runner
- Python: 3.12
- local application CLI verified by CI: `0.39.1`
- Direct Mode harness: `genlayer-testing-suite@v0.29.2`
- GenVM runner bundle: `v0.3.0-rc7`
- contract runner hash verified in bundle: `py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6`
- static preflight: **passed**
- test command: `pytest tests/direct -q`
- passed count: **16**
- failed count: **0**
- CI conclusion: **success**
- runtime: **31.12s**
- notes: the repository includes `scripts/prepare_direct_mode.py` because the stable v0.29.2 harness expects the historical universal-bundle cache name while the official rc7 release now publishes the runner archive as `genvm-runners-all.tar.xz`.

## Main coalition proof

- task ID: `3`
- task definition hash: `ef968270c58c732e5cc9ef40b75819863c5dca4691b6082a917676fdf6a45ead`
- provider profile ID: `5` (`OpenZeppelin`)
- bid ID/price: `5 / 20`
- qualification transaction: `0xcb76dd9a7d0ed0c20dbc291a9723200ad6f3bf59697a175bde2b0689ce0cdf70`
- solve transaction: `0x982c194675b4ae9842b2d103d49325d1cf6febcdbe26b68b78f19a20d1dbdf87`
- selected bid IDs: `[5]`
- total cost: `20`
- solution hash: `4a2b24ae3df039bb4c69604089ebc2dd97535f293f401dcaf032037203d6c7e0`
- exact `is_solution` result: `true`
- altered-hash `is_solution` result: `false`

The live qualification returned `QUALIFIED` with grounded evidence from
`https://github.com/OpenZeppelin/openzeppelin-contracts`. A separate live task
with generic pages returned `AMBIGUOUS` and solved `UNSATISFIABLE`, preserving
fail-closed semantic behavior.

## Liveness hardening

- Active solver/admission bound: 10 bids.
- Total retained bid-history bound: 20 records per task.
- Withdrawn bids release an active slot but remain bounded audit records.
- Direct Mode adversarial coverage proves a replacement slot is available, ten
  active addresses cannot admit an eleventh, and 20 withdraw/submit cycles
  cannot grow task history beyond 20 entries.

## Redundancy proof

- task ID:
- requirement:
- qualification transactions:
- selected coalition:
- solve transaction:

## Unsatisfiable proof

- task ID:
- frozen budget:
- qualification transactions:
- solve transaction:
- terminal state:
## Provenance upgrade pending live deployment

The current review source adds:

- `OPEN` and `FROZEN_PROFILES` admission modes;
- definition-hash binding for the admission set and sealed profile hashes;
- deterministic qualification `receipt_hash` values;
- complete active-matrix `matrix_hash` values bound into `solution_hash`;
- `is_qualification` and `is_solution_bundle` consumer checks.

Live values below this point must be populated only from finalized Studionet
61999 receipts for the new source. Existing deployment evidence above remains
historical evidence for the preceding source.

## Provenance deployment evidence

- Final source commit: `577d52f0a13b09cf3ac0b055fd409678678d377a`
- Final source SHA-256: `0dc05e635ae64e9a0d77c35e2393e9b9a34a06836f248e1822cfda4fca38fee2`
- Contract: `0xcb211f72AecB476c1366102cFD6F4fFa6786be41`
- Deployment: `0x3d0767d7d38ade906f70528fe700d8c59563cd5d0a650f3913c82acb54858e78`
- Result: `FINALIZED / MAJORITY_AGREE / SUCCESS`
- Explorer: `https://explorer-studio.genlayer.com/address/0xcb211f72AecB476c1366102cFD6F4fFa6786be41`

The live frozen-admission setup is recorded in `DEPLOYMENT.md`: profile 1 was
sealed, task 1 was configured with `FROZEN_PROFILES`, sealed, and read back with
definition hash `8567a76058778f31d2a0b7d7d326850d85d2af1dac1c554eb9e0e65988a8acfb`.
The full qualification/solve lifecycle was not claimed: a short-window follow-
up bid finalized after its deadline with `EXPECTED: task is not accepting bids`.
