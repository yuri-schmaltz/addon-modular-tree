# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import importlib.util
import os
import sys
from pathlib import Path
import bpy

MIN_BLENDER_VERSION = (4, 2, 0)
_python_classes_module = None
_dll_search_handles = []

bl_info = {
    "name" : "Modular Tree",
    "author" : "Maxime",
    "description" : "create trees",
    "blender" : (4, 2, 0),
    "version" : (4, 0, 2),
    "location" : "",
    "warning" : "Requires Blender 4.2+",
    "category" : "Generic"
}


# auto_load.init()

def _find_native_module():
    addon_root = Path(__file__).resolve().parent
    major, minor = sys.version_info.major, sys.version_info.minor
    abi_markers = (
        f"cp{major}{minor}",
        f"cpython-{major}{minor}",
        f"cpython-{major}.{minor}",
    )

    candidates = []
    for pattern in ("m_tree*.pyd", "m_tree*.so", "m_tree*.dylib"):
        candidates.extend(sorted(addon_root.glob(pattern)))

    for candidate in candidates:
        lowered = candidate.name.lower()
        if any(marker in lowered for marker in abi_markers):
            return candidate

    if candidates:
        return candidates[0]
    return None


def _ensure_native_module_loaded():
    module_name = f"{__name__}.m_tree"
    if module_name in sys.modules:
        return

    native_module = _find_native_module()
    if native_module is None:
        py_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        raise RuntimeError(
            "Modular Tree native module not found. Build/package a 'm_tree' extension "
            f"for Python {py_version} and place it next to this __init__.py."
        )

    if hasattr(os, "add_dll_directory"):
        _dll_search_handles.append(os.add_dll_directory(str(native_module.parent)))

    spec = importlib.util.spec_from_file_location(module_name, str(native_module))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load native module spec from '{native_module}'.")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    except Exception as exc:
        raise RuntimeError(
            f"Failed to load native module '{native_module.name}'. "
            "Check Blender/Python compatibility for this binary."
        ) from exc

def _ensure_supported_blender():
    if bpy.app.version < MIN_BLENDER_VERSION:
        required = ".".join(map(str, MIN_BLENDER_VERSION))
        current = ".".join(map(str, bpy.app.version))
        raise RuntimeError(f"Modular Tree requires Blender {required}+ (found {current}).")

def register():
    global _python_classes_module
    _ensure_supported_blender()
    _ensure_native_module_loaded()
    if _python_classes_module is None:
        from . import python_classes as imported_python_classes

        _python_classes_module = imported_python_classes
    _python_classes_module.register()
    # auto_load.register()

def unregister():
    global _python_classes_module, _dll_search_handles
    if _python_classes_module is not None:
        _python_classes_module.unregister()
        _python_classes_module = None
    for dll_handle in _dll_search_handles:
        dll_handle.close()
    _dll_search_handles = []
    # auto_load.unregister()
