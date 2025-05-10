# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['reminder_app.py'],
    pathex=[],
    binaries=[],
    datas=[('icon.ico', '.'), ('sounds/*', 'sounds')],  # 包含声音文件夹
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
    [],
    exclude_binaries=True,
    name='reminder_app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # 关键修改点：关闭控制台窗口
    icon='icon.ico',  # 确保图标参数存在
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='reminder_app',
)

# 添加运行时依赖
added_files = [
    ('vcruntime140.dll', '.'),
    ('icon.ico', '.')
]
a.datas += added_files
