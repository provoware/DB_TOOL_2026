-- PROVOWARE Datenbank – main.db Schema V1
-- Autoritative Nutzerdaten. Keine Testfixtures.

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA synchronous = FULL;
PRAGMA busy_timeout = 5000;
PRAGMA user_version = 1;

CREATE TABLE schema_migrations (
    version INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    checksum TEXT NOT NULL,
    applied_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    app_version TEXT NOT NULL
) STRICT;

CREATE TABLE categories (
    id TEXT PRIMARY KEY NOT NULL,
    name TEXT NOT NULL CHECK (length(trim(name)) BETWEEN 1 AND 120),
    name_key TEXT NOT NULL CHECK (length(name_key) BETWEEN 1 AND 240),
    description TEXT,
    sort_order INTEGER NOT NULL DEFAULT 0 CHECK (sort_order >= 0),
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    deleted_at TEXT,
    revision INTEGER NOT NULL DEFAULT 1 CHECK (revision >= 1)
) STRICT;

CREATE UNIQUE INDEX ux_categories_active_name_key
ON categories(name_key)
WHERE deleted_at IS NULL;

CREATE INDEX ix_categories_active_sort
ON categories(sort_order, name_key)
WHERE deleted_at IS NULL;

CREATE TABLE entries (
    id TEXT PRIMARY KEY NOT NULL,
    category_id TEXT NOT NULL,
    title TEXT NOT NULL CHECK (length(trim(title)) BETWEEN 1 AND 240),
    title_key TEXT NOT NULL CHECK (length(title_key) BETWEEN 1 AND 480),
    is_favorite INTEGER NOT NULL DEFAULT 0 CHECK (is_favorite IN (0,1)),
    sort_order INTEGER NOT NULL DEFAULT 0 CHECK (sort_order >= 0),
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    deleted_at TEXT,
    revision INTEGER NOT NULL DEFAULT 1 CHECK (revision >= 1),
    FOREIGN KEY (category_id) REFERENCES categories(id) ON UPDATE CASCADE ON DELETE RESTRICT
) STRICT;

CREATE INDEX ix_entries_category_active_sort
ON entries(category_id, sort_order, title_key)
WHERE deleted_at IS NULL;

CREATE INDEX ix_entries_category_title_key
ON entries(category_id, title_key)
WHERE deleted_at IS NULL;

CREATE INDEX ix_entries_favorites
ON entries(category_id, title_key)
WHERE deleted_at IS NULL AND is_favorite = 1;

CREATE TABLE field_definitions (
    id TEXT PRIMARY KEY NOT NULL,
    scope TEXT NOT NULL CHECK (scope IN ('category','entry')),
    category_id TEXT,
    entry_id TEXT,
    name TEXT NOT NULL CHECK (length(trim(name)) BETWEEN 1 AND 120),
    name_key TEXT NOT NULL CHECK (length(name_key) BETWEEN 1 AND 240),
    field_type TEXT NOT NULL CHECK (field_type IN (
        'text','long_text','integer','decimal','money','date','datetime',
        'boolean','single_choice','multi_choice'
    )),
    is_required INTEGER NOT NULL DEFAULT 0 CHECK (is_required IN (0,1)),
    sort_order INTEGER NOT NULL DEFAULT 0 CHECK (sort_order >= 0),
    help_text TEXT,
    placeholder TEXT,
    unit_label TEXT,
    currency_code TEXT,
    validation_json TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    deleted_at TEXT,
    revision INTEGER NOT NULL DEFAULT 1 CHECK (revision >= 1),
    CHECK (
        (scope = 'category' AND category_id IS NOT NULL AND entry_id IS NULL)
        OR
        (scope = 'entry' AND category_id IS NULL AND entry_id IS NOT NULL)
    ),
    CHECK (
        (field_type = 'money' AND currency_code IS NOT NULL AND length(currency_code) = 3)
        OR
        (field_type <> 'money' AND currency_code IS NULL)
    ),
    FOREIGN KEY (category_id) REFERENCES categories(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (entry_id) REFERENCES entries(id) ON UPDATE CASCADE ON DELETE RESTRICT
) STRICT;

CREATE UNIQUE INDEX ux_field_defs_category_active_name
ON field_definitions(category_id, name_key)
WHERE scope = 'category' AND deleted_at IS NULL;

CREATE UNIQUE INDEX ux_field_defs_entry_active_name
ON field_definitions(entry_id, name_key)
WHERE scope = 'entry' AND deleted_at IS NULL;

CREATE INDEX ix_field_defs_category_sort
ON field_definitions(category_id, sort_order, name_key)
WHERE scope = 'category' AND deleted_at IS NULL;

CREATE INDEX ix_field_defs_entry_sort
ON field_definitions(entry_id, sort_order, name_key)
WHERE scope = 'entry' AND deleted_at IS NULL;

CREATE TABLE field_options (
    id TEXT PRIMARY KEY NOT NULL,
    field_definition_id TEXT NOT NULL,
    label TEXT NOT NULL CHECK (length(trim(label)) BETWEEN 1 AND 120),
    option_key TEXT NOT NULL CHECK (length(option_key) BETWEEN 1 AND 240),
    sort_order INTEGER NOT NULL DEFAULT 0 CHECK (sort_order >= 0),
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    deleted_at TEXT,
    FOREIGN KEY (field_definition_id) REFERENCES field_definitions(id) ON UPDATE CASCADE ON DELETE RESTRICT
) STRICT;

CREATE UNIQUE INDEX ux_field_options_active_key
ON field_options(field_definition_id, option_key)
WHERE deleted_at IS NULL;

CREATE INDEX ix_field_options_active_sort
ON field_options(field_definition_id, sort_order, option_key)
WHERE deleted_at IS NULL;

CREATE TABLE scalar_field_values (
    entry_id TEXT NOT NULL,
    field_definition_id TEXT NOT NULL,
    value_kind TEXT NOT NULL CHECK (value_kind IN (
        'text','integer','real','decimal_text','money_minor','date','datetime','boolean'
    )),
    value_text TEXT,
    value_integer INTEGER,
    value_real REAL,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    revision INTEGER NOT NULL DEFAULT 1 CHECK (revision >= 1),
    PRIMARY KEY (entry_id, field_definition_id),
    CHECK (
        (value_kind IN ('text','decimal_text','date','datetime')
            AND value_text IS NOT NULL AND value_integer IS NULL AND value_real IS NULL)
        OR
        (value_kind IN ('integer','money_minor')
            AND value_text IS NULL AND value_integer IS NOT NULL AND value_real IS NULL)
        OR
        (value_kind = 'boolean'
            AND value_text IS NULL AND value_integer IN (0,1) AND value_real IS NULL)
        OR
        (value_kind = 'real'
            AND value_text IS NULL AND value_integer IS NULL AND value_real IS NOT NULL)
    ),
    FOREIGN KEY (entry_id) REFERENCES entries(id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (field_definition_id) REFERENCES field_definitions(id) ON UPDATE CASCADE ON DELETE RESTRICT
) STRICT;

CREATE INDEX ix_scalar_values_field
ON scalar_field_values(field_definition_id, entry_id);

CREATE TABLE single_choice_values (
    entry_id TEXT NOT NULL,
    field_definition_id TEXT NOT NULL,
    option_id TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    revision INTEGER NOT NULL DEFAULT 1 CHECK (revision >= 1),
    PRIMARY KEY (entry_id, field_definition_id),
    FOREIGN KEY (entry_id) REFERENCES entries(id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (field_definition_id) REFERENCES field_definitions(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (option_id) REFERENCES field_options(id) ON UPDATE CASCADE ON DELETE RESTRICT
) STRICT;

CREATE INDEX ix_single_choice_option
ON single_choice_values(option_id, entry_id);

CREATE TABLE multi_choice_values (
    entry_id TEXT NOT NULL,
    field_definition_id TEXT NOT NULL,
    option_id TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    PRIMARY KEY (entry_id, field_definition_id, option_id),
    FOREIGN KEY (entry_id) REFERENCES entries(id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (field_definition_id) REFERENCES field_definitions(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (option_id) REFERENCES field_options(id) ON UPDATE CASCADE ON DELETE RESTRICT
) STRICT;

CREATE INDEX ix_multi_choice_option
ON multi_choice_values(option_id, entry_id);

CREATE TABLE audit_events (
    id TEXT PRIMARY KEY NOT NULL,
    operation_id TEXT NOT NULL,
    occurred_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    actor_kind TEXT NOT NULL CHECK (actor_kind IN ('user','system','recovery','migration')),
    action TEXT NOT NULL CHECK (length(action) BETWEEN 1 AND 80),
    entity_type TEXT NOT NULL CHECK (entity_type IN ('category','entry','field_definition','field_value','system')),
    entity_id TEXT,
    category_id TEXT,
    entry_id TEXT,
    summary TEXT NOT NULL CHECK (length(summary) BETWEEN 1 AND 500),
    before_json TEXT,
    after_json TEXT,
    is_undoable INTEGER NOT NULL DEFAULT 0 CHECK (is_undoable IN (0,1)),
    app_version TEXT NOT NULL,
    schema_version INTEGER NOT NULL CHECK (schema_version >= 1)
) STRICT;

CREATE INDEX ix_audit_events_time
ON audit_events(occurred_at DESC);

CREATE INDEX ix_audit_events_entity
ON audit_events(entity_type, entity_id, occurred_at DESC);

CREATE INDEX ix_audit_events_operation
ON audit_events(operation_id);
