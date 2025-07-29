#!/usr/bin/env python3
"""
Example usage of the Arch Reggie registration checker package.

This script demonstrates the basic usage patterns shown in the README.
"""

import sys
from pathlib import Path

# Add the package to the path for development
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from reggie import RegistrationProcessor, ProcessingConfig


def basic_usage_example():
    """Demonstrate basic usage with default configuration."""
    print("=== Basic Usage Example ===")

    # Initialize with default configuration (now works with the test CSV format)
    processor = RegistrationProcessor()

    # Process a CSV file (using test data)
    csv_path = "tests/test_data/example_input.csv"

    print(
        f"Processing: {csv_path}\n"
        "Using default configuration:\n"
        f"  Column names: {processor.config.column_names}\n"
        f"  Check registrations: {processor.config.check_registrations}\n"
    )

    results = processor.process_csv(csv_path)

    # Save results as JSON
    processor.save_json(results, "example_output.json")

    print(f"Processed {len(results)} people")
    print("Results saved to: example_output.json")


def custom_config_example():
    """Demonstrate usage with custom configuration."""
    print("\n=== Custom Configuration Example ===")

    # Create custom configuration for different CSV format or processing options
    config = ProcessingConfig(
        # If your CSV has different column names, you can specify them:
        # column_names=["email", "name", "linkedin", "body", "number", "state"],
        # email_column="email",
        # full_name_column="name",
        # Processing options you might want to customize:
        check_registrations=False,  # Skip web scraping for faster testing
        selenium_headless=False,  # Show browser window for debugging
        selenium_implicit_wait=3,  # Faster timeouts
        output_format="json",
    )

    processor = RegistrationProcessor(config=config)

    # Show supported registration bodies
    supported_bodies = processor.get_supported_bodies()
    print(f"Supported registration bodies: {supported_bodies}")

    print("Custom configuration:")
    print(f"  Check registrations: {config.check_registrations}")
    print(f"  Selenium headless: {config.selenium_headless}")
    print(f"  Default column names: {config.column_names}")


def main():
    """Run all examples."""
    print("Arch Reggie - Example Usage")
    print("=" * 40)

    try:
        basic_usage_example()
        # custom_config_example()

        print("\n✅ Examples completed successfully!")

    except Exception as e:
        print(f"❌ Error running examples: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
