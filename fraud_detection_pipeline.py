import mysql.connector
from mysql.connector import Error

# Database connection details
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '' # Assuming empty password for the lab environment
}

def run_fraud_pipeline():
    """
    ETL pipeline to process product returns data and generate customer risk scores for fraud detection.
    1. Extracts data from the 'product_returns.details' table.
    2. Transforms data by aggregating features at the customer level.
    3. Loads the result into a 'customer_return_risk' table in a new 'analytics_db'.
    """
    conn = None
    try:
        # --- PREPARE: Connect and set up target database/table ---
        print("Connecting to MySQL server...")
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print("Connection successful.")

        # Create the analytics database if it doesn't exist
        analytics_db_name = 'analytics_db'
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {analytics_db_name}")
        cursor.execute(f"USE {analytics_db_name}")
        print(f"Database '{analytics_db_name}' is ready.")

        # Define and create the target reporting table. Dropping it makes the script re-runnable.
        target_table_name = 'customer_return_risk'
        print(f"Preparing target table '{target_table_name}'...")
        cursor.execute(f"DROP TABLE IF EXISTS {target_table_name}")
        create_table_query = f"""
        CREATE TABLE {target_table_name} (
            customer_id INT PRIMARY KEY,
            total_returns INT,
            recent_returns_last_30d INT,
            suspicious_reason_count INT,
            risk_score DECIMAL(10, 4)
        );
        """
        cursor.execute(create_table_query)
        print(f"Table '{target_table_name}' created successfully.")

        # --- EXTRACT & TRANSFORM ---
        # This query aggregates return data per customer to create risk features.
        # It assumes the 'product_returns.details' table exists from the previous lab.
        print("Extracting and transforming data for fraud detection features...")
        
        # First, check if the source table exists to avoid errors.
        cursor.execute("USE product_returns")
        cursor.execute("SHOW TABLES LIKE 'details'")
        if not cursor.fetchone():
            print("\nERROR: Source table 'product_returns.details' not found.")
            print("Please ensure you have completed the NoSQL to RDBMS migration lab first.")
            return

        extract_query = """
        WITH CustomerReturnFeatures AS (
            SELECT
                customer_id,
                COUNT(return_id) AS total_returns,
                SUM(CASE WHEN return_date >= CURDATE() - INTERVAL 30 DAY THEN 1 ELSE 0 END) AS recent_returns_last_30d,
                SUM(CASE WHEN reason IN ('Item damaged on arrival', 'Wrong item delivered', 'Poor fabric quality') THEN 1 ELSE 0 END) AS suspicious_reason_count
            FROM
                product_returns.details
            WHERE customer_id IS NOT NULL
            GROUP BY
                customer_id
        )
        SELECT
            customer_id,
            total_returns,
            recent_returns_last_30d,
            suspicious_reason_count,
            -- Calculate a simple weighted risk score for fraud potential
            (total_returns * 0.2) + (recent_returns_last_30d * 0.5) + (suspicious_reason_count * 0.3) AS risk_score
        FROM
            CustomerReturnFeatures;
        """
        cursor.execute(extract_query)
        transformed_data = cursor.fetchall()
        print(f"Extracted and transformed data for {len(transformed_data)} customers.")

        # --- LOAD ---
        if transformed_data:
            cursor.execute(f"USE {analytics_db_name}")
            insert_query = f"INSERT INTO {target_table_name} VALUES (%s, %s, %s, %s, %s);"
            print(f"Loading data into '{target_table_name}'...")
            cursor.executemany(insert_query, transformed_data)
            conn.commit()
            print(f"Successfully loaded {cursor.rowcount} records.")

        print("\nFraud detection feature pipeline completed successfully!")

    except Error as e:
        print(f"A MySQL error occurred: {e}")
        if conn: conn.rollback()
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
            print("MySQL connection closed.")

if __name__ == '__main__':
    run_fraud_pipeline()
