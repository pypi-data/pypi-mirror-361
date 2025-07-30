import mlgos

def test_fit_predict():
    model = mlgos.LinearRegression()
    X = [1, 2, 3]
    y = [2, 4, 6]
    model.fit(X, y)
    print("Slope:", model.get_slope())
    print("Intercept:", model.get_intercept())
    preds = model.predict([4])
    print("Predicted value for input [4]:", preds)
    assert abs(model.get_slope() - 2.0) < 1e-6
    assert abs(model.get_intercept()) < 1e-6
    assert abs(preds[0] - 8.0) < 1e-6
    print("Test passed!")

if __name__ == "__main__":
    test_fit_predict()
