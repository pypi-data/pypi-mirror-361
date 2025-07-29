"""Board of Architects of Queensland checker."""

from typing import Dict, Any, List
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement

from .base import BaseRegistrationChecker, register_checker
from ..utils import normalise_status


@register_checker
class QLDArchitectsChecker(BaseRegistrationChecker):
    """Checker for Board of Architects of Queensland."""

    @property
    def registration_body_name(self) -> str:
        """Return the name of the registration body."""
        return "Board of Architects of Queensland"

    def check_registration(self, reg_number: str, **kwargs) -> Dict[str, Any]:
        """
        Check registration status with Board of Architects of Queensland.

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
            url = (
                "https://www.boaq.qld.gov.au/BOAQ/Search_Register/Architect_Search.aspx"
            )

            # Element IDs for the QLD website
            reg_num_entry_box_id = (
                "ctl00_"
                "TemplateBody_"
                "WebPartManager1_"
                "gwpciArchitectsearch_"
                "ciArchitectsearch_"
                "ResultsGrid_"
                "Sheet0_"
                "Input3_"
                "TextBox1"
            )
            results_row_id = (
                "ctl00_"
                "TemplateBody_"
                "WebPartManager1_"
                "gwpciArchitectsearch_"
                "ciArchitectsearch_"
                "ResultsGrid_Grid1_ctl00__0"
            )

            self.driver.get(url)

            # Find and fill the registration number field
            box = self.driver.find_element(By.ID, reg_num_entry_box_id)
            box.clear()
            box.send_keys(str(reg_number))
            box.send_keys(Keys.ENTER)

            # Look for results
            try:
                result_cells = self.driver.find_elements(
                    By.CSS_SELECTOR, f"#{results_row_id} > td"
                )

                if not result_cells:
                    return {"status": "not found"}

                result = self.extract_values(reg_number, result_cells)

                return result
            except NoSuchElementException:
                return {"status": "not found"}

        except Exception as e:
            return self.handle_error(reg_number, e)

    def extract_values(
        self, reg_number: str, result_cells: List[WebElement]
    ) -> Dict[str, Any]:
        """
        Extract registration values from table cells.

        Args:
            reg_number: The registration number that was searched for
            result_cells: List of WebElement objects representing table cells from the results row.
                         Expected structure: [first_name, last_name, reg_number, status, ...]

        Returns:
            Dictionary containing:
                - status: Normalized status string
                - name: Architect's full name (first + last)
                - registration_number: Registration number
                - original_status: Raw status text for debugging

        Note:
            Combines cells[0] and cells[1] for full name, uses cells[3] for status.
        """
        name = f"{result_cells[0].text.strip()} {result_cells[1].text.strip()}"
        status_text = result_cells[3].text.strip()

        # Normalize status
        normalized_status = normalise_status(status_text)

        result = {
            "status": normalized_status,
            "name": name,
            "registration_number": reg_number,
            "original_status": status_text,
        }

        return result
