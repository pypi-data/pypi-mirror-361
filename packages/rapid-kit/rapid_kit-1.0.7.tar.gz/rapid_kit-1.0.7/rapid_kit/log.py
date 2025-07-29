import ctypes
from .lib import get_lib

lib = get_lib()

RAPID_LOG_UNKNOWN = 0
RAPID_LOG_DEFAULT = 1
RAPID_LOG_VERBOSE = 2
RAPID_LOG_DEBUG = 3
RAPID_LOG_INFO = 4
RAPID_LOG_WARN = 5
RAPID_LOG_ERROR = 6
RAPID_LOG_FATAL = 7
RAPID_LOG_SILENT = 8

lib.RAPID_Core_LeveledLoggingPrint.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p]
lib.RAPID_Core_LeveledLoggingPrint.restype = None

lib.RAPID_Core_UploadLogging.argtypes = []
lib.RAPID_Core_UploadLogging.restype = ctypes.c_char_p

def leveled_logging_print(level, tag, message):
    tag_bytes = tag.encode('utf-8') if isinstance(tag, str) else tag
    message_bytes = message.encode('utf-8') if isinstance(message, str) else message
    lib.RAPID_Core_LeveledLoggingPrint(level, tag_bytes, message_bytes)

def leveled_logging_info(tag, message):
    leveled_logging_print(RAPID_LOG_INFO, tag, message)

def leveled_logging_error(tag, message):
    leveled_logging_print(RAPID_LOG_ERROR, tag, message)

def upload_logging():
    result = lib.RAPID_Core_UploadLogging()
    if result:
        return result.decode('utf-8')
    return None 