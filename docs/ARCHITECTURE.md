# Architecture

## Boundary

COALITION has two layers.

### Semantic consensus

Consensus answers one bounded question:

> Does this provider's sealed public evidence materially demonstrate this frozen capability requirement?

Possible receipts are `QUALIFIED`, `NOT_QUALIFIED`, `AMBIGUOUS`, or `UNAVAILABLE`.

Positive receipts must be anchored to a short verbatim excerpt from a registered public source. Validators independently re-fetch and re-judge.

### Deterministic mechanics

Prices, budgets, team-size bounds, minimum coverage, subset enumeration, tie-breaking and final winner selection are ordinary deterministic code.

No model sees all bids and returns a preferred coalition.

## State objects

- `ProviderProfile`: immutable after sealing; pins evidence URLs and a profile hash.
- `Task`: freezes budget, deadline, team size and requirement set.
- `Requirement`: natural-language capability plus deterministic `min_coverage`.
- `Bid`: sealed profile reference plus deterministic price.
- `Qualification`: one consensus receipt for one `(bid, requirement)` cell.

## Complete matrix requirement

Selection cannot start until every active bid has a terminal receipt for every task requirement. This prevents a caller from omitting a cheaper competitor and solving only the favourable part of the market.

`NOT_QUALIFIED`, `AMBIGUOUS` and `UNAVAILABLE` are terminal cells but contribute zero coverage.

## Exact bounded solver

`MAX_BIDS = 10`, so at most `2^10 - 1 = 1023` non-empty candidate subsets are inspected.

A candidate survives only when it meets every deterministic task constraint.

Valid candidates are totally ordered by `(total_price, member_count, bid_id_sequence)`.

## Reuse

A consumer can pin both the expected task and exact coalition receipt through:

`is_solution(task_id, expected_definition_hash, expected_solution_hash)`
