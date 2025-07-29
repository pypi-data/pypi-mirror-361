import ctypes
from enum import Enum
from .lib import get_media_lib

lib = get_media_lib()

class RGBFormat(Enum):
    RGBA = 0
    BGRA = 1

lib.RAPID_Media_RGBPixel_SetFormat.argtypes = [ctypes.c_int]
lib.RAPID_Media_RGBPixel_SetFormat.restype = None

def set_rgb_pixel_format(format):
    if isinstance(format, RGBFormat):
        lib.RAPID_Media_RGBPixel_SetFormat(format.value)
    else:
        lib.RAPID_Media_RGBPixel_SetFormat(format) 