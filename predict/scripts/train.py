from sklearn.preprocessing import StandardScaler, OrdinalEncoder
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from joblib import dump
import pandas as pd
import numpy as np


def train_model(data_path, model_type="decision_tree"):
    """
    Train a machine learning model (Decision Tree or Random Forest) on the given dataset using Ordinal Encoding.

    Args:
        data_path (str): Path to the dataset CSV file.
        model_type (str): Type of model to train ("decision_tree" or "random_forest").

    Returns:
        None
    """
    # Load data
    data = pd.read_csv(data_path)
    target_column = "Expected_Joining_Score"
    X = data.drop(columns=[target_column])
    y = data[target_column]

    # Separate categorical and numerical columns
    categorical_columns = X.select_dtypes(include=["object"]).columns
    numerical_columns = X.select_dtypes(include=["int64", "float64"]).columns

    # Preprocess categorical data using Ordinal Encoder
    encoder = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)
    X_categorical = encoder.fit_transform(X[categorical_columns])

    # Preprocess numerical data using Standard Scaler
    scaler = StandardScaler()
    X_numerical = scaler.fit_transform(X[numerical_columns])

    # Combine preprocessed features
    X_processed = np.hstack((X_categorical, X_numerical))

    # Split into train-test sets
    X_train, X_test, y_train, y_test = train_test_split(X_processed, y, test_size=0.2, random_state=42)

    # Select model type
    if model_type == "decision_tree":
        model = DecisionTreeRegressor(max_depth=10, random_state=42)
        model_name = "decision_tree_model.joblib"
    elif model_type == "random_forest":
        model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
        model_name = "random_forest_model.joblib"
    else:
        raise ValueError("Invalid model type. Choose 'decision_tree' or 'random_forest'.")

    # Train the model
    model.fit(X_train, y_train)

    # Save the model, scaler, and encoder
    dump(model, f"models/{model_name}")
    dump(scaler, "models/scaler.joblib")
    dump(encoder, "models/encoder.joblib")
    print(f"{model_type.replace('_', ' ').capitalize()} model, scaler, and encoder saved successfully.")

    # Evaluate the model
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    print(f"Mean Absolute Error: {mae:.2f}")


# Example Usage
if __name__ == "__main__":
    # Train Decision Tree
    train_model(data_path="data/weighted_candidate_data_updated.csv", model_type="decision_tree")

    # Train Random Forest
    train_model(data_path="data/weighted_candidate_data_updated.csv", model_type="random_forest")
