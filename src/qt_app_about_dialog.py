#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ===============================================================================================
from typing import override

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt

from .settings.gui_text import AppText, AppMenuBarText
from .settings.env_constants import EnvConst

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(AppMenuBarText.FILE_ABOUT)
        self.resize(300, 150)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        
        info_label = QLabel(
            "PicDupScan<br><br>"
            f"Version {EnvConst.APP_VERSION}<br>"
            "A powerful tool to find duplicate images, RAW files, and videos.<br><br>"
            "Powered by PyQt6, rawpy, imagehash, and FFmpeg."
        )
        info_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        info_label.setWordWrap(True)
        info_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                border: 1px solid palette(mid);
                padding: 15px;
                background-color: palette(window);
                border-radius: 4px;
            }
        """)
        main_layout.addWidget(info_label)
        
        main_layout.addStretch()
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.ok_btn = QPushButton(AppText.BUTTON_OK)
        self.ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_btn)
        button_layout.addStretch()
        
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    @override
    def accept(self):
        super().accept()
