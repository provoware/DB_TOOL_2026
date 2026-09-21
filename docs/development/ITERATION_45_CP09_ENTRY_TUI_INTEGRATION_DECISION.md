# Iteration 45 — CP-09 Entry TUI Integration Decision

## Decision

A functional entry-create integration **cannot be added without reopening frozen CP-07T runtime**.

The current runtime already owns the required selection provenance: `ProvowareDbTui._categories` is aligned with `#category-list`, `_select_category()` resolves the selected `NavItem.id`, and the existing category refresh preserves category identity by ID. However, there is no entry-write capability injection, entry-create command/input lifecycle, or dedicated post-write entry refresh path.

An external controller would have to duplicate or reach into runtime-owned Textual selection/focus state. That would create a second source of truth and is rejected.

## Smallest justified reopen

A later functional iteration may reopen CP-07T only for:

1. optional `EntryWriteAdapter` injection;
2. exactly one entry-create command, available only when a valid category is selected;
3. one temporary entry-name input with explicit confirm/cancel behavior;
4. capture of the selected category ID from the existing `_categories` + `#category-list` mapping at command time;
5. exactly one adapter call using that captured parent ID;
6. on success, reload entries for that same category while preserving category selection and returning focus predictably;
7. on cancel or failure, no write and no success refresh;
8. direct regressions for no selection, read-only/no-writer mode, success, cancel, domain failure, focus, and unchanged category navigation.

## Freeze boundaries

The reopen does **not** authorize changes to CP-03, schema/migrations, CP-06 domain/repositories, SQLite/storage, `CatalogService`, `EntryWriteAdapter`, CP-08, web, fields/values, undo, trash/restore, autosave, crash recovery, themes, dependencies or CI.

## Evidence

The decision is based on the current runtime contract: category selection is resolved internally from `category_list.index` to `self._categories[index].id`; entry reads are then loaded through `data_port.entries(category_id)`. Category refresh already preserves selected category identity by ID. Therefore selected-category provenance is reliable inside the runtime, but integrating entry creation necessarily changes that frozen runtime.

## Exit gate

I45 is complete when this decision-only two-file diff passes repository-foundation, agent-governance and iteration-scope validation. No product code is permitted in I45.
