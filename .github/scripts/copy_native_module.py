import argparse
import shutil
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="Copy built m_tree native module to addon root.")
    parser.add_argument("--source-dir", required=True, help="Directory containing built artifacts")
    parser.add_argument("--dest-dir", required=True, help="Destination directory")
    return parser.parse_args()


def find_native_module(source_dir):
    candidates = []
    for pattern in ("m_tree*.pyd", "m_tree*.so", "m_tree*.dylib"):
        candidates.extend(source_dir.glob(pattern))

    if not candidates:
        raise FileNotFoundError(f"No native module matching m_tree* found in '{source_dir}'.")

    return max(candidates, key=lambda path: path.stat().st_mtime)


def main():
    args = parse_args()
    source_dir = Path(args.source_dir).resolve()
    dest_dir = Path(args.dest_dir).resolve()
    dest_dir.mkdir(parents=True, exist_ok=True)

    source_file = find_native_module(source_dir)
    target_file = dest_dir / source_file.name
    shutil.copy2(source_file, target_file)
    print(f"copied {source_file} -> {target_file}")


if __name__ == "__main__":
    main()
