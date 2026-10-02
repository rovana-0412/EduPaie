# -*- mode: python ; coding: utf-8 -*-
"""
Fichier de configuration PyInstaller pour EduPaie.
Inclut le schéma SQL et les modules nécessaires.
"""

block_cipher = None

# Fichiers à inclure dans l'exécutable
datas = [
    ('schema.sql', '.'),
]

# Modules cachés (nécessaires pour PySide6, reportlab, cryptography)
hiddenimports = [
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'reportlab',
    'reportlab.pdfgen',
    'reportlab.lib',
    'cryptography',
    'cryptography.fernet',
    'sqlite3',
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='EduPaie',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,          # Pas de console noire
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)