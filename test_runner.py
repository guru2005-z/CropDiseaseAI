import sys
from pathlib import Path

# Provide minimal shim for py.path.local if py package is missing
import types
if "py" not in sys.modules:
    py_mod = types.ModuleType("py")
    py_path = types.ModuleType("py.path")
    py_path.local = Path
    py_error = types.ModuleType("py.error")
    py_mod.path = py_path
    py_mod.error = py_error
    sys.modules["py"] = py_mod
    sys.modules["py.path"] = py_path
    sys.modules["py.error"] = py_error

sys.path.insert(0, r'C:\Users\vamsi\OneDrive\Desktop\CropDiseaseAI\venv\Lib\site-packages')
sys.path.insert(0, r'C:\Users\vamsi\OneDrive\Desktop\CropDiseaseAI')

import pytest
ret = pytest.main(['tests', '-v'])
print(f"Pytest return code: {ret}")
sys.exit(ret)
