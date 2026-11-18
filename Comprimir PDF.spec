# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:/Users/johann/Documents/ChatGPT/Luis/Comprimir PDF/comprimir_pdf.py'],
    pathex=[],
    binaries=[],
    datas=[('C:/Users/johann/Documents/ChatGPT/Luis/Comprimir PDF/comprimir_pdf.ico', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['pymupdf_layout', 'pymupdf4llm', 'onnxruntime', 'networkx', 'yaml', 'numpy'],
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
    name='Comprimir PDF',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['C:/Users/johann/Documents/ChatGPT/Luis/Comprimir PDF/comprimir_pdf.ico'],
)
