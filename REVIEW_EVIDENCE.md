# Review evidence

This file intentionally contains no fabricated deployment information.

Fill it only after COALITION has been tested and finalized on **Studionet chain 61999**.

## Deployment

- repository commit used:
- local CLI version:
- network:
- RPC:
- chain ID:
- signer address:
- contract address:
- deployment transaction:
- finality evidence:

## Direct Mode

- CI run: https://github.com/ometere123/coalition/actions/runs/36338787962
- tested commit: `77613bdf6ac9f6a5616f1ca73dd19bc824ddf7dd`
- runner OS: Ubuntu 24.04 GitHub-hosted runner
- Python: 3.12
- local application CLI verified by CI: `0.39.1`
- Direct Mode harness: `genlayer-testing-suite@v0.29.2`
- GenVM runner bundle: `v0.3.0-rc7`
- contract runner hash verified in bundle: `py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6`
- static preflight: **passed**
- test command: `pytest tests/direct -q`
- passed count: **13**
- failed count: **0**
- runtime: **31.12s**
- notes: the repository includes `scripts/prepare_direct_mode.py` because the stable v0.29.2 harness expects the historical universal-bundle cache name while the official rc7 release now publishes the runner archive as `genvm-runners-all.tar.xz`.

## Main coalition proof

- task ID:
- task definition hash:
- provider profile IDs/hashes:
- bid IDs/prices:
- qualification transaction hashes:
- solve transaction:
- selected bid IDs:
- total cost:
- solution hash:
- exact `is_solution` result:
- altered-hash `is_solution` result:

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
