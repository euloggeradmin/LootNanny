# -*- mode: python ; coding: utf-8 -*-
import os
import sys
sys.path.append(DISTPATH + "\\..")
from version import VERSION

block_cipher = None

PYTHON_VERSION = "_".join(map(str, sys.version_info[:3]))

a = Analysis(['LootNanny.py'],
             pathex=[],
             binaries=[],
             datas=[
                ("attachments.json", "."),
                ("weapons.json", "."),
                ("light.qss", "."),
                ("dark.qss", "."),
                ("sights.json", "."),
                ("scopes.json", ".")
             ],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,  
          [],
          name=f'LootNanny-{VERSION}-p{PYTHON_VERSION}',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None , icon='favicon.ico')
