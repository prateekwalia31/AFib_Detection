from flask import Flask, jsonify
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

app = Flask(__name__)

# Modify here to use DATABASE_URL
#DATABASE_URL = os.getenv("DATABASE_URL")

DATABASE_URL = "postgres://udmogfdf79duqn:pd455d073269e4c55b94408d5cf7c296d1b6839ba9a2912c9f8d9d35241a58f45@cbbirn8v9855bl.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/df2677dbqqjia9"
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

@app.route('/predict/patient/<patient_id>', methods=['GET'])
def predict_by_patient_id(patient_id):
    cursor = None

    try:
        logger.debug('Start of prediction process')
        # Connect to the MySQL database
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Fetch atrial fibrillation data from the atrial_fibrillation table based on patient_id
        cursor.execute(f"SELECT Age, Gender, Channel_1, Channel_2, Channel_3, Channel_4, Channel_5, Channel_6, Channel_7, Channel_8, Channel_9, Channel_10, Channel_11, Channel_12 FROM atrial_fibrillation WHERE patient_id = {patient_id}")
        patient_data = cursor.fetchone()
        logging.debug('Cursor ',patient_data)

        if not patient_data:
            return jsonify({'error': 'Patient data not found'}), 404

        age, gender, *channels = patient_data
        # Ensure that 'male' is 1 if Gender is 'Male', else 0, adjusting for your model's requirements
        sex = 1 if gender == 'Male' else 0

        # Initialize features with age and sex in correct order
        features = [age, sex]

        # Extract features from each channel's JSON data
        for channel_json in channels:
            channel_data = json.loads(channel_json)
            features.extend([channel_data['SDNN'][0], channel_data['RMSSD'][0], channel_data['PNN50'][0], channel_data['Mean_RR'][0]])

        # Prediction
        logger.debug('Stating pred')
        prediction = model.predict([features])[0]
        # Assuming your model's output maps directly to these labels
        logger.debug('Finish pred')
        prediction_label = {
            0: 'Atrial Fibrillation',
            1: 'Sinus Rhythm',
            2: 'Various Arrhythmias'
        }.get(prediction, 'Unknown')

        return jsonify({
            'patient_id': patient_id,
            'prediction': prediction_label,
            'features': {
                'age': age,
                'sex': gender
            }
        })
    
    except mysql.connector.Error as err:
        logger.debug('Found an error')
        return jsonify({'error': f'Database error: {err}'}), 500
    
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

if __name__ == '__main__':
    app.run(debug=True)
