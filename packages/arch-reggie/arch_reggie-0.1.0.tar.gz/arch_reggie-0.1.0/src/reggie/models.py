"""Data models for the registration checker package."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union
from enum import Enum


class RegistrationStatus(Enum):
    """Enumeration of possible registration statuses."""

    CURRENT_AND_ACTIVE = "current and active"
    EXPIRED = "expired"
    SUSPENDED = "suspended"
    RETIRED = "retired"
    NOT_FOUND = "not found"
    UNKNOWN = "unknown"
    ERROR = "error, check manually"


@dataclass
class Registration:
    """Represents a professional registration."""

    reg_body: Optional[str]
    reg_number: Optional[str]
    reg_status: Union[
        str, RegistrationStatus
    ]  # Accept string, will convert to enum in __post_init__
    additional_data: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Convert string status to enum if needed."""
        if isinstance(self.reg_status, str):
            # Find matching enum value
            for status_enum in RegistrationStatus:
                if status_enum.value == self.reg_status:
                    self.reg_status = status_enum
                    return
            # If no match found, default to ERROR
            self.reg_status = RegistrationStatus.ERROR

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            "reg_body": self.reg_body,
            "reg_number": self.reg_number,
            "reg_status": (
                self.reg_status.value
                if isinstance(self.reg_status, RegistrationStatus)
                else self.reg_status
            ),
        }
        if self.additional_data:
            result.update(self.additional_data)
        return result


@dataclass
class Person:
    """Represents a person with their registrations."""

    full_name: str
    email: str
    linked_in_url: Optional[str] = None
    registrations: List[Registration] = field(default_factory=list)

    @property
    def live_rego_count(self) -> int:
        """Count of current and active registrations."""
        if not self.registrations:
            return 0
        return sum(
            1
            for reg in self.registrations
            if reg.reg_status == RegistrationStatus.CURRENT_AND_ACTIVE
        )

    def add_registration(self, registration: Registration) -> None:
        """Add a registration to this person."""
        self.registrations.append(registration)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "full_name": self.full_name,
            "email": self.email,
            "linked_in_url": self.linked_in_url,
            "registrations": [reg.to_dict() for reg in self.registrations],
            "live_rego_count": self.live_rego_count,
        }


@dataclass
class ProcessingConfig:
    """Configuration for the registration processor."""

    # Column mappings - defaults match the expected CSV format
    email_column: str = "Email"
    full_name_column: str = "Full Name"
    linked_in_url_column: str = "LinkedIn URL"
    reg_body_column: str = "State Board Name"
    reg_number_column: str = "Registration Number"
    state_column: str = "State Board Code"  # This is optional, but useful for debugging

    # CSV handling options - default column names for headerless CSVs
    column_names: Optional[List[str]] = field(default_factory=lambda: [
        "Email",
        "Full Name", 
        "LinkedIn URL",
        "State Board Name",
        "Registration Number",
        "State Board Code",
    ])

    # Processing options
    check_registrations: bool = True
    output_format: str = "json"
    selenium_headless: bool = True
    selenium_implicit_wait: int = 10

    # File paths
    driver_cache_dir: str = "driver"
    output_file: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "columns": {
                "email": self.email_column,
                "full_name": self.full_name_column,
                "linked_in_url": self.linked_in_url_column,
                "reg_body": self.reg_body_column,
                "reg_number": self.reg_number_column,
                "state": self.state_column,
            },
            "csv_handling": {
                "column_names": self.column_names,
            },
            "processing": {
                "check_registrations": self.check_registrations,
                "output_format": self.output_format,
                "selenium_headless": self.selenium_headless,
                "selenium_implicit_wait": self.selenium_implicit_wait,
            },
            "paths": {
                "driver_cache_dir": self.driver_cache_dir,
                "output_file": self.output_file,
            },
        }
