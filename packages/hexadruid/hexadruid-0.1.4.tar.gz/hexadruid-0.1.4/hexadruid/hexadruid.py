# hexadruid/hexadruid.py

import importlib.util
import os

def _load_core_class():
    base_dir = os.path.dirname(__file__)
    pycache_dir = os.path.join(base_dir, '__pycache__')
    pyc_file = next((f for f in os.listdir(pycache_dir)
                     if f.startswith('_core') and f.endswith('.pyc')), None)

    if not pyc_file:
        raise ImportError("Compiled _core module not found.")

    pyc_path = os.path.join(pycache_dir, pyc_file)
    spec = importlib.util.spec_from_file_location("_core", pyc_path)
    _core = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(_core)

    return _core._HexaDruidCore

_HexaDruidCore = _load_core_class()

class HexaDruid(_HexaDruidCore):
    """Public HexaDruid interface — safe user wrapper."""
    pass
