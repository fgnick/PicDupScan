#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ===============================================================================================

from dataclasses import dataclass

@dataclass(frozen=True)
class PicConst:
    
    # Image extensions
    IMG_EXTENSIONS = { '.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff' }
    
    # Raw extensions
    RAW_EXTENSIONS = { '.arw', '.cr2', '.nef', '.dng', '.orf', '.rw2', '.pef', '.srw', '.raf' }

    # Video extensions
    VIDEO_EXTENSIONS = { 
        '.mp4', '.mov', '.avi', '.mkv',
        '.mts', '.m2ts',                    # AVCHD (Sony, Panasonic)
        '.mxf',                             # Professional (Canon, Sony)
        '.wmv', '.mpg', '.mpeg',            # General
        '.webm', '.flv', '.3gp'             # Other
    }