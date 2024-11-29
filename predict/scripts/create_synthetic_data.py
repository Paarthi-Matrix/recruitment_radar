import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Define synthetic data parameters
locations = ['Madanapalle', 'Munger', 'Darbhanga', 'Chennai', 'Bangalore', 'Hyderabad', 'Mumbai', 'Delhi', 'Kolkata', 'Pune']
roles = ['Software Engineer', 'Analyst', 'Data Scientist', 'Project Manager', 'Consultant']
seniority_levels = ['Entry-Level', 'Mid-Level', 'Senior-Level', 'Lead']
education_levels = ['Diploma', 'Bachelor\'s Degree', 'Master\'s Degree', 'PhD']
skills = ['Java, Spring Boot', 'Python, SQL, ML', 'JavaScript, React', 'C++, Algorithms', 'AWS, Docker, Kubernetes']
certifications = ['AWS Certified', 'Scrum Master', 'None', 'PMP', 'Google Cloud Certified']
companies = ['HCL', 'Cognizant', 'Infosys', 'TCS', 'Accenture']
industries = ['Consulting', 'IT Services', 'Banking', 'Retail', 'Healthcare']
job_roles = ['Developer', 'Team Lead', 'Data Analyst', 'Manager']
offer_benefits = ['Health Insurance', 'Flexible Hours', 'Stock Options']
work_modes = ['Offline', 'Hybrid', 'Remote']
offer_deadlines = [datetime.today() + timedelta(days=i) for i in range(10, 60)]

# Generate synthetic data
np.random.seed(42)
data = {
    "Candidate_Location": np.random.choice(locations, 5000),
    "Distance_From_Job_Location (km)": np.random.randint(5, 50, 5000),
    "Cost_of_Living_Area": np.random.choice(['Low', 'Medium', 'High'], 5000),
    "Current_Role": np.random.choice(roles, 5000),
    "Seniority_Level": np.random.choice(seniority_levels, 5000),
    "Experience_Years": np.random.randint(1, 15, 5000),
    "Current_Salary (INR)": np.random.randint(300000, 2000000, 5000),
    "Expected_Salary (INR)": np.random.randint(400000, 2500000, 5000),
    "Education_Qualification": np.random.choice(education_levels, 5000),
    "Relevant_Skills": np.random.choice(skills, 5000),
    "Certifications": np.random.choice(certifications, 5000),
    "Notice_Period (Days)": np.random.randint(0, 90, 5000),
    "Planned_Leaves": np.random.randint(0, 15, 5000),
    "Shift_Preference": np.random.choice(['Day', 'Night', 'Flexible'], 5000),
    "Service_Bond_Acceptance": np.random.choice(['Yes', 'No'], 5000),
    "Work_Mode_Preference": np.random.choice(work_modes, 5000),
    "Current_Company_Name": np.random.choice(companies, 5000),
    "Current_Company_Industry": np.random.choice(industries, 5000),
    "Current_Company_Brand_Perception": np.random.choice(['Positive', 'Neutral', 'Negative'], 5000),
    "Job_Hopping_History (Years)": np.random.randint(0, 10, 5000),
    "Technology_Fit": np.random.choice(['Low', 'Moderate', 'High'], 5000),
    "Offered_Salary (INR)": np.random.randint(400000, 3000000, 5000),
    "Salary_Difference (INR)": np.random.randint(10000, 500000, 5000),
    "Salary_Competitiveness": np.random.choice(['Below Average', 'Average', 'Above Average'], 5000),
    "Offered_Position_Level": np.random.choice(seniority_levels, 5000),
    "Offered_Job_Role": np.random.choice(job_roles, 5000),
    "Job_Location": np.random.choice(locations, 5000),
    "Relocation_Required": np.random.choice(['Yes', 'No'], 5000),
    "Benefits_Package": np.random.choice(offer_benefits, 5000),
    "Career_Growth_Opportunities": np.random.choice(['Limited', 'Moderate', 'Excellent'], 5000),
    "Job_Security": np.random.choice(['Weak', 'Stable', 'Strong'], 5000),
    "Offer_Company_Brand_Value": np.random.choice(['Low', 'Moderate', 'High'], 5000),
    "Offer_Validity_Date": np.random.choice(offer_deadlines, 5000),
    "Offer_Letter_Clarity": np.random.choice(['Clear', 'Ambiguous'], 5000),
    "Expected_Joining_Score" :  np.random.randint(1, 1000, 5000)
}

df = pd.DataFrame(data)

# Assign weights and calculate Expected Joining Score
def calculate_joining_score(row):
    score = row['Expected_Joining_Score']
    score += 100 - row["Distance_From_Job_Location (km)"] * 2  # Closer is better
    score += row["Offered_Salary (INR)"] / 30000  # Higher salary is better
    score += 100 if row["Relocation_Required"] == "No" else -50
    score += {"Limited": 30, "Moderate": 60, "Excellent": 100}[row["Career_Growth_Opportunities"]]
    score += {"Weak": 20, "Stable": 60, "Strong": 100}[row["Job_Security"]]
    score = np.clip(score, 1, 1000)
    return score

df["Expected_Joining_Score"] = df.apply(calculate_joining_score, axis=1)

# Save to CSV
csv_path = 'data/weighted_candidate_data_updated.csv'
df.to_csv(csv_path, index=False)

print('Synthetic data created...')