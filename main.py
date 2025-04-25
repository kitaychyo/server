from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Разрешаем CORS для всех доменов

def get_db_connection():
    conn = sqlite3.connect('sensor_data.db')
    conn.row_factory = sqlite3.Row  # Для доступа к полям по имени
    return conn

@app.route('/get_data', methods=['GET'])
def get_data():
    start_date = request.args.get('start')
    end_date = request.args.get('end')

    if not start_date or not end_date:
        return jsonify({"error": "Необходимо указать параметры start и end"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Преобразуем даты в формат базы данных (YYYY-MM-DD HH:MM:SS)
        start_datetime = datetime.strptime(start_date, '%m/%d/%Y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
        end_datetime = datetime.strptime(end_date, '%m/%d/%Y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')

        cursor.execute('''
        SELECT date, time, temperature, humidity, timestamp
        FROM temperature_data
        WHERE timestamp BETWEEN ? AND ?
        ORDER BY timestamp
        ''', (start_datetime, end_datetime))

        data = []
        for row in cursor.fetchall():
            data.append({
                'date': row['date'],
                'time': row['time'],
                'temperature': row['temperature'],
                'humidity': row['humidity'],
                'timestamp': row['timestamp']
            })

        conn.close()
        return jsonify(data)

    except ValueError as e:
        return jsonify({"error": f"Неверный формат даты: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_stats', methods=['GET'])
def get_stats():
    start_date = request.args.get('start')
    end_date = request.args.get('end')

    if not start_date or not end_date:
        return jsonify({"error": "Необходимо указать параметры start и end"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        start_datetime = datetime.strptime(start_date, '%m/%d/%Y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
        end_datetime = datetime.strptime(end_date, '%m/%d/%Y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')

        # Получаем статистику
        cursor.execute('''
        SELECT 
            MIN(temperature) as min_temp,
            MAX(temperature) as max_temp,
            AVG(temperature) as avg_temp,
            COUNT(*) as count
        FROM temperature_data
        WHERE timestamp BETWEEN ? AND ?
        ''', (start_datetime, end_datetime))

        stats = cursor.fetchone()
        result = {
            'min_temperature': stats['min_temp'],
            'max_temperature': stats['max_temp'],
            'avg_temperature': round(stats['avg_temp'], 2) if stats['avg_temp'] else None,
            'count': stats['count']
        }

        conn.close()
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)