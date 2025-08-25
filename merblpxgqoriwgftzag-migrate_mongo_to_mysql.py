import pymongo
import mysql.connector
from mysql.connector import Error

def migrate_mongo_to_mysql():
    """
    Connects to MongoDB to fetch product returns data, then connects to MySQL
    to create a structured table and insert the fetched data.
    """
    mongo_client = None
    mysql_conn = None
    try:
        # 1. Connect to MongoDB and fetch data
        mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
        mongo_db = mongo_client["product_returns"]
        returns_data = list(mongo_db["returns"].find())
        print(f"Fetched {len(returns_data)} documents from MongoDB.")

        # 2. Connect to MySQL
        mysql_conn = mysql.connector.connect(
            host="localhost", user="root", password="", database="product_returns"
        )
        mysql_cursor = mysql_conn.cursor()
        print("Successfully connected to MySQL.")

        # 3. Define and Create MySQL Table Schema
        mysql_cursor.execute("DROP TABLE IF EXISTS returns")
        create_table_query = """
        CREATE TABLE returns (
            return_id VARCHAR(255) PRIMARY KEY,
            order_id VARCHAR(255) NOT NULL,
            product_id INT NOT NULL,
            customer_id INT NOT NULL,
            return_date DATE,
            reason TEXT,
            status VARCHAR(50)
        );
        """
        mysql_cursor.execute(create_table_query)
        print("MySQL table 'returns' created successfully.")

        # 4. Transform and Insert Data into MySQL
        insert_query = """
        INSERT INTO returns (return_id, order_id, product_id, customer_id, return_date, reason, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        data_to_insert = [
            (str(doc.get('_id')), doc.get('order_id'), doc.get('product_id'),
             doc.get('customer_id'), doc.get('return_date'), doc.get('reason'),
             doc.get('status'))
            for doc in returns_data
        ]
        mysql_cursor.executemany(insert_query, data_to_insert)
        mysql_conn.commit() # Commit the transaction
        print(f"Successfully migrated {mysql_cursor.rowcount} records to MySQL.")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # 5. Ensure connections are closed
        if mongo_client:
            mongo_client.close()
        if mysql_conn and mysql_conn.is_connected():
            mysql_cursor.close()
            mysql_conn.close()

if __name__ == '__main__':
    migrate_mongo_to_mysql()