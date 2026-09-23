# Django-Resize-Image

A Django package providing model and admin mixins for automatic image resizing, aspect-ratio handling, and format conversion on model save.

---

## Installation

```bash
pip install git+https://github.com/djangomango/django-resize-image.git@0.1.0
```

Or add to your `requirements.txt`:

```txt
git+https://github.com/djangomango/django-resize-image.git@0.1.0
```

Add `django_resize_image` to your `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    ...
    "django_resize_image",
    ...
]
```

---

## Usage

### 1. Model Mixins for Image Variants

Use `ResizeImageSaveMixin` to generate multiple resized image variants from a source image field on save:

```python
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_resize_image.helpers import get_upload_path
from django_resize_image.modelmixins import ResizeImageSaveMixin


class MediaItem(ResizeImageSaveMixin, models.Model):
    image = models.ImageField(_("Source Image"), upload_to=get_upload_path, blank=True, null=True)
    image_thumb = models.ImageField(_("Thumbnail"), upload_to=get_upload_path, blank=True, null=True)
    image_large = models.ImageField(_("Large"), upload_to=get_upload_path, blank=True, null=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image_in_field = "image"
        self.image_out_fields = {
            "image_thumb": {"size": [160, 120], "force_format": "WEBP", "quality": 90},
            "image_large": {"size": [1200, 800], "force_format": "WEBP", "quality": 95},
        }
```

### 2. Standard Aspect Ratio Mixins

Convenience mixins are provided for common dimensions:

```python
from django.db import models
from django_resize_image.modelmixins import CoverSizeImageMixin


class Banner(CoverSizeImageMixin, models.Model):
    pass
```

### 3. ModelAdmin Mixin

Render image variant previews directly in the Django Admin list display:

```python
from django.contrib import admin
from django_resize_image.adminmixins import CoverSizeImageAdminMixin
from .models import Banner


@admin.register(Banner)
class BannerAdmin(CoverSizeImageAdminMixin, admin.ModelAdmin):
    pass
```

---

## License & Credits

- Licensed under the **GNU Lesser General Public License v3 (LGPLv3)**.
- Image reformatting functionality adapted from [django-resized](https://github.com/un1t/django-resized) by un1t.