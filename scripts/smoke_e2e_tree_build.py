import argparse
import importlib.util
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

    parser = argparse.ArgumentParser(description="Run a minimal E2E tree build smoke test.")
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


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


def run_negative_cases():
    node_tree = bpy.data.node_groups.new("SMOKE_MTREE_INVALID", "mt_MtreeNodeTree")
    mesher = node_tree.nodes.new("mt_MesherNode")

    assert_true(
        not mesher.get_tree_validity(),
        "Expected invalid tree graph with no trunk link",
    )

    trunk_a = node_tree.nodes.new("mt_TrunkNode")
    trunk_b = node_tree.nodes.new("mt_TrunkNode")
    node_tree.links.new(mesher.outputs["Tree"], trunk_a.inputs["Tree"])
    node_tree.links.new(mesher.outputs["Tree"], trunk_b.inputs["Tree"])

    assert_true(
        not mesher.get_tree_validity(),
        "Expected invalid tree graph with multiple trunk links",
    )


def run_e2e():
    run_negative_cases()

    node_tree = bpy.data.node_groups.new("SMOKE_MTREE", "mt_MtreeNodeTree")
    mesher = node_tree.nodes.new("mt_MesherNode")
    trunk = node_tree.nodes.new("mt_TrunkNode")
    node_tree.links.new(mesher.outputs["Tree"], trunk.inputs["Tree"])

    assert_true(mesher.get_tree_validity(), "Expected valid tree graph for mesher->trunk")
    mesher.build_tree()

    tree_object = bpy.data.objects.get(mesher.tree_object)
    assert_true(tree_object is not None, "Expected generated tree object to exist")
    assert_true(tree_object.type == "MESH", "Expected generated object type to be MESH")
    assert_true(len(tree_object.data.vertices) > 0, "Expected generated mesh to have vertices")
    assert_true(len(tree_object.data.polygons) > 0, "Expected generated mesh to have polygons")

    branch = node_tree.nodes.new("mt_BranchNode")
    node_tree.links.new(trunk.outputs["Tree"], branch.inputs["Tree"])
    node_tree.links.new(branch.outputs["Tree"], trunk.inputs["Tree"])
    assert_true(not mesher.get_tree_validity(), "Expected cycle detection to invalidate graph")


def main():
    args = parse_args()
    addon_dir = os.path.abspath(args.addon_dir)
    print(f"E2E addon_dir={addon_dir}")
    print(f"E2E module_name={args.module_name}")

    module = None
    try:
        module = load_module(addon_dir, args.module_name)
        print("E2E import=ok")
        module.register()
        print("E2E register=ok")
        run_e2e()
        print("E2E tree_build=ok")
        return 0
    except Exception:
        print("E2E status=failed")
        traceback.print_exc()
        return 1
    finally:
        if module is not None:
            try:
                module.unregister()
                print("E2E unregister=ok")
            except Exception:
                traceback.print_exc()
                return 1


if __name__ == "__main__":
    raise SystemExit(main())
