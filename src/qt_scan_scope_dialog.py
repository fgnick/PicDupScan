#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ===============================================================================================

from typing import override
import logging

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QStyle, QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QToolButton,
                             QLabel, QCheckBox, QSpacerItem, QSizePolicy, QLineEdit, QFormLayout, QMessageBox)

from .settings.gui_text import AppText, MsgBoxText, ErrorText
from .app_configs import AppConfigs

# =========================================================
# Scan Scope Dialog to edit scan extensions...
# =========================================================
class ScanScopeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(AppText.SCAN_SCOPE_DIALOG_TITLE)
        self.resize(300, 150)
        
        self.is_valid = True

        # Validation before creation
        self.scan_scope = AppConfigs.get_scan_scope() # to read the config file and get the values of SCAN_EXTENSIONS_SCOPE section
        if not self.scan_scope:
             QMessageBox.critical(parent, MsgBoxText.TITLE_CRITICAL, ErrorText.CONFIG_ERROR_SCAN_SCOPE)
             self.is_valid = False
             return

        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()

        # Top row: Label + Stretch + Browse Button
        top_layout = QHBoxLayout()
        
        self.info_label = QLabel(AppText.LABEL_SCAN_SCOPE)
        top_layout.addWidget(self.info_label)
        
        top_layout.addStretch()
        
        self.btn_config = QToolButton()
        self.btn_config.setText(AppText.BUTTON_EDIT)
        self.btn_config.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView))
        self.btn_config.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.btn_config.clicked.connect(self.open_extension_settings)
        top_layout.addWidget(self.btn_config)
        
        main_layout.addLayout(top_layout)

        # Checkboxes
        self.chk_image = QCheckBox(AppText.LABEL_IMAGE)
        self.chk_image.setChecked(self.scan_scope["IMAGE"])
        main_layout.addWidget(self.chk_image)

        self.chk_raw = QCheckBox(AppText.LABEL_RAW)
        self.chk_raw.setChecked(self.scan_scope["RAW"])
        main_layout.addWidget(self.chk_raw)

        self.chk_video = QCheckBox(AppText.LABEL_VIDEO)
        self.chk_video.setChecked(self.scan_scope["VIDEO"])
        main_layout.addWidget(self.chk_video)

        spacer = QSpacerItem(
            20, 10,
            QSizePolicy.Policy.Minimum,
            QSizePolicy.Policy.Fixed
        )
        main_layout.addItem(spacer)
        
        # Push everything above to top, and buttons to bottom
        main_layout.addStretch()

        # Button Layout (Bottom Right)
        button_layout = QHBoxLayout()
        button_layout.addStretch() # Push buttons to the right
        
        self.cancel_btn = QPushButton(AppText.BUTTON_CANCEL)
        self.save_btn = QPushButton(AppText.BUTTON_OK)
        
        self.save_btn.clicked.connect(self.accept) 
        self.cancel_btn.clicked.connect(self.reject) 
        
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    @override
    def accept(self):
        #... to save image scope checkboxes state, and save the True/False values to SCAN_EXTENSIONS_SCOPE section in config file 
        is_success = AppConfigs.save_scan_scope({
            "IMAGE": self.chk_image.isChecked(),
            "RAW": self.chk_raw.isChecked(),
            "VIDEO": self.chk_video.isChecked()
        })

        if not is_success:
            QMessageBox.warning(self, MsgBoxText.TITLE_INVALID_EXTENSIONS, MsgBoxText.MSG_INVALID_EXTENSIONS)
            return

        super().accept()

    @override
    def reject(self):
        #... to reject the dialog
        super().reject()

    def open_extension_settings(self):
        dialog = ExtensionSettingsDialog(self)
        if dialog.is_valid:
            if dialog.exec() == QDialog.DialogCode.Accepted:
                # Optional: print or log to verify
                logging.info(f"Updated scanning filter extensions: {dialog.get_filters()}")

class ExtensionSettingsDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle(AppText.EXTENSION_EDITOR_DIALOG_TITLE)
        self.resize(400, 200)

        self.is_valid = True

        # Validation before creation
        self.filters = AppConfigs.get_scan_extensions()
        if not self.filters:
             QMessageBox.critical(parent, MsgBoxText.TITLE_CRITICAL, ErrorText.CONFIG_ERROR_SCAN_EXTENSIONS)
             self.is_valid = False
             return

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        form_layout = QFormLayout()
        
        self.inputs = {}
        for category, ext in self.filters.items():
            line_edit = QLineEdit(ext)
            line_edit.setPlaceholderText(AppText.PLACEHOLDER_SCAN_FILE_EXTENSIONS)
            form_layout.addRow(f"{category} Extensions:", line_edit)
            self.inputs[category] = line_edit
            
        layout.addLayout(form_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.btn_ok = QPushButton(AppText.BUTTON_OK)
        self.btn_ok.clicked.connect(self.save_and_accept)
        
        self.btn_cancel = QPushButton(AppText.BUTTON_CANCEL)
        self.btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.btn_ok)
        btn_layout.addWidget(self.btn_cancel)
        
        layout.addLayout(btn_layout)

    def save_and_accept(self):
        temp_filters = {}
        for category, line_edit in self.inputs.items():
            temp_filters[category] = line_edit.text().strip()

        # Save to config
        if AppConfigs.save_scan_extensions(temp_filters) is False:
            QMessageBox.warning(self, MsgBoxText.TITLE_INVALID_EXTENSIONS, MsgBoxText.MSG_INVALID_EXTENSIONS)
            return
        
        self.filters = temp_filters # Update the filters to the new ones
        self.accept()

    def get_filters(self):
        return self.filters