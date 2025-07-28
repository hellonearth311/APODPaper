# -*- mode: python ; coding: utf-8 -*-

import os

# Get the directory where the spec file is located
# Use multiple methods to ensure we get the right path
try:
    # Try using SPECPATH first
    spec_root = os.path.dirname(os.path.abspath(SPECPATH))
except:
    # Fallback to current working directory
    spec_root = os.getcwd()

# Debug: Print the paths we're trying to use
print(f"Spec root directory: {spec_root}")
icon_png_path = os.path.join(spec_root, 'assets', 'icon.png')
icon_ico_path = os.path.join(spec_root, 'assets', 'icon.ico')
print(f"Looking for icon.png at: {icon_png_path}")
print(f"Looking for icon.ico at: {icon_ico_path}")
print(f"icon.png exists: {os.path.exists(icon_png_path)}")
print(f"icon.ico exists: {os.path.exists(icon_ico_path)}")

# Create the datas list, only including files that actually exist
datas_list = []
if os.path.exists(icon_png_path):
    datas_list.append((icon_png_path, 'assets'))
    print(f"✓ Including icon.png")
else:
    print(f"✗ Skipping icon.png (not found)")

if os.path.exists(icon_ico_path):
    datas_list.append((icon_ico_path, 'assets'))
    print(f"✓ Including icon.ico")
else:
    print(f"✗ Skipping icon.ico (not found)")

a = Analysis(
    ['main.py'],
    pathex=[spec_root],
    binaries=[],
    datas=datas_list,
    hiddenimports=[
        'customtkinter',
        'PIL._tkinter_finder',
        'pystray._win32',
        'schedule',
        'requests',
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
        '_tkinter',
        'PIL.ImageTk',
        'PIL.Image',
        'threading',
        'queue'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'jupyter',
        'IPython',
        'qtpy',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6'
    ],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='APODPaper',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # Disable UPX compression as it can cause DLL issues
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_ico_path if os.path.exists(icon_ico_path) else None,
)
