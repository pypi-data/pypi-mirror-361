import logging

from decouple import config
from django.conf import settings
from sorl.thumbnail import get_thumbnail

from ..models import Avatar

log = logging.getLogger(__name__)


def get_thumbnail_url(
    obj: Avatar,
    thumbnail_size: str,
    *,
    crop_image: bool,
) -> str:
    if not obj.file:
        log.debug(
            "Avatar file missing",
            extra={"avatar_uuid": getattr(obj, "uuid", None)},
        )
        return ""

    file_width = obj.file.width
    file_height = obj.file.height
    landscape = file_width >= file_height

    log.debug(
        "Avatar file dimensions",
        extra={
            "avatar_uuid": getattr(obj, "uuid", None),
            "file_width": file_width,
            "file_height": file_height,
            "landscape": landscape,
        },
    )

    thumbnail_config = {"quality": 100}

    if crop_image:
        thumbnail_config["crop"] = "center"
        geometry_string = thumbnail_size
        log.debug(
            "Crop image enabled for thumbnail",
            extra={
                "avatar_uuid": getattr(obj, "uuid", None),
                "geometry_string": geometry_string,
            },
        )
    else:
        preset_width, preset_height = thumbnail_size.split("x")
        geometry_string = f"x{preset_height}"
        if landscape:
            geometry_string = preset_width
        log.debug(
            "Crop image disabled for thumbnail",
            extra={
                "avatar_uuid": getattr(obj, "uuid", None),
                "geometry_string": geometry_string,
                "landscape": landscape,
            },
        )

    thumbnail_config["geometry_string"] = geometry_string

    thumbnail = get_thumbnail(
        obj.file,
        **thumbnail_config,
    )

    environment = config("API_ENV")
    thumbnail_url = thumbnail.url
    if environment == "dev":
        thumbnail_url = f"{settings.API_URL}{thumbnail.url}"

    log.debug(
        "Generated thumbnail URL",
        extra={
            "avatar_uuid": getattr(obj, "uuid", None),
            "thumbnail_url": thumbnail_url,
            "environment": environment,
        },
    )

    return thumbnail_url
