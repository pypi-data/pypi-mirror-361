import ctypes
from .lib import get_sdl_lib

lib = get_sdl_lib()

lib.RAPID_SDL_Vout_Silence_Create.argtypes = []
lib.RAPID_SDL_Vout_Silence_Create.restype = ctypes.c_void_p

lib.RAPID_SDL_Aout_Silence_Create.argtypes = []
lib.RAPID_SDL_Aout_Silence_Create.restype = ctypes.c_void_p

def create_silence_vout():
    return lib.RAPID_SDL_Vout_Silence_Create()

def create_silence_aout():
    return lib.RAPID_SDL_Aout_Silence_Create()