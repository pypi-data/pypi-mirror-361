from licitpy.core.http import AsyncHttpClient
from licitpy.core.models import Tender
from licitpy.core.provider.tender import BaseTenderProvider
from licitpy.core.services.attachments import AttachmentServices
from licitpy.countries.cl.parser import ChileTenderParser


class ChileProvider(BaseTenderProvider):
    name = "cl"
    BASE_URL = "https://www.mercadopublico.cl"

    def __init__(
        self,
        downloader: AsyncHttpClient | None = None,
        parser: ChileTenderParser | None = None,
        attachment: AttachmentServices | None = None,
    ) -> None:
        self.downloader = downloader or AsyncHttpClient()
        self.parser = parser or ChileTenderParser()
        self.attachment = attachment or AttachmentServices(downloader=self.downloader)

    async def get_url_by_code(self, code: str) -> str:
        url = f"{self.BASE_URL}/Procurement/Modules/RFB/DetailsAcquisition.aspx?idlicitacion={code}"

        response = await self.downloader.session.head(
            url, timeout=30, allow_redirects=False
        )

        return f"{self.BASE_URL}{response.headers['Location']}"

    async def get_by_code(self, code: str) -> Tender:
        url = await self.get_url_by_code(code)
        html = await self.downloader.get_html_by_url(url)

        title = self.parser.get_title(html)
        closing_date = self.parser.get_closing_date(html)

        attachment_url = self.parser.get_attachment_url(html)
        attachment_html = await self.downloader.get_html_by_url(attachment_url)
        attachments = await self.attachment.get_attachments(
            attachment_url, attachment_html
        )

        return Tender(
            code=code,
            title=title,
            closing_date=closing_date,
            attachment_url=attachment_url,
            attachments=attachments,
        )
