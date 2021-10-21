from modelregistry.utils.exception import SquirrelException
from modelregistry.utils.pip_patch import *
import pickle
from typing import List


def getModel(path: str):
    with open(path, "rb") as f:
        return pickle.load(f)


def _get_pip_modules(path: str) -> List:
    try:
        cap_cm = _CaptureImportedModules()
        with cap_cm:
            getModel(path)
        return list(cap_cm.imported_modules)
    except Exception as e:
        raise SquirrelException("Failed to get the dependencies")
