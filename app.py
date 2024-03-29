from flask import Flask, jsonify
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

app = Flask(__name__)

# Modify here to use DATABASE_URL
#DATABASE_URL = os.getenv("DATABASE_URL")

DATABASE_URL = "postgres://udmogfdf79duqn:pd455d073269e4c55b94408d5cf7c296d1b6839ba9a2912c9f8d9"
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

@app.route('/test_db_connection')
def test_db_connection():
    conn = None
    try:
        # Connect to the PostgreSQL database using DATABASE_URL
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
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
