#include "linear_regression.h"

LinearRegression::LinearRegression() {}

void LinearRegression::fit(const std::vector<double>& X, const std::vector<double>& y) {
    double n = X.size();
    double sum_x = 0.0, sum_y = 0.0, sum_xy = 0.0, sum_xx = 0.0;

    for (size_t i = 0; i < n; ++i) {
        sum_x += X[i];
        sum_y += y[i];
        sum_xy += X[i] * y[i];
        sum_xx += X[i] * X[i];
    }

    w = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x * sum_x);
    b = (sum_y - w * sum_x) / n;
}

std::vector<double> LinearRegression::predict(const std::vector<double>& X) const {
    std::vector<double> y_pred;
    for (double x : X) {
        y_pred.push_back(w * x + b);
    }
    return y_pred;
}

double LinearRegression::get_slope() const {
    return w;
}

double LinearRegression::get_intercept() const {
    return b;
}
