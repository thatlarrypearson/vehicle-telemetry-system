# vehicle-telemetry-system/src/telemetry_analysis/polynomial_multivariate_regression.py
#
# Polynomial Multivariate Regression Function
#
# See docs at vehicle-telemetry-system/docs/polynomial_multivariate_regression.md

import pandas as pd
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
import numpy as np

def perform_polynomial_regression(df:pd.core.frame.DataFrame, degree, dependent_variable):
    """
    Performs polynomial multivariate regression on data from a CSV file.

    Args:
        df (pd.core.frame.DataFrame): Pandas dataframe.
        degree (int): The degree of the polynomial features to generate.
        dependent_variable (str): The name of the dependent variable (column header) in the CSV.

    Returns:
        dict: A dictionary containing the fitted model, polynomial features transformer,
              and R-squared score on the test set.
              Returns None if an error occurs (e.g., file not found, column not found).
    """

    # 1. Identify independent and dependent variables
    if dependent_variable not in df.columns:
        print(f"Error: Dependent variable '{dependent_variable}' not found in CSV columns.")
        return None

    y = df[dependent_variable]
    X = df.drop(columns=[dependent_variable])

    # Check if there are any independent variables left
    if X.empty:
        print("Error: No independent variables found after dropping the dependent variable.")
        return None

    # Handle non-numeric columns in independent variables by dropping them
    numeric_cols = X.select_dtypes(include=np.number).columns
    if len(numeric_cols) < X.shape[1]:
        print(f"Warning: Dropping non-numeric independent columns: {list(set(X.columns) - set(numeric_cols))}")
        X = X[numeric_cols]
    if X.empty:
        print("Error: No numeric independent variables remaining after cleaning.")
        return None

    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 2. Create polynomial features
    poly = PolynomialFeatures(degree=degree, include_bias=False) # include_bias=False to avoid duplicate constant term
    X_train_poly = poly.fit_transform(X_train)
    X_test_poly = poly.transform(X_test)

    # 3. Perform linear regression on the polynomial features
    model = LinearRegression()
    model.fit(X_train_poly, y_train)

    # 4. Evaluate the model
    y_pred = model.predict(X_test_poly)
    r2 = r2_score(y_test, y_pred)

    print(f"\nPolynomial Regression Model Summary (Degree: {degree})")
    print(f"Dependent Variable: {dependent_variable}")
    print(f"Independent Variables: {list(X.columns)}")
    print(f"R-squared (on test set): {r2:.4f}")

    return {
        "model": model,
        "polynomial_features_transformer": poly,
        "r_squared": r2
    }

# --- Example Usage ---

if __name__ == "__main__":
    # Create a dummy CSV file for demonstration
    data = {
        'feature_1': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'feature_2': [10, 8, 6, 4, 2, 1, 3, 5, 7, 9],
        'target_variable': [2, 5, 12, 22, 35, 50, 68, 89, 113, 140]
    }
    dummy_df = pd.DataFrame(data)
    dummy_csv_path = 'dummy_data.csv'
    dummy_df.to_csv(dummy_csv_path, index=False)
    print(f"Created dummy CSV file: {dummy_csv_path}")

    # Example 1: Using degree 2
    print("\n--- Running Example 1 (Degree 2) ---")
    results_degree_2 = perform_polynomial_regression(
        csv_filepath=dummy_csv_path,
        degree=2,
        dependent_variable='target_variable'
    )

    if results_degree_2:
        print("\nModel Coefficients:")
        # Get feature names after polynomial transformation
        feature_names_poly = results_degree_2["polynomial_features_transformer"].get_feature_names_out(
            ['feature_1', 'feature_2'] # Pass original feature names
        )
        for i, coef in enumerate(results_degree_2["model"].coef_):
            print(f"  {feature_names_poly[i]}: {coef:.4f}")
        print(f"  Intercept: {results_degree_2['model'].intercept_:.4f}")

        # How to use the model for new predictions:
        print("\n--- Making a prediction with the trained model (Degree 2) ---")
        new_data = pd.DataFrame({'feature_1': [11], 'feature_2': [10]})
        new_data_poly = results_degree_2["polynomial_features_transformer"].transform(new_data)
        prediction = results_degree_2["model"].predict(new_data_poly)
        print(f"Prediction for new data ([feature_1=11, feature_2=10]): {prediction[0]:.4f}")

    # Example 2: Using degree 3
    print("\n--- Running Example 2 (Degree 3) ---")
    results_degree_3 = perform_polynomial_regression(
        csv_filepath=dummy_csv_path,
        degree=3,
        dependent_variable='target_variable'
    )

    if results_degree_3:
        print("\nModel Coefficients:")
        # Get feature names after polynomial transformation
        feature_names_poly_3 = results_degree_3["polynomial_features_transformer"].get_feature_names_out(
            ['feature_1', 'feature_2'] # Pass original feature names
        )
        for i, coef in enumerate(results_degree_3["model"].coef_):
            print(f"  {feature_names_poly_3[i]}: {coef:.4f}")
        print(f"  Intercept: {results_degree_3['model'].intercept_:.4f}")

