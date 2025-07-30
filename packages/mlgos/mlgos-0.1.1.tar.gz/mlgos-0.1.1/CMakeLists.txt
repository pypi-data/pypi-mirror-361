cmake_minimum_required(VERSION 3.14)
project(mlgos)

include(FetchContent)

# Fetch pybind11
FetchContent_Declare(
  pybind11
  GIT_REPOSITORY https://github.com/pybind/pybind11.git
  GIT_TAG v2.12.0
)
FetchContent_MakeAvailable(pybind11)

# Build the Python module
pybind11_add_module(mlgos
  bindings.cpp
  models/linear_regression.cpp
)
