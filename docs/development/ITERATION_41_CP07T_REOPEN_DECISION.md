# Iteration 41 – CP-07T Reopen Decision

## Decision

I41 is a decision-only iteration. No product code is changed.

The external-controller candidate from I40 is not sufficient for the complete category-create interaction. `ProvowareDbTui` owns the Textual `App`, its key bindings, widget tree, focus handling and the existing `action_refresh_categories()` path. It accepts only `TuiDataPort`; there is no public input, command, callback or controller hook through which an external layer can collect a category name, invoke `CategoryWriteAdapter`, report a conflict and then request the existing in-app refresh without reaching into private runtime state.

Creating a second external event loop or mutating Textual widgets from outside the App would duplicate lifecycle/focus ownership and would be a less safe architecture than an explicit narrow reopen.

Therefore the next functional step requires an **explicit minimal CP-07T reopen**. This decision does not itself reopen or modify CP-07T.

## Narrow reopen boundary for the next functional iteration

Only the following CP-07T surface may be considered for reopening:

1. inject the already-frozen `CategoryWriteAdapter` into `ProvowareDbTui` as an optional write capability;
2. add exactly one explicit category-create command/binding;
3. collect one category name through a minimal Textual-owned input interaction;
4. invoke the adapter exactly once after explicit confirmation;
5. show success or the existing conflict/error at the presentation boundary;
6. on success only, reuse `action_refresh_categories()` rather than create a second refresh implementation;
7. preserve existing category → entry → field navigation, focus behavior outside the temporary input interaction, health/events surfaces and layout policy.

The write capability should remain optional so the existing read-only construction contract can continue to work and its regressions remain meaningful.

## Frozen boundaries

Remain closed: CP-03/schema/migrations, CP-06/domain/repositories, `storage/sqlite/**`, `CatalogService`, `CategoryWriteAdapter`, CP-08 health/events, web/browser UI, entry/field/value writes, trash/restore, undo, autosave, crash recovery, themes and CI/dependencies.

The next implementation must not rename or refactor unrelated CP-07T code merely because `runtime.py` is narrowly reopened.

## Required direct regressions for the reopen implementation

- existing read-only `ProvowareDbTui(data_port)` behavior remains valid;
- category-create capability is unavailable when no write adapter is injected;
- one confirmed valid name calls the adapter exactly once;
- success refreshes categories exactly through the existing refresh path and makes the new category visible;
- conflict/error performs no success refresh and is shown without corrupting navigation/focus;
- cancel performs no write;
- existing category → entry → field navigation remains green;
- directly affected TUI layout/focus test is run; visual evidence is required only if the implementation changes rendered geometry rather than using a transient overlay/input.

## Exit gate for I41

I41 is complete only when this decision document and its manifest are the sole changes and repository-foundation, agent-governance and iteration-scope gates are green. Only after I41 is frozen may a fresh iteration implement the narrow reopen above.

## Remaining risk

The exact Textual input primitive is intentionally not selected here. The implementation iteration must choose the smallest primitive supported by the repository's installed Textual version and must not widen the reopen to a general form framework, CRUD system or layout redesign.
