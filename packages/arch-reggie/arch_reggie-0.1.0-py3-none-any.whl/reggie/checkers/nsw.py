"""NSW Architects Registration Board checker."""

from typing import Dict, Any, List
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from .base import BaseRegistrationChecker, register_checker
from ..utils import normalise_status


@register_checker
class NSWArchitectsChecker(BaseRegistrationChecker):
    """Checker for NSW Architects Registration Board."""

    @property
    def registration_body_name(self) -> str:
        """Return the name of the registration body."""
        return "NSW Architects Registration Board"

    def check_registration(self, reg_number: str, **kwargs) -> Dict[str, Any]:
        """
        Check registration status with NSW Architects Registration Board.

        Args:
            reg_number: The registration number to check

        Returns:
            Dictionary with registration status and details
        """
        if not self.driver:
            raise RuntimeError(
                "WebDriver instance is not available. "
                "Ensure the driver is initialized before calling this method."
            )
        try:
            url = "https://www.architects.nsw.gov.au/architects-register/architects"
            self.driver.get(url)

            # Find and fill the registration number field
            search_box = self.driver.find_element(By.ID, "regSearchNo")
            search_box.clear()
            search_box.send_keys(str(reg_number))

            # Submit the search
            search_button = self.driver.find_element(
                By.CSS_SELECTOR,
                "#tm-main > div > div.search > form > fieldset > div > div.control-group > div.controls > input.uk-button.uk-button-primary",
            )
            search_button.click()

            # Check for results
            try:
                # Look for the results table
                results_table = self.driver.find_element(By.ID, "arbresults")

                # Extract the first row of results
                first_row = results_table.find_element(By.CSS_SELECTOR, "tbody tr")
                cells = first_row.find_elements(By.TAG_NAME, "td")

                if len(cells) == 6:
                    result = self.extract_values(cells)
                    return result
                else:
                    message = (
                        "Unexpected number of cells in results row. There are suppsed to be 6, but "
                        f"there were actually {len(cells)} This probably means that NSW ARB have "
                        "updated their website so someone will need to update the scraper."
                        "You probably need to talk to Ben Doherty (ben_doherty@bvn.com.au)."
                    )
                    print(message)
                    raise ValueError(message)

            except NoSuchElementException:
                # No results found
                return {"status": "not found"}

        except Exception as e:
            return self.handle_error(reg_number, e)

    def extract_values(self, cells: List[WebElement]) -> Dict[str, Any]:
        """
        Extract registration values from table cells.

        Args:
            cells: List of WebElement objects representing table cells from the results row.
                   Expected structure: [name, registration_number, status, suburb, postcode]

        Returns:
            Dictionary containing:
                - status: Normalized status string
                - name: Architect's name
                - registration_number: Registration number
                - original_status: Raw status for debugging

        Note:
            Currently expects 6 cells but only uses the first 3 (name, reg_number, status).
        """
        # The structure of the table is currently:
        # |0    | 1                   | 2      | 3      | 4        |
        # |name | registration_number | status | suburb | postcode |
        status = cells[2].text.strip().lower()
        result = {
            "status": normalise_status(status),
            "name": cells[0].text.strip(),
            "registration_number": cells[1].text.strip(),
            "original_status": status,  # for debugging
        }

        return result
