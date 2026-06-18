import pandas as pd
import numpy as np
from sqlalchemy import create_engine

df_patients = pd.read_csv('patients.csv')
df_appointments = pd.read_csv('appointments.csv')
df_clinics = pd.read_csv("clinics.csv")

print("\nSimulating real-world omissions (Missing Demographics)...")

gender_col = 'gender' 
insurance_col = 'insurance_type'
age_col = "age"

#error injection 
gender_missing_indices = df_patients.sample(n=50, random_state=42).index
df_patients.loc[gender_missing_indices, gender_col] = np.nan

print(df_patients.isnull().sum())


insurance_missing_indices = df_patients.sample(n=50, random_state=24).index
df_patients.loc[insurance_missing_indices, insurance_col] = np.nan

print(df_patients.isnull().sum())



print(f" We have {df_patients["gender"].isnull().sum()} missing values in the gender column")

print(f" We have {df_patients["insurance_type"].isnull().sum()} in the insurance_type column")

gender_mode = df_patients["gender"].mode()[0]
insurance_mode = df_patients["insurance_type"].mode()[0]

if df_patients["gender"].isnull().sum() > 0:
    df_patients["gender"] = df_patients["gender"].fillna(gender_mode)
    print("Replaced gender missing columns with mode of the column.")

print(df_patients["gender"].isnull().sum())

if df_patients["insurance_type"].isnull().sum() > 0:
    df_patients["insurance_type"] = df_patients["insurance_type"].fillna(gender_mode)
    print("Replaced insurance type missing columns with the mode of the column.")



print(df_patients["insurance_type"].isnull().sum())

age_missing_indices = df_patients.sample(n=50, random_state=42).index
df_patients.loc[age_missing_indices, age_col] = np.nan

print(f"We have {df_patients["age"].isnull().sum()} missing values in the age column")

if df_patients["age"].isnull().sum() > 0:
    df_patients["age"] = df_patients["age"].fillna(df_patients.groupby("insurance_type")["age"].transform("mean"))
    df_patients["age"] = df_patients["age"].round(0).astype(int)
    print("No more missing values in the age column!")
    
print(df_patients["age"].isnull().sum())


# data quality check to catch invalid / outlying data


# patients data validation 

invalid_ages = df_patients[(df_patients["age"]<0) | (df_patients["age"] > 120)]
print(invalid_ages.empty)

if not invalid_ages.empty:
    print(f" There are {len(invalid_ages)} rows with an invalid age number.")
    print(invalid_ages.head())


    median_age = df_patients["age"].median()
    df_patients["age"] = df_patients["age"].apply(lambda x: median_age if x>120 else (0 if x<0 else x) )

    print("Patient data is validated and cleaned the invalid parts.")

else:
    print("Patients data passed validity and data quality check.")





revenue_col = "revenue_realized"

negative_revenue = df_appointments[df_appointments[revenue_col]<0]

print(negative_revenue.empty)

if not negative_revenue.empty:
    print(f"There are {len(negative_revenue)} rows with negative invalid revenue amounts.")
    df_appointments[revenue_col] = df_appointments[revenue_col].abs()
    print(" The revenue column has cleaned and is now valid")




# clinics data validation and quality check.

# finding any missing values

print(f" missing values in the clinics dataset are the following\n {df_clinics.isnull().sum()} .")
print(f"Missing values in total: {df_clinics.isnull().sum().sum()}")


# invalid value check and dealing with it


print("\n Running Clinics Data Quality Check")

# Checking Primary Key Constraints (clinic_id)


duplicate_clinics = df_clinics[df_clinics.duplicated(subset = ["clinic_id"])]

missing_clinic_ids = df_clinics["clinic_id"].isnull().sum()


if missing_clinic_ids>0 or not duplicate_clinics.empty:
    print("There are duplicate ids for the clinics primary keys(ids).")
    if missing_clinic_ids>0:
        df_clinics = df_clinics.dropna(subset = ["clinic_id"])

    if not duplicate_clinics.empty:
        df_clinics = df_clinics.drop_duplicates(subset = ["clinic_id"])
    print("The data is cleaned")



# numeric values validation
# we loop through all financial and operational metrics to catch negative/zero anomalies

numeric_columns = [
    "monthly_fixed_cost",
    "number_of_doctors",
    "avg_daily_capacity",
    "monthly_marketing_spend"

]

for col in numeric_columns:
    invalid_rows = df_clinics[df_clinics[col] <= 0]

    if not invalid_rows.empty:
        print(f"There are {len(invalid_rows)}  invalid (less than 0) entries in {col}")

        # replace invalid values with column's median

        col_median = df_clinics[col].median()
        df_clinics[col] = df_clinics[col].apply(lambda x: col_median if x<=0 else x)

print("Clinics data is validated and cleaned!")



print(" Data quality check, validation and cleaning is complete!.")


database_url = "postgresql://postgres:nel1ush2ik@localhost:5432/clinic_db"


try:
    print("Connecting to PostgreSQL")
    engine = create_engine(database_url)
    df_patients.to_sql(name = "patients", con  = engine, if_exists = "replace", index = False )
    df_clinics.to_sql(name = "clinics", con = engine, if_exists = "replace", index = False )
    df_appointments.to_sql(name = "appointments", con = engine, if_exists = "replace", index = False )
    print("All data is uploaded to PostgreSQL!")

except Exception as e:
    print("Failed to load data into PostgreSQL.")

# connection to postgresql
