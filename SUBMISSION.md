# COALITION — submission notes

COALITION is a standalone GenLayer Intelligent Contract primitive for forming multi-provider teams.

The hard part is not choosing the cheapest provider. It is establishing which independently owned providers actually demonstrate each natural-language capability, then finding the cheapest team that jointly covers every frozen requirement.

COALITION splits that problem cleanly:

1. GenLayer consensus establishes only provider → requirement qualification edges from frozen public evidence.
2. Deterministic code selects the lowest-cost subset satisfying every requirement, coverage count, budget and team-size constraint.

The LLM never chooses a winner, ranks bids, changes prices, relaxes requirements or invents a compromise.

## Why GenLayer is necessary

A deterministic contract can solve a capability matrix once the matrix exists. It cannot reliably infer from public documentation, portfolios or completed-work records whether a provider materially demonstrates a natural-language capability.

For `QUALIFIED`, validators independently re-fetch the provider's sealed source set, independently re-evaluate the requirement, require the same terminal verdict, require the positive excerpt to occur verbatim in the validator's own fetch, and independently check that the excerpt supports the frozen requirement.

## Deterministic selection

At most 10 bids are accepted, bounding the non-empty subset space to 1,023 candidates.

A candidate is valid only if its total cost is within budget, member count is within the frozen maximum, and every requirement reaches `min_coverage` qualified providers.

Valid candidates are ordered by: lowest total cost, then fewer members, then lower bid-ID sequence.

If no candidate works, the task becomes `UNSATISFIABLE`.

## Integrity properties

- task definition is hash-pinned before bidding;
- provider evidence surface is hash-pinned before bidding;
- bidding cannot be closed before the frozen deadline;
- one bid per provider address per task;
- every active bid × requirement cell must be resolved before solving;
- non-positive qualification receipts cannot carry positive evidence;
- semantic consensus never controls prices or winner selection;
- solved tasks expose immutable definition and solution hashes.

## Category fit

COALITION intentionally has no frontend, marketplace UI, hidden backend or off-chain database. It is a reusable contract primitive.

Target: **Studionet / chain 61999 / https://studio.genlayer.com/api**.

The repository pins **GenLayer CLI 0.39.1** locally and intentionally does not target Studio-dev / 61997.
## Current quality pass

The current source adds an explicit high-assurance admission option without
removing open bidding. `FROZEN_PROFILES` freezes sealed profile IDs before
bidding and binds them into the task definition hash. Qualification receipts
and the complete active qualification matrix are also hash-pinned, so a
consumer can verify both semantic-cell provenance and the exact decision
surface used by the deterministic solver.

The final address and lifecycle values for this source will be added only from
finalized Studionet 61999 receipts.
