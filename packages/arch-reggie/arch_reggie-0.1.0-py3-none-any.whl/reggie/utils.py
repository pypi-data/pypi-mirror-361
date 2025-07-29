"""Utility functions for the registration checker package."""

from .models import RegistrationStatus


def normalise_status(status: str) -> str:
    """
    Normalize registration status to standard format across all checkers.

    This function provides a single source of truth for status normalization,
    ensuring consistent return values across different registration bodies.

    Args:
        status: Raw status string from any registration website (case-insensitive)

    Returns:
        Normalized status string. Possible values:
            - "current and active": For active/current registrations
            - "expired": For expired registrations
            - "suspended": For suspended registrations
            - "retired": For retired/non-practicing registrations
            - "error, check manually": For unrecognized statuses that need manual review

    Examples:
        >>> normalise_status("Current")
        "current and active"
        >>> normalise_status("Architect")  # QLD-specific
        "current and active"
        >>> normalise_status("Non Prac Architect")  # QLD-specific
        "retired"
        >>> normalise_status("EXPIRED")
        "expired"
        >>> normalise_status("Unknown Status")
        "check manually"
    """
    if not status:
        return RegistrationStatus.UNKNOWN.value

    # Convert to lowercase for case-insensitive matching
    status_lower = status.strip().lower()

    # Retired/Non-practicing statuses
    if any(
        keyword in status_lower
        for keyword in ["retired", "non prac", "non-prac", "inactive"]
    ):
        return RegistrationStatus.RETIRED.value

    # Active/Current statuses
    if any(keyword in status_lower for keyword in ["current", "active", "architect"]):
        # Special case for QLD "Non Prac Architect" which should be retired
        if "non prac" in status_lower or "non-prac" in status_lower:
            return RegistrationStatus.RETIRED.value
        return RegistrationStatus.CURRENT_AND_ACTIVE.value

    # Expired statuses
    if "expired" in status_lower:
        return RegistrationStatus.EXPIRED.value

    # Suspended statuses
    if "suspended" in status_lower:
        return RegistrationStatus.SUSPENDED.value

    # Default for unrecognized statuses
    return RegistrationStatus.ERROR.value
