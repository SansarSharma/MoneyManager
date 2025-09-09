# File: utils/general_helper.py

"""
GeneralHelper provides small, reusable utility functions
used across different parts of the application.

Abstraction Function:
    - Maps common tasks into simple helper functions.

Representation Invariant:
    - Functions should remain stateless and not depend on
      or modify external variables.
"""


class GeneralHelper:

    @staticmethod
    def get_days_in_month(month: str, year: int) -> int:
        """
        REQUIRES:
            - month is a valid month name (e.g., "January" to "December")
            - year is a positive integer
        EFFECTS:
            - Returns the number of days in the given month for the given year.
              February is 29 days in leap years, 28 otherwise.
        """
        # Normalize month to lowercase for comparison
        month = month.strip().lower()

        # Mapping of months to days (default for February is 28)
        month_days = {
            "january": 31,
            "february": 28,
            "march": 31,
            "april": 30,
            "may": 31,
            "june": 30,
            "july": 31,
            "august": 31,
            "september": 30,
            "october": 31,
            "november": 30,
            "december": 31
        }

        # Validate month
        if month not in month_days:
            raise ValueError(f"Invalid month name: {month}")

        # Adjust February for leap year
        if month == "february" and GeneralHelper.is_leap_year(year):
            return 29

        return month_days[month]

    @staticmethod
    def is_leap_year(year: int) -> bool:
        """
        REQUIRES: year is a positive integer
        EFFECTS: Returns True if the given year is a leap year, False otherwise.
        """
        return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
