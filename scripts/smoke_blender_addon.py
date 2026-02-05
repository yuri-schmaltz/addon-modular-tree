import argparse
import importlib.util
import os
import sys
import traceback


def parse_args():
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1 :]
    else:
        argv = []

    parser = argparse.ArgumentParser(description="Smoke test a Blender addon package.")
    parser.add_argument("--addon-dir", required=True, help="Directory containing addon __init__.py")
    parser.add_argument(
        "--module-name",
        default="modular_tree",
        help="Module name to assign when importing the addon package",
    )
    return parser.parse_args(argv)


def load_module(addon_dir, module_name):
    init_path = os.path.join(addon_dir, "__init__.py")
    if not os.path.exists(init_path):
        raise FileNotFoundError(f"Addon init file not found: {init_path}")

    spec = importlib.util.spec_from_file_location(
        module_name,
        init_path,
        submodule_search_locations=[addon_dir],
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def main():
    args = parse_args()
    addon_dir = os.path.abspath(args.addon_dir)
    print(f"SMOKE addon_dir={addon_dir}")
    print(f"SMOKE module_name={args.module_name}")

    try:
        module = load_module(addon_dir, args.module_name)
        print("SMOKE import=ok")
        module.register()
        print("SMOKE register=ok")
        module.unregister()
        print("SMOKE unregister=ok")
        return 0
    except Exception:
        print("SMOKE status=failed")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
