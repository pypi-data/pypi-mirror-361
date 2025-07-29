from datetime import date, datetime
from typing import Any
from zoneinfo import ZoneInfo


class TenderQuery:
    """
    A class to build queries for tenders.
    query = TenderQuery().published_today().limit(10)
    async for tender in query:
        print(tender)
    """

    def __init__(self) -> None:
        self._filters: dict[str, Any] = {}

    def published_on(
        self, when: date | datetime | str, allow_weekends: bool = False
    ) -> "TenderQuery":
        """Filters tenders published on a specific date."""

        if not isinstance(when, (str, datetime, date)):
            raise TypeError(
                f"Invalid date type: {type(when)}. Expected string, datetime, or date."
            )

        if isinstance(when, str):
            try:
                when = datetime.strptime(when, "%Y-%m-%d").date()
            except ValueError:
                raise ValueError(
                    f"Invalid date format: {when}. Expected format is YYYY-MM-DD."
                )

        elif isinstance(when, datetime):
            if when.tzinfo is None:
                raise ValueError(
                    f"Date is naive and lacks timezone information: {when}. "
                    "Please provide a timezone-aware datetime."
                )

            when = when.date()

        # Check if the date is in the future
        if when > datetime.now(ZoneInfo("UTC")).date():
            raise ValueError(
                f"Date cannot be in the future: {when}. Please provide a valid date."
            )

        self._filters["publication_on_date"] = when

        return self

    def published_today(self) -> "TenderQuery":
        """Filters tenders published today (UTC)."""
        today_utc = datetime.now(ZoneInfo("UTC")).date()
        return self.published_on(today_utc)

    def limit(self, count: int) -> "TenderQuery":
        self._filters["limit"] = count
        return self

    async def __aiter__(self) -> Any:
        pass
