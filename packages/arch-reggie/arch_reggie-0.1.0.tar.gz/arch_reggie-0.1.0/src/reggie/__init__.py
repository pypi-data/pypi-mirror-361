"""Registration Checker - A package for checking professional registration status."""

from .core import RegistrationProcessor
from .models import Person, Registration, ProcessingConfig, RegistrationStatus
from .checkers.base import BaseRegistrationChecker, RegistrationCheckerRegistry

__version__ = "0.1.0"
__author__ = "Ben Doherty"
__email__ = "ben_doherty@bvn.com.au"

__all__ = [
    "RegistrationProcessor",
    "Person",
    "Registration",
    "ProcessingConfig",
    "RegistrationStatus",
    "BaseRegistrationChecker",
    "RegistrationCheckerRegistry",
]
