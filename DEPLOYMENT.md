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
