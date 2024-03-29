from flask import Flask, jsonify
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

app = Flask(__name__)

# Setup database configuration using environment variables
# db_config = {
#     "dbname": os.getenv("DB_NAME"),
#     "user": os.getenv("DB_USER"),
#     "password": os.getenv("DB_PASSWORD"),
#     "host": os.getenv("DB_HOST")
# }

db_config = {
    "dbname": os.getenv("df2677dbqqjia9"),
    "user": os.getenv("udmogfdf79duqn"),
    "password": os.getenv("pd455d073269e4c55b94408d5cf7c296d1b6839ba9a2912c9f8d9d35241a58f45"),
    "host": os.getenv("cbbirn8v9855bl.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com
")
}


@app.route('/test_db_connection')
def test_db_connection():
    conn = None
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        
        # Perform a simple query to check the database connection
        cur.execute("SELECT count(*) FROM patient_data;")
        count = cur.fetchone()[0]
        
        cur.close()
        return jsonify({'message': f'Database connection successful. Found {count} records in the table.'}), 200
    except Exception as e:
        return jsonify({'error': f'Database connection failed: {e}'}), 500
    finally:
        if conn is not None:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
