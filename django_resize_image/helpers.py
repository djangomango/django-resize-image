import os
from io import BytesIO
from typing import Any
from uuid import uuid4

from django.core.files import File
from django.utils import timezone
from PIL import ExifTags, Image, ImageOps, UnidentifiedImageError


def get_upload_path(instance: Any, filename: str) -> str:
    """Return upload path partitioned by app, model, year, month, and uuid."""
    path = os.path.join(
        instance._meta.app_label,
        instance._meta.model_name,
        timezone.now().strftime("%Y"),
        timezone.now().strftime("%m"),
        uuid4().hex,
        filename,
    )
    return path


def rename_file(
    file_path: str, prefix: str | None = None, ext: str | None = None
) -> str:
    """Rename file path with optional prefix and extension."""
    basename = os.path.basename(file_path)
    if prefix:
        basename = f"{prefix}{basename}"
    if ext:
        basename = f"{os.path.splitext(basename)[0]}{ext}"

    return basename


def get_pil_supported_format_or_default(image: Any, format: str | None = None) -> str:
    """Return supported format of image or default format if unsupported."""
    default_formats = [
        "JPEG",
        "PNG",
        "WEBP",
    ]

    if format:
        format = format.upper()
        if format in default_formats:
            return format

        for pil_format in Image.EXTENSION.values():
            if pil_format == format:
                return format

    return image.format.upper()


def pil_extension_to_format_or_none(ext: str) -> str | None:
    """Return PIL format for file extension or None if unsupported."""
    return Image.EXTENSION.get(ext.lower(), None)


def pil_format_to_extension_or_none(format: str) -> str | None:
    """Return file extension for format or None if unsupported."""
    default_extensions = {
        "JPEG": ".jpg",
        "PNG": ".png",
        "WEBP": ".webp",
    }

    format = format.upper()
    if format in default_extensions:
        return default_extensions[format]

    for pil_ext, pil_format in Image.EXTENSION.items():
        if pil_format == format:
            return pil_ext

    return None


def resize_image(
    image: Any, size: tuple[int, int] | list[int], thumb: bool = True
) -> Any:
    """Resize given image to target size."""
    if thumb:
        image.thumbnail(size, Image.Resampling.LANCZOS)
        return image

    return image.resize(size, Image.Resampling.LANCZOS)


def normalize_rotation(image: Any) -> Any:
    """Normalize image rotation based on EXIF orientation."""
    try:
        image._getexif()
    except AttributeError:
        return image

    for orientation in ExifTags.TAGS:
        if ExifTags.TAGS[orientation] == "Orientation":
            break
    else:
        return image

    format = image.format
    exif = image._getexif()
    if exif is None:
        return image

    action_nr = exif.get(orientation, None)

    if action_nr is None:
        return image
    if action_nr in (3, 4):
        image = image.rotate(180, expand=True)
    elif action_nr in (5, 6):
        image = image.rotate(270, expand=True)
    elif action_nr in (7, 8):
        image = image.rotate(90, expand=True)
    if action_nr in (2, 4, 5, 7):
        image = ImageOps.mirror(image)

    image.format = format

    return image


def get_centring_from_crop(crop: tuple[str, str] | list[str]) -> list[float]:
    """Return centering coordinates for given crop anchors."""
    vertical = {
        "top": 0.0,
        "middle": 0.5,
        "bottom": 1.0,
    }
    horizontal = {
        "left": 0.0,
        "center": 0.5,
        "right": 1.0,
    }
    return [
        vertical[crop[0]],
        horizontal[crop[1]],
    ]


def get_processed_image(
    image_file: Any, image_name: str, **kwargs: Any
) -> tuple[BytesIO | None, str]:
    """Return processed image bytes and output filename."""
    size = kwargs.get("size")
    scale = kwargs.get("scale")
    crop = kwargs.get("crop")
    quality = kwargs.pop("quality", -1)
    keep_meta = kwargs.get("keep_meta", True)
    force_format = kwargs.get("force_format")
    prefix = kwargs.get("prefix")

    try:
        img = Image.open(image_file)
    except UnidentifiedImageError:
        return None, ""

    img = normalize_rotation(img)

    rgb_formats = ("jpeg", "jpg")
    rgba_formats = ("png",)

    if force_format and force_format.lower() in rgb_formats and img.mode != "RGB":
        img = img.convert("RGB")
    if force_format and force_format.lower() in rgba_formats and img.mode != "RGBA":
        img = img.convert("RGBA")

    resample = Image.Resampling.LANCZOS

    if size is None:
        size = img.size

    if crop:
        thumb = ImageOps.fit(
            img,
            size,
            resample,
            centering=get_centring_from_crop(crop),
        )
    elif None in size:
        thumb = img
        if size[0] is None and size[1] is not None:
            scale = size[1] / img.size[1]
        elif size[1] is None and size[0] is not None:
            scale = size[0] / img.size[0]
    else:
        img.thumbnail(
            size,
            resample,
        )
        thumb = img

    if scale is not None:
        thumb = ImageOps.scale(
            thumb,
            scale,
            resample,
        )

    img_info = img.info
    if not keep_meta:
        img_info.pop("exif", None)

    bytes_io = BytesIO()
    img_format = get_pil_supported_format_or_default(img, force_format)

    if img_format == "WEBP" and quality == -1:
        quality = 100

    thumb.save(bytes_io, format=img_format, quality=quality, **img_info)

    ext = pil_format_to_extension_or_none(img_format)
    filename = rename_file(image_name, prefix, ext)

    return bytes_io, filename


def get_processed_image_as_field_file(
    image_file: Any, image_name: str, **kwargs: Any
) -> File | None:
    """Return processed image wrapped in a Django File object or None if processing fails."""
    bytes_io, filename = get_processed_image(image_file, image_name, **kwargs)
    if bytes_io is None:
        return None

    return File(bytes_io, name=filename)
