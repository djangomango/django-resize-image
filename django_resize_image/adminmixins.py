class LogoSizeImageAdminMixin:
    """Admin mixin managing logo image field with generated variant sizes."""

    list_display = [
        "image",
        "alt",
    ]

    fields = [
        "image",
        "image_xs",
        "image_md",
        "alt",
    ]

    readonly_fields = [
        "image_xs",
        "image_md",
    ]


class CoverSizeImageAdminMixin:
    """Admin mixin managing cover image field with generated variant sizes."""

    list_display = [
        "image",
        "alt",
    ]

    fields = [
        "image",
        "image_md",
        "image_xl",
        "alt",
    ]

    readonly_fields = [
        "image_md",
        "image_xl",
    ]
