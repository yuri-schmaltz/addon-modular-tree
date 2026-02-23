import os
import re
import sys
import platform
import subprocess

from distutils.version import LooseVersion


VCPKG_PATH = os.path.join(os.path.dirname(__file__), "dependencies", "vcpkg")

PACKAGES = ["eigen3"]


def get_vcpkg_triplet():
    triplet_override = os.environ.get("VCPKG_TRIPLET")
    if triplet_override:
        return triplet_override

    generator = os.environ.get("CMAKE_GENERATOR", "")
    if platform.system() == "Windows" and "MinGW" in generator:
        return "x64-mingw-dynamic"

    if platform.system() == "Windows":
        return "x64-windows"
    if platform.system() == "Linux":
        return "x64-linux"
    return "x64-osx"


def get_vcpkg_executable():
    if platform.system() == "Windows":
        return os.path.join(VCPKG_PATH, "vcpkg.exe")
    return os.path.join(VCPKG_PATH, "vcpkg")


def install():
    try:
        out = subprocess.check_output(['cmake', '--version'])
    except OSError:
        raise RuntimeError("CMake must be installed")

    if platform.system() == "Windows":
        cmake_version = LooseVersion(re.search(r'version\s*([\d.]+)', out.decode()).group(1))
        if cmake_version < '3.1.0':
            raise RuntimeError("CMake >= 3.1.0 is required on Windows")

    install_vcpkg_dependencies()
    build()

    
def install_vcpkg_dependencies():
    print(f"system is {platform.system()}")
    vcpkg = get_vcpkg_executable()
    if not os.path.exists(vcpkg):
        if platform.system() == "Windows":
            subprocess.check_call(["cmd", "/c", "bootstrap-vcpkg.bat"], cwd=VCPKG_PATH)
        else:
            subprocess.check_call([os.path.join(VCPKG_PATH, "bootstrap-vcpkg.sh")], cwd=VCPKG_PATH)
    else:
        print(f"using existing vcpkg executable at {vcpkg}")

    triplet = get_vcpkg_triplet()
    for package in PACKAGES:
        print(f"installing {package}:{triplet}")
        subprocess.check_call([vcpkg, "install", f"{package}:{triplet}", "--binarysource=clear"])

def build():
    build_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "build"))
    if not os.path.exists(build_dir):
        os.makedirs(build_dir)

    python_executable = os.environ.get("PYTHON_EXECUTABLE", sys.executable)
    python_version = os.environ.get("MTREE_PYTHON_VERSION", f"{sys.version_info.major}.{sys.version_info.minor}")
    print(f"building python bindings for Python {python_version}")

    pybind11_dir = os.environ.get("PYBIND11_DIR")
    use_system_pybind11 = os.environ.get("MTREE_USE_SYSTEM_PYBIND11", "0") == "1"
    if not pybind11_dir and use_system_pybind11:
        try:
            pybind11_dir = subprocess.check_output(
                [python_executable, "-c", "import pybind11; print(pybind11.get_cmake_dir())"],
                text=True,
            ).strip()
        except Exception:
            pybind11_dir = ""

    triplet = get_vcpkg_triplet()
    configure_cmd = ['cmake']
    if os.environ.get("CMAKE_FRESH", "1") == "1":
        configure_cmd.append("--fresh")
    configure_cmd.extend(
        [
            "../",
            f"-DPYBIND11_PYTHON_VERSION={python_version}",
            f"-DPYTHON_EXECUTABLE={python_executable}",
            f"-DPython_EXECUTABLE={python_executable}",
            f"-DVCPKG_TARGET_TRIPLET={triplet}",
        ]
    )
    if pybind11_dir:
        configure_cmd.append(f"-Dpybind11_DIR={pybind11_dir}")
    generator = os.environ.get("CMAKE_GENERATOR")
    if generator:
        configure_cmd.extend(["-G", generator])

    c_compiler = os.environ.get("CMAKE_C_COMPILER")
    cxx_compiler = os.environ.get("CMAKE_CXX_COMPILER")
    if c_compiler:
        configure_cmd.append(f"-DCMAKE_C_COMPILER={c_compiler}")
    if cxx_compiler:
        configure_cmd.append(f"-DCMAKE_CXX_COMPILER={cxx_compiler}")

    subprocess.check_call(configure_cmd, cwd=build_dir)
    subprocess.check_call(['cmake', '--build', '.', "--config", "Release"], cwd=build_dir)

    print([i for i in os.listdir(os.path.join(os.path.dirname(__file__), "binaries"))])
    

if __name__ == "__main__":
    install()
