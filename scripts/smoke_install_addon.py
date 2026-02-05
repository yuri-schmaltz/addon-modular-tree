import argparse
import os
import sys
import traceback

import bpy


def parse_args():
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1 :]
    else:
        argv = []

    parser = argparse.ArgumentParser(description="Install and enable addon from a zip.")
    parser.add_argument("--zip-path", required=True, help="Path to addon zip file")
    parser.add_argument("--module-name", default="modular_tree", help="Addon module name")
    return parser.parse_args(argv)


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    args = parse_args()
    zip_path = os.path.abspath(args.zip_path)
    print(f"INSTALL zip_path={zip_path}")
    print(f"INSTALL module={args.module_name}")

    if not os.path.exists(zip_path):
        raise FileNotFoundError(zip_path)

    try:
        result = bpy.ops.preferences.addon_install(filepath=zip_path, overwrite=True)
        print(f"INSTALL addon_install={result}")
        result = bpy.ops.preferences.addon_enable(module=args.module_name)
        print(f"INSTALL addon_enable={result}")

        enabled = args.module_name in bpy.context.preferences.addons
        assert_true(enabled, f"Addon '{args.module_name}' not enabled.")

        print("INSTALL status=ok")
        return 0
    except Exception:
        print("INSTALL status=failed")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
