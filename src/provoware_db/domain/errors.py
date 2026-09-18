class DomainError(RuntimeError):
    """Base exception for user/domain level rule violations."""


class NotFoundError(DomainError):
    """A requested active domain object does not exist."""


class ConflictError(DomainError):
    """A uniqueness/business conflict prevents the requested operation."""


class ValidationError(DomainError):
    """Input is structurally valid Python but violates a domain rule."""


class RevisionConflictError(ConflictError):
    """Optimistic locking conflict: object changed since it was loaded."""
