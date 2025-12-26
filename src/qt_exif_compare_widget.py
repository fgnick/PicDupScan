#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ===============================================================================================
import exifread

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel, QPushButton, 
                             QFrame, QApplication, QSplitter)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPalette

class ExifCompareWidget(QWidget):
    close_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAutoFillBackground(True)
        # Remove hardcoded background/border that forces light mode
        # Use simple separator line if needed, but rely on Palette for background
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Header with Close Button
        self.header_frame = QFrame()
        self.header_frame.setFixedHeight(30)
        # Use window color for header background to differentiate slightly from base
        self.header_frame.setAutoFillBackground(True)
        
        # Add a subtle bottom border using frame shape or simple style that respects palette
        self.header_frame.setFrameShape(QFrame.Shape.HLine)
        self.header_frame.setFrameShadow(QFrame.Shadow.Sunken)
        
        # To ensure header stands out slightly, we can darken/lighten slightly based on theme
        # But safest is just a border.
        self.header_frame.setStyleSheet("border-bottom: 1px solid palette(mid);")

        header_layout = QHBoxLayout(self.header_frame)
        header_layout.setContentsMargins(10, 0, 5, 0)
        
        title_label = QLabel("EXIF Comparison")
        # Font weight is fine, but color should be default
        title_label.setStyleSheet("font-weight: bold; border: none;")
        
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(24, 24)
        self.close_btn.setFlat(True)
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        # Use palette colors for button
        self.close_btn.setStyleSheet("""
            QPushButton {
                border: none;
                font-weight: bold;
            }
            QPushButton:hover {
                color: red;
                background-color: palette(midlight);
                border-radius: 12px;
            }
        """)
        self.close_btn.clicked.connect(self.close_signal.emit)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.close_btn)
        
        self.main_layout.addWidget(self.header_frame)
        
        self.main_layout.addWidget(self.header_frame)
        
        # Split View for Content using QSplitter
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setHandleWidth(5) # Visible handle
        self.splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #ccc;
            }
        """)
        
        # Left: Target Image EXIF
        self.left_view = QTextEdit()
        self.left_view.setReadOnly(True)
        self.left_view.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap) # No word break
        self.left_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Right: Scan Image EXIF
        self.right_view = QTextEdit()
        self.right_view.setReadOnly(True)
        self.right_view.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap) # No word break
        self.right_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.splitter.addWidget(self.left_view)
        self.splitter.addWidget(self.right_view)
        
        # Set initial stretch factors (1:1)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 1)
        
        self.main_layout.addWidget(self.splitter)

    def _get_exif_data(self, path):
        """Extracts EXIF data using exifread (supports RAW + JPG)."""
        if not path:
            return {}
        
        try:
            with open(path, 'rb') as f:
                # details=False skips MakerNotes (huge binary blobs)
                tags = exifread.process_file(f, details=False)
            
            if not tags:
                return {}
            
            exif_data = {}
            
            # Tags to ignore
            IGNORE_PREFIXES = ('Thumbnail', 'Interoperability', 'MakerNote')
            
            for tag_key, value in tags.items():
                # tag_key looks like "EXIF DateTimeOriginal" or "Image Make"
                
                # 1. Filter Check
                if any(tag_key.startswith(prefix) for prefix in IGNORE_PREFIXES):
                    continue
                    
                # 2. Cleanup Key Name
                # Remove "EXIF ", "Image ", "GPS " prefixes for cleaner display
                display_key = tag_key
                for prefix in ["EXIF ", "Image ", "GPS "]:
                    if display_key.startswith(prefix):
                        display_key = display_key[len(prefix):]
                        break
                
                # Filter out unknown tags that couldn't be named (e.g. "Tag 0xC614")
                if display_key.startswith("Tag 0x"):
                    continue
                
                # 3. Value Cleaning
                val_str = str(value).strip()
                if not val_str:
                    continue
                    
                # Skip binary-looking garbage if it slipped through
                if len(val_str) > 100 and any(c not in '0123456789ABCDEFabcdef ' for c in val_str[:20]):
                     # Heuristic: long text that looks like hex dump or garbage
                     pass

                exif_data[display_key] = val_str
                
            return exif_data
        except Exception as e:
            return {"Error": str(e)}

    def load_exif(self, main_path, thumb_path):
        """Loads and compares EXIF data for two images."""
        main_exif = self._get_exif_data(main_path)
        thumb_exif = self._get_exif_data(thumb_path)
        
        # Sort keys to display in consistent order
        all_keys = sorted(set(list(main_exif.keys()) + list(thumb_exif.keys())))
        
        # Get current palette colors to use in HTML
        palette = QApplication.palette()
        text_color = palette.color(QPalette.ColorRole.Text).name()
        # Use a slightly dimmed color for labels
        label_color = palette.color(QPalette.ColorRole.WindowText).name() 
        # Or standard text but maybe with opacity, but simplest is just Text color or slightly different.
        # Let's use WindowText for labels (usually similar to Text)
        
        # Diff highlighting color
        # Red is usually fine in both dark/light
        
        # Photoshop style: Clean, tabular, no grid lines usually. 
        # Using a table with fixed widths for labels can emulate two columns well.
        
        common_style = f"""
            <style>
                table {{ margin: 0; padding: 0; width: 100%; border-collapse: collapse; }}
                td {{ padding: 4px; vertical-align: top; white-space: nowrap; font-family: 'Segoe UI', sans-serif; }}
                .label {{ color: {text_color}; opacity: 0.7; width: 150px; text-align: left; }}
                .val {{ color: {text_color}; }}
                h3 {{ margin: 5px 0 10px 0; font-size: 14px; font-weight: bold; color: {text_color}; }}
            </style>
        """
        
        left_html = common_style + f"<h3>Target Image</h3>"
        if not main_exif:
             left_html += "<div style='padding:10px; color:gray; font-style:italic;'>No EXIF data found or unable to interpret.</div>"
        else:
             left_html += "<table>"
             for key in all_keys:
                val = main_exif.get(key)
                if val:
                    # Compare with thumb
                    val_thumb = thumb_exif.get(key, "")
                    val_style = f"color: {text_color};"
                    if val != val_thumb:
                        val_style = "color: #ff4444; font-weight: bold;"
                    left_html += f"<tr><td class='label'>{key}</td><td class='val' style='{val_style}'>{val}</td></tr>"
             left_html += "</table>"

        right_html = common_style + f"<h3>Scan Image</h3>"
        if not thumb_exif:
             right_html += "<div style='padding:10px; color:gray; font-style:italic;'>No EXIF data found or unable to interpret.</div>"
        else:
             right_html += "<table>"
             for key in all_keys:
                val = thumb_exif.get(key)
                if val:
                    right_html += f"<tr><td class='label'>{key}</td><td class='val'>{val}</td></tr>"
             right_html += "</table>"
        
        self.left_view.setHtml(left_html)
        self.right_view.setHtml(right_html)
