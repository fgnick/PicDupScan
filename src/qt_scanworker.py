#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ===============================================================================================

import os
from PyQt6.QtCore import QThread, pyqtSignal

# custom modules -- constants
from .settings.pic_constants import PicConst

# custom modules
from .log_proc import Logger
from .pic_similar_proc import PicSimilarProc
from .settings.gui_text import LogText

# Background thread for running the image scanning process.
class QtScanWorker(QThread):
    # Signals to emit log messages, duplicate found, and scan finished for GUI update
    log_signal = pyqtSignal(str)
    duplicate_found_signal = pyqtSignal(str, str)
    finished_signal = pyqtSignal()

    def __init__(self, target_folder_path, scan_folder_path):
        super().__init__()
        self.target_folder_path = target_folder_path
        self.scan_folder_path = scan_folder_path
        self._is_running = True

    def run(self):
        # Redirect Logger output to signal
        Logger.setCallback(self.log_signal.emit)
        
        try:
            pic_proc = PicSimilarProc()
            
            # Get target files
            target_image_files = pic_proc.get_image_files(self.target_folder_path, PicConst.IMG_EXTENSIONS)
            target_raw_files = pic_proc.get_image_files(self.target_folder_path, PicConst.RAW_EXTENSIONS)

            if not target_image_files and not target_raw_files:
                Logger.setLog(Logger.LOG_LV_ERROR, LogText.NO_TARGET_FILES.format(path=self.target_folder_path))
                self.finished_signal.emit()
                return

            # Get scan files
            scan_image_files = pic_proc.get_image_files(self.scan_folder_path, PicConst.IMG_EXTENSIONS)
            scan_raw_files = pic_proc.get_image_files(self.scan_folder_path, PicConst.RAW_EXTENSIONS)

            if not scan_image_files and not scan_raw_files:
                Logger.setLog(Logger.LOG_LV_ERROR, LogText.NO_SCAN_FILES.format(path=self.scan_folder_path))
                self.finished_signal.emit()
                return

            # Compare standard images
            if target_image_files and scan_image_files:
                Logger.setLog(Logger.LOG_LV_INFO, LogText.FOUND_TARGET_IMAGES.format(count=len(target_image_files)))
                
                for file1 in target_image_files:
                    if not self._is_running: 
                        break
                    
                    Logger.setLog(Logger.LOG_LV_INFO, LogText.TARGET_IMAGE.format(path=os.path.basename(file1)))

                    for file2 in scan_image_files:
                        if not self._is_running: 
                            break
                        
                        Logger.setLog(Logger.LOG_LV_INFO, LogText.SCAN_IMAGE.format(path=os.path.basename(file2)))
                        if pic_proc.images_are_similar(file1, file2, cutoff=10):
                            Logger.setLog(Logger.LOG_LV_INFO, LogText.SCAN_MATCH.format(file1=os.path.basename(file1), file2=os.path.basename(file2)))
                            self.duplicate_found_signal.emit(file1, file2)

            # Compare RAW images
            if target_raw_files and scan_raw_files:
                Logger.setLog(Logger.LOG_LV_INFO, LogText.FOUND_TARGET_RAWS.format(count=len(target_raw_files)))
                
                for file1 in target_raw_files:
                    if not self._is_running: 
                        break
                    
                    Logger.setLog(Logger.LOG_LV_INFO, LogText.TARGET_RAW.format(path=os.path.basename(file1)))

                    for file2 in scan_raw_files:
                        if not self._is_running: 
                            break
                        
                        Logger.setLog(Logger.LOG_LV_INFO, LogText.SCAN_RAW.format(path=os.path.basename(file2)))
                        if pic_proc.raws_are_similar(file1, file2):
                            Logger.setLog(Logger.LOG_LV_INFO, LogText.SCAN_MATCH.format(file1=os.path.basename(file1), file2=os.path.basename(file2)))
                            self.duplicate_found_signal.emit(file1, file2)
        
        except Exception as e:
            Logger.setLog(Logger.LOG_LV_ERROR, LogText.SCAN_ERROR.format(error=str(e)))
        finally:
            self.finished_signal.emit()

    def stop(self):
        self._is_running = False