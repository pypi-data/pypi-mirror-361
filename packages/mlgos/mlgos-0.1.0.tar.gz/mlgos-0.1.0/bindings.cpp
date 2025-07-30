#include <pybind11/pybind11.h>
#include <pybind11/stl.h>  // Needed to bind std::vector
#include "models/linear_regression.cpp"

namespace py = pybind11;

PYBIND11_MODULE(mlgos, m) {
    m.doc() = "MLGOS: Classic ML algorithms in C++ with Python bindings";

    py::class_<LinearRegression>(m, "LinearRegression")
        .def(py::init<>())
        .def("fit", &LinearRegression::fit)
        .def("predict", &LinearRegression::predict)
        .def("get_slope", &LinearRegression::get_slope)
        .def("get_intercept", &LinearRegression::get_intercept);
}
