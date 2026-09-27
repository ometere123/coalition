# Review evidence

Verified live evidence for COALITION on **Studionet chain 61999**.

## Deployment

- repository commit used: see final commit containing this exact deployed source
- local CLI version: `0.39.1`
- network: Studionet
- RPC: `https://studio.genlayer.com/api`
- chain ID: `61999`
- contract address: `0x19b6bB183859b4418c6347C24Fa15d09316e432f`
- deployment transaction: `0x6a057cf8f50d3dc48ec3e4ded57bf295defc7a3c581875f97983a5341a970e81`
- finality evidence: `FINALIZED / ACCEPTED / SUCCESS`

## Direct Mode

- CI run: https://github.com/ometere123/coalition/actions/runs/36349467079
- tested commit: `fe89002543a0c226ba1bd49318a90de3d1024423`
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
