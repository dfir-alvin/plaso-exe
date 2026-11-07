# PyInstaller spec: builds all five plaso tools into ONE onedir folder that
# shares a single _internal\ directory (like the old plaso-YYYYMMDD-py3.x-amd64.zip).
#
# Run from the root of a plaso source checkout, with plaso installed in the
# active Python:   pyinstaller --noconfirm --clean path\to\plaso.spec
import os

from PyInstaller.utils.hooks import collect_all, collect_submodules

block_cipher = None

# plaso's console scripts; each has `if __name__ == "__main__": freeze_support()`
TOOLS = ["log2timeline", "psort", "pinfo", "psteal", "image_export"]
# Paths in a spec resolve relative to the spec file, so anchor on the CWD
# (the plaso checkout) instead.
SRC = os.getcwd()
SCRIPTS_DIR = os.path.join(SRC, "plaso", "scripts")

# Packages that load YAML / data files relative to their own __file__,
# or register parsers/plugins dynamically. collect_all grabs code + data + metadata.
COLLECT_ALL = [
    "plaso",       # data\, parsers\*.yaml, preprocessors\*.yaml, formatters
    "artifacts",   # artifacts\data\*.yaml  (artifact definitions)
    "dfvfs",       # dfvfs\lib\*.yaml (dtFabric definitions)
    "dfwinreg",    # dfwinreg\*.yaml
    "dfdatetime",
    "dtfabric",
    "acstore",
    "certifi",     # CA bundle for opensearch / requests
]

datas, binaries, hiddenimports = [], [], []
for pkg in COLLECT_ALL:
    d, b, h = collect_all(pkg)
    datas += d
    binaries += b
    hiddenimports += h

# Parsers, plugins, output modules and analysis plugins are imported through
# registries, so make sure every submodule is in the bundle.
hiddenimports += collect_submodules("plaso")
hiddenimports += [
    # C extensions imported lazily / via dependency checks
    "pybde", "pycaes", "pycreg", "pyesedb", "pyevt", "pyevtx", "pyewf",
    "pyfcrypto", "pyfsapfs", "pyfsext", "pyfsfat", "pyfshfs", "pyfsntfs",
    "pyfsxfs", "pyfvde", "pyfwnt", "pyfwsi", "pylnk", "pyluksde", "pymodi",
    "pymsiecf", "pyolecf", "pyphdi", "pyqcow", "pyregf", "pyscca",
    "pysigscan", "pysmdev", "pysmraw", "pytsk3", "pyvhdi", "pyvmdk",
    "pyvsapm", "pyvsgpt", "pyvshadow", "pyvslvm",
    "yara", "zstd", "lz4.frame", "zmq", "redis", "opensearchpy", "requests",
    "xlsxwriter", "psutil", "pefile", "flor", "bencode", "defusedxml",
]
if os.name == "nt":
    # Optional: plaso.cli.status_view uses pywin32 for the "window" status view.
    hiddenimports += ["win32api", "win32console", "pywintypes"]

# Optional heavy stuff plaso doesn't need at runtime.
EXCLUDES = ["tkinter", "matplotlib", "IPython", "pytest", "unittest.mock"]

analyses = []
for tool in TOOLS:
    a = Analysis(
        [os.path.join(SCRIPTS_DIR, f"{tool}.py")],
        pathex=[SRC],
        binaries=binaries,
        datas=datas,
        hiddenimports=hiddenimports,
        excludes=EXCLUDES,
        noarchive=False,
        cipher=block_cipher,
    )
    analyses.append((tool, a))

exes, collect_args = [], []
for tool, a in analyses:
    pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,   # onedir: binaries go into the shared COLLECT
        name=tool,
        console=True,
        upx=False,               # UPX on .pyd files triggers AV false positives
    )
    collect_args += [exe, a.binaries, a.zipfiles, a.datas]

# One COLLECT => dist\plaso\{log2timeline,psort,...}.exe + one shared _internal\
coll = COLLECT(*collect_args, strip=False, upx=False, name="plaso")
