#!/usr/bin/env python3
"""
Debug script for stepping through the registration checker code.

This script provides a convenient entry point for debugging the registration
checker package. You can set breakpoints and step through the code to understand
how it works.

Usage:
1. Set breakpoints in VS Code or your debugger
2. Run this script in debug mode
3. Step through the code to see how it processes registrations

Key areas to explore:
- RegistrationProcessor.process_csv() - Main processing logic
- BaseRegistrationChecker and subclasses - Individual checker implementations
- Person and Registration models - Data structures
"""

import os
import sys
import logging
from pathlib import Path

# Configure logging for verbose output
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Add the package to the path for development
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from reggie import RegistrationProcessor, ProcessingConfig
from reggie.models import Person, Registration
from reggie.checkers.qld import QLDArchitectsChecker
from reggie.checkers.nsw import NSWArchitectsChecker


def debug_single_registration():
    """
    Debug a single registration check.

    This function demonstrates how to check a single registration
    and is useful for debugging the checker logic.
    """
    print("=== Debug Single Registration ===")

    # Example registration number - replace with a real one for testing
    test_reg_number = "12345"

    # Create a QLD checker instance
    qld_checker = QLDArchitectsChecker()

    print(f"Checking registration number: {test_reg_number}")
    print(f"Registration body: {qld_checker.registration_body_name}")

    # Set a breakpoint here to step through the check_registration method
    result = qld_checker.check_registration(test_reg_number)

    print(f"Result: {result}")

    # Clean up
    qld_checker.cleanup()

    return result


def debug_person_creation():
    """
    Debug the creation and manipulation of Person objects.

    This function shows how Person and Registration objects work together.
    """
    print("\n=== Debug Person Creation ===")

    # Create a person
    person = Person(
        full_name="John Test",
        email="john.test@example.com",
        linked_in_url="https://linkedin.com/in/johntest",
    )

    print(f"Created person: {person.full_name}")
    print(f"Initial registration count: {person.live_rego_count}")
    print(f"Registrations list length: {len(person.registrations)}")

    # Create a registration
    registration = Registration(
        reg_body="Board of Architects of Queensland",
        reg_number="12345",
        reg_status="current and active",
        additional_data={"test_field": "test_value"},
    )

    print(f"Created registration: {registration.reg_body} - {registration.reg_number}")

    # Add registration to person
    person.add_registration(registration)

    print(f"After adding registration:")
    print(f"  Registration count: {person.live_rego_count}")
    print(f"  Registrations list length: {len(person.registrations)}")

    # Convert to dict for inspection
    person_dict = person.to_dict()
    print(f"Person as dict: {person_dict}")

    return person


def debug_csv_processing():
    """
    Debug the CSV processing workflow.

    This is the main entry point that mirrors your calling code.
    """
    print("\n=== Debug CSV Processing ===")

    # Check if the CSV file exists
    csv_path = "tests/test_data/example_input.csv"
    if not os.path.exists(csv_path):
        print(f"WARNING: CSV file not found at {csv_path}")
        print("Creating a sample CSV for debugging...")
        # Create long format sample without headers (matching your real CSV format)
        csv_path = "sample_long_no_headers.csv"
        create_sample_long_format_no_headers(csv_path)

    #  For headerless CSV in long format (State Code, Registration Number columns)
    config = ProcessingConfig(
        check_registrations=True,
        column_names=[
            "Email",
            "Full Name",
            "LinkedIn URL",
            "State Board Name",
            "Registration Number",
            "State Board Code",
        ],
        # Configure column names
        full_name_column="Full Name",
        email_column="Email",
        linked_in_url_column="LinkedIn URL",
        reg_body_column="State Board Name",  # Fixed: changed from "State Code" to "State Board Name"
        reg_number_column="Registration Number",
        state_column="State Board Code",  # Added this for the actual state code column
        # Make browser visible and add debugging options
        selenium_headless=False,  # Show browser window
        selenium_implicit_wait=5,  # Reduce wait time for faster debugging
    )

    # For debugging, enable actual registration checking to see the verbose output
    config.check_registrations = True  # Set to False if you want to skip web scraping

    print(f"Created config with check_registrations: {config.check_registrations}")
    print(f"Column names: {config.column_names}")

    # Create processor
    processor = RegistrationProcessor(config=config)

    print(f"Created processor with config")
    print(f"Available checkers: {processor.get_supported_bodies()}")

    print(f"Processing CSV: {csv_path}")

    # Set a breakpoint here to step through the CSV processing
    try:
        people = processor.process_csv(csv_path)

        print(f"Processed {len(people)} people")

        # Show details of first person for debugging
        if people:
            first_person = people[0]
            print(f"First person: {first_person.full_name}")
            print(f"  Registrations: {len(first_person.registrations)}")
            print(f"  Live registrations: {first_person.live_rego_count}")

        # Save results
        output_path = os.path.join("intermediate_data", "reg_results.json")
        os.makedirs("intermediate_data", exist_ok=True)

        processor.save_json(people, output_path)

        print(f"Saved results to: {output_path}")

        return people

    except Exception as e:
        print(f"Error during processing: {e}")
        import traceback

        traceback.print_exc()
        return []


def create_sample_csv(csv_path):
    """Create a sample CSV file for testing if one doesn't exist."""
    import pandas as pd

    # Ensure directory exists
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)

    # Also create the long format version for reference WITH headers
    long_format_path = csv_path.replace(".csv", "_long_format.csv")
    long_sample_data = {
        "Full Name": ["John Test", "John Test", "Jane Test", "Bob Test"],
        "Email": ["john@test.com", "john@test.com", "jane@test.com", "bob@test.com"],
        "LinkedIn URL": [
            "https://linkedin.com/in/johntest",
            "https://linkedin.com/in/johntest",
            "https://linkedin.com/in/janetest",
            "https://linkedin.com/in/bobtest",
        ],
        "Registration Body": [
            "Board of Architects of Queensland",
            "NSW Architects Registration Board",
            "NSW Architects Registration Board",
            "Board of Architects of Queensland",
        ],
        "Registration Number": ["12345", "67890", "ABC123", "DEF456"],
    }

    long_df = pd.DataFrame(long_sample_data)
    long_df.to_csv(long_format_path, index=False)
    print(f"Created long format sample (with headers) at: {long_format_path}")

    print(f"Long format CSV content (for reference):")
    with open(long_format_path, "r") as f:
        lines = f.readlines()[:3]  # Show first 3 lines
        print("".join(lines) + "...")


def create_sample_long_format_no_headers(csv_path):
    """Create a sample CSV in long format WITHOUT headers (matching user's real CSV format)."""
    import pandas as pd

    # Create long format sample data (one row per registration) - NO HEADERS
    # Columns: Full Name, Email, LinkedIn URL, State Code, Registration Number
    long_sample_data = [
        [
            "John Test",
            "john@test.com",
            "https://linkedin.com/in/johntest",
            "QLD",  # State Code (column 4)
            "12345",  # Registration Number (column 5)
        ],
        [
            "John Test",
            "john@test.com",
            "https://linkedin.com/in/johntest",
            "NSW",  # State Code (column 4)
            "67890",  # Registration Number (column 5)
        ],
        [
            "Jane Test",
            "jane@test.com",
            "https://linkedin.com/in/janetest",
            "NSW",  # State Code (column 4)
            "ABC123",  # Registration Number (column 5)
        ],
        [
            "Bob Test",
            "bob@test.com",
            "https://linkedin.com/in/bobtest",
            "QLD",  # State Code (column 4)
            "DEF456",  # Registration Number (column 5)
        ],
    ]

    # Ensure directory exists
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)

    # Save without headers (matching your real CSV format)
    long_df = pd.DataFrame(long_sample_data)
    long_df.to_csv(csv_path, index=False, header=False)

    print(f"Created long format sample CSV (NO HEADERS) at: {csv_path}")
    print("Columns: Full Name, Email, LinkedIn URL, State Code, Registration Number")
    print("Sample data:")
    for i, row in enumerate(long_sample_data[:3]):  # Show first 3 rows
        print(f"  Row {i+1}: {row}")
    print("...")

    return csv_path


def main():
    """
    Main debug function - your entry point for debugging.

    Set breakpoints in this function and the functions it calls
    to step through the entire workflow.
    """
    print("Starting registration checker debug session...")
    print("=" * 50)

    # Uncomment the debug functions you want to run:

    # 1. Debug single registration check
    # debug_single_registration()

    # 2. Debug person creation and manipulation
    # debug_person_creation()

    # 3. Debug full CSV processing (this mirrors your main function)
    people = debug_csv_processing()

    print(f"\nDebug session complete. Processed {len(people)} people.")

    return people


if __name__ == "__main__":
    # This is the entry point when running the script directly
    # Set breakpoints here or in main() and run in debug mode

    print("Debug script starting...")
    print("Set breakpoints and step through the code!")

    try:
        result = main()
        print(
            f"Script completed successfully. Result: {len(result) if result else 0} people processed"
        )
    except Exception as e:
        print(f"Script failed with error: {e}")
        import traceback

        traceback.print_exc()
