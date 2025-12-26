#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ===============================================================================================

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QToolBar, QStyle
from PyQt6.QtGui import QAction, QPainter, QColor, QPixmap, QIcon

from .settings.gui_text import AppText

class PicDupToolbar(QToolBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMovable(True)
        self.setFloatable(True)

        # Start Action
        self.start_action = QAction(self)
        self.start_action.setText(AppText.BUTTON_START_SCAN)
        self.start_action.setIcon(self.create_colored_icon(QStyle.StandardPixmap.SP_MediaPlay, "#4CAF50")) # Green
        self.addAction(self.start_action)

        # Stop Action
        self.stop_action = QAction(self)
        self.stop_action.setText(AppText.BUTTON_STOP_SCAN)
        self.stop_action.setIcon(self.create_colored_icon(QStyle.StandardPixmap.SP_MediaStop, "#F44336")) # Red
        self.stop_action.setEnabled(False) # Initially disabled
        self.addAction(self.stop_action)

    # Creates a QIcon from a standard pixmap, tinted with the specified color.
    # Attempts to follow the OS style by using the standard mask.
    def create_colored_icon(self, standard_pixmap, color_str):
        
        # Get the standard icon
        icon = self.style().standardIcon(standard_pixmap)
        pixmap = icon.pixmap(32, 32) # Get a reasonable size pixmap
        
        # Create a matching blank pixmap for drawing
        colored_pixmap = QPixmap(pixmap.size())
        colored_pixmap.fill(QColor(0,0,0,0)) # Transparent
        
        painter = QPainter(colored_pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 1. Draw the color
        painter.setBrush(QColor(color_str))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(colored_pixmap.rect())
        
        # 2. Draw the standard pixmap as a mask (CompositionMode_DestinationIn keeps destination where source is opaque)
        # However, standard pixmaps might not be single-color masks. 
        # Better approach for "OS Style" allows using the alpha channel of the OS icon.
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationIn)
        painter.drawPixmap(0, 0, pixmap)
        
        painter.end()
        
        return QIcon(colored_pixmap)

