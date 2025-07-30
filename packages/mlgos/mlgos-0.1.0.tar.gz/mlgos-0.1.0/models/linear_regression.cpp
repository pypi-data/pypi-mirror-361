#include <vector>

class LinearRegression {
private:
    double w = 0.0; // slope
    double b = 0.0; // intercept

public:
    LinearRegression() {}

    void fit(const std::vector<double>& X, const std::vector<double>& y) {
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

    std::vector<double> predict(const std::vector<double>& X) const {
        std::vector<double> y_pred;
        for (double x : X) {
            y_pred.push_back(w * x + b);
        }
        return y_pred;
    }

    double get_slope() const { return w; }
    double get_intercept() const { return b; }
};
