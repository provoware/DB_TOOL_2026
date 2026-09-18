class StorageError(RuntimeError):
    """Base storage exception."""


class ProductionPathGuardError(StorageError):
    """A test attempted to access a forbidden production path."""


class MigrationError(StorageError):
    """Migration failed or drift was detected."""


class SchemaGuardError(StorageError):
    """Database identity/schema did not match expectations."""


class PreValidationError(StorageError):
    """Write was blocked before mutation."""


class PostValidationError(StorageError):
    """Mutation did not satisfy transactional postconditions."""


class PostCommitValidationError(StorageError):
    """Committed state could not be verified; caller should enter safe mode."""
