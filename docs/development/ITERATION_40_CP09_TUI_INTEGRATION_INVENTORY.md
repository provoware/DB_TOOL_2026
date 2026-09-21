# Iteration 40 – CP-09 TUI integration inventory

## Decision

I40 is read-only planning. No product code is changed.

The current TUI runtime is still an explicitly read-only CP-07T shell. It accepts only `TuiDataPort`, exposes `q` and category refresh (`r`), and contains no text input, modal, write-service injection, or composition root for `CategoryWriteAdapter`.

I39 deliberately created only the write adapter seam and explicitly deferred input binding, user-facing error wording, and refresh behavior.

## Smallest safe integration boundary

The next functional step must not edit frozen `runtime.py` directly without an explicit CP-07T reopen decision. The smallest candidate is therefore a new write-capable TUI composition/controller layer that:

1. injects the frozen `CategoryWriteAdapter` beside the read port;
2. owns category-name collection outside the frozen runtime contract;
3. invokes the adapter exactly once after explicit user confirmation;
4. converts success/conflict into a presentation result without changing CatalogService/domain/storage;
5. requests the already-existing category refresh path only after successful creation.

Whether Textual can attach that controller without modifying `ProvowareDbTui` is the gate for the next iteration. If not, the next step must be an explicit, narrowly scoped CP-07T reopen; it must not silently patch `runtime.py`.

## Frozen boundaries

Remain closed:

- CP-03 schema/migrations and fixtures;
- CP-06 domain/repository contracts;
- `src/provoware_db/storage/sqlite/**`;
- `CatalogService` implementation and category-create contract;
- existing CP-07T runtime/navigation/layout/refresh semantics;
- CP-08 health/events;
- entry/field/value writes;
- trash/restore, undo, autosave and crash recovery;
- browser/web UI.

## Exit gates

I40 is complete when:

- this inventory and its iteration manifest are the only changed files;
- repository foundation, agent governance and iteration-scope gates are green;
- no product/runtime file changed;
- the next iteration is constrained to either a controller/composition seam with no frozen edit, or a separate explicit CP-07T reopen decision.
