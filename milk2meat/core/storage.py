import logging

from django.conf import settings
from django.core.exceptions import PermissionDenied
from storages.backends.s3boto3 import S3Boto3Storage

logger = logging.getLogger(__name__)


class PrivateMediaStorage(S3Boto3Storage):
    """
    Custom storage backend for private media files in Cloudflare R2.
    This prevents direct access to files and only allows access through
    signed URLs for authenticated users.
    """

    location = settings.AWS_LOCATION
    file_overwrite = False

    def url(self, name, parameters=None, expire=None):
        """
        Generate a signed URL that expires in a short time for authenticated access.

        Args:
            name: Name of the file
            parameters: Additional parameters for the URL
            expire: Expiration time in seconds (default: 300 seconds / 5 minutes)

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


def get_secure_file_url(file_path, user, expire=300):
    """
    Generate a secure URL for a file, but only if the user has access.

    Args:
        file_path: Path to the file in storage
        user: The user requesting access
        expire: Expiration time in seconds

    Returns:
        A signed URL or raises PermissionDenied
    """
    if not user_can_access_file(file_path, user):
        raise PermissionDenied("You don't have permission to access this file")

    storage = PrivateMediaStorage()
    return storage.url(file_path, expire=expire)
