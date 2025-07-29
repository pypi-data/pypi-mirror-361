from enum import Enum
from typing import Awaitable, Callable, Optional

from pydantic import BaseModel, PrivateAttr


class FileType(Enum):
    PDF = "pdf"
    XLSX = "xlsx"
    DOCX = "docx"
    DOC = "doc"
    ZIP = "zip"
    KMZ = "kmz"
    JPG = "jpg"
    RTF = "rtf"
    RAR = "rar"
    DWG = "dwg"
    XLS = "xls"
    PNG = "png"
    ODT = "odt"
    JPEG = "jpeg"


class ContentStatus(Enum):
    """
    Enum representing the content's download status.

    Attributes:
        PENDING_DOWNLOAD: Content is ready to be downloaded. Access `.content` to trigger the download.
        AVAILABLE: Content has been downloaded and is ready to use.
    """

    PENDING_DOWNLOAD = "Pending download"
    AVAILABLE = "Downloaded"


class Attachment(BaseModel):
    id: str
    name: str
    type: str
    description: str | None
    size: int
    upload_date: str
    file_type: FileType
    _download_fn: Callable[[], Awaitable[str]] = PrivateAttr()
    _content: Optional[str] = PrivateAttr(default=None)

    @property
    async def content(self) -> Optional[str]:
        if self._content is None:
            self._content = await self._download_fn()

        return self._content

    @property
    def content_status(self) -> ContentStatus:
        if self._content is None:
            return ContentStatus.PENDING_DOWNLOAD

        return ContentStatus.AVAILABLE
