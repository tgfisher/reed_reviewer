# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['entry_point.py'],
    pathex=[],
    binaries=[('./portaudio-binaries/libportaudio.dylib', '.')],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='Reed Tracker',
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
    icon=['app_images/oboeapp.icns'],
)
app = BUNDLE(
    exe,
    name='Reed Tracker.app',
    icon='./app_images/oboeapp.icns',
    bundle_identifier=None,
    info_plist={'NSMicrophoneUsageDescription': 'Reed Reviewer wants to listen to your reeds!'}
)
