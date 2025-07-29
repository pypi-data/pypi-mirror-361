import ctypes
import os
import platform
import sys
from pathlib import Path

MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(MODULE_DIR)

def _get_libraries_dir():
    system = platform.system().lower()    
    cwd = os.getcwd()
    
    possible_dirs = [
        os.path.join(cwd, "libraries"),  # 当前目录下的libraries
        os.path.join(cwd, "libraries", "lib"),  # libraries/lib子目录        
    ]
    
    # 根据系统确定库文件名
    if system == 'darwin':
        lib_name = 'libRapidCore.dylib'
    elif system == 'windows':
        lib_name = 'RapidCore.dll'
    elif system == 'linux':
        lib_name = 'libRapidCore.so'
    else:
        raise RuntimeError(f"Unsupported system: {system}")
    
    # 遍历可能的库目录查找
    for lib_dir in possible_dirs:
        core_lib_path = os.path.join(lib_dir, lib_name)
        if os.path.exists(core_lib_path):
            print(f"Found libraries in: {lib_dir}")
            return lib_dir
    
    # 构建错误信息
    error_msg = f"\n================================================\n"
    error_msg += f"Could not find libraries directory with {lib_name}.\n"
    error_msg += f"Searched in:\n"
    for lib_dir in possible_dirs:
        error_msg += f"  - {lib_dir}\n"
    error_msg += f"Please create one of these directories and copy the required libraries there,\n"
    error_msg += f"such as libRapidCore.dylib, libRapidSDL.dylib, libRapidMedia.dylib, etc.\n"
    error_msg += f"================================================\n"
    raise RuntimeError(error_msg)

try:
    libraries_dir = _get_libraries_dir()
    system = platform.system().lower()
    if system == 'darwin':
        core_lib = 'libRapidCore.dylib'
        sdl_lib = 'libRapidSDL.dylib'
        media_lib = 'libRapidMedia.dylib'
    elif system == 'windows':
        core_lib = 'RapidCore.dll'
        sdl_lib = 'RapidSDL.dll'
        media_lib = 'RapidMedia.dll'
    elif system == 'linux':
        core_lib = 'libRapidCore.so'
        sdl_lib = 'libRapidSDL.so'
        media_lib = 'libRapidMedia.so'
    else:
        raise RuntimeError(f"Unsupported system: {system}")
    
    core_path = os.path.join(libraries_dir, core_lib)
    sdl_path = os.path.join(libraries_dir, sdl_lib)
    media_path = os.path.join(libraries_dir, media_lib)
    
    if not os.path.exists(core_path):
        raise RuntimeError(f"Core library not found: {core_path}")
    
    _core_lib = ctypes.CDLL(core_path, mode=ctypes.RTLD_GLOBAL)
    
    if not os.path.exists(sdl_path):
        print(f"Warning: SDL library not found: {sdl_path}")
        _sdl_lib = None
    else:
        try:
            _sdl_lib = ctypes.CDLL(sdl_path, mode=ctypes.RTLD_GLOBAL)
        except Exception as e:
            print(f"Warning: Failed to load SDL library: {e}")
            _sdl_lib = None
    
    if not os.path.exists(media_path):
        print(f"Warning: Media library not found: {media_path}")
        _media_lib = None
    else:
        try:
            _media_lib = ctypes.CDLL(media_path, mode=ctypes.RTLD_GLOBAL)
        except Exception as e:
            print(f"Warning: Failed to load Media library: {e}")
            _media_lib = None

except Exception as e:
    raise RuntimeError(f"Failed to load RAPID libraries: {e}")

def get_lib():
    return _core_lib

def get_media_lib():
    if _media_lib is None:
        raise RuntimeError("Media library is not loaded")
    return _media_lib

def get_sdl_lib():
    if _sdl_lib is None:
        raise RuntimeError("SDL library is not loaded")
    return _sdl_lib

def get_all_loaded_libs():
    libs = {os.path.basename(core_path): _core_lib}
    
    if _media_lib is not None:
        libs[os.path.basename(media_path)] = _media_lib
        
    if _sdl_lib is not None:
        libs[os.path.basename(sdl_path)] = _sdl_lib
        
    return libs