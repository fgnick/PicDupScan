# PicDupScan (v2.0)

## About

PicDupScan was born out of a personal need.

As a photography enthusiast, I often found myself accumulating large numbers of
duplicate and near-duplicate photos. Many existing solutions are commercial
products with extensive feature sets, much of which I did not need for my
workflow. Rather than paying for a tool that felt overly complex, I built
PicDupScan to focus on the core problem in a more controlled and transparent way.

PicDupScan is a graphical user interface (GUI) tool developed with Python and PyQt6, designed to help users scan and find duplicate or highly similar images within specified folders. It supports common image formats as well as RAW files, and provides intuitive preview and management functions, making the process of cleaning up your image library much easier.

## Branch Strategy

- **main**: v2 (current development)
- **v1**: legacy v1 codebase (maintenance only)

## ✨ Features

### 🔍 Advanced Scanning
- **Visual Similarity Search**: Uses perceptual hashing (pHash) to detect duplicate images even if they are resized, rotated, or minorly edited.
- **RAW File Support**: Native support for scanning camera RAW formats (DNG, CR2, ARW, NEF, etc.) by comparing direct sensor data.
- **Configurable Scope**: Toggle scanning for specific file types (Images, RAWs, Videos) and customize file extension filters.

### 🖥️ Modern GUI (PyQt6)
- **Split-View Interface**: Real-time log, hierarchical results tree, and image preview all in one window.
- **Side-by-Side Comparison**: Instantly compare a candidate duplicate against the original "Target" image.
- **System Theme Integration**: The interface adapts to your OS light/dark mode preferences.

### 📸 Universal EXIF Viewer
- **Comprehensive Metadata**: Reads EXIF data from both standard images and RAW files.
- **Smart Diffing**: Automatically highlights differences between the two compared images in red.
- **Clean UI**: "Photoshop-like" tabular display with smart filtering of noise/unknown tags.
- **Auto-Fallbacks**: Handles missing or unreadable metadata gracefully.

### 📂 File Management
- **Safe Deletion**: Deletes files to the Recycle Bin (`send2trash`) rather than permanent removal, preventing accidental data loss.
- **Batch Operations**: "Select All", "Deselect All", and "Delete Checked" for efficient cleanup.
- **Context Actions**: Right-click to open files directly or view them in their explorer folder.

(I am working on it... = = b, and I will update the README.md file as soon as I have something to show or a new function to add.)

## 🛠️ Requirements

This project was developed and tested in a **Windows** environment using **Python 3**.
You can use pyinstaller to package the application into an executable file on you OS.

### Core Language
* Python 3.8 or higher

### Dependencies

So far is similar to v1, but I will add more features in the future.

---
**License**: MIT