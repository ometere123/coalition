# Live reviewer demo

## Main scenario

Freeze a task with:

- `SOLIDITY_SECURITY`, coverage 1
- `MECHANISM_DESIGN`, coverage 1
- budget 100
- maximum team size 2

Create three independently owned sealed profiles and bids:

| Provider | Demonstrated capability | Price |
| --- | --- | ---: |
| Alice | Solidity security | 20 |
| Bob | Mechanism design | 25 |
| Carol | Solidity security | 10 |

The cheapest individual bid is Carol at 10, but Carol cannot cover the whole task.

Expected qualification matrix:

| Provider | Solidity | Mechanism design |
| --- | --- | --- |
| Alice | QUALIFIED | NOT_QUALIFIED |
| Bob | NOT_QUALIFIED | QUALIFIED |
| Carol | QUALIFIED | NOT_QUALIFIED |

Resolve **all six** matrix cells. Then call `solve_task(task_id)`.

Expected deterministic result:

- selected: Bob + Carol
- total cost: 35

It must not choose Alice + Bob at 45, and it must not choose Carol alone at 10 because Carol is incomplete.

## Consumer receipt

Read the task definition hash and solution hash, then call:

`is_solution(task_id, exact_definition_hash, exact_solution_hash)`

Expected: `true`.

Change either hash. Expected: `false`.

## Redundancy proof

Create a second task with `SECURITY_REVIEW min_coverage = 2`, budget 100 and max team size 2. Two distinct providers qualify. The solver must select both; one provider can never satisfy coverage 2.

## Unsatisfiable proof

Create two requirements whose only complete coalition exceeds the frozen budget. Resolve the complete matrix and solve.

Expected terminal state: `UNSATISFIABLE`, with no AI-generated compromise.

## Evidence quality

Use stable public pages that clearly demonstrate the narrow frozen capability. Do not use private dashboards, authenticated pages, or vague marketing copy.
## High-assurance admission path

For the strongest reviewer path, create and seal the required provider
profiles first, then set the task to `FROZEN_PROFILES` and admit the exact
sealed profile IDs in ascending order. Seal the task before any bids are
submitted. Record `definition_hash`, then qualify every active bid/requirement
cell. After solving, record `matrix_hash`, `solution_hash`, and verify them
with `is_solution_bundle`.

This path prevents unrelated profiles from consuming the frozen candidate
universe, but it does not claim that blockchain addresses represent people.
