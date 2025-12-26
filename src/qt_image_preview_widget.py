#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ===============================================================================================
import os
import subprocess
from typing import override
import send2trash
import rawpy

from PyQt6.QtWidgets import QFrame, QToolButton, QMenu, QMessageBox
from PyQt6.QtCore import pyqtSignal, Qt, QUrl, QEvent
from PyQt6.QtGui import QPainter, QColor, QImage, QPixmap, QImageReader, QDesktopServices

from .settings.gui_text import MenuText, MsgBoxText, ErrorText
from .settings.pic_constants import PicConst
from .qt_exif_compare_widget import ExifCompareWidget

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
        self.action_exif = self.menu.addAction(MenuText.EXIF)
        self.action_view = self.menu.addAction(MenuText.VIEW)
        self.action_open = self.menu.addAction(MenuText.OPEN_IN_FOLDER)
        self.action_delete = self.menu.addAction(MenuText.DELETE)
        self.more_btn.setMenu(self.menu)
        
        # Connect actions
        self.action_view.triggered.connect(self.view_file)
        self.action_open.triggered.connect(self.open_in_folder)
        self.action_delete.triggered.connect(self.delete_file)
        self.action_exif.triggered.connect(self.show_exif)
        self.action_exif.setCheckable(True)
        
        # Exif Widget
        self.exif_widget = ExifCompareWidget(self)
        self.exif_widget.hide()
        self.exif_widget.close_signal.connect(self.hide_exif)
        self.exif_widget.installEventFilter(self) # Install filter to catch resize events on header
        self.thumb_path = None
        
        # Exif Resizing State
        self._exif_height = 300
        self._is_resizing_exif = False
        self._resize_handle_height = 10
        self.setMouseTracking(True) # Enable mouse tracking for cursor change
        
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
        
        # Resize Exif Widget
        if self.exif_widget.isVisible():
            exif_h = self._exif_height
            # Ensure height is within reasonable bounds
            exif_h = max(100, min(self.height() - 100, exif_h))
            self._exif_height = exif_h
            
            self.exif_widget.setGeometry(0, self.height() - exif_h, self.width(), exif_h)
            
        super().resizeEvent(event)

    @override
    def eventFilter(self, obj, event):
        if obj == self.exif_widget:
            if event.type() == QEvent.Type.MouseMove:
                y = event.pos().y()
                # Check top edge (header area)
                if y <= 5 or self._is_resizing_exif:
                    self.setCursor(Qt.CursorShape.SplitVCursor)
                    
                    if self._is_resizing_exif:
                        global_y = self.exif_widget.mapToParent(event.pos()).y()
                        new_height = self.height() - global_y
                        new_height = max(100, min(self.height() - 100, new_height))
                        self._exif_height = new_height
                        self.exif_widget.setGeometry(0, self.height() - new_height, self.width(), new_height)
                        self.update() 
                        return True
                else:
                    self.setCursor(Qt.CursorShape.ArrowCursor)
            elif event.type() == QEvent.Type.MouseButtonPress:
                if event.button() == Qt.MouseButton.LeftButton:
                    if event.pos().y() <= 5:
                        self._is_resizing_exif = True
                        return True
            elif event.type() == QEvent.Type.MouseButtonRelease:
                if self._is_resizing_exif:
                    self._is_resizing_exif = False
                    self.setCursor(Qt.CursorShape.ArrowCursor)
                    return True
        return super().eventFilter(obj, event)

    @override
    def mousePressEvent(self, event):
        if self.exif_widget.isVisible() and event.button() == Qt.MouseButton.LeftButton:
            exif_top = self.height() - self._exif_height
            if exif_top - 5 <= event.pos().y() <= exif_top:
                self._is_resizing_exif = True
                event.accept()
                return
        super().mousePressEvent(event)

    @override
    def mouseReleaseEvent(self, event):
        if self._is_resizing_exif:
            self._is_resizing_exif = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
            return
        super().mouseReleaseEvent(event)

    @override
    def mouseMoveEvent(self, event):
        if self.exif_widget.isVisible():
            exif_top = self.height() - self._exif_height
            
            # Check for hover to change cursor
            if exif_top - 5 <= event.pos().y() <= exif_top:
                self.setCursor(Qt.CursorShape.SplitVCursor)
            elif not self._is_resizing_exif:
                self.setCursor(Qt.CursorShape.ArrowCursor)
                
            # Handle resizing
            if self._is_resizing_exif:
                new_height = self.height() - event.pos().y()
                # Constrain height
                new_height = max(100, min(self.height() - 100, new_height))
                self._exif_height = new_height
                self.exif_widget.setGeometry(0, self.height() - new_height, self.width(), new_height)
                self.update() # Trigger repaint to adjust image area
                event.accept()
                return

        super().mouseMoveEvent(event)

    def hide_exif(self):
        self.exif_widget.hide()
        self.action_exif.setChecked(False)
        self.update()

    def show_exif(self):
        is_checked = self.action_exif.isChecked()
        self.exif_widget.setVisible(is_checked)
        
        if is_checked:
            # Re-position and load content
            exif_h = self._exif_height
            self.exif_widget.setGeometry(0, self.height() - exif_h, self.width(), exif_h)
            
            if self.current_file_path and self.thumb_path:
                self.exif_widget.load_exif(self.current_file_path, self.thumb_path)
            self.exif_widget.raise_()
            
        self.update()

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
        self.thumb_path = thumb_path
        
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
            
        # Update exif if visible
        if self.exif_widget.isVisible():
            self.exif_widget.load_exif(main_path, thumb_path)

        self.update() # Trigger repaint

    @override
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self.main_pixmap:
            # Draw Main Image (Scaled to fit, keep aspect ratio)
            
            # Adjust drawing area if exif is open
            draw_h = self.height()
            if self.exif_widget.isVisible():
                draw_h -= self.exif_widget.height()
                
            scaled_main = self.main_pixmap.scaled(self.width(), draw_h, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            x = (self.width() - scaled_main.width()) // 2
            y = (draw_h - scaled_main.height()) // 2
            painter.drawPixmap(x, y, scaled_main)

        if self.thumb_pixmap:
            # Draw Thumbnail (Bottom-Right, 1/4 size of widget or fixed max size)
            thumb_w = min(200, self.width() // 3)
            thumb_h = min(150, self.height() // 3)
            scaled_thumb = self.thumb_pixmap.scaled(thumb_w, thumb_h, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            
            # Add border/background for visibility
            margin = 10
            
            # Adjust thumb position if exif is open
            bottom_offset = 0
            if self.exif_widget.isVisible():
                bottom_offset = self.exif_widget.height()

            thumb_x = self.width() - scaled_thumb.width() - margin
            thumb_y = self.height() - scaled_thumb.height() - margin - bottom_offset
            
            # Draw background rect for thumbnail
            painter.fillRect(thumb_x - 2, thumb_y - 2, scaled_thumb.width() + 4, scaled_thumb.height() + 4, QColor(255, 255, 255, 200))
            painter.setPen(QColor(0, 0, 0))
            painter.drawRect(thumb_x - 2, thumb_y - 2, scaled_thumb.width() + 4, scaled_thumb.height() + 4)
            
            painter.drawPixmap(thumb_x, thumb_y, scaled_thumb)