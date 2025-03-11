# Reference: https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types
ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp", "image/bmp", "image/svg+xml"]
ALLOWED_DOCUMENT_TYPES = [
    # pdf
    "application/pdf",
    # doc
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/rtf",
    "application/vnd.oasis.opendocument.text",
    # spreadsheet
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.oasis.opendocument.spreadsheet",
    "text/csv",
    # presentation
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "application/vnd.oasis.opendocument.presentation",
]
