#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ===============================================================================================
import os
import subprocess
from typing import override
import send2trash
import rawpy

from PyQt6.QtWidgets import QFrame, QToolButton, QMenu, QMessageBox
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QPainter, QColor, QImage, QPixmap, QImageReader

from .settings.gui_text import MenuText, MsgBoxText, ErrorText
from .settings.pic_constants import PicConst

class ImagePreviewWidget(QFrame):
    file_deleted_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Sunken)
        self.main_pixmap = None
        self.thumb_pixmap = None
        self.current_file_path = None
        
        # "More" Button
        self.more_btn = QToolButton(self)
        self.more_btn.setText("⋮")
        self.more_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.more_btn.setAutoRaise(True)
        self.more_btn.setFixedSize(30, 30)
        self.more_btn.setStyleSheet("""
            QToolButton {
                font-size: 20px;
                font-weight: bold;
                border: none;
                background-color: rgba(0,0,0,40);
                border-radius: 14px;
            }
            QToolButton::menu-indicator {
                image: none;
                width: 0px;
            }
            QToolButton:hover {
                background-color: rgba(0,0,0,70);
            }
        """)
        
        # Menu for More Button
        self.menu = QMenu(self)
        self.action_view = self.menu.addAction(MenuText.VIEW)
        self.action_open = self.menu.addAction(MenuText.OPEN_IN_FOLDER)
        self.action_delete = self.menu.addAction(MenuText.DELETE)
        self.more_btn.setMenu(self.menu)
        
        # Connect actions
        self.action_view.triggered.connect(self.view_file)
        self.action_open.triggered.connect(self.open_in_folder)
        self.action_delete.triggered.connect(self.delete_file)
        
        # Position button in top-right
        self.more_btn.move(self.width() - 40, 10)
        self.more_btn.hide() # Hide by default

    @override
    def resizeEvent(self, event):
        margin = 5
        x = self.width() - self.more_btn.width() - margin
        y = margin
        self.more_btn.move(x, y)
        self.more_btn.raise_()
        super().resizeEvent(event)

    def view_file(self):
        if self.current_file_path and os.path.exists(self.current_file_path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(self.current_file_path))

    def open_in_folder(self):
        if self.current_file_path and os.path.exists(self.current_file_path):
            # Windows specific command to select file in explorer
            subprocess.Popen(f'explorer /select,"{self.current_file_path}"')

    def delete_file(self):
        if self.current_file_path and os.path.exists(self.current_file_path):
            # show confirm dialog
            reply = QMessageBox.question(
                self,
                MsgBoxText.TITLE_CONFIRM,
                MsgBoxText.MSG_CONFIRM_DELETE.format(filename=self.current_file_path),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            # delete file if user confirm
            if reply == QMessageBox.StandardButton.Yes:
                file_path_to_delete = self.current_file_path
                try:
                    send2trash.send2trash(file_path_to_delete)
                    self.main_pixmap = None
                    self.thumb_pixmap = None
                    self.current_file_path = None # Clear path
                    self.more_btn.hide() # Hide more button
                    self.update()
                    # Signal to parent to update tree
                    self.file_deleted_signal.emit(file_path_to_delete)
                except Exception as e:
                    print(f"Error deleting file: {e}")
                    QMessageBox.warning(self, MsgBoxText.TITLE_ERROR, ErrorText.FILE_DELETE_FAILED.format(error=e))
        else:
            QMessageBox.warning(self, MsgBoxText.TITLE_ERROR, ErrorText.FILE_NOT_FOUND)
                
    def get_pixmap(self, path):
        if not path or not os.path.exists(path):
            return None
        
        try:
            lower_path = path.lower()
            # Simple check for common RAW formats
            if lower_path.endswith(tuple(PicConst.RAW_EXTENSIONS)):
                with rawpy.imread(path) as raw:
                    # Postprocess to get an RGB image
                    rgb = raw.postprocess(use_camera_wb=True, no_auto_bright=True, output_bps=8)
                    height, width, channel = rgb.shape
                    bytesPerLine = 3 * width
                    qImg = QImage(rgb.data, width, height, bytesPerLine, QImage.Format.Format_RGB888)
                    return QPixmap.fromImage(qImg)
            else:
                # Use QImageReader to respect EXIF orientation (setAutoTransform)
                reader = QImageReader(path)
                reader.setAutoTransform(True)
                img = reader.read()
                if img.isNull():
                    print(f"Failed to read image: {path}, error: {reader.errorString()}")
                    return None
                return QPixmap.fromImage(img)
        except Exception as e:
            print(f"Error loading image {path}: {e}")
            return None

    def load_images(self, main_path, thumb_path):
        self.current_file_path = main_path
        
        # Check if this is a parent view (Source file, not duplicate)
        is_parent = False
        if main_path and thumb_path and main_path == thumb_path:
            is_parent = True

        if is_parent:
            self.main_pixmap = None # Don't show main image for parent
        else:
            self.main_pixmap = self.get_pixmap(main_path)
            
        self.thumb_pixmap = self.get_pixmap(thumb_path)
        
        # Show button if we have any image to show
        if self.main_pixmap or self.thumb_pixmap:
            self.more_btn.show()
        else:
            self.more_btn.hide()
            
        # Hide delete option for parent (Source) files
        self.action_delete.setVisible(not is_parent)
            
        self.update() # Trigger repaint

    @override
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self.main_pixmap:
            # Draw Main Image (Scaled to fit, keep aspect ratio)
            scaled_main = self.main_pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            x = (self.width() - scaled_main.width()) // 2
            y = (self.height() - scaled_main.height()) // 2
            painter.drawPixmap(x, y, scaled_main)

        if self.thumb_pixmap:
            # Draw Thumbnail (Bottom-Right, 1/4 size of widget or fixed max size)
            thumb_w = min(200, self.width() // 3)
            thumb_h = min(150, self.height() // 3)
            scaled_thumb = self.thumb_pixmap.scaled(thumb_w, thumb_h, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            
            # Add border/background for visibility
            margin = 10
            thumb_x = self.width() - scaled_thumb.width() - margin
            thumb_y = self.height() - scaled_thumb.height() - margin
            
            # Draw background rect for thumbnail
            painter.fillRect(thumb_x - 2, thumb_y - 2, scaled_thumb.width() + 4, scaled_thumb.height() + 4, QColor(255, 255, 255, 200))
            painter.setPen(QColor(0, 0, 0))
            painter.drawRect(thumb_x - 2, thumb_y - 2, scaled_thumb.width() + 4, scaled_thumb.height() + 4)
            
            painter.drawPixmap(thumb_x, thumb_y, scaled_thumb)