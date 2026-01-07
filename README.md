# PicDupScan (v2.0)

## About

PicDupScan was born out of a personal need.

As a photography enthusiast, I often found myself accumulating large numbers of duplicate and near-duplicate photos. Many existing solutions are commercial products with extensive feature sets, much of which I did not need for my workflow. Rather than paying for a tool that felt overly complex, I built PicDupScan to focus on the core problem in a more controlled and transparent way.

PicDupScan is a powerful graphical user interface (GUI) tool developed with Python and PyQt6, designed to help users scan and find duplicate or highly similar media files. It goes beyond simple image matching, offering deep support for professional RAW formats and video files.

## ✨ Key Features

### 🔍 Advanced Scanning & Performance
- **Two-Phase Hashing (High Performance)**: Implements a "Hashing Cache" mechanism. Features are pre-calculated once per file and compared in memory, drastically reducing I/O overhead and speeding up large scans.
- **Visual Similarity Search**: Uses perceptual hashing (pHash) to detect duplicate images even if they are resized, rotated, or minorly edited.
- **RAW File Support**: Native support for scanning camera RAW formats (DNG, CR2, ARW, NEF, etc.) by comparing direct sensor data for 100% accuracy.
- **Video Comparison**: Samples multiple frames from videos to compute perceptual signatures, allowing you to find duplicate video clips efficiently.
- **Configurable Scope**: Toggle scanning for specific categories (Images, RAWs, Videos) and customize file extension filters via a dedicated settings dialog.

### 🎥 Media Preview & Analytics
- **Animated Video Preview**: Automatically samples and animates keyframes from video files in the preview window, giving you a quick visual summary without opening an external player.
- **Side-by-Side Comparison**: Instantly compare a candidate duplicate against the original "Target" image with high-quality scaling.
- **EXIF Diffing Engine**: A specialized EXIF viewer that compares metadata between files and highlights differences (e.g., capture time, camera settings) in red.

### �️ Robust Architecture
- **Smart Logging System**: High-efficiency logger with daily file rotation, persistent file handles, and selective flushing to minimize performance impact.
- **Stable Memory Management**: Strict enforcement of the QObject lifecycle. Worker threads, dialogs, and menus are automatically deallocated using `deleteLater()` to ensure zero memory leaks during long sessions.
- **Theme-Aware UI**: Fully responsive PyQt6 interface that respects system light/dark mode and maintains responsiveness during bulk operations.

### 📂 File Management
- **Safe Deletion**: Integrated with `send2trash` to move duplicates to the Recycle Bin instead of permanent deletion.
- **Bulk Cleanup**: Tools for "Select All", "Deselect All", and "Progressive Bulk Deletion" with real-time UI feedback.
- **Explorer Integration**: Right-click context menus to "Open File" or "Show in Folder".

## 🛠️ Requirements & Installation

### Core Language
* Python 3.10 or higher (Tested with Python 3.13)

### Dependencies
Install the required packages via pip:

```bash
pip install PyQt6 rawpy imagehash imageio imageio-ffmpeg exifread send2trash
```

*Note: For video support, `imageio-ffmpeg` provides the necessary binaries. No manual FFmpeg installation is required in most environments.*

## 🚀 Getting Started
1. Clone the repository.
2. Install dependencies.
3. Run `python main.py` to launch the application.
4. Select your **Target folder** (the original source) and **Scan folder** (where to look for duplicates).
5. Let PicDupScan clean up your library!

---
**License**: MIT