import base64
import secrets
from functools import partial

from aiohttp import ClientResponse
from tqdm import tqdm

from licitpy.core.enums import Attachment
from licitpy.core.http import AsyncHttpClient
from licitpy.core.parser.attachments import AttachmentParser


class AttachmentServices:
    def __init__(
        self,
        downloader: AsyncHttpClient | None = None,
        parser: AttachmentParser | None = None,
    ):
        self._downloader: AsyncHttpClient = downloader or AsyncHttpClient()
        self._parser: AttachmentParser = parser or AttachmentParser()

    async def get_attachments(self, url: str, html: str) -> list[Attachment]:
        attachments: list[Attachment] = self._parser.get_attachments(html)

        for attachment in attachments:
            download_attachment_fn = partial(
                self.download_attachment_from_url, url, attachment
            )

            attachment._download_fn = download_attachment_fn

        return attachments

    async def download_attachment_from_url(
        self, url: str, attachment: Attachment
    ) -> str:
        """
        Downloads an attachment from a URL using a POST request with the attachment ID.
        """

        file_code = attachment.id
        file_size = attachment.size
        file_name = attachment.name

        search_x = str(secrets.randbelow(30) + 1)
        search_y = str(secrets.randbelow(30) + 1)

        # Fetch the HTML content of the page to extract the __VIEWSTATE
        # this request should be made without the cache
        html = await self._downloader.get_html_by_url(url)

        response = await self._downloader.session.post(
            url,
            data={
                "__EVENTTARGET": "",
                "__EVENTARGUMENT": "",
                "__VIEWSTATE": self._parser.get_view_state(html),
                "__VIEWSTATEGENERATOR": "13285B56",
                # Random parameters that simulate the button click
                f"DWNL$grdId$ctl{file_code}$search.x": search_x,
                f"DWNL$grdId$ctl{file_code}$search.y": search_y,
                "DWNL$ctl10": "",
            },
            timeout=30,
        )

        return await self.download_file_base64(response, file_size, file_name)

    async def download_file_base64(
        self,
        response: ClientResponse,
        file_size: int,
        file_name: str,
    ) -> str:
        file_content = bytearray()

        with tqdm(
            total=file_size,
            unit="B",
            unit_scale=True,
            desc=f"Downloading {file_name}",
            disable=False,
        ) as progress_bar:
            async for chunk in response.content.iter_chunked(8192):
                if chunk:
                    file_content.extend(chunk)
                    progress_bar.update(len(chunk))
                    progress_bar.refresh()

        base64_content = base64.b64encode(file_content).decode("utf-8")

        return base64_content
