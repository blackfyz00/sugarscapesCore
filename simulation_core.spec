from PyInstaller.utils.hooks import collect_submodules

datas = [
    ('src/maps', 'maps'), 
    ('src/templates', 'templates'),
]

binaries = []

hiddenimports = ['numpy', 'matplotlib.pyplot', 'PIL']
hiddenimports += collect_submodules('scipy')

local_modules = [
    'core.agents',
    'core.world',
    'classes',
    'utils.create_map',
    'utils.metrics',
    'utils.plotter',
    'utils.exporter',
    'pipeline',
    'registry',
    
    'mechanics',
    'mechanics.movement',
    'mechanics.movement.move_cobb_strategy',
    'mechanics.movement.findperspectivecell',
    
    'mechanics.eat',
    'mechanics.eat.eat_all_strategy',
    
    'mechanics.trade',
    'mechanics.trade.trade_cobb_strategy',
    'mechanics.trade.trade',
    
    'mechanics.reproduce',
    'mechanics.reproduce.reproduce_strategy',
    
    'mechanics.aging',
    'mechanics.aging.aging_strategy',
    
    'mechanics.death',
    'mechanics.death.death_strategy',
    
    'mechanics.regenerate_res',
    'mechanics.regenerate_res.regenerate_resources',
]

hiddenimports.extend(local_modules)

a = Analysis(
    ['src/main.py'],
    pathex=['src'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    name='simulation_core',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
