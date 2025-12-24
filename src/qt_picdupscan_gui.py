#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ===============================================================================================

import os
import subprocess
from typing import override
import send2trash

# PyQt6 modules
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QLineEdit, 
                             QPushButton, QTextEdit, QFileDialog, QMessageBox, QMainWindow,
                             QTreeWidget, QTreeWidgetItem, QSplitter, QMenu, QStyleFactory,
                             QStyle, QStyleOptionViewItem, QStatusBar)
from PyQt6.QtCore import Qt, QUrl, QPoint, QEvent
from PyQt6.QtGui import QDesktopServices, QCursor

# custom modules -- constants
from .settings.env_constants import EnvConst
from .settings.gui_text import MenuText, MsgBoxText, AppText, LogText

# custom modules -- Qt GUI
from .qt_scanworker import QtScanWorker
from .qt_app_menu_bar import PicDupMenu
from .qt_app_toolbar import PicDupToolbar
from .qt_image_preview_widget import ImagePreviewWidget

class PicDupScanGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.worker = None

    def __del__(self):
        print("PicDupScanGUI is deleted and memory is released.")

    @override
    def closeEvent(self, event):
        # Stop the worker thread if it's running
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()
        event.accept()

    def init_ui(self):
        self.setWindowTitle(AppText.WINDOW_TITLE)
        self.setGeometry(100, 100, 1200, 700)
        
        # Release memory when closed
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout()
        
        # Folder Selection (Grid Layout for alignment)
        folder_grid = QGridLayout()
        
        self.target_folder_label = QLabel(AppText.LABEL_TARGET_FOLDER)
        self.target_folder_input = QLineEdit()
        self.browse_target_btn = QPushButton(AppText.BUTTON_BROWSE)
        self.browse_target_btn.clicked.connect(self.browse_target_folder)
        
        self.scan_folder_label = QLabel(AppText.LABEL_SCAN_FOLDER)
        self.scan_folder_input = QLineEdit()
        self.browse_scan_btn = QPushButton(AppText.BUTTON_BROWSE)
        self.browse_scan_btn.clicked.connect(self.browse_scan_folder)

        # Add to Grid: Label=Col0, Input=Col1, Btn=Col2
        folder_grid.addWidget(self.target_folder_label, 0, 0)
        folder_grid.addWidget(self.target_folder_input, 0, 1)
        folder_grid.addWidget(self.browse_target_btn, 0, 2)
        
        folder_grid.addWidget(self.scan_folder_label, 1, 0)
        folder_grid.addWidget(self.scan_folder_input, 1, 1)
        folder_grid.addWidget(self.browse_scan_btn, 1, 2)
        
        layout.addLayout(folder_grid)

        # Splitter for Log, Tree View, and Preview
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Log Display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        splitter.addWidget(self.log_display)
        
        # Tree View for Duplicates container
        tree_container = QWidget()
        tree_layout = QVBoxLayout(tree_container)
        tree_layout.setContentsMargins(0, 0, 0, 0)
        
        # Toolbar for Tree View
        tree_toolbar = QHBoxLayout()
        self.btn_select_all = QPushButton(AppText.BUTTON_SELECT_ALL)
        self.btn_select_all.clicked.connect(self.select_all_duplicates)
        
        self.btn_deselect_all = QPushButton(AppText.BUTTON_DESELECT_ALL)
        self.btn_deselect_all.clicked.connect(self.deselect_all_duplicates)
        
        self.btn_delete_checked = QPushButton()
        self.btn_delete_checked.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_TrashIcon))
        self.btn_delete_checked.setToolTip(AppText.BUTTON_DELETE_CHECKED)
        self.btn_delete_checked.clicked.connect(self.delete_checked_items)
        
        tree_toolbar.addWidget(self.btn_select_all)
        tree_toolbar.addWidget(self.btn_deselect_all)
        tree_toolbar.addStretch()
        tree_toolbar.addWidget(self.btn_delete_checked)
        
        tree_layout.addLayout(tree_toolbar)

        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels([AppText.TREE_VIEW_TITLE])
        self.tree_widget.setStyle(QStyleFactory.create("windows"))
        self.tree_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree_widget.customContextMenuRequested.connect(self.open_menu)
        self.tree_widget.itemClicked.connect(self.on_tree_item_clicked)
        self.tree_widget.viewport().installEventFilter(self)
        
        tree_layout.addWidget(self.tree_widget)
        
        splitter.addWidget(tree_container)
        
        # Preview Area
        self.preview_widget = ImagePreviewWidget()
        self.preview_widget.file_deleted_signal.connect(self.handle_preview_delete)
        splitter.addWidget(self.preview_widget)
        
        # Set initial sizes (Log: 25%, Tree: 35%, Preview: 40%)
        splitter.setSizes([300, 400, 500])
        
        layout.addWidget(splitter, 1)

        self.central_widget.setLayout(layout)

        # Menu Bar
        self.menu_bar = PicDupMenu(self)
        self.setMenuBar(self.menu_bar)

        # Tool Bar
        self.toolbar = PicDupToolbar(self)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)
        self.toolbar.start_action.triggered.connect(self.start_scan)
        self.toolbar.stop_action.triggered.connect(self.stop_scan)

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(LogText.SCAN_READY)

        # Set default folder if exists
        if os.path.exists(EnvConst.TARGET_PATH):
            self.target_folder_input.setText(os.path.abspath(EnvConst.TARGET_PATH))
        if os.path.exists(EnvConst.SCAN_PATH):
            self.scan_folder_input.setText(os.path.abspath(EnvConst.SCAN_PATH))
        
    def browse_target_folder(self):
        folder = QFileDialog.getExistingDirectory(self, AppText.BROWSE_DIALOG_TITLE)
        if folder:
            self.target_folder_input.setText(folder)

    def browse_scan_folder(self):
        folder = QFileDialog.getExistingDirectory(self, AppText.BROWSE_DIALOG_TITLE)
        if folder:
            self.scan_folder_input.setText(folder)

    def append_log(self, message):
        self.log_display.append(message)
        # Scroll to bottom
        sb = self.log_display.verticalScrollBar()
        sb.setValue(sb.maximum())

    def elide_path(self, path, max_len=60):
        if len(path) <= max_len:
            return path
        n = (max_len - 3) // 2
        return path[:n] + "..." + path[-n:]

    def add_duplicate_to_tree(self, file1, file2):
        # file1 is the "Source" (Parent), file2 is the "Duplicate" (Child)
        abs_file1 = os.path.abspath(file1)
        abs_file2 = os.path.abspath(file2)
        
        display_file1 = self.elide_path(abs_file1)
        display_file2 = self.elide_path(abs_file2)

        # ---- 1. Check if file1 already exists as a parent item ----
        parent_item = self.find_treeitem_parent(abs_file1)

        if parent_item is None:
            # ---- 2. file1 does not exist → Create new parent item ----
            parent_item = QTreeWidgetItem(self.tree_widget)
            parent_item.setText(0, display_file1)
            parent_item.setToolTip(0, abs_file1)
            parent_item.setData(0, Qt.ItemDataRole.UserRole, abs_file1)
            parent_item.setData(0, Qt.ItemDataRole.UserRole + 1, abs_file1)
        
        # ---- 3. Add child (file2) ----
        if not self.treeview_child_exists(parent_item, abs_file2):
            child = QTreeWidgetItem(parent_item)
            child.setText(0, display_file2)
            child.setToolTip(0, abs_file2)
            child.setData(0, Qt.ItemDataRole.UserRole, abs_file2)
            child.setData(0, Qt.ItemDataRole.UserRole + 1, abs_file1)
            child.setCheckState(0, Qt.CheckState.Unchecked) # Add checkbox

        parent_item.setExpanded(True)

    def select_all_duplicates(self):
        root = self.tree_widget
        for i in range(root.topLevelItemCount()):
            parent = root.topLevelItem(i)
            for j in range(parent.childCount()):
                child = parent.child(j)
                child.setCheckState(0, Qt.CheckState.Checked)

    def deselect_all_duplicates(self):
        root = self.tree_widget
        for i in range(root.topLevelItemCount()):
            parent = root.topLevelItem(i)
            for j in range(parent.childCount()):
                child = parent.child(j)
                child.setCheckState(0, Qt.CheckState.Unchecked)

    def delete_checked_items(self):
        # Collect all checked items
        items_to_delete = []
        root = self.tree_widget
        for i in range(root.topLevelItemCount()):
            parent = root.topLevelItem(i)
            for j in range(parent.childCount()):
                child = parent.child(j)
                if child.checkState(0) == Qt.CheckState.Checked:
                    file_path = child.data(0, Qt.ItemDataRole.UserRole)
                    if file_path and os.path.exists(file_path): # to prevent user has changed the file path or deleted the file
                        items_to_delete.append((child, file_path))
        
        if not items_to_delete:
            QMessageBox.information(self, MsgBoxText.TITLE_INFO, MsgBoxText.MSG_NO_ITEMS_SELECTED)
            return

        # Confirm delete
        itemNum = len(items_to_delete)
        reply = QMessageBox.question(
            self,
            MsgBoxText.TITLE_CONFIRM,
            MsgBoxText.MSG_CONFIRM_DELETE_MULTI.format(count=itemNum),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Process deletion
            # We iterate and delete. 
            # IMPORTANT: Deleting files and updating tree could be tricky if we modify tree while iterating.
            # But handle_preview_delete finds item by path, so we can just extract paths first.
            
            paths = [path for _, path in items_to_delete]
            
            success_count = 0
            fail_count = 0
            
            for path in paths:
                if path and os.path.exists(path):
                    try:
                        send2trash.send2trash(path)
                        self.handle_preview_delete(path)
                        success_count += 1
                    except Exception as e:
                        print(f"Failed to delete {path}: {e}")
                        fail_count += 1
                else:
                    # Maybe already deleted or invalid? still try to remove from tree
                    self.handle_preview_delete(path)
            
            self.append_log(f"\n[Bulk Delete] Deleted: {success_count}, Failed: {fail_count}")

    def find_treeitem_parent(self, path: str):
        root = self.tree_widget
        for i in range(root.topLevelItemCount()):
            item = root.topLevelItem(i)
            stored_path = item.data(0, Qt.ItemDataRole.UserRole)
            if stored_path == path:
                return item
        return None

    def treeview_child_exists(self, parent_item, path):
        for i in range(parent_item.childCount()):
            child = parent_item.child(i)
            if child.data(0, Qt.ItemDataRole.UserRole) == path:
                return True
        return False

    def on_tree_item_clicked(self, item, column):
        # Check if click was on checkbox
        if column == 0:
            index = self.tree_widget.indexFromItem(item, column)
            rect = self.tree_widget.visualRect(index)
            pos = self.tree_widget.viewport().mapFromGlobal(QCursor.pos())
            
            option = QStyleOptionViewItem()
            option.initFrom(self.tree_widget)
            option.rect = rect
            option.features |= QStyleOptionViewItem.ViewItemFeature.HasCheckIndicator
            
            check_rect = self.tree_widget.style().subElementRect(QStyle.SubElement.SE_ItemViewItemCheckIndicator, option, self.tree_widget)
            
            if check_rect.contains(pos):
                return

        file_path = item.data(0, Qt.ItemDataRole.UserRole) # The file path of the clicked item
        source_path = item.data(0, Qt.ItemDataRole.UserRole + 1) # The source file path (parent of the duplicate group)
        
        if file_path and os.path.exists(file_path):
            # Mother picture is the clicked file, Son picture is the source (parent)
            self.preview_widget.load_images(file_path, source_path)

    def open_menu(self, position: QPoint):
        item = self.tree_widget.itemAt(position)
        if not item:
            return

        menu = QMenu()
        
        # Action: View File
        view_action = menu.addAction(MenuText.VIEW)
        view_action.triggered.connect(lambda: self.view_file(item))
        
        # Action: Open in Folder
        open_folder_action = menu.addAction(MenuText.OPEN_IN_FOLDER)
        open_folder_action.triggered.connect(lambda: self.open_in_folder(item))

        # Action: Delete File
        if item.parent(): # Only allow delete for children (duplicates)
            delete_action = menu.addAction(MenuText.DELETE)
            delete_action.triggered.connect(lambda: self.delete_file(item))
        
        menu.exec(self.tree_widget.viewport().mapToGlobal(position))

    def view_file(self, item):
        file_path = item.data(0, Qt.ItemDataRole.UserRole)
        if file_path and os.path.exists(file_path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))

    def open_in_folder(self, item):
        file_path = item.data(0, Qt.ItemDataRole.UserRole)
        if file_path and os.path.exists(file_path):
            # Windows specific command to select file in explorer
            subprocess.Popen(f'explorer /select,"{file_path}"')

    def delete_file(self, item):
        file_path = item.data(0, Qt.ItemDataRole.UserRole)
        if file_path and os.path.exists(file_path):
            # show confirm dialog
            reply = QMessageBox.question(
                self,
                MsgBoxText.TITLE_CONFIRM,
                MsgBoxText.MSG_CONFIRM_DELETE.format(filename=file_path),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            # delete file if user confirm
            if reply == QMessageBox.StandardButton.Yes:
                send2trash.send2trash(file_path)
                self.handle_preview_delete(file_path)
        else:
             # to let user know the file has been deleted or moved
            QMessageBox.warning(self, MsgBoxText.TITLE_ERROR, MsgBoxText.MSG_FILE_NOT_FOUND)

    def handle_preview_delete(self, path):
        # 1. Clear preview if it's showing the deleted file
        # We check path match to avoid clearing if user deletes a background file (not the one they are looking at)
        if self.preview_widget.current_file_path and os.path.normpath(self.preview_widget.current_file_path) == os.path.normpath(path):
            self.preview_widget.load_images(None, None)

        # 2. Iterate all top level items to find and remove the deleted item from Tree
        root = self.tree_widget
        for i in reversed(range(root.topLevelItemCount())): # Reverse to safely remove
            item = root.topLevelItem(i)
            # Check if this top-level item is the deleted file
            if item.data(0, Qt.ItemDataRole.UserRole) == path:
                 root.takeTopLevelItem(i)
                 continue # Item found and removed, continue to next
            
            # Check its children
            for j in reversed(range(item.childCount())):
                child = item.child(j)
                if child.data(0, Qt.ItemDataRole.UserRole) == path:
                    item.removeChild(child)
            
            if item.childCount() == 0:
                root.takeTopLevelItem(i)

    @override
    def eventFilter(self, source, event):
        if source == self.tree_widget.viewport() and event.type() == QEvent.Type.MouseButtonPress:
            # Check if click is on an item
            if self.tree_widget.itemAt(event.position().toPoint()) is None:
                self.tree_widget.clearSelection()
                self.preview_widget.load_images(None, None)
        return super().eventFilter(source, event)

    def start_scan(self):
        target_folder = self.target_folder_input.text()
        scan_folder = self.scan_folder_input.text()
        if not scan_folder or not os.path.exists(scan_folder):
            QMessageBox.warning(self, MsgBoxText.TITLE_ERROR, MsgBoxText.MSG_FOLDER_NOT_FOUND)
            return
        if not target_folder or not os.path.exists(target_folder):
            QMessageBox.warning(self, MsgBoxText.TITLE_ERROR, MsgBoxText.MSG_FOLDER_NOT_FOUND)
            return

        self.toolbar.start_action.setEnabled(False)
        self.toolbar.stop_action.setEnabled(True)
        self.browse_target_btn.setEnabled(False)
        self.browse_scan_btn.setEnabled(False)
        self.log_display.clear()
        self.tree_widget.clear()
        self.preview_widget.load_images(None, None) # Clear preview

        self.worker = QtScanWorker(self, target_folder, scan_folder)
        # Connect log signal to append_log slot
        self.worker.log_signal.connect(self.append_log)
        # Connect duplicate found signal to add_duplicate_to_tree slot
        self.worker.duplicate_found_signal.connect(self.add_duplicate_to_tree)
        # Connect finished signal to scan_finished slot
        self.worker.finished_signal.connect(self.scan_finished)
        self.worker.start()
        self.status_bar.showMessage(LogText.SCAN_STARTING)

    def stop_scan(self):
        if self.worker:
            self.worker.stop()
            self.append_log(LogText.SCAN_STOPPING)
            self.status_bar.showMessage(LogText.SCAN_STOPPING)

    def scan_finished(self):
        self.toolbar.start_action.setEnabled(True)
        self.toolbar.stop_action.setEnabled(False)
        self.browse_target_btn.setEnabled(True)
        self.browse_scan_btn.setEnabled(True)
        self.append_log(LogText.SCAN_FINISHED)
        self.status_bar.showMessage(LogText.SCAN_FINISHED)