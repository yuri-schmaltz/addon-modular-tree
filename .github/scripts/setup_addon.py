from genericpath import exists
import os
import zipfile
from pathlib import Path
import shutil
import platform


TMP_DIRPATH = r"./tmp"
ADDON_SOURCE_DIRNAME = "python_classes"
RESOURCES_DIRNAME = "resources"
VERSION_FILEPATH = os.path.join(Path(__file__).parent.parent.parent, "VERSION")
MANIFEST_FILENAME = "blender_manifest.toml"
EXTRA_ROOT_FILES = ["LICENSE.md", "README.md", "VERSION", MANIFEST_FILENAME]

def get_platform_tag():
    system = platform.system()
    machine = platform.machine().lower()
    if machine in {"x86_64", "amd64"}:
        arch = "x64"
    elif machine in {"arm64", "aarch64"}:
        arch = "arm64"
    else:
        arch = machine or "unknown"

    if system == "Windows":
        return f"windows-{arch}"
    if system == "Linux":
        return f"linux-{arch}"
    if system == "Darwin":
        return f"macos-{arch}"
    return f"{system.lower()}-{arch}"

def setup_addon_directory():
    version = read_version()
    addon_dirpath = os.path.join(TMP_DIRPATH, "modular_tree")
    if os.path.isdir(addon_dirpath):
        shutil.rmtree(addon_dirpath)
    root = addon_dirpath
    Path(root).mkdir(exist_ok=True, parents=True)

    all_files = os.listdir(".")

    if not [i for i in all_files if i.endswith(".pyd") or i.endswith(".so")]:
        list_files(".")
        raise Exception("no libraries were output")
    for f in all_files:
        if f.endswith(".py") or f.endswith(".pyd") or f.endswith(".so") or f.endswith(".dll"):
            shutil.copy2(os.path.join(".",f), root)
        elif f == ADDON_SOURCE_DIRNAME or f == RESOURCES_DIRNAME:
            shutil.copytree(os.path.join(".",f), os.path.join(root, f))

    for fname in EXTRA_ROOT_FILES:
        src = os.path.join(".", fname)
        if os.path.exists(src):
            shutil.copy2(src, root)
        else:
            raise FileNotFoundError(f"Required file missing: {fname}")

    return addon_dirpath

def create_zip(input_dir, output_dir, version):
    platform_tag = get_platform_tag()
    basename = os.path.join(output_dir, f"modular_tree-{version}-{platform_tag}")
    filepath = shutil.make_archive(basename, "zip", root_dir=os.path.dirname(input_dir), base_dir=os.path.basename(input_dir))
    return filepath


def list_files(root_directory):
    excluded_directories = {"dependencies", "build", "__pycache__", ".github", ".git"}
    for root, _, files in os.walk(root_directory):
        should_skip = False
        for exclusion in excluded_directories:
            if exclusion in root:
                should_skip = True
                break
        if should_skip:
            continue


        level = root.replace(root_directory, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print('{}{}/'.format(indent, os.path.basename(root)))
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            print('{}{}'.format(subindent, f))

def read_version():
    with open(VERSION_FILEPATH, "r") as f:
        return f.read().strip()

if __name__ == "__main__":
    addon_dirpath = setup_addon_directory()
    archive_filepath = create_zip(addon_dirpath, TMP_DIRPATH, read_version())
