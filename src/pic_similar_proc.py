#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ===============================================================================================

import os
import imagehash
from PIL import Image
import rawpy
import numpy as np

from .log_proc import Logger
from .settings.pic_constants import PicConst

class PicSimilarProc:
    
    def __init__(self):
        pass

    # get image files depending on extensions
    def get_source_files(self, directory, extensions = None):
        if extensions is None:
            extensions = PicConst.IMG_EXTENSIONS
        else:
            if not isinstance(extensions, (set, list, tuple)):
                raise ValueError("Extensions must be a set, list, or tuple.")
            extensions = set(extensions) # Convert to set for search

        files = []
        # Use os.scandir for better performance (it iterates once and avoids multiple system calls)
        try:
            with os.scandir(directory) as entries:
                for entry in entries:
                    if entry.is_file():
                        # Check extension case-insensitively
                        _, ext = os.path.splitext(entry.name)
                        if ext.lower() in extensions:
                            files.append(entry.path)
        except OSError as e:
            Logger.setLog(Logger.LOG_LV_ERROR, f"Error {extensions} scanning directory {directory}: {e}")
            return []
        # remove all duplicates and sort
        return sorted(files)

    # compare images
    def images_are_similar(self, img1_path, img2_path, cutoff=5):
        try:
            image1 = Image.open(img1_path)
            image2 = Image.open(img2_path)

            if image1.mode != image2.mode:
                return False

            #if image1.size != image2.size:
            #    return False

            hash1 = imagehash.phash(image1)
            hash2 = imagehash.phash(image2)
            
            # 1. Direct comparison
            if abs(hash1 - hash2) < cutoff:
                return True
                
            # 2. Try rotating (90, 180, 270 degrees)
            # phash does not have rotation invariance, so we need to manually rotate and test
            for angle in [90, 180, 270]:
                # expand=True ensures that the size is automatically adjusted after rotation
                rotated_img2 = image2.rotate(angle, expand=True)
                rotated_hash2 = imagehash.phash(rotated_img2)
                
                if abs(hash1 - rotated_hash2) < cutoff:
                    # Logger.setLog(Logger.LOG_LV_INFO, f"Match found with {angle} degree rotation.")
                    return True
                    
            return False
        except Exception as e:
            Logger.setLog( Logger.LOG_LV_ERROR, "Error comparing images: " + str(e) )
            return False

    # compare raws' sensor data
    def raws_are_similar(self, raw1_path, raw2_path):
        try:
            with rawpy.imread(raw1_path) as raw1:
                with rawpy.imread(raw2_path) as raw2:
                    # RawPy object does not have .mode attribute. 
                    # We can compare raw_pattern or color_desc if needed, but raw_image comparison implies structure match.
                    
                    # convert raw sensor data to bytes
                    # This performs an EXACT comparison of the sensor data.
                    raw1_bytes = np.array(raw1.raw_image).tobytes()
                    raw2_bytes = np.array(raw2.raw_image).tobytes()

                    # compare bytes
                    return raw1_bytes == raw2_bytes
        except Exception as e:
            Logger.setLog( Logger.LOG_LV_ERROR, "Error comparing raws: " + str(e) )
            return False