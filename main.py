from flask import Flask, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

def get_db_connection():
    conn = sqlite3.connect('sensor_data.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/get_data', methods=['GET'])
def get_data():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Получаем все данные из таблицы
        cursor.execute('''
        SELECT date, time, temperature, humidity, timestamp
        FROM temperature_data
        ORDER BY timestamp
        ''')

        # Формируем ответ в виде списка словарей
        data = [dict(row) for row in cursor.fetchall()]
        conn.close()

        if not data:
            return jsonify({"error": "Данные не найдены"}), 404

        return jsonify(data)

    except Exception as e:
        return jsonify({"error": f"Ошибка сервера: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)