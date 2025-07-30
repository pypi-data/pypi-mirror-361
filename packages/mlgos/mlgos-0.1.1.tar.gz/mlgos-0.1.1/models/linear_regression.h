#pragma once
#include <vector>

class LinearRegression {
private:
    double w = 0.0;
    double b = 0.0;

public:
    LinearRegression();

    void fit(const std::vector<double>& X, const std::vector<double>& y);
    std::vector<double> predict(const std::vector<double>& X) const;

    double get_slope() const;
    double get_intercept() const;
};
