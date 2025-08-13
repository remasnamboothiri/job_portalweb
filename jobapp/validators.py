import os
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible

@deconstructible
class FileValidator:
    """
    Validator for file uploads with size and extension checks
    """
    def __init__(self, max_size=None, allowed_extensions=None):
        self.max_size = max_size
        self.allowed_extensions = allowed_extensions or []

    def __call__(self, value):
        if not value:
            return

        # Check file size
        if self.max_size and value.size > self.max_size:
            size_mb = self.max_size / (1024 * 1024)
            raise ValidationError(f'File size must be less than {size_mb:.1f}MB.')

        # Check file extension
        if self.allowed_extensions:
            ext = os.path.splitext(value.name)[1].lower()
            if ext not in self.allowed_extensions:
                allowed = ', '.join(self.allowed_extensions)
                raise ValidationError(f'File type not supported. Allowed types: {allowed}')

# Pre-configured validators
resume_validator = FileValidator(
    max_size=5 * 1024 * 1024,  # 5MB
    allowed_extensions=['.pdf', '.doc', '.docx']
)