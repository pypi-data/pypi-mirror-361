# Distributed under the OSI-approved BSD 3-Clause License.  See accompanying
# file Copyright.txt or https://cmake.org/licensing for details.

cmake_minimum_required(VERSION 3.5)

# If CMAKE_DISABLE_SOURCE_CHANGES is set to true and the source directory is an
# existing directory in our source tree, calling file(MAKE_DIRECTORY) on it
# would cause a fatal error, even though it would be a no-op.
if(NOT EXISTS "E:/Users/srkv0/source/repos/mlgos/_deps/pybind11-src")
  file(MAKE_DIRECTORY "E:/Users/srkv0/source/repos/mlgos/_deps/pybind11-src")
endif()
file(MAKE_DIRECTORY
  "E:/Users/srkv0/source/repos/mlgos/_deps/pybind11-build"
  "E:/Users/srkv0/source/repos/mlgos/_deps/pybind11-subbuild/pybind11-populate-prefix"
  "E:/Users/srkv0/source/repos/mlgos/_deps/pybind11-subbuild/pybind11-populate-prefix/tmp"
  "E:/Users/srkv0/source/repos/mlgos/_deps/pybind11-subbuild/pybind11-populate-prefix/src/pybind11-populate-stamp"
  "E:/Users/srkv0/source/repos/mlgos/_deps/pybind11-subbuild/pybind11-populate-prefix/src"
  "E:/Users/srkv0/source/repos/mlgos/_deps/pybind11-subbuild/pybind11-populate-prefix/src/pybind11-populate-stamp"
)

set(configSubDirs Debug)
foreach(subDir IN LISTS configSubDirs)
    file(MAKE_DIRECTORY "E:/Users/srkv0/source/repos/mlgos/_deps/pybind11-subbuild/pybind11-populate-prefix/src/pybind11-populate-stamp/${subDir}")
endforeach()
if(cfgdir)
  file(MAKE_DIRECTORY "E:/Users/srkv0/source/repos/mlgos/_deps/pybind11-subbuild/pybind11-populate-prefix/src/pybind11-populate-stamp${cfgdir}") # cfgdir has leading slash
endif()
