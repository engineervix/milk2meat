from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from milk2meat.core.utils.validators import FileSizeValidator


class TestFileSizeValidator(TestCase):
    def test_valid_file_size(self):
        # Create a valid file size (within the limit)
        file = SimpleUploadedFile("valid_file.txt", b"valid_content")
        validator = FileSizeValidator(limit=5 * 1024 * 1024)  # 5MB limit

        # This should not raise an exception
        validator(file)

    def test_invalid_file_size(self):
        # Create an invalid file size (exceeds the limit)
        file = SimpleUploadedFile("invalid_file.txt", b"some_random_content" * 1_000_000)  # > 10MB
        validator = FileSizeValidator()  # 10MB limit

        # This should raise a ValidationError
        with self.assertRaises(ValidationError):
            validator(file)
