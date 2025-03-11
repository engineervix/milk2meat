from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible


@deconstructible
class FileSizeValidator(object):
    """
    A custom validator to check the file size of a Django FileField.

    Attributes:
        limit (int): The maximum allowed file size in bytes. Default is 10MB.

    Usage:
        Attach an instance of this validator to a FileField in your model. You can
        specify the maximum file size limit when initializing the validator.

        Example:
        file = models.FileField(
            upload_to='your_upload_path',
            validators=[FileSizeValidator(limit=5 * 1024 * 1024)]  # 5MB limit
        )
    """

    def __init__(self, limit=10 * 1024 * 1024):
        self.limit = limit

    def __call__(self, value):
        filesize = value.size

        if filesize > self.limit:
            raise ValidationError(
                f"File too large. The maximum file size that can be uploaded is {self.limit / (1024 * 1024)}MB"
            )
