#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ===============================================================================================
import os
from typing import override

from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QMessageBox

from .log_proc import Logger
from .pic_similar_proc import PicSimilarProc
from .settings.gui_text import LogText, ErrorText, MsgBoxText
from .app_configs import AppConfigs

# Background thread for running the image scanning process.
class QtScanWorker(QThread):
    # Signals to emit log messages, duplicate found, and scan finished for GUI update
    log_signal = pyqtSignal(str)
    duplicate_found_signal = pyqtSignal(str, str)
    finished_signal = pyqtSignal()

    def __init__(self, parent, target_folder_path, scan_folder_path):
        super().__init__(parent)
        self.target_folder_path = target_folder_path
        self.scan_folder_path = scan_folder_path
        self._is_running = True
        self.is_config_valid = True

        self.scan_scope = AppConfigs.get_scan_scope()
        if not self.scan_scope:
            QMessageBox.critical(parent, MsgBoxText.TITLE_CRITICAL, ErrorText.CONFIG_ERROR_SCAN_SCOPE)
            Logger.setLog(Logger.LOG_LV_CRITICAL, ErrorText.CONFIG_ERROR_SCAN_SCOPE)
            self.is_config_valid = False
            return

        self.extension_filters = AppConfigs.get_scan_extensions(return_type="set")
        if not self.extension_filters:
            QMessageBox.critical(parent, MsgBoxText.TITLE_CRITICAL, ErrorText.CONFIG_ERROR_SCAN_EXTENSIONS)
            Logger.setLog(Logger.LOG_LV_CRITICAL, ErrorText.CONFIG_ERROR_SCAN_EXTENSIONS)
            self.is_config_valid = False
            return
    
    @override
    def run(self):
        # Redirect Logger output to signal
        Logger.setCallback(self.log_signal.emit)
        
        if not self.is_config_valid:
             self.finished_signal.emit()
             return
        
        try:
            # show scan scope to logviewer
            scope_formatted = []
            for k, v in self.scan_scope.items():
                # Display Green Check for True, Red Cross for False (using Unicode)
                mark = "✅" if v else "❌"
                scope_formatted.append(f"{k}: {mark}")
            
            Logger.setLog(Logger.LOG_LV_INFO, LogText.SCAN_SCOPE.format(scope=", ".join(scope_formatted))) 


            # Define like function index
            # Each config: (ScopeKey, FilterKey, FindLog, TargetLog, ScanLog, CompareFunc)
            # Use partials or lambdas if compare func needs extra args like cutoff
            scan_configs = [
                ("IMAGE", "Image", LogText.FOUND_TARGET_IMAGES, LogText.TARGET_IMAGE, LogText.SCAN_IMAGE, PicSimilarProc.calculate_image_hashes, PicSimilarProc.images_compare_cached),
                ("RAW",   "Raw",   LogText.FOUND_TARGET_RAWS,   LogText.TARGET_RAW,   LogText.SCAN_RAW,   PicSimilarProc.calculate_raw_metadata, PicSimilarProc.raws_compare_cached),
                ("VIDEO", "Video", LogText.FOUND_TARGET_VIDEOS, LogText.TARGET_VIDEO, LogText.SCAN_VIDEO, PicSimilarProc.calculate_video_hashes, PicSimilarProc.videos_compare_cached)
            ]

            for scope_key, filter_key, log_found, log_target, log_scan, calc_func, compare_func in scan_configs:
                if not self._is_running: break
                
                if not self.scan_scope.get(scope_key, False):
                    continue

                exts = self.extension_filters.get(filter_key)
                target_paths = PicSimilarProc.get_source_files(self.target_folder_path, exts)
                scan_paths = PicSimilarProc.get_source_files(self.scan_folder_path, exts)

                if target_paths and scan_paths:
                    Logger.setLog(Logger.LOG_LV_INFO, log_found.format(count=len(target_paths)))
                    
                    # --- Hashing Cache Phase ---
                    hash_cache = {}
                    all_unique_files = list(set(target_paths + scan_paths))
                    
                    Logger.setLog(Logger.LOG_LV_INFO, f"Pre-calculating features for {len(all_unique_files)} files...")
                    for i, path in enumerate(all_unique_files):
                        if not self._is_running: break
                        if i % 10 == 0: # Periodically update status or log
                             self.log_signal.emit(f"Progress: {i}/{len(all_unique_files)} files processed")
                        
                        hash_cache[path] = calc_func(path)

                    # --- Comparison Phase ---
                    Logger.setLog(Logger.LOG_LV_INFO, "Starting comparison (Fast Phase)...")
                    for file1 in target_paths:
                        if not self._is_running: break
                        h1 = hash_cache.get(file1)
                        if h1 is None: continue

                        Logger.setLog(Logger.LOG_LV_INFO, log_target.format(path=os.path.basename(file1)))
                        
                        for file2 in scan_paths:
                            if not self._is_running: break
                            # Skip if same file
                            if file1 == file2: continue
                            
                            h2 = hash_cache.get(file2)
                            if h2 is None: continue
                            
                            if compare_func(h1, h2):
                                match_msg = LogText.SCAN_MATCH.format(file1=os.path.basename(file1), file2=os.path.basename(file2))
                                Logger.setLog(Logger.LOG_LV_INFO, match_msg)
                                self.duplicate_found_signal.emit(file1, file2)
        
        except Exception as e:
            Logger.setLog(Logger.LOG_LV_ERROR, LogText.SCAN_ERROR.format(error=str(e)))
        finally:
            self.finished_signal.emit()

    def stop(self):
        self._is_running = False