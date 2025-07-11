import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql.functions import col
from awsglue.context import GlueContext
from awsglue.job import Job

# --- Job Initialization ---
args = getResolvedOptions(sys.argv, ["JOB_NAME"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

# --- Configuration ---
S3_BUCKET = "s3://mysitebucketuta" # <--- CHANGE THIS TO YOUR BUCKET
RAW_PATH = f"{S3_BUCKET}/raw_data"
PROCESSED_PATH = f"{S3_BUCKET}/processed_data"

# --- Data Loading ---
# Load all necessary raw datasets from S3
customers_df = spark.read.option("header", "true").csv(f"{RAW_PATH}/olist_customers_dataset.csv")
orders_df = spark.read.option("header", "true").csv(f"{RAW_PATH}/olist_orders_dataset.csv")
order_items_df = spark.read.option("header", "true").csv(f"{RAW_PATH}/olist_order_items_dataset.csv")
products_df = spark.read.option("header", "true").csv(f"{RAW_PATH}/olist_products_dataset.csv")
sellers_df = spark.read.option("header", "true").csv(f"{RAW_PATH}/olist_sellers_dataset.csv")
payments_df = spark.read.option("header", "true").csv(f"{RAW_PATH}/olist_order_payments_dataset.csv")
reviews_df = spark.read.option("header", "true").csv(f"{RAW_PATH}/olist_order_reviews_dataset.csv")

# --- Transformation & Dimension Creation ---

# Create dim_customers
dim_customers = customers_df.select(
    col("customer_id"),
    col("customer_unique_id"),
    col("customer_zip_code_prefix").cast("int"),
    col("customer_city"),
    col("customer_state")
).distinct()

# Create dim_products
dim_products = products_df.select(
    col("product_id"),
    col("product_category_name"),
    col("product_name_lenght").alias("product_name_length").cast("int"),
    col("product_description_lenght").alias("product_description_length").cast("int"),
    col("product_photos_qty").cast("int"),
    col("product_weight_g").cast("int"),
    col("product_length_cm").cast("int"),
    col("product_height_cm").cast("int"),
    col("product_width_cm").cast("int")
).distinct()

# Create dim_sellers
dim_sellers = sellers_df.select(
    col("seller_id"),
    col("seller_zip_code_prefix").cast("int"),
    col("seller_city"),
    col("seller_state")
).distinct()

# --- Fact Table Creation ---
# Join all tables to build the fact table
fct_order_items = order_items_df.join(orders_df, "order_id") \
    .join(payments_df, "order_id") \
    .join(reviews_df, "order_id") \
    .select(
        col("order_id"),
        col("order_item_id").cast("int"),
        col("product_id"),
        col("seller_id"),
        col("customer_id"),
        col("order_status"),
        col("price").cast("decimal(10, 2)"),
        col("freight_value").cast("decimal(10, 2)"),
        col("payment_sequential").cast("int"),
        col("payment_type"),
        col("payment_installments").cast("int"),
        col("payment_value").cast("decimal(10, 2)"),
        col("review_score").cast("int"),
        col("order_purchase_timestamp").cast("timestamp"),
        col("order_approved_at").cast("timestamp"),
        col("order_delivered_carrier_date").cast("timestamp"),
        col("order_delivered_customer_date").cast("timestamp"),
        col("order_estimated_delivery_date").cast("timestamp")
    )

# --- Data Writing ---
# Write final dimension and fact tables back to S3 in Parquet format
dim_customers.write.mode("overwrite").parquet(f"{PROCESSED_PATH}/dim_customers/")
dim_products.write.mode("overwrite").parquet(f"{PROCESSED_PATH}/dim_products/")
dim_sellers.write.mode("overwrite").parquet(f"{PROCESSED_PATH}/dim_sellers/")
fct_order_items.write.mode("overwrite").parquet(f"{PROCESSED_PATH}/fct_order_items/")

job.commit()