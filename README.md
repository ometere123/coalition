# COALITION

**Consensus-qualified, deterministically selected multi-provider coalitions for GenLayer.**

COALITION is a standalone GenLayer Intelligent Contract primitive. It forms the lowest-cost team of independently owned providers that jointly satisfies a task's frozen capability requirements.

It deliberately separates **judgement** from **selection**:

```text
public provider evidence
        │
        ▼
GenLayer consensus establishes provider → requirement capability edges
        │
        ▼
QUALIFIED / NOT_QUALIFIED / AMBIGUOUS / UNAVAILABLE
        │
        ▼
deterministic bounded set-cover search
        │
        ▼
lowest-cost valid coalition
```

The AI layer never chooses a winner, invents a price, ranks providers, relaxes a requirement, or creates a compromise coalition. Once the semantic capability matrix exists, ordinary deterministic code computes the result.

COALITION has **no frontend**. It is intended for the standalone Intelligent Contract category and for reuse by marketplaces, autonomous procurement systems, agent orchestrators, grant systems and other Intelligent Contracts.

## Network target

This repository is intentionally pinned to the stable hosted GenLayer environment:

| Setting | Value |
| --- | --- |
| Network | **Studionet** |
| RPC | `https://studio.genlayer.com/api` |
| Chain ID | **61999** |
| Local GenLayer CLI | **0.39.1** |

This repository is **not** configured for `studio-dev`, chain `61997`, or the 0.40 RC CLI family.

The project-local `package.json` pins `genlayer@0.39.1`, so use `npm install` and `npx genlayer ...` (or the npm scripts) even if another GenLayer CLI is installed globally.

## Why this primitive exists

Single-provider markets are easy to model: one task, several providers, one winner.

Many useful tasks are inherently multi-provider:

- a protocol review may need Solidity security + mechanism design + infrastructure analysis;
- a research deliverable may need domain research + statistical review + translation;
- an agent workflow may require a payment specialist + data specialist + compliance specialist;
- a high-assurance task may require two independently qualified reviewers for one capability.

The difficult part is that the capability edges are semantic. A provider may have public evidence that demonstrates Solidity review work without exposing a machine-readable `solidity_security=true` field.

COALITION uses GenLayer only for that irreducibly semantic boundary. It then solves the team-formation problem deterministically.

## Core invariants

### 1. Frozen task definition

A task is editable only while `DRAFT`. Sealing freezes:

- task title and description;
- budget;
- maximum team size;
- bidding deadline;
- every capability requirement;
- each requirement's minimum independent coverage count.

The resulting `definition_hash` is immutable.

### 2. Frozen provider evidence surface

A provider profile is built in `DRAFT`, given 1–3 public HTTPS evidence sources, then sealed.

Sealing creates `profile_hash`. A bid always references that immutable provider profile version. Updating a provider means publishing another profile, not mutating the one already used by a task.

### 3. Bidding closes by time, not requester preference

The creator cannot strategically close bidding early. `close_bidding()` succeeds only after the frozen bidding deadline and can be called by anyone.

One provider address can submit at most one bid to a task, which prevents a provider from flooding the bounded subset search with several profile aliases.

### 4. Validators independently re-observe capability evidence

For every active bid × requirement pair, `resolve_qualification()` asks consensus to establish one bounded edge:

```text
provider profile ──QUALIFIED?──> capability requirement
```

The leader:

1. fetches the profile's frozen public evidence URLs;
2. treats all returned text as hostile data;
3. proposes one bounded verdict;
4. for `QUALIFIED`, supplies a short verbatim evidence excerpt and the exact registered source URL.

A validator independently:

1. re-fetches the same frozen source set;
2. re-runs the semantic capability test;
3. requires the same terminal verdict;
4. verifies any positive excerpt occurs verbatim in its own fetched source;
5. independently checks that the excerpt actually supports the frozen requirement.

A format-correct forged `QUALIFIED` output is therefore insufficient.

### 5. Non-positive verdicts cannot smuggle evidence

`NOT_QUALIFIED`, `AMBIGUOUS` and `UNAVAILABLE` receipts always store empty evidence/source fields.

`QUALIFIED` is the only verdict capable of contributing coverage to a coalition.

### 6. Selection cannot start from a selectively incomplete matrix

Before solving, every active bid must have a terminal qualification receipt for every frozen requirement.

This prevents a caller from simply omitting qualification calls for a cheaper competitor and solving only the favourable subset of the market.

### 7. The LLM never selects the coalition

With at most 10 active bids, the deterministic solver enumerates at most 1,023 non-empty subsets.

A candidate is valid only if:

- member count ≤ `max_team_size`;
- total bid price ≤ `budget`;
- every requirement receives at least `min_coverage` independently qualified members.

Among valid candidates, the winner is chosen by this total order:

1. lowest total price;
2. fewer team members;
3. lexicographically lower bid-ID sequence.

That tie-break makes selection reproducible and reviewable.

### 8. No hidden fallback coalition

If no subset satisfies the frozen requirements, budget and team-size bounds, the task becomes `UNSATISFIABLE`.

The model is never asked to relax requirements, increase the budget, reduce redundancy or improvise a compromise.

## State machine

```text
PROVIDER
DRAFT ──seal──> SEALED
  └──cancel──> CANCELLED

TASK
DRAFT ──seal──> BIDDING ──deadline──> QUALIFYING ──solve──> SOLVED
  │                                                   └──> UNSATISFIABLE
  └──cancel──> CANCELLED

BID
ACTIVE ──withdraw (before deadline)──> WITHDRAWN
ACTIVE ──task solved─────────────────> SELECTED / NOT_SELECTED
```

## Example

A task requires:

```text
SOLIDITY  coverage 1
ECONOMICS coverage 1
budget    100
max team  2
```

Bids:

| Bid | Qualified capabilities | Price |
| --- | --- | ---: |
| A | SOLIDITY | 20 |
| B | ECONOMICS | 25 |
| C | SOLIDITY | 10 |

A naïve "cheapest provider" algorithm picks C for 10 and fails the task.

COALITION's deterministic search evaluates the complete qualification matrix and selects:

```text
C + B = 35
```

because it is the cheapest complete coalition.

## Redundancy

Requirements can demand more than one independently qualified provider:

```text
SECURITY_REVIEW min_coverage = 2
```

A one-member coalition cannot satisfy it even if that member is strongly qualified. Coverage is counted by distinct bid/provider addresses.

This makes the primitive useful for tasks where "one expert says yes" is itself insufficient.

## Contract surface

### Provider lifecycle

- `create_provider(name, summary)`
- `add_provider_evidence(profile_id, label, url)`
- `seal_provider(profile_id)`
- `cancel_provider_draft(profile_id)`

### Task lifecycle

- `create_task(title, description, budget, max_team_size, bidding_deadline)`
- `add_requirement(task_id, label, description, min_coverage)`
- `seal_task(task_id)`
- `cancel_task_draft(task_id)`

### Market / qualification

- `submit_bid(task_id, profile_id, price)`
- `withdraw_bid(bid_id)`
- `close_bidding(task_id)`
- `resolve_qualification(task_id, bid_id, requirement_id)`
- `solve_task(task_id)`

### Reuse / inspection

- `get_provider(...)`
- `get_task(...)`
- `get_requirement(...)`
- `get_bid(...)`
- `get_qualification(...)`
- `get_solution(...)`
- `is_solution(task_id, expected_definition_hash, expected_solution_hash)`

`is_solution(...)` is the narrow consumer boundary intended for another contract that wants to act only on a pinned, solved coalition.

## Security boundaries

COALITION proves only what it claims to prove.

A `QUALIFIED` receipt means:

> independent GenLayer validators agreed that the provider's frozen registered public evidence materially demonstrated the frozen capability requirement at qualification time.

It does **not** mean:

- the provider will perform correctly in the future;
- the provider's website is a government-certified identity source;
- the evidence source can never change later;
- the provider is honest in every context;
- the selected coalition has already performed the task.

Those are different primitives.

## Public-web hardening

Registered evidence URLs:

- must use HTTPS;
- reject credentials/ports in the authority component;
- reject local/internal names;
- reject private IPv4 targets and common wrapper forms;
- are capped in number and per-source readable text size.

Prompts explicitly treat source material as untrusted data and prohibit following embedded instructions. Positive evidence must also be anchored verbatim to the validator's own fetch.

## Bounds

The contract intentionally stays small enough for deterministic exhaustive selection:

| Bound | Maximum |
| --- | ---: |
| Evidence sources / profile | 3 |
| Requirements / task | 6 |
| Bids / task | 10 |
| Coalition members | 5 |
| Minimum coverage / requirement | 3 |
| Candidate subsets | 1,023 |

These are protocol safety limits, not frontend limits.

## Local setup

### Node / stable CLI

```bash
npm install
npx genlayer --version
```

Expected project-local CLI:

```text
0.39.1
```

Do **not** rely on a globally installed `0.40.0rc2` for this repository.

### Direct-mode Python tests

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-test.txt
pytest tests/direct -q
```

Windows users can run these steps under WSL.

## Studionet deployment

```bash
npm install
npm run network:studionet
```

Verify the network output corresponds to:

```text
https://studio.genlayer.com/api
chain ID 61999
```

Then:

```bash
npm run deploy:studionet
```

See [`DEPLOYMENT.md`](DEPLOYMENT.md) before sending a live deployment.

## Reviewer path

A reviewer can understand the core primitive without reading every helper:

1. `create_task()` / `add_requirement()` / `seal_task()` freeze the optimisation problem.
2. `resolve_qualification()` builds the semantic capability matrix through independent validator re-observation.
3. `_assert_qualification_matrix_complete()` prevents selective omission.
4. `_choose_coalition()` performs the bounded deterministic set-cover search.
5. `solve_task()` commits either a unique deterministic coalition or `UNSATISFIABLE`.
6. `is_solution()` exposes a pinned reusable consumer boundary.

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md), [`docs/SECURITY.md`](docs/SECURITY.md), and [`LIVE_DEMO.md`](LIVE_DEMO.md).

## What is deliberately absent

- no frontend;
- no marketplace UI;
- no subjective provider ranking;
- no LLM-selected winner;
- no hidden backend;
- no off-chain database;
- no admin override of a solved task;
- no automatic payment/escrow product flow.

The repository is the primitive itself.
