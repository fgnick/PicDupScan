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