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
