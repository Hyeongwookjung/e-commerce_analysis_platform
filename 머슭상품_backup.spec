# -*- mode: python ; coding: utf-8 -*-
ui = [('python310.dll','.'),('Analysis Interface.ui','.'),('free.ui','.'),('Find.ui','.'),('Login.ui','.'),('recommend.ui','.'),('Keyword.ui','.'),('Register.ui','.'),('test.qrc','.'),('KoPubWorld Dotum Bold.ttf','.'),('KoPubWorld Dotum Light.ttf','.'),('KoPubWorld Dotum Medium.ttf','.'),('category.csv','.'),('login_logo.png','.'),('icon.png','.'),('icon.ico','.'),('test_rc.py','.')]


block_cipher = pyi_crypto.PyiBlockCipher(key='guddnr0308')


a = Analysis(['C:\\Users\\ekam3\\Documents\\e-commerce_analysis_platform\\shopping_trend.py'],
             pathex=[],
             binaries=[],
             datas=ui,
             hiddenimports=['sklearn.utils._vector_sentinel', 'sklearn.utils._sorting', 'sklearn.utils._heap', 'sklearn.utils._cython_blas', 'sklearn.neighbors.typedefs', 'sklearn.neighbors.quad_tree', 'sklearn.tree._utils', 'sklearn.neighbors._typedefs', 'sklearn.utils._typedefs', 'sklearn.neighbors._partition_nodes'],
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
          [],
          exclude_binaries=True,
          name='머슭상품',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None , icon='icon.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas, 
               strip=False,
               upx=True,
               upx_exclude=[],
               name='머슭상품')
