#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ===============================================================================================
import os
import re
import subprocess
import exifread
from typing import override

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel, QPushButton, 
                             QFrame, QApplication, QSplitter)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPalette

from .settings.pic_constants import PicConst
from .settings.gui_text import AppText, ErrorText, MsgBoxText
from .app_configs import AppConfigs

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
        
        title_label = QLabel(AppText.EXIF_COMPARE_WIDGET_TITLE)
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
        
        # Split View for Content using QSplitter
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setHandleWidth(5) # Visible handle
        self.splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #ccc;
            }
        """)
        
        # Left Container (Header + Scrollable Content)
        self.main_exif_widget = QWidget()
        main_exif_layout = QVBoxLayout(self.main_exif_widget)
        main_exif_layout.setContentsMargins(0, 0, 0, 0)
        main_exif_layout.setSpacing(0)
        
        # Sticky Header for image main preview
        self.left_header_label = QLabel(AppText.EXIF_COMPARE_WIDGET_MAIN_EXIF)
        self.left_header_label.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px; background-color: palette(midlight);")
        # Ensure header text uses window text color (implied by label, but background helps separation)
        
        self.main_exif_view = QTextEdit()
        self.main_exif_view.setReadOnly(True)
        self.main_exif_view.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.main_exif_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        # Remove border to blend with container
        self.main_exif_view.setStyleSheet("border: none;")

        main_exif_layout.addWidget(self.left_header_label)
        main_exif_layout.addWidget(self.main_exif_view)

        # Right Container (Header + Scrollable Content)
        self.thumb_exif_widget = QWidget()
        thumb_exif_layout = QVBoxLayout(self.thumb_exif_widget)
        thumb_exif_layout.setContentsMargins(0, 0, 0, 0)
        thumb_exif_layout.setSpacing(0)

        # Sticky Header for image target preview (thumbnail)
        self.right_header_label = QLabel(AppText.EXIF_COMPARE_WIDGET_THUMBNAIL_EXIF)
        self.right_header_label.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px; background-color: palette(midlight);")

        self.thumb_exif_view = QTextEdit()
        self.thumb_exif_view.setReadOnly(True)
        self.thumb_exif_view.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.thumb_exif_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.thumb_exif_view.setStyleSheet("border: none;")
        
        thumb_exif_layout.addWidget(self.right_header_label)
        thumb_exif_layout.addWidget(self.thumb_exif_view)
        
        self.splitter.addWidget(self.main_exif_widget)
        self.splitter.addWidget(self.thumb_exif_widget)
        
        # Set initial stretch factors (1:1)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 1)
        
        self.main_layout.addWidget(self.splitter)

        # Initialize extensions from config for performance
        self._img_exts = tuple(PicConst.IMG_EXTENSIONS)
        self._raw_exts = tuple(PicConst.RAW_EXTENSIONS)
        self._video_exts = tuple(PicConst.VIDEO_EXTENSIONS)
        self._load_extensions_from_config()

    # Load extensions from config
    def _load_extensions_from_config(self):
        # properly load as tuple from AppConfigs
        ext_map = AppConfigs.get_scan_extensions(return_type="tuple")
        if ext_map:
            if "Image" in ext_map:
                self._img_exts = ext_map["Image"]
            if "Raw" in ext_map:
                self._raw_exts = ext_map["Raw"]
            if "Video" in ext_map:
                self._video_exts = ext_map["Video"]
        else:
            QMessageBox.critical(self, MsgBoxText.TITLE_CRITICAL, ErrorText.CONFIG_ERROR_SCAN_EXTENSIONS)

    @override
    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Initialize splitter sizes to 1:1 if they are not yet set and we have width
        if sum(self.splitter.sizes()) == 0 and self.width() > 10:
            w = self.width()
            self.splitter.setSizes([w // 2, w // 2])

    # Extracts EXIF data using exifread (supports RAW + JPG).
    def _get_exif_data(self, path):
        if not path:
            return {}
        
        try:
            with open(path, 'rb') as f:
                # details=False skips MakerNotes (huge binary blobs)
                tags = exifread.process_file(f, details=False)
            
            if not tags:
                return {}
            
            exif_data = {}
            
            # Tags to ignore (containment check)
            # Filter out technical data, offsets, binary blobs, and color math that isn't human-readable
            IGNORE_KEYWORDS = (
                'Thumbnail', 'Interoperability', 'MakerNote', 
                'PrintIM', 'Padding', 'Offset',
                'PrimaryChromaticities', 'WhitePoint', 'YCbCr', 'ReferenceBlackWhite',
                'ComponentsConfiguration', 'CompressedBitsPerPixel'
            )
            
            for tag_key, value in tags.items():
                # tag_key looks like "EXIF DateTimeOriginal" or "Image Make"
                
                # 1. Filter Check: Check if any keyword is IN the tag_key (not just startswith)
                if any(keyword in tag_key for keyword in IGNORE_KEYWORDS):
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

    # Combined loader that auto-detects type
    def load_metadata(self, main_path, thumb_path):
        main_data = {}
        if main_path:
            lower = main_path.lower()
            if lower.endswith(self._video_exts):
                main_data = self._get_video_data(main_path)
            elif lower.endswith(self._img_exts) or lower.endswith(self._raw_exts):
                main_data = self._get_exif_data(main_path)
        else:
            self.main_exif_view.clear()
        
        thumb_data = {}
        if thumb_path:
            lower = thumb_path.lower()
            if lower.endswith(self._video_exts):
                thumb_data = self._get_video_data(thumb_path)
            elif lower.endswith(self._img_exts) or lower.endswith(self._raw_exts):
                thumb_data = self._get_exif_data(thumb_path)
        else:
            self.thumb_exif_view.clear()

        self._render_comparison(main_data, thumb_data)

    def _render_comparison(self, main_data, thumb_data):
        # Sort keys to display in consistent order
        all_keys = sorted(set(list(main_data.keys()) + list(thumb_data.keys())))

        # Get current palette colors to use in HTML
        palette = QApplication.palette()
        text_color = palette.color(QPalette.ColorRole.Text).name()
        
        common_style = f"""
            <style>
                table {{ margin: 0; padding: 0; width: 100%; border-collapse: collapse; }}
                td {{ padding: 4px; vertical-align: top; white-space: nowrap; font-family: 'Segoe UI', sans-serif; }}
                .label {{ color: {text_color}; opacity: 0.7; width: 150px; text-align: left; }}
                .val {{ color: {text_color}; }}
            </style>
        """
        
        # main exif PANE
        main_exif_html = common_style
        if not main_data:
             main_exif_html += "<div style='padding:10px; color:gray; font-style:italic;'>No data found.</div>"
        else:
             main_exif_html += "<table>"
             for key in all_keys:
                val = main_data.get(key)
                if val:
                    # Compare
                    val_thumb = thumb_data.get(key, "")
                    val_style = f"color: {text_color};"
                    if val != val_thumb:
                         val_style = "color: #ff4444; font-weight: bold;"
                    
                    main_exif_html += f"<tr><td class='label'>{key}</td><td class='val' style='{val_style}'>{val}</td></tr>"
             main_exif_html += "</table>"
        
        # thumb exif PANE
        thumb_exif_html = common_style
        if not thumb_data:
             thumb_exif_html += "<div style='padding:10px; color:gray; font-style:italic;'>No data found.</div>"
        else:
             thumb_exif_html += "<table>"
             for key in all_keys:
                val = thumb_data.get(key)
                if val:
                    thumb_exif_html += f"<tr><td class='label'>{key}</td><td class='val'>{val}</td></tr>"
             thumb_exif_html += "</table>"
             
        self.main_exif_view.setHtml(main_exif_html)
        self.thumb_exif_view.setHtml(thumb_exif_html)

    # Combined loader that auto-detects type
    def _get_video_data(self, path):
        parsed_data = {}
        if not path or not os.path.exists(path):
            return parsed_data

        try:
            import imageio_ffmpeg   # lazy import
            ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
            
            # Run ffmpeg -i to get info (to stderr)
            cmd = [ffmpeg_exe, '-i', path]
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo)
            output = res.stderr.decode('utf-8', errors='ignore')
            
            # 1. Duration & Bitrate
            m_dur = re.search(r"Duration:\s*(\d{2}:\d{2}:\d{2}\.\d+).*?bitrate:\s*(\d+\s*kb/s)", output)
            if m_dur:
                parsed_data['Duration'] = m_dur.group(1)
                parsed_data['Bitrate'] = m_dur.group(2)
            else:
                m_dur_only = re.search(r"Duration:\s*(\d{2}:\d{2}:\d{2}\.\d+)", output)
                if m_dur_only:
                    parsed_data['Duration'] = m_dur_only.group(1)

            # 2. Video Stream
            m_video = re.search(r"Stream #\d+:\d+.*?: Video: (.*)", output)
            if m_video:
                raw_video = m_video.group(1)
                parts = [p.strip() for p in raw_video.split(',')]
                parsed_data['Video Codec'] = parts[0]
                for p in parts:
                    if re.match(r"\d{3,4}x\d{3,4}", p):
                        parsed_data['Resolution'] = p
                        break
                for p in parts:
                    if 'fps' in p:
                        parsed_data['FPS'] = p
                        break

            # 3. Audio Stream
            m_audio = re.search(r"Stream #\d+:\d+.*?: Audio: (.*)", output)
            if m_audio:
                raw_audio = m_audio.group(1)
                parts = [p.strip() for p in raw_audio.split(',')]
                parsed_data['Audio Codec'] = parts[0]
                for p in parts:
                    if 'Hz' in p:
                        parsed_data['Audio Sample Rate'] = p
                        break

            # 4. Container Metadata
            m_create = re.search(r"creation_time\s*:\s*(.*)", output)
            if m_create:
                parsed_data['Creation Time'] = m_create.group(1).strip()
            
            m_encoder = re.search(r"encoder\s*:\s*(.*)", output)
            if m_encoder:
                parsed_data['Encoder'] = m_encoder.group(1).strip()
                
        except Exception as e:
            parsed_data['Error'] = str(e)
            
        # Whitelist (Positive Selection) - Similar to IGNORE_KEYWORDS but opposite
        # Also defines the order of display
        VIDEO_TAGS = (
            'Duration', 'Resolution', 'FPS', 'Video Codec', 'Bitrate', 
            'Audio Codec', 'Audio Sample Rate', 'Creation Time', 'Encoder'
        )
        
        # Select and Order based on VIDEO_TAGS (Whitelist)
        final_data = {}

        # We initialize keys in order so they appear even if missing (as None)
        # This ensures the UI renders them in correct order when we use list(keys())
        for tag in VIDEO_TAGS:
            if tag in parsed_data:
                final_data[tag] = parsed_data[tag]
            else:
                final_data[tag] = None
                
        # Include error if present
        if 'Error' in parsed_data:
            final_data['Error'] = parsed_data['Error']
            
        return final_data

