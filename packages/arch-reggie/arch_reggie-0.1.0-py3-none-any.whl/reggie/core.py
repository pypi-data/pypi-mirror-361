"""Core registration processing functionality."""

import json
import logging
from pathlib import Path
from typing import List, Optional, Union
import pandas as pd
from numpy import nan as np_nan
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.driver_cache import DriverCacheManager


from .models import Person, Registration, ProcessingConfig
from .checkers.base import RegistrationCheckerRegistry, get_registered_checkers
# Import checker modules to trigger registration
from .checkers import nsw, qld


logger = logging.getLogger(__name__)


class RegistrationProcessor:
    """Main class for processing registration data."""

    def __init__(self, config: Optional[ProcessingConfig] = None):
        """
        Initialize the registration processor.

        Args:
            config: Processing configuration. If None, uses defaults.
        """
        self.config = config or ProcessingConfig()
        self.driver: Optional[WebDriver] = None
        self.registry = RegistrationCheckerRegistry()
        self._setup_checkers()

    def _setup_checkers(self) -> None:
        """Set up the registration checkers."""
        # Note: Checkers will be registered when driver is created
        pass

    def _create_driver(self) -> WebDriver:
        """Create and configure a WebDriver instance."""
        try:
            options = webdriver.ChromeOptions()
            options.add_argument("--ignore-certificate-error")
            options.add_argument("--ignore-ssl-errors")

            if self.config.selenium_headless:
                options.add_argument("--headless")

            # Set up driver cache
            driver_cache_manager = DriverCacheManager(
                root_dir=self.config.driver_cache_dir
            )
            service = Service(
                ChromeDriverManager(cache_manager=driver_cache_manager).install()
            )

            driver = webdriver.Chrome(service=service, options=options)
            driver.implicitly_wait(self.config.selenium_implicit_wait)

            return driver

        except (ValueError, NameError) as val_err:
            logger.warning(
                f"ChromeDriverManager failed: {val_err}. Trying local driver."
            )
            try:
                driver = webdriver.Chrome()
                driver.implicitly_wait(self.config.selenium_implicit_wait)
                return driver
            except WebDriverException as wde:
                logger.error(f"Chrome driver failed: {wde}")
                raise wde

    def _register_checkers(self) -> None:
        """Register all available checkers with the driver."""
        if not self.driver:
            return

        # Auto-register all decorated checkers
        for checker_class in get_registered_checkers():
            try:
                checker_instance = checker_class(self.driver)
                self.registry.register(checker_instance)
                logger.debug(f"Registered checker: {checker_class.__name__}")
            except Exception as e:
                logger.warning(f"Failed to register checker {checker_class.__name__}: {e}")

    def process_csv(
        self, file_path: Union[str, Path], encoding: str = "utf-8"
    ) -> List[Person]:
        """
        Process a CSV file containing registration data.

        Args:
            file_path: Path to the CSV file
            encoding: File encoding

        Returns:
            List of Person objects with registration data
        """
        # Read CSV file
        df = pd.read_csv(
            file_path,
            encoding=encoding,
            na_values=["NULL", ""],
            header=None,
            names=self.config.column_names,
        )

        # Clean data
        df = df.fillna(np_nan).replace([np_nan], [None])

        logger.info(
            f"Processing {len(df)} rows covering {len(df[self.config.full_name_column].unique())} people"
        )
        print(
            f"Processing {len(df)} rows covering {len(df[self.config.full_name_column].unique())} people"
        )

        # Set up driver if registration checking is enabled
        if self.config.check_registrations:
            print("Setting up browser for registration checking...")
            self.driver = self._create_driver()
            self._register_checkers()
            print("Browser setup complete. Starting registration checks...")

        try:
            # Process registrations if enabled
            if self.config.check_registrations:
                print(f"Checking registrations for {len(df)} entries...")
                # Add a counter for progress tracking
                statuses = []
                for idx, (index, row) in enumerate(df.iterrows(), 1):
                    print(f"\n--- Processing entry {idx}/{len(df)} ---")
                    status = self._check_registration_status(row)
                    statuses.append(status)
                df["reg_status"] = statuses
                print("Registration checking complete!")
            else:
                # Still add reg_status column but with placeholder values
                df["reg_status"] = "not checked"

            # Convert to Person objects
            people = self._dataframe_to_people(df)

            return people

        finally:
            # Clean up driver
            if self.driver:
                self.driver.quit()
                self.driver = None

    def _check_registration_status(self, row: pd.Series) -> str:
        """
        Check registration status for a single row.

        Args:
            row: DataFrame row with registration data

        Returns:
            Registration status string
        """
        reg_body = row["State Board Name"]
        reg_number = row["Registration Number"]
        full_name = row["Full Name"]

        # Print verbose output for debugging
        print(f"Checking registration for: {full_name}")
        print(f"  Registration Body: {reg_body}")
        print(f"  Registration Number: {reg_number}")

        # Handle missing/invalid registration body
        if pd.isna(reg_body) or not reg_body:
            status = "unknown - no registration body specified"
            print(f"  Result: {status}")
            return status

        # Handle missing/invalid registration number
        if pd.isna(reg_number) or not reg_number:
            status = "unknown - no registration number specified"
            print(f"  Result: {status}")
            return status

        # Get appropriate checker
        checker = self.registry.get_checker(reg_body)
        if not checker:
            status = f"unsupported registration body: {reg_body}"
            print(f"  Result: {status}")
            return status

        try:
            print(f"  Launching browser to check {reg_body} registration...")
            result = checker.check_registration(str(reg_number))
            status = result.get("status", "unknown")
            print(f"  Result: {full_name}: {status} \n", row)
            return status
        except Exception as e:
            status = f"error: {str(e)}"
            logger.error(
                f"Error checking registration {reg_number} with {reg_body}: {e}"
            )
            print(f"  Result: {status}")
            return status

    def _dataframe_to_people(self, df: pd.DataFrame) -> List[Person]:
        """
        Convert DataFrame to list of Person objects.

        Args:
            df: DataFrame with registration data

        Returns:
            List of Person objects
        """
        people = []

        # Group by email to handle multiple registrations per person
        for email, person_df in df.groupby(self.config.email_column):
            if pd.isna(email):
                continue

            # Get person details from first row
            first_row = person_df.iloc[0]

            person = Person(
                full_name=first_row[self.config.full_name_column],
                email=str(email),
                linked_in_url=first_row.get(self.config.linked_in_url_column),
            )

            # Add registrations
            for _, reg_row in person_df.iterrows():
                reg_body = reg_row[self.config.reg_body_column]
                reg_number = reg_row[self.config.reg_number_column]

                # Skip rows with no registration info
                if pd.isna(reg_body) and pd.isna(reg_number):
                    continue

                reg_status = reg_row.get("reg_status", "unknown")

                registration = Registration(
                    reg_body=reg_body if not pd.isna(reg_body) else None,
                    reg_number=str(reg_number) if not pd.isna(reg_number) else None,
                    reg_status=reg_status,
                )

                person.add_registration(registration)

            people.append(person)

        return people

    def save_json(self, people: List[Person], output_path: Union[str, Path]) -> None:
        """
        Save people data to JSON file.

        Args:
            people: List of Person objects
            output_path: Path for output file
        """
        data = [person.to_dict() for person in people]

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        logger.info(f"Saved {len(people)} people to {output_path}")

    def get_supported_bodies(self) -> List[str]:
        """Get list of supported registration bodies."""
        bodies = []
        for checker_class in get_registered_checkers():
            try:
                # Create a mock driver for getting the registration body name
                # We only need the name, not actual web driver functionality
                temp_checker = checker_class(driver=None)  # type: ignore
                bodies.append(temp_checker.registration_body_name)
            except Exception as e:
                logger.warning(f"Could not get registration body name from {checker_class.__name__}: {e}")
                # Continue to next checker rather than failing completely
                continue
        
        return bodies
