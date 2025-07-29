import re

from lxml.html import HtmlElement

from licitpy.core.enums import Attachment, FileType
from licitpy.core.exceptions import (
    AttachmentIdNotFoundError,
    AttachmentNameNotFoundError,
    AttachmentSizeFormatError,
    AttachmentTableNotFoundError,
    AttachmentTableRowsNotFoundError,
)
from licitpy.core.parser.base import BaseParser


class AttachmentParser(BaseParser):
    def get_table_attachments(self, html: str) -> HtmlElement:
        """
        Get the table containing the attachments from the HTML content.
        """

        table = self.get_html_element_by_id(html, "DWNL_grdId")

        if not table:
            raise AttachmentTableNotFoundError("Table with ID 'DWNL_grdId' not found")

        return table[0]

    def get_table_attachments_rows(self, table: HtmlElement) -> list[HtmlElement]:
        """
        Get the rows of the table containing the attachments.
        """

        rows = table.xpath("tr[@class]")

        if not rows:
            raise AttachmentTableRowsNotFoundError("No rows found in the table")

        return rows

    def get_size_attachment(self, td: HtmlElement) -> int:
        """
        Parse the size of an attachment from the HTML content.
        """

        size_text: str = td.xpath("span/text()")[0]
        match = re.match(r"(\d+)\s*Kb", size_text.strip())

        if not match:
            raise AttachmentSizeFormatError(f"Invalid size format: {size_text}")

        size_kb = int(match.group(1))

        return size_kb * 1024

    def get_attachment_id(self, td: HtmlElement) -> str:
        """
        Extract the attachment ID from the HTML content.
        """

        input_id = td.xpath("input/@id")

        if not input_id:
            raise AttachmentIdNotFoundError("No input ID found in the first column")

        match = re.search(r"ctl(\d+)", input_id[0])

        if not match:
            raise AttachmentIdNotFoundError("No match found for attachment ID")

        return match.group(1)

    def get_content_from_attachment_row(self, td: HtmlElement) -> str | None:
        """
        Extract the content from an attachment row in the HTML content.
        """

        content = td.xpath("span/text()")

        if content:
            return content[0]

        return None

    def get_attachments(self, html: str) -> list[Attachment]:
        """
        Get the attachments of a tender from the HTML content.
        """

        table = self.get_table_attachments(html)
        rows: list[HtmlElement] = self.get_table_attachments_rows(table)

        attachments: list[Attachment] = []

        for tr in rows:
            td: list[HtmlElement] = tr.xpath("td")

            attachment_id: str = self.get_attachment_id(td[0])
            name = self.get_content_from_attachment_row(td[1])
            attachment_type = self.get_content_from_attachment_row(td[2])

            description = self.get_content_from_attachment_row(td[3])

            size: int = self.get_size_attachment(td[4])
            upload_date = self.get_content_from_attachment_row(td[5])

            if not name:
                raise AttachmentNameNotFoundError("Attachment name not found")

            file_type = FileType(name.split(".")[-1].lower().strip())

            attachment = Attachment(
                **{
                    "id": attachment_id,
                    "name": name,
                    "type": attachment_type,
                    "description": description,
                    "size": size,
                    "upload_date": upload_date,
                    "file_type": file_type,
                }
            )

            attachments.append(attachment)

        return attachments
