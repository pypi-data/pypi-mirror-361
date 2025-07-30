# CMakeList.txt : CMake project for mlgos, include source and define
# project specific logic here.
#

# Add source to this project's executable.
add_executable (mlgos "mlgos.cpp" "mlgos.h" "models/linear_regression.cpp" "models/linear_regression.h" "bindings.cpp")

if (CMAKE_VERSION VERSION_GREATER 3.12)
  set_property(TARGET mlgos PROPERTY CXX_STANDARD 20)
endif()

# TODO: Add tests and install targets if needed.
