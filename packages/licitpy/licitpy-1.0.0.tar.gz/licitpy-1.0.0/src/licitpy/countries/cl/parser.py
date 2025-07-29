import re
from datetime import datetime
from zoneinfo import ZoneInfo

from licitpy.core.enums import Attachment
from licitpy.core.parser.attachments import AttachmentParser
from licitpy.core.parser.base import BaseParser


class ChileTenderParser(BaseParser):
    def __init__(self) -> None:
        self._attachment = AttachmentParser()

    def get_attachment_url(self, html: str) -> str:
        """
        Get the URL of an attachment from the HTML content.
        """

        attachment_url = self.get_on_click_by_element_id(html, "imgAdjuntos")

        url_match = re.search(r"ViewAttachment\.aspx\?enc=(.*)','", attachment_url)

        if not url_match:
            raise ValueError("Attachment URL hash not found")

        enc: str = url_match.group(1)
        url = f"https://www.mercadopublico.cl/Procurement/Modules/Attachment/ViewAttachment.aspx?enc={enc}"

        return url

    def get_attachments(self, html: str) -> list[Attachment]:
        return self._attachment.get_attachments(html)

    def get_opening_date(self, html: str) -> datetime:
        """
        Get the opening date of a tender from its HTML content.
        """

        opening_date = self.get_text_by_element_id(html, "lblFicha3Publicacion")

        # eg: 06-08-2024 9:11:02
        return datetime.strptime(opening_date, "%d-%m-%Y %H:%M:%S").replace(
            tzinfo=ZoneInfo("America/Santiago")
        )

    def get_closing_date_from_eligibility(self, html: str) -> datetime:
        # Extract the closing date for the eligibility phase (idoneidad técnica).
        # This date marks the final deadline for all participants to submit their initial technical eligibility documents.
        # After this point, only participants who meet the technical requirements can proceed.

        # Example date format from the HTML: "16-12-2024 12:00:00"
        closing_date = self.get_text_by_element_id(html, "lblFicha3CierreIdoneidad")

        # Parse the extracted date string into a datetime object, ensuring the correct format and time zone.
        return datetime.strptime(closing_date, "%d-%m-%Y %H:%M:%S").replace(
            tzinfo=ZoneInfo(
                "America/Santiago"
            )  # Set the time zone to Chile's local time.
        )

    def get_closing_date(self, html: str) -> datetime:
        # Check if the eligibility closing date (idoneidad técnica) exists in the HTML.
        # If lblFicha3CierreIdoneidad exists, it indicates that the process includes an eligibility phase.
        # In such cases, the usual closing date element (lblFicha3Cierre) contains a string like
        # "10 días a partir de la notificación 12:00" instead of a concrete date.

        if self.has_element_id(html, "lblFicha3CierreIdoneidad"):
            # Extract and return the eligibility closing date as the definitive closing date.
            # The eligibility phase defines the last moment when anyone can participate.
            return self.get_closing_date_from_eligibility(html)

        # If lblFicha3CierreIdoneidad does not exist, assume lblFicha3Cierre contains a concrete closing date.
        # Example: "11-11-2024 15:00:00"
        closing_date = self.get_text_by_element_id(html, "lblFicha3Cierre")

        # Parse the extracted date string into a datetime object, ensuring the correct format and time zone.
        return datetime.strptime(closing_date, "%d-%m-%Y %H:%M:%S").replace(
            tzinfo=ZoneInfo(
                "America/Santiago"
            )  # Set the time zone to Chile's local time.
        )

    def get_title(self, html: str) -> str:
        return self.get_text_by_element_id(html, "lblNombreLicitacion")
