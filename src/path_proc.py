#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ========================================================================================================

from pathlib import Path
import os
import sys

class PathProc:

    def __init__(self):
        raise Exception( "You cannot construct PathProc class! This is a static class." )

    # Let PyInstaller find the resource path correctly
    @staticmethod
    def get_real_base_path():
        if getattr(sys, 'frozen', False):  # EXE execution
            return os.path.dirname(sys.executable)
        return os.path.abspath(".")        # Development stage

    # Search from the current script position to find the project root directory (through marker file).
    @staticmethod
    def get_project_root(root_main_py_str="main.py"):
        if root_main_py_str == "" or root_main_py_str is None:
            return None
            
        current_file_path = Path(__file__).resolve()
        
        for parent in current_file_path.parents:
            mark_path = parent / root_main_py_str
            if mark_path.exists():
                return str(parent)
        return None
        
