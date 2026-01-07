#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ===============================================================================================
import io
import os
import re
import hashlib
import subprocess
import imagehash
from PIL import Image
import rawpy
import numpy as np

from .log_proc import Logger
from .settings.pic_constants import PicConst

class PicSimilarProc:
    
    def __init__(self):
        raise Exception( "You cannot construct PicSimilarProc class! This is a static class." )

    # get image files depending on extensions
    @staticmethod
    def get_source_files(directory, extensions = None):
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

    # ------------------------------------------------------------------------------
    # Calculation methods for Hashing Cache
    # ------------------------------------------------------------------------------
    
    @staticmethod
    def calculate_image_hashes(path):
        """Calculate image hashes including 90, 180, 270 rotations."""
        try:
            image = Image.open(path)
            # Standard phash
            hashes = [imagehash.phash(image)]
            # Rotations
            for angle in [90, 180, 270]:
                rotated = image.rotate(angle, expand=True)
                hashes.append(imagehash.phash(rotated))
            return hashes
        except Exception as e:
            Logger.setLog(Logger.LOG_LV_ERROR, f"Error calculating image hash for {path}: {e}")
            return None

    @staticmethod
    def calculate_raw_metadata(path):
        """Calculate raw sensor data bytes."""
        try:
            with rawpy.imread(path) as raw:
                return np.array(raw.raw_image).tobytes()
        except Exception as e:
            Logger.setLog(Logger.LOG_LV_ERROR, f"Error calculating raw metadata for {path}: {e}")
            return None

    @staticmethod
    def calculate_video_hashes(path):
        """Calculate video frame hashes."""
        try:
            import imageio_ffmpeg   # lazy import
            ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
            if not ffmpeg_exe or not os.path.exists(ffmpeg_exe):
                return None
            
            # Use the existing internal logic but wrap it
            pic_proc = PicSimilarProc
            return pic_proc._get_video_frame_hashes_static(path, ffmpeg_exe)
        except Exception as e:
            Logger.setLog(Logger.LOG_LV_ERROR, f"Error calculating video hash for {path}: {e}")
            return None

    @staticmethod
    def images_compare_cached(h1_list, h2_list, cutoff=10):
        """Compare pre-calculated image hash lists."""
        # h1_list is target, usually we compare h1[0] against all of h2 (target's original vs scan's rotations)
        # Or more commonly: any rotation matches.
        # Logic: Compare target's original (h1[0]) with any of scan's rotations (h2_list)
        target_hash = h1_list[0]
        for scan_hash in h2_list:
            if abs(target_hash - scan_hash) < cutoff:
                return True
        return False

    @staticmethod
    def raws_compare_cached(b1, b2):
        """Compare pre-calculated raw bytes."""
        return b1 == b2

    @staticmethod
    def videos_compare_cached(h1_list, h2_list, cutoff=10):
        """Compare pre-calculated video frame hash lists."""
        if not h1_list or not h2_list or len(h1_list) != len(h2_list):
            return False
            
        diffs = [abs(h1 - h2) for h1, h2 in zip(h1_list, h2_list)]
        return max(diffs) < cutoff

    # ------------------------------------------------------------------------------
    # Internal helpers (Static version for logic separation if needed)
    # ------------------------------------------------------------------------------

    @staticmethod
    def _get_video_frame_hashes_static(video_path, ffmpeg_exe):
        duration = PicSimilarProc._get_video_duration_static(video_path, ffmpeg_exe)
        if duration is None or duration < 5:
            return PicSimilarProc._extract_frame_hash_at_time_static(video_path, ffmpeg_exe, "00:00:01")
            
        timestamps = [duration * 0.1, duration * 0.5, duration * 0.9]
        hashes = []
        for ts in timestamps:
            ts_str = f"{ts:.2f}"
            extracted = PicSimilarProc._extract_frame_hash_at_time_static(video_path, ffmpeg_exe, ts_str)
            if extracted:
                hashes.extend(extracted)
        return hashes

    @staticmethod
    def _get_video_duration_static(path, ffmpeg_exe):
        try:
             cmd = [ffmpeg_exe, '-i', path]
             startupinfo = None
             if os.name == 'nt':
                 startupinfo = subprocess.STARTUPINFO()
                 startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
             res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo, timeout=5)
             output = res.stderr.decode('utf-8', errors='ignore')
             m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", output)
             if m:
                 h, m, s = map(float, m.groups())
                 return h * 3600 + m * 60 + s
        except: pass
        return None

    @staticmethod
    def _extract_frame_hash_at_time_static(video_path, ffmpeg_exe, timestamp):
         cmd = [
             ffmpeg_exe, '-ss', timestamp, '-i', video_path,
             '-vframes', '1', '-f', 'image2pipe', '-vcodec', 'bmp', '-', '-hide_banner', '-loglevel', 'panic'
         ]
         startupinfo = None
         if os.name == 'nt':
             startupinfo = subprocess.STARTUPINFO()
             startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
         try:
             res = subprocess.run(cmd, stdout=subprocess.PIPE, startupinfo=startupinfo, timeout=5)
             if res.stdout:
                 img = Image.open(io.BytesIO(res.stdout))
                 return [imagehash.phash(img)]
         except: pass
         return []

    # compare images (DEPRECATED: Use caching methods for performance)
    @staticmethod
    def images_are_similar(img1_path, img2_path, cutoff=5):
        h1 = PicSimilarProc.calculate_image_hashes(img1_path)
        h2 = PicSimilarProc.calculate_image_hashes(img2_path)
        if h1 and h2:
            return PicSimilarProc.images_compare_cached(h1, h2, cutoff)
        return False

    # compare raws' sensor data (DEPRECATED: Use caching methods for performance)
    @staticmethod
    def raws_are_similar(raw1_path, raw2_path):
        b1 = PicSimilarProc.calculate_raw_metadata(raw1_path)
        b2 = PicSimilarProc.calculate_raw_metadata(raw2_path)
        if b1 is not None and b2 is not None:
            return PicSimilarProc.raws_compare_cached(b1, b2)
        return False

    # compare videos (DEPRECATED: Use caching methods for performance)
    @staticmethod
    def videos_are_similar(video1_path, video2_path, strict=True):
        if strict:
            # For strict, we still use the partial MD5 as it's already fast
            return PicSimilarProc._compare_videos_strict_static(video1_path, video2_path)
        else:
            h1 = PicSimilarProc.calculate_video_hashes(video1_path)
            h2 = PicSimilarProc.calculate_video_hashes(video2_path)
            if h1 and h2:
                return PicSimilarProc.videos_compare_cached(h1, h2)
            return False

    @staticmethod
    def _compare_videos_strict_static(vid1, vid2):
        try:
            return PicSimilarProc._compute_partial_md5_static(vid1) == PicSimilarProc._compute_partial_md5_static(vid2)
        except Exception as e:
            Logger.setLog(Logger.LOG_LV_ERROR, f"Error (Strict) video compare: {e}")
            return False

    @staticmethod
    def _compute_partial_md5_static(file_path, chunk_size=4096):
        md5 = hashlib.md5()
        try:
            total_size = os.path.getsize(file_path)
            with open(file_path, 'rb') as f:
                md5.update(f.read(chunk_size))
                if total_size > chunk_size * 2:
                    f.seek(total_size // 2)
                    md5.update(f.read(chunk_size))
                if total_size > chunk_size:
                    f.seek(max(0, total_size - chunk_size))
                    md5.update(f.read(chunk_size))
            return md5.hexdigest()
        except Exception as e:
            Logger.setLog(Logger.LOG_LV_ERROR, f"Hash Error: {e}")
            return None

            