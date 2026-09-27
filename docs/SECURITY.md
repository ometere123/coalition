# Security model

## Hostile public evidence

Provider-controlled pages are untrusted. COALITION bounds public HTTPS sources, rejects obvious local/private URL forms, treats source text as hostile data, independently re-fetches it in the validator, and requires positive evidence to be verbatim source-grounded.

A schema-valid leader response is not enough.

## Selective omission

A task cannot be solved while any active bid lacks a terminal qualification receipt for any frozen requirement. Qualification is permissionless after bidding closes.

## Early close manipulation

The bidding deadline is frozen into the task definition. `close_bidding` reverts before it and may be called by anyone after it.

## Evidence mutability

Profile metadata and source URLs are immutable after sealing. The external page at a URL can still change, so a qualification is an observation-time consensus result, not a future-performance guarantee.

## Sybil boundary

One provider address can occupy only one bid slot per task. In `OPEN` mode this
is bounded admission, not real-world identity or Sybil resistance. In
`FROZEN_PROFILES` mode the task creator freezes the exact sealed candidate set
before bidding; duplicate owners are rejected and outsiders cannot consume
the frozen solver slots. This is an admission policy, not an identity oracle.

## Cryptographic provenance

Sealed profiles commit their public evidence with `profile_hash`. A frozen task
commits its requirements and admission set with `definition_hash`. Each
qualification cell commits its exact semantic result and source-grounded
evidence with `receipt_hash`. Solving commits the complete active matrix,
including non-selected bids, with `matrix_hash`, and binds that hash into the
deterministic `solution_hash`.

## Subjective optimisation

There is none. GenLayer consensus determines capability edges only. It does not rank providers, compare prices, alter budgets, reduce coverage, or invent fallback requirements.

## Combinatorial bound

Ten bids cap exhaustive selection at 1,023 non-empty subsets.

## Task-author bias

The requester controls requirement wording. COALITION guarantees deterministic formation relative to the frozen task; it does not claim the task specification itself is unbiased.

## Non-goals

COALITION is not identity verification, reputation, escrow, completion adjudication, future-performance insurance, a web-authority oracle, or a frontend marketplace.
