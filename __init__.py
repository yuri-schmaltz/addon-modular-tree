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
from .core.logger import setup_logger, get_logger

# Initialize logger
setup_logger()
logger = get_logger()

MIN_BLENDER_VERSION = (4, 2, 0)
_core_module = None
_dll_search_handles = []

bl_info = {
    "name" : "Modular Tree",
    "author" : "Maxime",
    "description" : "A powerful node-based procedural tree generation tool.",
    "blender" : (4, 2, 0),
    "version" : (4, 1, 0),
    "location" : "View3D > Sidebar > Mtree | Node Editor > Sidebar > Mtree",
    "warning" : "Requires Blender 4.2+ and compiled native module.",
    "doc_url": "https://github.com/MaximeHerpin/modular_tree",
    "tracker_url": "https://github.com/MaximeHerpin/modular_tree/issues",
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
    # Search in root and in core/m_tree/binaries (common for dev)
    for search_path in (addon_root, addon_root / "core", addon_root / "core" / "m_tree" / "binaries"):
        if not search_path.exists():
            continue
        for pattern in ("m_tree*.pyd", "m_tree*.so", "m_tree*.dylib"):
            candidates.extend(sorted(search_path.glob(pattern)))

    for candidate in candidates:
        lowered = candidate.name.lower()
        if any(marker in lowered for marker in abi_markers):
            logger.info(f"Found matching native module candidate: {candidate.name}")
            return candidate

    if candidates:
        logger.warning(f"No exact Python ABI match found. Falling back to: {candidates[0].name}")
        return candidates[0]
    return None


def _ensure_native_module_loaded():
    module_name = f"{__name__}.m_tree"
    if module_name in sys.modules:
        return

    logger.debug(f"Attempting to load native module: {module_name}")
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
        logger.info(f"Successfully loaded native module: {native_module.name}")
    except Exception as exc:
        logger.error(f"Failed to load native module '{native_module.name}': {exc}")
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
    global _core_module
    _ensure_supported_blender()
    _ensure_native_module_loaded()
    if _core_module is None:
        from . import core as imported_core

        _core_module = imported_core
    _core_module.register()
    # auto_load.register()

def unregister():
    global _core_module, _dll_search_handles
    if _core_module is not None:
        _core_module.unregister()
        _core_module = None
    for dll_handle in _dll_search_handles:
        dll_handle.close()
    _dll_search_handles = []
    # auto_load.unregister()
