import pandas as pd

def get_weightage(company, numerical_columns, categorical_columns):


    # Define the list of factors and their default weights
    factors = [
        'Candidate_Location', 'Distance_From_Job_Location (km)', 'Cost_of_Living_Area',
        'Current_Role', 'Seniority_Level', 'Experience_Years', 'Current_Salary (INR)',
        'Expected_Salary (INR)', 'Education_Qualification', 'Relevant_Skills',
        'Certifications', 'Notice_Period (Days)', 'Planned_Leaves', 'Shift_Preference',
        'Service_Bond_Acceptance', 'Work_Mode_Preference', 'Current_Company_Name',
        'Current_Company_Industry', 'Current_Company_Brand_Perception', 'Job_Hopping_History (Years)',
        'Technology_Fit', 'Offered_Salary (INR)', 'Salary_Difference (INR)', 'Salary_Competitiveness',
        'Offered_Position_Level', 'Offered_Job_Role', 'Job_Location', 'Relocation_Required',
        'Benefits_Package', 'Career_Growth_Opportunities', 'Job_Security', 'Offer_Company_Brand_Value',
        'Offer_Validity_Date', 'Offer_Letter_Clarity'
    ]

   
    # Create the DataFrame
    factor_weightage_df = pd.DataFrame({
        'Factor': factors,
        'Company_A': [1, 1, 1, 1, 1, 0.1, 0.1, 0.1, 0.1, 0.1, 
                      0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 
                      0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 
                      0.1, 0.1, 0.1, 0.1, ],

        'Company_B': [0.1, 0.1, 0.1, 1, 1, 0.1, 1, 1, 1, 1, 
                      0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 
                      0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 
                      0.1, 0.1, 0.1, 0.1, ],
    }).set_index('Factor')

    # View the DataFrame
    # print(factor_weightage_df)

    numerical_weights = factor_weightage_df[company][numerical_columns].values
    categorical_weights = factor_weightage_df[company][categorical_columns].values

    return numerical_weights, categorical_weights



if __name__ == '__main__':
    weightage = get_weightage()