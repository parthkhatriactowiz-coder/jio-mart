import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "actowiz",
    "database": "jio_mart",
}

connection_pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="jio_mart_pool", pool_size=30, **DB_CONFIG
)


def get_db_connection():
    return connection_pool.get_connection()


GET_PENDING_INPUTS = """
SELECT
    id,
    url,
    pincode
FROM jiomart_inputs
WHERE status = 'pending'
"""

CREATE_PRODUCT_TABLE = """
CREATE TABLE IF NOT EXISTS jiomart_products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    input_id INT,
    slug VARCHAR(255),
    product_name TEXT,
    size VARCHAR(50),
    mrp DECIMAL(10, 2),
    selling_price DECIMAL(10, 2),
    effective_price DECIMAL(10, 2),
    currency_code VARCHAR(10),
    currency_symbol VARCHAR(10),
    discount VARCHAR(50),
    available BOOLEAN,
    pincode VARCHAR(10),
    distance_in_meter INT,
    quantity VARCHAR(50),
    delivery_promise INT,
    key_features TEXT,
    brand_name VARCHAR(255),
    sold_by VARCHAR(255),
    origin_countries TEXT,
    manufacturer_name VARCHAR(255),
    manufacturer_address TEXT,
    product_code VARCHAR(255),
    shelf_life VARCHAR(50),
    item_dimensions TEXT,
    item_specifications TEXT,
    product_showcase TEXT,
    disclaimer TEXT,
    response_hash VARCHAR(64),
    raw_response_file VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (input_id) REFERENCES jiomart_inputs(id) ON DELETE CASCADE
)
"""

UPDATE_INPUT_STATUS = """
UPDATE jiomart_inputs 
SET status = %s 
WHERE id = %s
"""

INSERT_PRODUCT = """
INSERT INTO jiomart_products (
    input_id, slug, product_name, size, mrp, selling_price, effective_price,
    currency_code, currency_symbol, discount, available, pincode, distance_in_meter,
    quantity, delivery_promise, key_features, brand_name, sold_by,
    origin_countries, manufacturer_name, manufacturer_address, product_code,
    shelf_life, item_dimensions, item_specifications, product_showcase, disclaimer,
    response_hash, raw_response_file
) VALUES (
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
)
"""