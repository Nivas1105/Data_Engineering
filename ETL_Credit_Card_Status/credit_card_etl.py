from airflow import DAG
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
import pandas as pd
import boto3
import json
import os
import logging
from google.cloud import storage

# Configuration
AWS_SECRET_NAME = ""
AWS_REGION_NAME = "us-east-1"
GCS_BUCKET_NAME = "data_source_project"
S3_FINAL_BUCKET = "mysitebucketuta"
GCS_SOURCE_FILE = "Application_Data.csv"
S3_OUTPUT_LOCATION = f"s3://{S3_FINAL_BUCKET}/transformed_data/"
DATABASE_NAME = "credit_card_approval_status"
TABLE_NAME = "applicant_details"
ATHENA_QUERY_OUTPUT = f"s3://{S3_FINAL_BUCKET}/athena-query-results/"

# Default DAG arguments
default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
    'retries': 1,
}


# Function to fetch GCP credentials from AWS Secrets Manager
def get_gcp_credentials():
    """Fetch GCP service account credentials from AWS Secrets Manager."""
    client = boto3.client("secretsmanager", region_name=AWS_REGION_NAME)
    secret_value = client.get_secret_value(SecretId=AWS_SECRET_NAME)
    secret_data = json.loads(secret_value['SecretString'])

    # Replace \\n with actual newline characters in the private key
    if 'private_key' in secret_data:
        secret_data['private_key'] = secret_data['private_key'].replace('\\n', '\n')

    return secret_data


# Initialize DAG
with DAG(
        dag_id="gcs_to_s3_data_pipeline_with_secrets",
        default_args=default_args,
        schedule_interval=None,
        catchup=False,
        tags=['data_pipeline', 'GCS', 'S3', 'Athena', 'SecretsManager'],
) as dag:
    def list_gcs_files(**kwargs):
        """List files in the GCS bucket."""
        credentials = get_gcp_credentials()

        # Write credentials to a temporary file
        service_account_file = "/tmp/gcp_service_account.json"
        with open(service_account_file, "w") as f:
            json.dump(credentials, f)

        # Authenticate and list files in the GCS bucket
        client = storage.Client.from_service_account_json(service_account_file)
        bucket = client.get_bucket(GCS_BUCKET_NAME)
        blobs = bucket.list_blobs()
        print(f"Files in bucket '{GCS_BUCKET_NAME}':")
        for blob in blobs:
            print(f"Name: {blob.name}, Size: {blob.size} bytes, Updated: {blob.updated}")
            # Download the file to /tmp with the same name as the GCS object
            download_path = os.path.join("/tmp", blob.name)

            # Ensure that the directory exists before downloading
            os.makedirs(os.path.dirname(download_path), exist_ok=True)

            blob.download_to_filename(download_path)
            print(f"Downloaded {blob.name} to {download_path}")


    def transform_data(**kwargs):
        """Reads, transforms data, and writes back to a temporary file."""
        # Path to temporary file in MWAA environment
        tmp_file_path = f"/tmp/{GCS_SOURCE_FILE}"

        # Read CSV file into a DataFrame
        df = pd.read_csv(tmp_file_path)

        # Strip whitespace and handle nulls
        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

        # Infer data types
        data_types = {col: str(df[col].dtype) for col in df.columns}

        # Save transformed data
        transformed_file_path = "/tmp/transformed_data.csv"
        df.to_csv(transformed_file_path, index=False)

        # Pass file path to next task
        kwargs['ti'].xcom_push(key='transformed_file_path', value=transformed_file_path)


    # Task: List files in GCS bucket
    list_files_task = PythonOperator(
        task_id='list_gcs_files',
        python_callable=list_gcs_files,
        provide_context=True,
    )

    # Task: Transform data
    transform_data_task = PythonOperator(
        task_id='transform_data',
        python_callable=transform_data,
        provide_context=True,
    )


    # Task: Upload transformed data to S3
    def upload_to_s3(**kwargs):
        transformed_file_path = kwargs['ti'].xcom_pull(key='transformed_file_path')
        S3Hook().load_file(
            filename=transformed_file_path,
            key="transformed_data.csv",
            bucket_name=S3_FINAL_BUCKET,
            replace=True,
        )


    upload_to_s3_task = PythonOperator(
        task_id='upload_to_s3',
        python_callable=upload_to_s3,
        provide_context=True,
    )


    # Create Athena Db and Table

    def athena_table_creation(**kwargs):
        """Creates an Athena database and table for the dataset."""
        transformed_file_path = kwargs['ti'].xcom_pull(key='transformed_file_path')
        df = pd.read_csv(transformed_file_path)

        def map_dtype_to_athena(dtype):
            """Maps Pandas dtypes to Athena data types."""
            if "int" in dtype:
                return "BIGINT"
            elif "float" in dtype:
                return "DOUBLE"
            elif "object" in dtype:
                return "STRING"
            elif "datetime" in dtype:
                return "TIMESTAMP"
            elif "bool" in dtype:
                return "BOOLEAN"
            else:
                return "STRING"

        # Get column names and their Athena-compatible data types
        columns_and_types = {col: map_dtype_to_athena(str(dtype)) for col, dtype in zip(df.columns, df.dtypes)}

        # Athena table schema
        columns_schema = ",\n".join([f"{col} {dtype}" for col, dtype in columns_and_types.items()])

        # Create database query (if the database doesn't exist)
        create_db_query = f"""
        CREATE DATABASE IF NOT EXISTS {DATABASE_NAME};
        """

        # Create table query
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

        # Initialize logging
        logging.basicConfig(level=logging.INFO)

        # Run Athena query to create the database
        athena_client = boto3.client('athena')

        try:
            # First, create the database
            logging.info("Executing query to create database...")
            db_response = athena_client.start_query_execution(
                QueryString=create_db_query,
                ResultConfiguration={'OutputLocation': ATHENA_QUERY_OUTPUT},
            )
            logging.info(f"Database creation query started, execution ID: {db_response['QueryExecutionId']}")

            # Then, create the table
            logging.info("Executing query to create table...")
            table_response = athena_client.start_query_execution(
                QueryString=create_table_query,
                ResultConfiguration={'OutputLocation': ATHENA_QUERY_OUTPUT},
            )
            logging.info(f"Table creation query started, execution ID: {table_response['QueryExecutionId']}")

        except Exception as e:
            logging.error(f"Error occurred while creating database or table: {str(e)}")


    # Task: Create Athena table
    create_athena_table = PythonOperator(
        task_id='create_athena_table',
        python_callable=athena_table_creation,
        provide_context=True,
    )

    # Task dependencies
    list_files_task >> transform_data_task >> upload_to_s3_task >> create_athena_table