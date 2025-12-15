# PicDupScan

PicDupScan was born out of a personal need.

As a photography enthusiast, I often found myself accumulating large numbers of
duplicate and near-duplicate photos. Many existing solutions are commercial
products with extensive feature sets, much of which I did not need for my
workflow. Rather than paying for a tool that felt overly complex, I built
PicDupScan to focus on the core problem in a more controlled and transparent way.

PicDupScan is a graphical user interface (GUI) tool developed with Python and PyQt6, designed to help users scan and find duplicate or highly similar images within specified folders. It supports common image formats as well as RAW files, and provides intuitive preview and management functions, making the process of cleaning up your image library much easier.

## ✨ Features

* **Similar Image Scanning**: Compares image similarity using the **Perceptual Hashing** algorithm, supporting comparison after rotation (90°, 180°, 270°). 
* **RAW File Support**: Reads RAW files directly via `rawpy`. Decoding and standardization are performed first before image-level similarity comparison.
* **Dual Folder Comparison**:
    * **Target Folder**: The primary folder to be scanned.
    * **Scan Folder**: The folder used as the comparison baseline.
* **Intuitive GUI Interface**:
    * **Tree View List**: Clearly lists the original image and its duplicates.
    * **Live Preview**: Click an item in the list to preview the image, supporting thumbnail display.
    * **Quick Actions**: Provides right-click menu functions such as "View," "Open in Folder," and "Delete."
* **Safe Deletion**: Uses `send2trash` to move files to the Recycle Bin/Trash, rather than permanent deletion, mitigating the risk of accidental deletion.
* **Batch Processing**: Supports select all, deselect all, and batch deletion of checked items.

## 🛠️ Requirements

This project was developed and tested in a **Windows** environment using **Python 3**.

### Core Language
* Python 3.8 or higher

### Dependencies
Please ensure the following Python packages are installed in your environment:

* **PyQt6**: Used for the Graphical User Interface (GUI).
* **Pillow**: Used for image reading and processing.
* **ImageHash**: Used for calculating the perceptual hash value of images.
* **rawpy**: Used for handling RAW image formats.
* **numpy**: The mathematical foundation for `rawpy` and image processing.
* **Send2Trash**: Used for safely deleting files to the Recycle Bin/Trash.

## 📦 Installation

1.  **Clone Repository**
    ```bash
    git clone [https://github.com/fgnick/PicDupScan.git](https://github.com/fgnick/PicDupScan.git)
    cd PicDupScan
    ```

2.  **Create a Virtual Environment (Recommended)**
    It is recommended to use a virtual environment to manage package dependencies:
    ```bash
    python -m venv venv
    # Activate virtual environment on Windows:
    .\venv\Scripts\activate
    # Activate virtual environment on macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    You can manually install the required packages:
    ```bash
    pip install PyQt6 Pillow ImageHash rawpy numpy send2trash
    ```
    *(If a `requirements.txt` is available, you can use `pip install -r requirements.txt`)*

## 🚀 Usage

1.  **Launch the Application**
    Run `main.py` from the project's root directory:
    ```bash
    python main.py
    ```

2.  **Operation Steps**
    * **Select Target Folder**: Click "Browse" to select the folder you want to clean up.
    * **Select Scan Folder**: Click "Browse" to select the reference folder (it can be the same one).
    * **Start Scan**: Click the "Start Scan" button to begin searching for duplicate images.
    * **View Results**: After the scan is complete, the duplicate images will be displayed in the tree view list below.
    * **Handle Files**:
        * Click an item in the list to preview the image on the right.
        * Check the duplicate items you wish to delete (Duplicate).
        * Click the trash can icon (Delete Checked) in the toolbar to perform batch deletion.
        * You can also click the "⋮" button in the preview window for individual file operations.

## 📝 Notes

* The delete operation moves files to the system Recycle Bin/Trash; if permanent deletion is needed, please empty the Recycle Bin/Trash.
* RAW file comparison can be time-consuming; please wait patiently for the scan to complete.

---
**License**: MIT