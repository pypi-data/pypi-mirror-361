cmake_minimum_required(VERSION 3.15)
project(mlgos VERSION 0.1.0 LANGUAGES CXX)

# Use modern Python finding
set(PYBIND11_FINDPYTHON ON)

# Fetch pybind11 automatically if not found
include(FetchContent)
FetchContent_Declare(
  pybind11
  GIT_REPOSITORY https://github.com/pybind/pybind11.git
  GIT_TAG        v2.12.0
)
FetchContent_MakeAvailable(pybind11)

# Your Python extension module
pybind11_add_module(mlgos bindings.cpp)

# Include your models folder
target_include_directories(mlgos
  PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/models
)

# Example: link math lib if needed
target_link_libraries(mlgos PRIVATE pybind11::module)

# Compiler flags
set_target_properties(mlgos PROPERTIES
  CXX_STANDARD 17
  CXX_STANDARD_REQUIRED YES
  CXX_EXTENSIONS NO
)
