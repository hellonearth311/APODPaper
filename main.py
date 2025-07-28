#!/usr/bin/env python3
"""
APODPaper - NASA Astronomy Picture of the Day Wallpaper Application

Automatically downloads and sets your desktop wallpaper to NASA's
daily Astronomy Picture of the Day (APOD).

Author: Swarit Narang
Version: 1.0.0
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import customtkinter as ctk
from src.app import main

if __name__ == "__main__":
    root = ctk.CTk()
    from src.gui import WindowUtils
    WindowUtils.set_window_icon(root)
    root.withdraw()
    main(root)
