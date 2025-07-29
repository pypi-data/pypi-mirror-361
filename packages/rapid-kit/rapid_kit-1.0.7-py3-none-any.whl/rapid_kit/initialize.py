import ctypes
import os
import sys
from .lib import get_lib

lib = get_lib()

lib.RAPID_Core_Initialize.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p,
                                      ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_int]
lib.RAPID_Core_Initialize.restype = ctypes.c_int

lib.RAPID_Core_VersionName.argtypes = []
lib.RAPID_Core_VersionName.restype = ctypes.c_char_p

lib.RAPID_Core_BuildId.argtypes = []
lib.RAPID_Core_BuildId.restype = ctypes.c_char_p

lib.RAPID_Core_CommitHash.argtypes = []
lib.RAPID_Core_CommitHash.restype = ctypes.c_char_p

lib.RAPID_Core_AppId.argtypes = []
lib.RAPID_Core_AppId.restype = ctypes.c_char_p

lib.RAPID_Core_PackageName.argtypes = []
lib.RAPID_Core_PackageName.restype = ctypes.c_char_p

def initialize(app_id, package_name="", language="zh-cn", environment=0, console_logging=False):
    app_id_bytes = app_id.encode('utf-8') if isinstance(app_id, str) else app_id
    package_name_bytes = package_name.encode('utf-8') if isinstance(package_name, str) else package_name
    platform_bytes = "android".encode('utf-8')
    language_bytes = language.encode('utf-8') if isinstance(language, str) else language
    
    home = os.path.expanduser("~")
    default_cache = os.path.join(home, ".rapid_cache")
    os.makedirs(default_cache, exist_ok=True)
    cache_dir_bytes = default_cache.encode('utf-8')
    
    console_log_value = 1 if console_logging else 0
    
    result = lib.RAPID_Core_Initialize(app_id_bytes, package_name_bytes, platform_bytes,
                                      language_bytes, environment, cache_dir_bytes, console_log_value)
    return result == 1

def version_name():
    result = lib.RAPID_Core_VersionName()
    return result.decode('utf-8') if result else ""

def build_id():
    result = lib.RAPID_Core_BuildId()
    return result.decode('utf-8') if result else ""

def commit_hash():
    result = lib.RAPID_Core_CommitHash()
    return result.decode('utf-8') if result else ""

def app_id():
    result = lib.RAPID_Core_AppId()
    return result.decode('utf-8') if result else ""

def package_name():
    result = lib.RAPID_Core_PackageName()
    return result.decode('utf-8') if result else "" 