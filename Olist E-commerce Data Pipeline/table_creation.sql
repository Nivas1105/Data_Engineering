-- Dimension: Customers
CREATE TABLE public.dim_customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    customer_unique_id VARCHAR(50),
    customer_zip_code_prefix INTEGER,
    customer_city VARCHAR(100),
    customer_state VARCHAR(10)
);

-- Dimension: Products
CREATE TABLE public.dim_products (
    product_id VARCHAR(50) PRIMARY KEY,
    product_category_name VARCHAR(100),
    product_name_length INTEGER,
    product_description_length INTEGER,
    product_photos_qty INTEGER,
    product_weight_g INTEGER,
    product_length_cm INTEGER,
    product_height_cm INTEGER,
    product_width_cm INTEGER
);

-- Dimension: Sellers
CREATE TABLE public.dim_sellers (
    seller_id VARCHAR(50) PRIMARY KEY,
    seller_zip_code_prefix INTEGER,
    seller_city VARCHAR(100),
    seller_state VARCHAR(10)
);

-- Fact Table: Order Items
CREATE TABLE public.fct_order_items (
    order_id VARCHAR(50),
    order_item_id INTEGER,
    product_id VARCHAR(50) REFERENCES public.dim_products(product_id),
    seller_id VARCHAR(50) REFERENCES public.dim_sellers(seller_id),
    customer_id VARCHAR(50) REFERENCES public.dim_customers(customer_id),
    order_status VARCHAR(20),
    price DECIMAL(10, 2),
    freight_value DECIMAL(10, 2),
    payment_sequential INTEGER,
    payment_type VARCHAR(30),
    payment_installments INTEGER,
    payment_value DECIMAL(10, 2),
    review_score INTEGER,
    order_purchase_timestamp TIMESTAMP,
    order_approved_at TIMESTAMP,
    order_delivered_carrier_date TIMESTAMP,
    order_delivered_customer_date TIMESTAMP,
    order_estimated_delivery_date TIMESTAMP
);