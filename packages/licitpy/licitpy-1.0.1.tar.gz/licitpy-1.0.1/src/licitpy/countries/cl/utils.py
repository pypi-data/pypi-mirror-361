import base64
import os

from licitpy.core.enums import Attachment
from licitpy.core.exceptions import AttachmentDownloadError


async def save_attachment(
    attachment: Attachment,
    content: str | None = None,
    path: str = ".",
    filename: str | None = None,
) -> str:
    # If content is not provided, fetch it from the attachment
    if content is None:
        content = await attachment.content

    if not content:
        raise AttachmentDownloadError(
            f"Failed to download attachment: {attachment.name}"
        )

    filename = filename or attachment.name
    full_path = os.path.join(path, filename)

    with open(full_path, "wb") as file:
        file.write(base64.b64decode(content))

    return full_path
