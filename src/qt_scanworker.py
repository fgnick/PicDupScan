#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ===============================================================================================

import os
from typing import override

from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QMessageBox

# custom modules
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

        self.extension_filters = AppConfigs.get_scan_extensions(as_set=True)
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

            pic_proc = PicSimilarProc()

            # Define like function index
            # Each config: (ScopeKey, FilterKey, FindLog, TargetLog, ScanLog, CompareFunc)
            # Use partials or lambdas if compare func needs extra args like cutoff  <---- maybe not used XDD
            scan_configs = [
                ("IMAGE", "Image", LogText.FOUND_TARGET_IMAGES, LogText.TARGET_IMAGE, LogText.SCAN_IMAGE, lambda f1, f2: pic_proc.images_are_similar(f1, f2, cutoff=10)),
                ("RAW",   "Raw",   LogText.FOUND_TARGET_RAWS,   LogText.TARGET_RAW,   LogText.SCAN_RAW,   pic_proc.raws_are_similar),
                # ("VIDEO", "Video", LogText.FOUND_TARGET_VIDEOS, LogText.TARGET_VIDEO, LogText.SCAN_VIDEO, pic_proc.videos_are_similar)
            ]

            for scope_key, filter_key, log_found, log_target, log_scan, compare_func in scan_configs:
                if not self._is_running: break
                
                # Check if this category is enabled
                if not self.scan_scope.get(scope_key, False):
                    continue

                # Get files
                exts = self.extension_filters.get(filter_key)
                target_files = pic_proc.get_source_files(self.target_folder_path, exts)
                scan_files = pic_proc.get_source_files(self.scan_folder_path, exts)

                if target_files and scan_files:
                    Logger.setLog(Logger.LOG_LV_INFO, log_found.format(count=len(target_files)))
                    
                    for file1 in target_files:
                        if not self._is_running: break
                        Logger.setLog(Logger.LOG_LV_INFO, log_target.format(path=os.path.basename(file1)))
                        
                        for file2 in scan_files:
                            if not self._is_running: break
                            Logger.setLog(Logger.LOG_LV_INFO, log_scan.format(path=os.path.basename(file2)))
                            
                            if compare_func(file1, file2):
                                match_msg = LogText.SCAN_MATCH.format(file1=os.path.basename(file1), file2=os.path.basename(file2))
                                Logger.setLog(Logger.LOG_LV_INFO, match_msg)
                                self.duplicate_found_signal.emit(file1, file2)
        
        except Exception as e:
            Logger.setLog(Logger.LOG_LV_ERROR, LogText.SCAN_ERROR.format(error=str(e)))
        finally:
            self.finished_signal.emit()

    def stop(self):
        self._is_running = False