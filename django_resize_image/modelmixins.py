from typing import Any

from django.db import models
from django.utils.translation import gettext_lazy as _

from .helpers import get_processed_image_as_field_file, get_upload_path


class ResizeImageSaveMixin(models.Model):
    """Model mixin that resizes an image field into multiple dimensions on save."""

    _stored: dict[str, Any]

    class Meta:
        abstract = True

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize mixin and configure default image input/output mapping."""
        super().__init__(*args, **kwargs)

        self.image_in_field = "image"
        self.image_out_fields = {
            "image_xxs": {"size": [40, 30], "force_format": "WEBP", "quality": 99},
            "image_xs": {"size": [160, 120], "force_format": "WEBP", "quality": 99},
            "image_sm": {"size": [480, 360], "force_format": "WEBP", "quality": 99},
            "image_md": {"size": [800, 600], "force_format": "WEBP", "quality": 99},
            "image_lg": {"size": [1280, 960], "force_format": "WEBP", "quality": 99},
            "image_xl": {"size": [1920, 1440], "force_format": "WEBP", "quality": 99},
            "image_xxl": {"size": [2560, 1920], "force_format": "WEBP", "quality": 99},
        }

    @classmethod
    def from_db(cls, db: str | None, field_names: list[str], values: list[Any]) -> Any:
        """Store initial field values when model is loaded from database."""
        instance = super().from_db(db, field_names, values)
        instance._stored = dict(zip(field_names, values, strict=False))
        return instance

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Process and save resized image variants if input image changed."""
        image_in = getattr(self, self.image_in_field, None)
        stored_image_in = (
            self._stored.pop(self.image_in_field, None)
            if hasattr(self, "_stored")
            else None
        )

        if image_in != stored_image_in:
            for field_name, image_kwargs in self.image_out_fields.items():
                if hasattr(self, field_name):
                    if image_in:
                        image_out = get_processed_image_as_field_file(
                            image_in.file, image_in.name, **image_kwargs
                        )
                    else:
                        image_out = None

                    setattr(self, field_name, image_out)

        super().save(*args, **kwargs)


class LogoSizeImageMixin(ResizeImageSaveMixin, models.Model):
    """Model mixin providing standard logo image variants and alt text."""

    image = models.ImageField(
        _("Image"), upload_to=get_upload_path, max_length=255, blank=True, null=True
    )
    image_xs = models.ImageField(
        _("Image xs"), upload_to=get_upload_path, max_length=255, blank=True, null=True
    )
    image_md = models.ImageField(
        _("Image md"), upload_to=get_upload_path, max_length=255, blank=True, null=True
    )

    alt = models.CharField(_("Alt"), max_length=100, blank=True, null=True)

    class Meta:
        abstract = True


class CoverSizeImageMixin(ResizeImageSaveMixin, models.Model):
    """Model mixin providing standard cover image variants and alt text."""

    image = models.ImageField(
        _("Image"), upload_to=get_upload_path, max_length=255, blank=True, null=True
    )
    image_md = models.ImageField(
        _("Image md"), upload_to=get_upload_path, max_length=255, blank=True, null=True
    )
    image_xl = models.ImageField(
        _("Image xl"), upload_to=get_upload_path, max_length=255, blank=True, null=True
    )

    alt = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        abstract = True
