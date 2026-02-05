cmake_minimum_required(VERSION 3.16)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

set(CMAKE_TOOLCHAIN_FILE ../dependencies/vcpkg/scripts/buildsystems/vcpkg.cmake CACHE STRING "")

find_package(pybind11 CONFIG QUIET)
if(NOT pybind11_FOUND)
    add_subdirectory(../dependencies/pybind11 [EXCLUDE_FROM_ALL])
endif()

file(GLOB_RECURSE sources
    "./*.hpp"
    "./*.cpp"
)

pybind11_add_module(m_tree ${sources})
target_link_libraries(m_tree PRIVATE m_tree-lib)
