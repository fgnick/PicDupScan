#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ===============================================================================================
import sys

from PyQt6.QtWidgets import QApplication

from src.qt_picdupscan_gui import PicDupScanGUI
from src.log_proc import Logger

# =========================================================
# Main function to run the application
# =========================================================
def main():
    app = QApplication(sys.argv)
    window = PicDupScanGUI()
    window.show()
    try:
        sys.exit(app.exec())
    finally:
        Logger.close()

if __name__ == '__main__':
    main()