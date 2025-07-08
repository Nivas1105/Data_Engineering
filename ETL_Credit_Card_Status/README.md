# Credit Card Approval Prediction ETL Pipeline
# Overview
This project involves building an ETL (Extract, Transform, Load) pipeline to process and analyze credit card approval data. The goal is to automate the extraction of raw data, transform it for analysis, and load it into AWS S3. The project also includes SQL-based analysis using AWS Athena and data visualization with Tableau.

# Table of Contents
1. Project Overview
2. Dataset
3. Technologies Used
4. Steps to Reproduce
5. ETL Pipeline
6. Athena SQL Analysis
7. Visualization
8. Results

# Dataset
The dataset used in this project is taken from Kaggle: https://www.kaggle.com/datasets/rikdifos/credit-card-approval-prediction 

### Credit Card Approval Prediction

This dataset contains various attributes of credit card applicants, including demographic information, financial features, and the approval status. The target variable is whether the application was approved (1) or denied (0).

# Key Features:
 - Applicant_ID: Unique identifier for each applicant
 - Applicant_Gender: Gender of the applicant
 - Owned_Car: Whether the applicant owns a car 
 - Owned_Realty: Whether the applicant owns real estate 
 - Total_Children: Total number of children the applicant has
 - Total_Income: Annual income of the applicant
 - Income_Type: Type of income
 - Education_Type: Education level of the applicant
 - Family_Status: Family status of the applicant
 - Housing_Type: Type of housing the applicant lives in
 - Owned_Mobile_Phone: Whether the applicant owns a mobile phone 
 - Owned_Work_Phone: Whether the applicant owns a work phone 
 - Owned_Phone: Whether the applicant owns a phone 
 - Owned_Email: Whether the applicant owns an email address 
 - Job_Title: The job title or occupation of the applicant
 - Total_Family_Members: Total number of family members in the household
 - Applicant_Age: Age of the applicant
 - Years_of_Working: Number of years the applicant has been working
 - Total_Bad_Debt: Total amount of bad debt the applicant has
 - Total_Good_Debt: Total amount of good debt the applicant has
 - Status: Whether the application was approved (1) or denied (0)

# Technologies Used
 - Python (for ETL pipeline, data processing, and automation)
 - AWS (S3, Athena, EC2, AWS Secrets Manager)
 - Apache Airflow (for orchestration and automation of the ETL pipeline)
 - Tableau (for data visualization)
 - SQL (for querying data in Athena)

# Steps to Reproduce
### Step 1: Create GCP Bucket and Set up Credentials
Set up a Google Cloud Platform (GCP) bucket to store the data.
Generate GCP credentials using a service account and save the credentials JSON file securely in AWS Secrets Manager for secure access.

### Step 2: ETL Pipeline
Set up an EC2 instance on AWS to run the ETL pipeline.

Install Apache Airflow and required dependencies for automation.

Create an Airflow DAG (Directed Acyclic Graph) to automate the ETL process:

 - Extract: Retrieve the dataset from a source .
 - Transform: Perform necessary transformations such as handling missing values, checking data types, and preprocessing for analysis.
 - Load: Load the transformed data into an S3 bucket in CSV format for further analysis and storage.
Example code for creating a table in Athena from the CSV file:

### SQL EG:
create_table_query = f"""
    CREATE EXTERNAL TABLE IF NOT EXISTS {DATABASE_NAME}.{TABLE_NAME} (
        {columns_schema}
    )
    ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
    WITH SERDEPROPERTIES (
        "separatorChar" = ",",
        "quoteChar" = "\""
    )
    STORED AS TEXTFILE
    LOCATION '{S3_OUTPUT_LOCATION}'
    TBLPROPERTIES ("skip.header.line.count" = "1");
"""

### Step 3: Athena SQL Analysis
Use Apache Airflow to dynamically create the Athena table and database by reading the CSV file columns.
Write SQL queries in Athena to explore and analyze the credit card approval data. The queries can focus on various aspects, such as:
Trends in approval based on demographic features
Distribution of applicants by income, age, and other factors

### Step 4: Data Visualization
Install the Athena ODBC driver and configure Tableau to connect to Athena.
Import the database and tables into Tableau.
Use Tableau's Custom SQL option to execute SQL queries and visualize the results.
Create various visualizations, such as:
Approval rates based on demographic and financial factors
Pie charts for categorical data 
Trend analysis based on applicant age and income

### Step 5: Create Dashboards
Combine individual visualizations into a cohesive dashboard to provide insights into the dataset.
Dashboards can include visualizations like:
Approval rate by income level and age group
Distribution of applicants by job title, family status, and housing type

# Results
The ETL pipeline successfully extracted, transformed, and loaded the data into AWS S3.
SQL queries performed in Athena helped uncover insights
