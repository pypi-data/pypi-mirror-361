"""Tests for the registration checker package."""

import pytest
from reggie.models import Person, Registration, ProcessingConfig, RegistrationStatus
from reggie.core import RegistrationProcessor
from reggie.utils import normalise_status
from reggie.checkers.base import RegistrationCheckerRegistry, BaseRegistrationChecker


def test_person_creation():
    """Test creating a Person object."""
    person = Person(
        full_name="John Doe",
        email="john@example.com",
        linked_in_url="https://linkedin.com/in/johndoe",
    )

    assert person.full_name == "John Doe"
    assert person.email == "john@example.com"
    assert person.live_rego_count == 0
    assert len(person.registrations) == 0


def test_registration_creation():
    """Test creating a Registration object."""
    reg = Registration(
        reg_body="NSW Architects Registration Board",
        reg_number="12345",
        reg_status="current and active",
    )

    assert reg.reg_body == "NSW Architects Registration Board"
    assert reg.reg_number == "12345"
    assert reg.reg_status == RegistrationStatus.CURRENT_AND_ACTIVE


def test_person_with_registration():
    """Test person with registrations."""
    person = Person(full_name="Jane Doe", email="jane@example.com")

    reg = Registration(
        reg_body="NSW Architects Registration Board",
        reg_number="54321",
        reg_status="current and active",
    )

    person.add_registration(reg)

    assert len(person.registrations) == 1
    assert person.live_rego_count == 1


def test_processor_config():
    """Test processor configuration."""
    config = ProcessingConfig(email_column="email_address", check_registrations=False)

    processor = RegistrationProcessor(config=config)

    assert processor.config.email_column == "email_address"
    assert processor.config.check_registrations is False


def test_person_to_dict():
    """Test converting person to dictionary."""
    person = Person(full_name="Test Person", email="test@example.com")

    reg = Registration(
        reg_body="Test Body", reg_number="123", reg_status="current and active"
    )

    person.add_registration(reg)

    data = person.to_dict()

    assert data["full_name"] == "Test Person"
    assert data["email"] == "test@example.com"
    assert data["live_rego_count"] == 1
    assert len(data["registrations"]) == 1
    assert data["registrations"][0]["reg_body"] == "Test Body"


# Tests for utils.py functions
class TestNormaliseStatus:
    """Test the normalise_status utility function."""

    def test_current_and_active_statuses(self):
        """Test recognition of current and active statuses."""
        test_cases = [
            "current",
            "Current",
            "CURRENT",
            "active",
            "Active",
            "ACTIVE",
            "architect",
            "Architect",
            "Current and Active",
        ]

        for status in test_cases:
            assert normalise_status(status) == "current and active"

    def test_retired_statuses(self):
        """Test recognition of retired/non-practicing statuses."""
        test_cases = [
            "retired",
            "Retired",
            "RETIRED",
            "non prac architect",
            "Non Prac Architect",
            "non-prac architect",
            "inactive",
            "Inactive",
        ]

        for status in test_cases:
            assert normalise_status(status) == "retired"

    def test_expired_statuses(self):
        """Test recognition of expired statuses."""
        test_cases = [
            "expired",
            "Expired",
            "EXPIRED",
            "Registration Expired",
        ]

        for status in test_cases:
            assert normalise_status(status) == "expired"

    def test_suspended_statuses(self):
        """Test recognition of suspended statuses."""
        test_cases = [
            "suspended",
            "Suspended",
            "SUSPENDED",
            "Registration Suspended",
        ]

        for status in test_cases:
            assert normalise_status(status) == "suspended"

    def test_unknown_statuses(self):
        """Test handling of unknown/unrecognized statuses."""
        test_cases = [
            "unknown status",
            "some weird status",
            "pending",
            "",
            None,
        ]

        for status in test_cases:
            result = normalise_status(status)
            assert result in ["unknown", "error, check manually"]

    def test_case_insensitive(self):
        """Test that status normalization is case insensitive."""
        assert normalise_status("CURRENT") == normalise_status("current")
        assert normalise_status("Expired") == normalise_status("EXPIRED")
        assert normalise_status("Suspended") == normalise_status("suspended")


# Tests for Registration model
class TestRegistration:
    """Test the Registration model."""

    def test_registration_with_string_status(self):
        """Test registration creation with string status that gets converted to enum."""
        reg = Registration(
            reg_body="Test Body",
            reg_number="123",
            reg_status="current and active",
        )

        assert reg.reg_status == RegistrationStatus.CURRENT_AND_ACTIVE
        assert isinstance(reg.reg_status, RegistrationStatus)

    def test_registration_with_enum_status(self):
        """Test registration creation with enum status."""
        reg = Registration(
            reg_body="Test Body",
            reg_number="123",
            reg_status=RegistrationStatus.EXPIRED,
        )

        assert reg.reg_status == RegistrationStatus.EXPIRED
        assert isinstance(reg.reg_status, RegistrationStatus)

    def test_registration_with_invalid_status(self):
        """Test registration with invalid status defaults to ERROR."""
        reg = Registration(
            reg_body="Test Body",
            reg_number="123",
            reg_status="invalid status",
        )

        assert reg.reg_status == RegistrationStatus.ERROR

    def test_registration_to_dict(self):
        """Test converting registration to dictionary."""
        reg = Registration(
            reg_body="NSW Architects Registration Board",
            reg_number="12345",
            reg_status="current and active",
            additional_data={"test_field": "test_value"},
        )

        data = reg.to_dict()

        assert data["reg_body"] == "NSW Architects Registration Board"
        assert data["reg_number"] == "12345"
        assert data["reg_status"] == "current and active"
        assert data["test_field"] == "test_value"

    def test_registration_to_dict_without_additional_data(self):
        """Test converting registration to dictionary without additional data."""
        reg = Registration(
            reg_body="Test Body", reg_number="123", reg_status="expired"
        )

        data = reg.to_dict()

        assert data["reg_body"] == "Test Body"
        assert data["reg_number"] == "123"
        assert data["reg_status"] == "expired"
        assert "additional_data" not in data


# Tests for Person model
class TestPerson:
    """Test the Person model."""

    def test_person_live_rego_count_with_mixed_statuses(self):
        """Test live registration count with mixed registration statuses."""
        person = Person(full_name="Test Person", email="test@example.com")

        # Add current registration
        reg1 = Registration(
            reg_body="Body 1",
            reg_number="123",
            reg_status=RegistrationStatus.CURRENT_AND_ACTIVE,
        )
        person.add_registration(reg1)

        # Add expired registration
        reg2 = Registration(
            reg_body="Body 2",
            reg_number="456",
            reg_status=RegistrationStatus.EXPIRED,
        )
        person.add_registration(reg2)

        # Add another current registration
        reg3 = Registration(
            reg_body="Body 3",
            reg_number="789",
            reg_status=RegistrationStatus.CURRENT_AND_ACTIVE,
        )
        person.add_registration(reg3)

        assert person.live_rego_count == 2
        assert len(person.registrations) == 3

    def test_person_live_rego_count_empty(self):
        """Test live registration count with no registrations."""
        person = Person(full_name="Test Person", email="test@example.com")
        assert person.live_rego_count == 0

    def test_person_to_dict_complete(self):
        """Test person to dict with all fields."""
        person = Person(
            full_name="John Doe",
            email="john@example.com",
            linked_in_url="https://linkedin.com/in/johndoe",
        )

        reg = Registration(
            reg_body="Test Body",
            reg_number="123",
            reg_status="current and active",
        )
        person.add_registration(reg)

        data = person.to_dict()

        assert data["full_name"] == "John Doe"
        assert data["email"] == "john@example.com"
        assert data["linked_in_url"] == "https://linkedin.com/in/johndoe"
        assert data["live_rego_count"] == 1
        assert len(data["registrations"]) == 1


# Tests for ProcessingConfig model
class TestProcessingConfig:
    """Test the ProcessingConfig model."""

    def test_processing_config_defaults(self):
        """Test ProcessingConfig with default values."""
        config = ProcessingConfig()

        assert config.email_column == "email"
        assert config.full_name_column == "full_name"
        assert config.reg_body_column == "reg_body"
        assert config.reg_number_column == "reg_number"
        assert config.check_registrations is True
        assert config.selenium_headless is True
        assert config.output_format == "json"

    def test_processing_config_custom_values(self):
        """Test ProcessingConfig with custom values."""
        config = ProcessingConfig(
            email_column="email_address",
            full_name_column="name",
            check_registrations=False,
            selenium_headless=False,
            output_format="csv",
        )

        assert config.email_column == "email_address"
        assert config.full_name_column == "name"
        assert config.check_registrations is False
        assert config.selenium_headless is False
        assert config.output_format == "csv"

    def test_processing_config_to_dict(self):
        """Test converting ProcessingConfig to dictionary."""
        config = ProcessingConfig(
            email_column="email_address", check_registrations=False
        )

        data = config.to_dict()

        assert data["columns"]["email"] == "email_address"
        assert data["processing"]["check_registrations"] is False
        assert "columns" in data
        assert "csv_handling" in data
        assert "processing" in data
        assert "paths" in data


# Tests for RegistrationCheckerRegistry
class TestRegistrationCheckerRegistry:
    """Test the RegistrationCheckerRegistry class."""

    def test_registry_initialization(self):
        """Test registry initialization."""
        registry = RegistrationCheckerRegistry()
        assert registry.list_supported_bodies() == []
        assert not registry.is_supported("Any Body")

    def test_registry_register_and_get_checker(self):
        """Test registering and retrieving checkers."""

        # Create a mock checker class for testing
        class MockChecker(BaseRegistrationChecker):
            @property
            def registration_body_name(self) -> str:
                return "Mock Registration Body"

            def check_registration(self, reg_number: str, **kwargs):
                return {"status": "mock"}

        registry = RegistrationCheckerRegistry()
        mock_checker = MockChecker(driver=None)

        # Register the checker
        registry.register(mock_checker)

        # Test retrieval
        retrieved_checker = registry.get_checker("Mock Registration Body")
        assert retrieved_checker is not None
        assert retrieved_checker is mock_checker
        assert retrieved_checker.registration_body_name == "Mock Registration Body"

        # Test non-existent checker
        assert registry.get_checker("Non-existent Body") is None

    def test_registry_list_supported_bodies(self):
        """Test listing supported registration bodies."""

        class MockChecker1(BaseRegistrationChecker):
            @property
            def registration_body_name(self) -> str:
                return "Body 1"

            def check_registration(self, reg_number: str, **kwargs):
                return {"status": "mock"}

        class MockChecker2(BaseRegistrationChecker):
            @property
            def registration_body_name(self) -> str:
                return "Body 2"

            def check_registration(self, reg_number: str, **kwargs):
                return {"status": "mock"}

        registry = RegistrationCheckerRegistry()

        # Initially empty
        assert registry.list_supported_bodies() == []

        # Add checkers
        registry.register(MockChecker1(driver=None))
        registry.register(MockChecker2(driver=None))

        supported_bodies = registry.list_supported_bodies()
        assert len(supported_bodies) == 2
        assert "Body 1" in supported_bodies
        assert "Body 2" in supported_bodies

    def test_registry_is_supported(self):
        """Test checking if registration body is supported."""

        class MockChecker(BaseRegistrationChecker):
            @property
            def registration_body_name(self) -> str:
                return "Supported Body"

            def check_registration(self, reg_number: str, **kwargs):
                return {"status": "mock"}

        registry = RegistrationCheckerRegistry()

        # Initially not supported
        assert not registry.is_supported("Supported Body")
        assert not registry.is_supported("Unsupported Body")

        # Add checker
        registry.register(MockChecker(driver=None))

        # Now supported
        assert registry.is_supported("Supported Body")
        assert not registry.is_supported("Unsupported Body")
