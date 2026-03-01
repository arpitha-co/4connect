# vision/__init__.py
from .camera_stream import get_frame
from .color_detection import detect_colors

__all__ = ["get_frame", "detect_colors"]
