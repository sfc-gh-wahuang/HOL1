# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.ml.registry import Registry
import pandas as pd
import json
import ast

# Get the current Snowflake session
session = get_active_session()

# Function to fetch available model versions
def get_model_versions():
    model_registry = Registry(session=session, database_name='HOL1_DB', schema_name='HOL1_SCHEMA')
    versions = model_registry.get_model('CREDIT_RISK_XGBOOST').show_versions()['name'].values
    return versions

# Define the actual prediction function
def predict(single_new_data, model_version):
    # Create a list of dicts to pass into the stored procedure
    new_customer_record = [single_new_data]
    
    # Call the stored procedure directly using session.call(), passing the selected model version
    result = session.call("sproc_predict_new_customer", new_customer_record, 'HOL1_DB', 'HOL1_SCHEMA', 'CREDIT_RISK_XGBOOST', 'PREDICTION_RESULTS', model_version)
    
    # Retrieve the prediction history for the customer from the PREDICTION_RESULTS table
    customer_id = single_new_data['ID']
    prediction_history_query = f"""
    SELECT ID, MODEL_VERSION, PREDICTION 
    FROM PREDICTION_RESULTS 
    WHERE ID = {customer_id}
    """

    result = ast.literal_eval(result)

    if result[str(customer_id)] == 0:
        msg = "Customer has low risk"
    elif result[str(customer_id)] == 1:
        msg = "Customer is risky, do NOT approve the credit card"
    
    # Execute the query to get the prediction history
    history_result = session.sql(prediction_history_query).to_pandas()
    
    return msg, history_result

# Predefined options for categorical columns
categorical_options = {
    'CODE_GENDER': ['M', 'F'],
    'FLAG_OWN_CAR': ['N', 'Y'],
    'FLAG_OWN_REALTY': ['Y', 'N'],
    'NAME_INCOME_TYPE': ['Working', 'Commercial associate', 'Pensioner', 'Student', 'State servant'],
    'NAME_EDUCATION_TYPE': ['Academic degree', 'Higher education', 'Incomplete higher', 'Secondary / secondary special', 'Lower secondary'],
    'NAME_FAMILY_STATUS': ['Single / not married', 'Widow', 'Married', 'Separated', 'Civil marriage'],
    'NAME_HOUSING_TYPE': ['Office apartment', 'Municipal apartment', 'Rented apartment', 'Co-op apartment', 'House / apartment', 'With parents'],
    'OCCUPATION_TYPE': ['IT staff', 'Low-skill Laborers', 'Waiters/barmen staff', 'Cooking staff', 'None', 'Sales staff', 'High skill tech staff', 'Private service staff', 'Medicine staff', 'Security staff', 'Secretaries', 'Accountants', 'Laborers', 'Realty agents', 'Drivers', 'Managers', 'Cleaning staff', 'HR staff', 'Core staff', 'None']
}

# Streamlit app
st.title("Credit Risk Prediction")

# Input fields for the user to enter data
ID = st.number_input("ID", value=5008804)
CODE_GENDER = st.selectbox("Gender", categorical_options['CODE_GENDER'])
FLAG_OWN_CAR = st.selectbox("Owns Car?", categorical_options['FLAG_OWN_CAR'])
FLAG_OWN_REALTY = st.selectbox("Owns Realty?", categorical_options['FLAG_OWN_REALTY'])
CNT_CHILDREN = st.number_input("Number of Children", value=0)
AMT_INCOME_TOTAL = st.number_input("Total Income", value=427500.0)
NAME_INCOME_TYPE = st.selectbox("Income Type", categorical_options['NAME_INCOME_TYPE'])
NAME_EDUCATION_TYPE = st.selectbox("Education Type", categorical_options['NAME_EDUCATION_TYPE'])
NAME_FAMILY_STATUS = st.selectbox("Family Status", categorical_options['NAME_FAMILY_STATUS'])
NAME_HOUSING_TYPE = st.selectbox("Housing Type", categorical_options['NAME_HOUSING_TYPE'])
DAYS_BIRTH = st.number_input("Days since Birth (Negative Value)", value=-12005)
DAYS_EMPLOYED = st.number_input("Days Employed (Negative Value)", value=-4542)
FLAG_MOBIL = st.selectbox("Mobile Flag", [0, 1])
FLAG_WORK_PHONE = st.selectbox("Work Phone Flag", [0, 1])
FLAG_PHONE = st.selectbox("Phone Flag", [0, 1])
FLAG_EMAIL = st.selectbox("Email Flag", [0, 1])
OCCUPATION_TYPE = st.selectbox("Occupation Type", categorical_options['OCCUPATION_TYPE'])
CNT_FAM_MEMBERS = st.number_input("Number of Family Members", value=2)

# Fetch the list of available model versions
model_versions = get_model_versions()

# Select model version
selected_model_version = st.selectbox("Select Model Version", model_versions)

# Convert input data into a dictionary
single_new_data = {
    "ID": ID,
    "CODE_GENDER": CODE_GENDER,
    "FLAG_OWN_CAR": FLAG_OWN_CAR,
    "FLAG_OWN_REALTY": FLAG_OWN_REALTY,
    "CNT_CHILDREN": CNT_CHILDREN,
    "AMT_INCOME_TOTAL": AMT_INCOME_TOTAL,
    "NAME_INCOME_TYPE": NAME_INCOME_TYPE,
    "NAME_EDUCATION_TYPE": NAME_EDUCATION_TYPE,
    "NAME_FAMILY_STATUS": NAME_FAMILY_STATUS,
    "NAME_HOUSING_TYPE": NAME_HOUSING_TYPE,
    "DAYS_BIRTH": DAYS_BIRTH,
    "DAYS_EMPLOYED": DAYS_EMPLOYED,
    "FLAG_MOBIL": FLAG_MOBIL,
    "FLAG_WORK_PHONE": FLAG_WORK_PHONE,
    "FLAG_PHONE": FLAG_PHONE,
    "FLAG_EMAIL": FLAG_EMAIL,
    "OCCUPATION_TYPE": OCCUPATION_TYPE,
    "CNT_FAM_MEMBERS": CNT_FAM_MEMBERS
}

# Button to trigger prediction
if st.button("Predict"):
    # Pass the input data and selected model version to the prediction function and display the result and history
    prediction, history = predict(single_new_data, selected_model_version)
    
    if prediction is not None:
        st.write(prediction)
    
    if history is not None:
        st.write("Prediction History")
        st.dataframe(history)
