# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for Vibrante-Node v1.3.0 Windows 64-bit build
# Run: pyinstaller vibrante_node.spec

import os
from pathlib import Path

block_cipher = None

# Collect all data files needed at runtime
datas = [
    # UI assets
    ('splash.png', '.'),
    ('logo.png', '.'),
    ('icons', 'icons'),
    # Node definitions
    ('nodes', 'nodes'),
    ('node_examples', 'node_examples'),
    # Houdini plugin nodes
    ('plugins/houdini/v_nodes_houdini', 'plugins/houdini/v_nodes_houdini'),
    ('plugins/houdini/v_scripts_houdini', 'plugins/houdini/v_scripts_houdini'),
    # Example workflows
    ('workflows', 'workflows'),
    # Examples
    ('examples', 'examples'),
]

a = Analysis(
    ['src/main.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=[
        # PyQt5
        'PyQt5',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'PyQt5.sip',
        # Google Generative AI
        'google.generativeai',
        'google.api_core',
        'google.auth',
        # Async
        'asyncio',
        'asyncio.events',
        # Other
        'toposort',
        'pydantic',
        # Node base
        'src.nodes.base',
        'src.core.engine',
        'src.core.graph',
        'src.core.registry',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'PIL',
        'tkinter',
        'wx',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Vibrante-Node',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,                  # No console window — GUI app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icons/vibrante-node-icon.png',  # App icon
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Vibrante-Node',
)
