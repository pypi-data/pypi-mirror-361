# hexadruid.py
import importlib.util
import os

def _load_core_class():
    path = os.path.join(os.path.dirname(__file__), "_core.cpython-311.pyc")
    spec = importlib.util.spec_from_file_location("_core", path)
    _core = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(_core)
    return _core._HexaDruidCore

_HexaDruidCore = _load_core_class()

class HexaDruid(_HexaDruidCore):
    """Public HexaDruid interface"""
    pass
