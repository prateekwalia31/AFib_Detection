from flask import Flask, jsonify
import os
from dotenv import load_dotenv
import logging
import json
from joblib import load
from flask_cors import CORS
import mysql.connector

load_dotenv()

# Setup basic configuration for logging
logging.basicConfig(level=logging.DEBUG)

# Create a logger object
logger = logging.getLogger(__name__)

app = Flask(__name__)

CORS(app)

model = load("RandomForest_best_model.pkl")

# Set up MySQL connection parameters
db_config = {
    "host": os.environ.get("DB_HOST"),
    "user": os.environ.get("DB_USER"),
    "password": os.environ.get("DB_PASSWORD"),
    "database": os.environ.get("DB_NAME")
}

@app.route('/test_db_connection')
def test_db_connection():
    conn = None
    try:
        # Connect to the MySQL database using the db_config
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Perform a simple query to check the database connection
        cursor.execute("SELECT count(*) FROM patient_data")
        count = cursor.fetchone()[0]

        cursor.close()
        return jsonify({'message': f'Database connection successful. Found {count} records in the table.'}), 200
    except Exception as e:
        return jsonify({'error': f'Database connection failed: {e}'}), 500
    finally:
        if conn is not None:
            conn.close()

@app.route('/predict/patient/<patient_id>', methods=['GET'])
def predict_by_patient_id(patient_id):
    cursor = None
    connection = None

    try:
        logger.debug('Start of prediction process for patient_id: %s', patient_id)

        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        logger.debug('Database connection established.')

        # Fetch atrial fibrillation data from the atrial_fibrillation table based on patient_id
        cursor.execute("SELECT Age, Gender, Channel_1, Channel_2, Channel_3, Channel_4, Channel_5, Channel_6, Channel_7, Channel_8, Channel_9, Channel_10, Channel_11, Channel_12 FROM atrial_fibrillation WHERE patient_id = %s", (patient_id,))
        patient_data = cursor.fetchone()

        if not patient_data:
            logger.debug('Patient data not found for patient_id: %s', patient_id)
            return jsonify({'error': 'Patient data not found'}), 404

        logger.debug('Patient data retrieved: %s', patient_data)

        age, gender, *channels = patient_data
        sex = 1 if gender == 'Male' else 0
        features = [age, sex]

        # Extract features from each channel's JSON data
        for channel_json in channels:
            channel_data = json.loads(channel_json)  # Decode JSON string to dict
            features.extend([channel_data['SDNN'][0], channel_data['RMSSD'][0], channel_data['PNN50'][0], channel_data['Mean_RR'][0]])

        logger.debug('Features extracted for prediction: %s', features)

        # prediction model logic here
        prediction = model.predict([features])[0]

        prediction_label = {
            0: 'Atrial Fibrillation',
            1: 'Sinus Rhythm',
            2: 'Various Arrhythmias'
        }.get(prediction, 'Unknown')

        logger.debug('Prediction completed. Label: %s', prediction_label)

        return jsonify({
            'patient_id': patient_id,
            'prediction': prediction_label,
            'features': {
                'age': age,
                'sex': gender
            }
        })

    except Exception as e:
        logger.error('Error during prediction process: %s', e, exc_info=True)
        return jsonify({'error': f'Prediction process failed: {e}'}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

if __name__ == '__main__':
    app.run(debug=True)
