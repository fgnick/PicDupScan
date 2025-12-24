#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ===============================================================================================
from typing import override

# Qt
from PyQt6.QtWidgets import QMenuBar, QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QApplication
from PyQt6.QtGui import QAction

from .qt_scan_scope_dialog import ScanScopeDialog
from .settings.gui_text import AppText, AppMenuBarText

class PicDupMenu(QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_menu()

    def init_menu(self):
        # File Menu
        file_menu = self.addMenu(AppMenuBarText.FILE)

        # File Menu > About Component
        about_action = QAction(AppMenuBarText.FILE_ABOUT, self)
        about_action.triggered.connect(self.about_app)
        file_menu.addAction(about_action)
        
        # File Menu > Close Component
        close_action = QAction(AppMenuBarText.FILE_CLOSE, self)
        close_action.triggered.connect(self.close_app)
        file_menu.addAction(close_action)

        # Settings Menu
        settings_menu = self.addMenu(AppMenuBarText.SETTINGS)

        # Settings Menu > Scan File Extensions Component
        settings_action = QAction(AppMenuBarText.SETTINGS_SCAN_FILE_EXTENSIONS, self)
        settings_action.triggered.connect(self.edit_scan_scope)
        settings_menu.addAction(settings_action)

    def about_app(self):
        dialog = AboutDialog(self)
        dialog.exec()

    def edit_scan_scope(self):
        dialog = ScanScopeDialog(self)
        if dialog.is_valid: #
            dialog.exec()

    def close_app(self):
        QApplication.instance().quit()

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(AppMenuBarText.FILE_ABOUT)
        self.resize(300, 150)
        self.setup_ui()

    def setup_ui(self):
        # TODO: 
        # maybe the app needs to show some info about itself in the dialog
        # like version, author, license, etc.
        # for now, just show a simple dialog with an ok button
        
        main_layout = QVBoxLayout()
        main_layout.addStretch()
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.ok_btn = QPushButton(AppText.BUTTON_OK)
        self.ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_btn)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    @override
    def accept(self):
        #...
        super().accept()

