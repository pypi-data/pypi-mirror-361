"""
RAPID Kit Python SDK
"""
import os
import sys

from .initialize import initialize, version_name, build_id, commit_hash, app_id, package_name
from .player import MediaPlayer, MediaRenderState
from .media_chat import MediaChat
from .format import RGBFormat, set_rgb_pixel_format
from .sdl import create_silence_vout, create_silence_aout
from .auth import authenticate
from .chat_channel import ChatChannel
from .stream import LiveStream, LocalReplayStream, CloudReplayStream, StreamProvider
from .debug import create_debugging_code, apply_debugging_code
from .http import HttpMethod, http_request, http_get, http_post, http_delete, http_patch, enable_http_logging
from .instruct import InstructStandard
from .packet import Packet, StreamCodecID
from .log import leveled_logging_info, leveled_logging_error, upload_logging
from .pipe import Pipe, PipeState

__version__ = "1.0.7"

# Export all modules and functions
__all__ = [
    # Core functionalities
    'initialize', 'version_name', 'build_id', 'commit_hash', 'app_id', 'package_name',
    'authenticate',
    'set_rgb_pixel_format',
    'create_silence_vout',
    'create_silence_aout',
    
    # HTTP related
    'HttpMethod',
    'http_request',
    'http_get',
    'http_post',
    'http_delete',
    'http_patch',
    'enable_http_logging',
    
    # Media playback
    'MediaPlayer',
    'MediaChat',
    'RGBFormat',
    'MediaRenderState',
    
    # Communication and streams
    'ChatChannel',
    'LiveStream',
    'LocalReplayStream',
    'CloudReplayStream',
    'StreamProvider',
    'Packet',
    'StreamCodecID',
    'Pipe',
    'PipeState',
    
    # Debugging
    'create_debugging_code',
    'apply_debugging_code',
    'InstructStandard',
    'leveled_logging_info',
    'leveled_logging_error',
    'upload_logging'
]
