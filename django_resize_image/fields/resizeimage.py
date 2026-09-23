from typing import Any

from django.core import checks
from django.core.files.base import ContentFile
from django.db.models import ImageField

from ..helpers import get_processed_image


class ResizedImageFieldFile(ImageField.attr_class):
    """FieldFile subclass intercepting save to auto-process and resize images."""

    def save(self, name: str, content: Any, save: bool = True) -> None:
        """Process and save resized image content."""
        content.file.seek(0)

        image_kwargs = {}
        for custom_kwargs in [
            "crop",
            "size",
            "scale",
            "quality",
            "keep_meta",
            "force_format",
        ]:
            image_kwargs[custom_kwargs] = getattr(self.field, custom_kwargs)

        bytes_io, filename = get_processed_image(content.file, name, **image_kwargs)
        if bytes_io is not None:
            new_content = ContentFile(bytes_io.getvalue())
            super().save(filename, new_content, save)
        else:
            super().save(name, content, save)


class ResizedImageField(ImageField):
    """Model image field automatically resizing and formatting uploads."""

    attr_class = ResizedImageFieldFile

    def __init__(
        self, verbose_name: str | None = None, name: str | None = None, **kwargs: Any
    ) -> None:
        """Initialize ResizedImageField with custom resizing attributes."""
        self.size = kwargs.pop("size", [1920, 1080])
        self.scale = kwargs.pop("scale", None)
        self.crop = kwargs.pop("crop", None)
        self.quality = kwargs.pop("quality", -1)
        self.keep_meta = kwargs.pop("keep_meta", True)
        self.force_format = kwargs.pop("force_format", None)
        super().__init__(verbose_name, name, **kwargs)

    def deconstruct(self) -> tuple[str, str, list[Any], dict[str, Any]]:
        """Deconstruct field for migration serialization."""
        name, path, args, kwargs = super().deconstruct()
        for custom_kwargs in [
            "crop",
            "size",
            "scale",
            "quality",
            "keep_meta",
            "force_format",
        ]:
            kwargs[custom_kwargs] = getattr(self, custom_kwargs)
        return name, path, args, kwargs

    def check(self, **kwargs: Any) -> list[checks.CheckMessage]:
        """Validate field parameters during system checks."""
        return [
            *super().check(**kwargs),
            *self._check_single_dimension_crop(),
            *self._check_webp_quality(),
        ]

    def _check_single_dimension_crop(self) -> list[checks.CheckMessage]:
        """Ensure single dimension size is not paired with crop."""
        if self.crop is not None and self.size is not None and None in self.size:
            return [
                checks.Error(
                    f"{self.__class__.__name__} has both a crop argument and a single dimension size. "
                    "Crop is not possible in that case as the second size dimension is computed from the "
                    "image size and the image will never be cropped.",
                    obj=self,
                    id="django_resized.E100",
                    hint="Remove the crop argument.",
                )
            ]
        return []

    def _check_webp_quality(self) -> list[checks.CheckMessage]:
        """Ensure WebP format specifies a quality value."""
        if (
            self.force_format is not None
            and self.force_format.lower() == "webp"
            and (self.quality is None or self.quality == -1)
        ):
            return [
                checks.Error(
                    f"{self.__class__.__name__} forces the webp format without the quality set.",
                    obj=self,
                    id="django_resized.E101",
                    hint="Set the quality argument.",
                )
            ]
        return []
