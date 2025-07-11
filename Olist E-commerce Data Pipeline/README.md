This project implements a complete, automated, and scalable data engineering pipeline on AWS. It ingests e-commerce data from the public Olist dataset, processes it using a modern ETL framework, builds a star-schema data warehouse in Amazon Redshift, and orchestrates the entire workflow. The final data model is designed to power business intelligence dashboards and analytical queries.
Project Architecture
The architecture is built on a modern, serverless-first data stack on AWS, emphasizing scalability, automation, and separation of concerns (storage, compute, and analytics).
Data Lake (Amazon S3): Serves as the central storage for raw source data (CSVs), processed data (Parquet), and ETL scripts.
ETL (AWS Glue & Apache Spark): A serverless Spark job reads the raw data, performs joins and transformations to create a denormalized star schema, and writes the results back to S3 in an optimized columnar format (Parquet).
Data Warehouse (Amazon Redshift Serverless): A high-performance, serverless data warehouse that stores the final fact and dimension tables, making them available for fast analytical queries.
Orchestration (AWS Step Functions): A serverless workflow orchestrator that automates the entire pipeline, ensuring the Glue ETL job runs before the data is loaded into Redshift. This provides robustness and error handling.
Permissions (AWS IAM): Dedicated IAM roles with least-privilege permissions are used for each service, ensuring secure access between components.
The Data Model: A Star Schema for Analytics
To optimize for fast analytical queries (the goal of a data warehouse), the original normalized source data was denormalized into a Star Schema. This model features a central fact table surrounded by descriptive dimension tables.
fct_order_items (Fact Table): A central table containing quantitative measures (price, freight_value, payment_value) and foreign keys to the dimension tables. Each row represents a single item within an order.
dim_customers (Dimension): Descriptive attributes about each unique customer.
dim_products (Dimension): Descriptive attributes about each unique product.
dim_sellers (Dimension): Descriptive attributes about each unique seller.
This model avoids complex joins at query time, drastically speeding up aggregations performed by BI tools or analysts.
Project Execution & Automation
The pipeline is fully automated using AWS Step Functions, which orchestrates the following workflow:
Start Execution: The workflow is initiated (this can be done manually or set on a schedule).
Glue ETL Job: The Step Function triggers the olist-etl-processor AWS Glue job. It waits for the job to complete successfully.
Load to Redshift: Upon successful completion of the Glue job, the Step Function executes a series of COPY commands on the Redshift Serverless cluster, loading the newly processed Parquet files from S3 into the final tables.
Learning Outcomes & Skills Demonstrated
This project showcases a range of essential data engineering skills and concepts:
Cloud Infrastructure (AWS): Proficient use of core AWS services including S3, Glue, Redshift, Step Functions, and IAM.
Big Data Processing (Apache Spark): Experience writing and executing distributed data processing jobs using PySpark within AWS Glue to handle transformations, joins, and data cleaning.
Data Warehousing:
Designed and implemented a star schema data model optimized for analytics.
Utilized Amazon Redshift for storing and querying large datasets efficiently.
Leveraged the COPY command for bulk data ingestion from a data lake.
ETL/ELT Design: Built a complete ETL pipeline, including extraction from a data lake, transformation in Spark, and loading into a data warehouse.
Data Formats: Utilized columnar storage formats like Apache Parquet for significant performance and cost savings.
Workflow Orchestration: Implemented automation and dependency management using AWS Step Functions.
SQL for Analytics: Wrote complex analytical queries to derive business insights from the final data model.
Cloud Security & Governance (IAM): Implemented security best practices by creating and managing dedicated IAM roles with specific, necessary permissions for each service, demonstrating the principle of least privilege.
Error Resolution & Real-World Debugging
A key part of this project was navigating and resolving real-world cloud permission errors, which is a critical skill for any cloud data engineer.
Challenge 1: S3 Access Denied for Glue
Error: The Glue ETL job failed with an s3:PutObject Access Denied error when trying to write processed data to the S3 bucket.
Root Cause: The IAM Role created for the Glue job (Olist-Glue-ETL-Role) initially only had permissions to read from S3, not write.
Resolution: I updated the Olist-Glue-ETL-Role by attaching the AmazonS3FullAccess managed policy (or a more granular custom policy allowing s3:PutObject on the target path). This granted the necessary write permissions.
Challenge 2: Redshift ExecuteStatement Access Denied for Step Functions
Error: The Step Functions workflow failed on the Redshift task with a redshift-data:ExecuteStatement Access Denied error.
Root Cause: The IAM Role used by the Step Function did not have permission to communicate with the Redshift Data API.
Resolution: I attached the AmazonRedshiftDataFullAccess managed policy to the Step Function's execution role, allowing it to successfully send SQL commands to Redshift.
Challenge 3: Redshift GetCredentials Access Denied for Step Functions
Error: After fixing the previous error, the workflow failed again with a redshift-serverless:GetCredentials Access Denied error.
Root Cause: The AmazonRedshiftDataFullAccess policy allows sending commands but does not include the specific permission required to generate the temporary login credentials needed to connect to a Redshift Serverless instance.
Resolution: I created a custom inline policy on the Step Function's role that explicitly granted the redshift-serverless:GetCredentials action on the specific Redshift workgroup ARN. This completed the chain of required permissions.