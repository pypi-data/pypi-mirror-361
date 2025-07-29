class ElementNotFoundException(Exception):
    """Raised when an HTML element with a specific ID is not found."""


class ElementAttributeNotFoundException(Exception):
    """Raised when an attribute is not found in an HTML element."""


class AttachmentTableNotFoundError(Exception):
    """Raised when the attachments table is not found in the HTML."""


class AttachmentTableRowsNotFoundError(Exception):
    """Raised when no rows are found in the attachments table."""


class AttachmentSizeFormatError(Exception):
    """Raised when the attachment size format is invalid."""


class AttachmentIdNotFoundError(Exception):
    """Raised when the attachment ID is not found."""


class AttachmentNameNotFoundError(Exception):
    """Raised when the attachment name is not found."""


class AttachmentDownloadError(Exception):
    """Raised when an attachment could not be downloaded or saved."""
