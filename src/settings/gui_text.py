#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ===============================================================================================

from dataclasses import dataclass

@dataclass(frozen=True)
class AppText:
    # Window Title
    WINDOW_TITLE: str = "PicDupScan"

    # Dialog Title
    BROWSE_DIALOG_TITLE: str = "Select Directory"
    SCAN_SCOPE_DIALOG_TITLE: str = "Scan Scope"
    EXTENSION_EDITOR_DIALOG_TITLE: str = "Extension Editor"

    # Panel Title
    PANEL_TITLE: str = "Duplicate Files"

    # Label Text
    LABEL_TARGET_FOLDER: str = "Target Folder:"
    LABEL_SCAN_FOLDER: str = "Scan Folder:"
    LABEL_SCAN_SCOPE: str = "Select file types to scan:"
    LABEL_IMAGE: str = "Image"
    LABEL_RAW: str = "Raw"
    LABEL_VIDEO: str = "Video"

    # Placeholder Text
    PLACEHOLDER_SCAN_FILE_EXTENSIONS: str = "e.g.: .jpg, .png"

    # Button Text
    BUTTON_CONFIRM: str = "Confirm"
    BUTTON_DELETE: str = "Delete"
    BUTTON_CANCEL: str = "Cancel"
    BUTTON_OK: str = "OK"
    BUTTON_SELECT_ALL: str = "Select All"
    BUTTON_DESELECT_ALL: str = "Deselect All"
    BUTTON_DELETE_CHECKED: str = "Delete Checked"
    BUTTON_BROWSE: str = "Browse"
    BUTTON_START_SCAN: str = "Start Scan"
    BUTTON_STOP_SCAN: str = "Stop Scan"
    BUTTON_SWITCH_SCAN: str = "Scanning Scope"
    BUTTON_EDIT: str = "Edit"

    # Tree View Text
    TREE_VIEW_TITLE: str = "Duplicate Files"

@dataclass(frozen=True)
class AppMenuBarText:
    FILE: str = "File"
    FILE_ABOUT: str = "About"
    FILE_CLOSE: str = "Close"
    SETTINGS: str = "Settings"
    SETTINGS_SCAN_FILE_EXTENSIONS: str = "Scan File Extensions"
    

@dataclass(frozen=True)
class LogText:
    TARGET_IMAGE: str = "Target Image: {path}"
    SCAN_IMAGE: str = "Scan Image: {path}"
    TARGET_RAW: str = "Target Raw: {path}"
    SCAN_RAW: str = "Scan Raw: {path}"
    SCAN_MATCH: str = "✅ MATCH: {file1} == {file2}"
    NO_TARGET_FILES: str = "No target image/raw files found in {path}"
    NO_SCAN_FILES: str = "No scan image/raw files found in {path}"
    FOUND_TARGET_IMAGES: str = "Found {count} target images. Starting comparison..."
    FOUND_TARGET_RAWS: str = "Found {count} target raws. Starting comparison..."

    SCAN_READY: str = "Ready"
    SCAN_SCOPE: str = "Scan Scope: {scope}"
    SCAN_STARTING: str = "[Scan Starting...]"
    SCAN_STOPPING: str = "[Scan Stopping...]"
    SCAN_FINISHED: str = "[Scan Finished]"

    SCAN_ERROR: str = "Scan error: {error}"

@dataclass(frozen=True)
class MenuText:
    VIEW: str = "View"
    OPEN_IN_FOLDER: str = "Open in Folder"
    DELETE: str = "Delete File"

@dataclass(frozen=True)
class MsgBoxText:
    TITLE_INFO: str = "Info"
    TITLE_CONFIRM: str = "Confirm"
    TITLE_ERROR: str = "Error"
    TITLE_WARNING: str = "Warning"
    TITLE_INVALID_EXTENSIONS: str = "Invalid Extensions"
    TITLE_CRITICAL: str = "Critical Error"

    # MsgBox Text
    MSG_FOLDER_NOT_FOUND: str = "Folder does not exist."
    MSG_FILE_NOT_FOUND: str = "File does not exist."
    MSG_NO_ITEMS_SELECTED: str = "No items selected."
    MSG_CONFIRM_DELETE: str = "Are you sure you want to delete \"{filename}\"?"
    MSG_CONFIRM_DELETE_MULTI: str = "Are you sure you want to delete {count} selected items?"

    MSG_INVALID_EXTENSIONS: str = "Invalid Extension input format!"
    
@dataclass(frozen=True)
class ErrorText:
    FILE_NOT_FOUND: str = "File does not exist."
    FILE_DELETE_FAILED: str = "Failed to delete file:\n{error}"
    
    CONFIG_ERROR_SCAN_SCOPE: str = "Failed to read scan scope from config!"
    CONFIG_ERROR_SCAN_EXTENSIONS: str = "Failed to read scan extensions from config!"