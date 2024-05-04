# Django-Resize-Image

This package provides model mixins which allow image field reformatting and resizing. Note that the majority of the
image reformatting functionality has been pulled from [django-resized](https://github.com/un1t/django-resized).

### Installation

1. Pip install or add to your requirements.txt:

    ```bash
    pip install git+https://github.com/djangomango/django-resize-image.git@main
    ```

2. Add to INSTALLED_APPS:

    ```bash
    INSTALLED_APPS = [
        ...
        'django_resize_image',
    ]
    ```

### Usage

Use the model mixins as needed:

```python
from django_resize_image.modelmixins import CoverSizeImageMixin

class ImageModel(CoverSizeImageMixin, models.Model):

    class Meta:
        verbose_name = "Image Model"
        verbose_name_plural = "Image Models"
```

```python
from django_resize_image.modelmixins import ResizeImageSaveMixin
from django_resize_image.helpers import get_upload_path

class ImageModel(ResizeImageSaveMixin, models.Model):
    image = models.ImageField(_('Image'), upload_to=get_upload_path, max_length=255, blank=True, null=True)
    image_xs = models.ImageField(_('Image xs'), upload_to=get_upload_path, max_length=255, blank=True, null=True)
    image_md = models.ImageField(_('Image md'), upload_to=get_upload_path, max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = "Image Model"
        verbose_name_plural = "Image Models"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.image_in_field = "image"
        self.image_out_fields = {
            'image_xs': {'size': [160, 120], 'force_format': 'WEBP', 'quality': 99},
            'image_md': {'size': [800, 600], 'force_format': 'WEBP', 'quality': 99},
        }
```