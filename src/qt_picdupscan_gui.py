#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ===============================================================================================

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QLineEdit, 
                             QPushButton, QTextEdit, QFileDialog, QMessageBox,
                             QTreeWidget, QTreeWidgetItem, QSplitter, QMenu, QStyleFactory,
                             QFrame, QToolButton, QSizePolicy, QStyle, QStyleOptionViewItem)
from PyQt6.QtCore import Qt, QUrl, QPoint, pyqtSignal, QEvent
from PyQt6.QtGui import QDesktopServices, QPainter, QColor, QImage, QPixmap, QCursor
import os
import subprocess
import rawpy
from typing import override
import send2trash

# custom modules -- constants
from .settings.env_constants import EnvConst
from .settings.gui_text import MenuText, MsgBoxText, ErrorText, AppText, LogText

# custom modules -- Qt GUI
from .qt_scanworker import QtScanWorker
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
                return QPixmap(path)
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

class PicDupScanGUI(QWidget):
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

        # Control Buttons
        btn_layout = QHBoxLayout()
        self.start_btn = QPushButton(AppText.BUTTON_START_SCAN)
        self.start_btn.clicked.connect(self.start_scan)
        self.stop_btn = QPushButton(AppText.BUTTON_STOP_SCAN)
        self.stop_btn.clicked.connect(self.stop_scan)
        self.stop_btn.setEnabled(False)
        
        # Set buttons to fit text only (Fixed policy)
        self.start_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.stop_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)
        btn_layout.addStretch() # Align to left
        layout.addLayout(btn_layout)

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
        
        layout.addWidget(splitter)

        self.setLayout(layout)

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
                # self.tree_widget.takeTopLevelItem(self.tree_widget.indexOfTopLevelItem(item))
                self.handle_preview_delete(file_path)
        else:
             # to let user know the file has been deleted or moved
            QMessageBox.warning(self, MsgBoxText.TITLE_ERROR, MsgBoxText.MSG_FILE_NOT_FOUND)

    def handle_preview_delete(self, path):
        # Iterate all top level items to find and remove the deleted item
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

        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.browse_target_btn.setEnabled(False)
        self.browse_scan_btn.setEnabled(False)
        self.log_display.clear()
        self.tree_widget.clear()
        self.preview_widget.load_images(None, None) # Clear preview
        
        self.worker = QtScanWorker(target_folder, scan_folder)
        # Connect log signal to append_log slot
        self.worker.log_signal.connect(self.append_log)
        # Connect duplicate found signal to add_duplicate_to_tree slot
        self.worker.duplicate_found_signal.connect(self.add_duplicate_to_tree)
        # Connect finished signal to scan_finished slot
        self.worker.finished_signal.connect(self.scan_finished)
        self.worker.start()

    def stop_scan(self):
        if self.worker:
            self.worker.stop()
            self.append_log(LogText.SCAN_STOPPING)

    def scan_finished(self):
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.browse_target_btn.setEnabled(True)
        self.browse_scan_btn.setEnabled(True)
        self.append_log(LogText.SCAN_FINISHED)