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


