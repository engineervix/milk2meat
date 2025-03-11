import logging

from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage

logger = logging.getLogger(__name__)


class PrivateS3Storage(S3Boto3Storage):
    """
    Custom S3 storage for Cloudflare R2 with private files and signed URLs.
    This is only used in production settings.
    """

    def __init__(self, **kwargs):
        # Ensure AWS settings are properly loaded
        self.location = getattr(settings, "AWS_LOCATION", "files")
        self.file_overwrite = getattr(settings, "AWS_S3_FILE_OVERWRITE", False)
        self.signature_version = getattr(settings, "AWS_S3_SIGNATURE_VERSION", "s3v4")
        self.addressing_style = getattr(settings, "AWS_S3_ADDRESSING_STYLE", "virtual")
        super().__init__(**kwargs)

    def url(self, name, parameters=None, expire=None):
        """
        Generate a signed URL with expiration for private files.

        Args:
            name: Name of the file
            parameters: Additional parameters for the URL
            expire: Expiration time in seconds

        Returns:
            A signed URL that grants temporary access to the file
        """
        if expire is None:
            expire = getattr(settings, "AWS_SIGNED_URL_EXPIRE_SECONDS", 300)

        # Generate the signed URL with expiration
        try:
            return super().url(name, parameters={"ResponseContentDisposition": "inline"}, expire=expire)
        except Exception as e:
            logger.error(f"Error generating signed URL for {name}: {str(e)}")
            raise


def user_can_access_file(file_path, user):
    """
    Determine if a user has permission to access a file.

    Args:
        file_path: Path to the file in storage
        user: The user requesting access

    Returns:
        bool: True if user has permission, False otherwise
    """
    # Basic check - user must be authenticated
    if not user.is_authenticated:
        return False

    # Extract the note ID from the file path
    # Example path: notes/{user_id}/{note_id}/filename.pdf
    parts = file_path.split("/")
    if len(parts) < 3 or parts[0] != "notes":
        return False

    # Check if the user_id in the path matches the requesting user
    user_id_in_path = parts[1]
    if user_id_in_path != str(user.id):
        return False

    return True
