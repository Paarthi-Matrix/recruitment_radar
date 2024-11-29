import shap
from joblib import load
import numpy as np
import pandas as pd
from factor_weightage import get_weightage

def align_columns_with_original_values(original_data, livedata):
    # Identify columns missing in livedata
    missing_columns = set(original_data.columns) - set(livedata.columns)
    
    # Add missing columns with corresponding values from original_data
    for col in missing_columns:
        livedata[col] = original_data[col]
    
    # Reorder columns to match original_data
    livedata = livedata[original_data.columns]
    
    return livedata

def split_data(original_data):
    """
    Splits the original data into numerical and categorical features.
    
    Args:
        original_data (pd.DataFrame): The full dataset containing both numerical and categorical features.
    
    Returns:
        numerical_data (np.array): Numerical feature values.
        categorical_data (np.array): Categorical feature values.
        numerical_columns (Index): Column names for numerical data.
        categorical_columns (Index): Column names for categorical data.
    """
    # Separate categorical and numerical columns
    categorical_columns = original_data.select_dtypes(include=["object"]).columns
    numerical_columns = original_data.select_dtypes(include=["int64", "float64"]).columns
    
    # Extract numerical and categorical data
    numerical_data = original_data[numerical_columns].values
    categorical_data = original_data[categorical_columns].values
    
    return numerical_data, categorical_data, numerical_columns, categorical_columns


def predict_with_weights_rf(model_path, numerical_data, categorical_data, numerical_weights, categorical_weights, numerical_columns, categorical_columns):
    """
    Perform inference using a saved Random Forest model with feature weightage.

    Args:
        model_path (str): Path to the saved Random Forest model file.
        numerical_data (np.array): Array of numerical feature values.
        categorical_data (np.array): Array of categorical feature values.
        numerical_weights (list): List of weights for numerical features.
        categorical_weights (list): List of weights for categorical features.

    Returns:
        float: Predicted joining score.
        np.array: SHAP values for each feature.
    """
    # Load the saved model, scaler, and encoder
    model = load(model_path)
    scaler = load("models/scaler.joblib")
    encoder = load("models/encoder.joblib")
    
    # Preprocess categorical features (one-hot encoding)
    categorical_encoded = encoder.transform(pd.DataFrame(categorical_data, columns=categorical_columns))
    
    # Scale numerical features
    numerical_scaled = scaler.transform(pd.DataFrame(numerical_data, columns=numerical_columns))
    
    # Apply feature weightage
    weighted_numerical = numerical_scaled * np.array(numerical_weights)
    weighted_categorical = categorical_encoded * np.array(categorical_weights)
    
    # Combine weighted features
    features = np.hstack([weighted_categorical, weighted_numerical])
    
    # Initialize SHAP Explainer
    explainer = shap.TreeExplainer(model)
    
    # Calculate SHAP values for the features
    shap_values = explainer.shap_values(features)
    
    # Perform prediction
    prediction = model.predict(features)[0]  # Extract single prediction
    
    return prediction, shap_values


def get_top_factors(shap_values, all_columns):
    """
    Get the top 10 factors that influenced the model decision based on SHAP values.

    Args:
        shap_values (np.array): Array of SHAP values for each feature.
        all_columns (list): List of all feature names (numerical and categorical).

    Returns:
        pd.DataFrame: Top 10 factors with their corresponding SHAP values.
    """
    # Summing up the absolute SHAP values to get overall importance
    shap_importances = np.abs(shap_values).mean(axis=0)
    
    # Create a DataFrame with features and their importance
    feature_df = pd.DataFrame({
        'Feature': all_columns,
        'SHAP Importance': shap_importances
    })
    
    # Sort by importance in descending order and take the top 10
    feature_df = feature_df.sort_values(by='SHAP Importance', ascending=False).head(10)
    
    return feature_df


def predict(company, data):

    # Split data into numerical and categorical
    numerical_data, categorical_data, numerical_columns, categorical_columns = split_data(data)

    numerical_weights, categorical_weights = get_weightage(company, numerical_columns, categorical_columns)

    # Predict using Random Forest model and get SHAP values
    predicted_scores = []
    shap_values_list = []
    
    for i in range(len(data)):  # Loop over each example
        # Predict and get SHAP values for the i-th example
        predicted_score, shap_values = predict_with_weights_rf(
            model_path="models/random_forest_model.joblib",
            numerical_data=numerical_data[i:i+1],  # Keep one row at a time
            categorical_data=categorical_data[i:i+1],  # Keep one row at a time
            numerical_weights=numerical_weights,
            categorical_weights=categorical_weights,
            numerical_columns=numerical_columns,
            categorical_columns=categorical_columns
        )

        predicted_scores.append(predicted_score)
        shap_values_list.append(shap_values)
    
    encoder = load("models/encoder.joblib")
  
    # Combine numerical and categorical columns
    all_columns = np.array(numerical_columns.tolist() + encoder.get_feature_names_out(categorical_columns).tolist())
    
    summaries = []
    for i, shap_values in enumerate(shap_values_list):
        # Get the top 10 factors influencing the model decision based on SHAP for each input
        top_factors = get_top_factors(shap_values, all_columns)  # shap_values[1] for class 1 (for binary classification)

        summary = ",".join(list(top_factors['Feature']))   
        summary = summary.replace('_', ' ')    
        summary = "The predicted score is arrived based on " + summary + "."

        summaries.append(summary)
    

    result = pd.DataFrame({
        'Expected_Joining_Score' : predicted_scores,
        'Summary' : summaries
    })

    return result
    

def inference(company, livedata):

    # Original Data with multiple rows
    original_data = pd.DataFrame({
        'Candidate_Location': ['Mumbai', 'Delhi'],
        'Distance_From_Job_Location (km)': [45, 31],
        'Cost_of_Living_Area': ['High', 'Medium'],
        'Current_Role': ['Analyst', 'Consultant'],
        'Seniority_Level': ['Entry-Level', 'Senior-Level'],
        'Experience_Years': [9, 5],
        'Current_Salary (INR)': [1267561, 648688],
        'Expected_Salary (INR)': [1255080, 2496952],
        'Education_Qualification': ['Master\'s Degree', 'PhD'],
        'Relevant_Skills': ['C++, Algorithms', 'Python, SQL, ML'],
        'Certifications': ['PMP', 'Scrum Master'],
        'Notice_Period (Days)': [10, 59],
        'Planned_Leaves': [14, 4],
        'Shift_Preference': ['Flexible', 'Flexible'],
        'Service_Bond_Acceptance': ['No', 'No'],
        'Work_Mode_Preference': ['Remote', 'Remote'],
        'Current_Company_Name': ['Cognizant', 'Accenture'],
        'Current_Company_Industry': ['Retail', 'IT Services'],
        'Current_Company_Brand_Perception': ['Negative', 'Neutral'],
        'Job_Hopping_History (Years)': [2, 8],
        'Technology_Fit': ['Moderate', 'Low'],
        'Offered_Salary (INR)': [2124620, 436382],
        'Salary_Difference (INR)': [146611, 345689],
        'Salary_Competitiveness': ['Above Average', 'Above Average'],
        'Offered_Position_Level': ['Senior-Level', 'Mid-Level'],
        'Offered_Job_Role': ['Developer', 'Data Analyst'],
        'Job_Location': ['Madanapalle', 'Bangalore'],
        'Relocation_Required': ['Yes', 'No'],
        'Benefits_Package': ['Stock Options', 'Stock Options'],
        'Career_Growth_Opportunities': ['Excellent', 'Limited'],
        'Job_Security': ['Stable', 'Strong'],
        'Offer_Company_Brand_Value': ['High', 'High'],
        'Offer_Validity_Date': ['12/31/2024 14:11', '1/12/2025 14:11'],
        'Offer_Letter_Clarity': ['Ambiguous', 'Clear'],
    })


    livedata_aligned = align_columns_with_original_values(original_data, livedata)
    result = predict(company, livedata_aligned)

    return result

    

# Example usage with actual input
if __name__ == "__main__":
    
    livedata = pd.DataFrame({
        'Candidate_Location': ['Mumbai', 'Delhi'],
        'Distance_From_Job_Location (km)': [45, 31],
        'Cost_of_Living_Area': ['High', 'Medium'],
        'Current_Role': ['Analyst', 'Consultant'],
        'Seniority_Level': ['Entry-Level', 'Senior-Level'],
        'Experience_Years': [9, 5],
        'Current_Salary (INR)': [1267561, 648688],
        'Expected_Salary (INR)': [1255080, 2496952],
        'Education_Qualification': ['Master\'s Degree', 'PhD'],
        'Relevant_Skills': ['C++, Algorithms', 'Python, SQL, ML'],
        'Certifications': ['PMP', 'Scrum Master'],
        'Notice_Period (Days)': [10, 59],
        'Planned_Leaves': [14, 4],
    })

    company = 'Company_A'
    result = inference(company, livedata)

    print(result)

