class CareerOSError(Exception):
    """Base exception for all Career OS errors."""


class ProfileNotFoundError(CareerOSError):
    pass


class IngestionError(CareerOSError):
    pass


class UnverifiedClaimError(CareerOSError):
    """Raised when the system would otherwise state something not backed
    by evidence in the Profile RAG."""


class UnsafeSourceError(CareerOSError):
    """Raised when a job source fails policy classification or URL safety
    verification."""


class ApprovalRequiredError(CareerOSError):
    """Raised when an irreversible action is attempted without a recorded
    UserApproval."""
