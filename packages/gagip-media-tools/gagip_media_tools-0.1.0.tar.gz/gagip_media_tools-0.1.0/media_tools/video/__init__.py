from .converter import convert_video
from .options import ConvertOptions

__all__ = ["convert_video", "ConvertOptions"]

DEFAULT_OPTIONS = ConvertOptions()
MOBILE_RESOLUTIONS = {"480p": "854x480", "720p": "1280x720", "1080p": "1920x1080"}
