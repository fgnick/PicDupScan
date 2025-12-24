#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ===============================================================================================

import sys
from PyQt6.QtWidgets import QApplication
from src.qt_picdupscan_gui import PicDupScanGUI


# =========================================================
# Main function to run the application
# =========================================================
def main():
    app = QApplication(sys.argv)
    window = PicDupScanGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()