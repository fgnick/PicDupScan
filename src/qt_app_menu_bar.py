#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ===============================================================================================
from typing import override

from PyQt6.QtWidgets import QMenuBar, QApplication
from PyQt6.QtGui import QAction
from PyQt6.QtCore import pyqtSignal, Qt

from .qt_scan_scope_dialog import ScanScopeDialog
from .qt_app_about_dialog import AboutDialog
from .settings.gui_text import AppMenuBarText

class PicDupMenu(QMenuBar):
    view_exif_toggled = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_menu()

    def init_menu(self):
        # File Menu
        file_menu = self.addMenu(AppMenuBarText.FILE)
        
        # File Menu > Settings
        settings_action = QAction(AppMenuBarText.SETTINGS, self)
        settings_action.triggered.connect(self.open_settings)
        file_menu.addAction(settings_action)

        # File Menu > About
        about_action = QAction(AppMenuBarText.FILE_ABOUT, self)
        about_action.triggered.connect(self.about_app)
        file_menu.addAction(about_action)
        
        file_menu.addSeparator()

        # File Menu > Close App
        close_action = QAction(AppMenuBarText.FILE_CLOSE, self)
        close_action.triggered.connect(self.close_app)
        file_menu.addAction(close_action)

        # View Menu
        view_menu = self.addMenu(AppMenuBarText.VIEW)

        # View Menu > Exif panel switch Component
        self.view_exif_widget_action = QAction(AppMenuBarText.VIEW_EXIF_PANEL, self)
        self.view_exif_widget_action.setCheckable(True)
        self.view_exif_widget_action.triggered.connect(self.toggle_exif)
        view_menu.addAction(self.view_exif_widget_action)

        # Settings Menu
        settings_menu = self.addMenu(AppMenuBarText.SETTINGS)

        # Settings Menu -> Scan File Extensions
        scan_ext_action = QAction(AppMenuBarText.SETTINGS_SCAN_FILE_EXTENSIONS, self)
        scan_ext_action.triggered.connect(self.open_settings) # Re-use open_settings for now or separate
        settings_menu.addAction(scan_ext_action)

    def open_settings(self):
        dialog = ScanScopeDialog(self)
        dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        dialog.exec()

    def about_app(self):
        dialog = AboutDialog(self)
        dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        dialog.exec()

    def close_app(self):
        QApplication.instance().quit()

    def toggle_exif(self, checked):
        self.view_exif_toggled.emit(checked)
