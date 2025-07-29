from datetime import datetime, timezone

from pydantic import BaseModel, HttpUrl

from licitpy.core.enums import Attachment


class Tender(BaseModel):
    code: str
    title: str
    closing_date: datetime
    attachment_url: HttpUrl
    attachments: list[Attachment]

    @property
    def is_open(self) -> bool:
        return datetime.now(timezone.utc) < self.closing_date

    class Config:
        extra = "forbid"
