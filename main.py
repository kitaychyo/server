from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
from datetime import datetime

app = Flask(__name__)
CORS(app)


def get_db_connection():
    conn = sqlite3.connect('sensor_data.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/get_data_by_range', methods=['GET'])
def get_data_by_range():
    start_date = request.args.get('start_date')  # "MM/DD/YYYY"
    end_date = request.args.get('end_date')  # "MM/DD/YYYY"
    start_time = request.args.get('start_time', '00:00:00')  # "HH:MM:SS" (опционально)
    end_time = request.args.get('end_time', '23:59:59')  # "HH:MM:SS" (опционально)

    # Проверка обязательных параметров
    if not start_date or not end_date:
        return jsonify({
            "error": "Необходимо указать start_date и end_date",
            "correct_format": "MM/DD/YYYY",
            "example": "/get_data_by_range?start_date=12/04/2024&end_date=12/06/2024",
            "example_with_time": "/get_data_by_range?start_date=12/04/2024&end_date=12/06/2024&start_time=08:00:00&end_time=20:00:00"
        }), 400

    try:
        # Преобразование дат в datetime объекты для проверки
        start_dt = datetime.strptime(start_date, '%m/%d/%Y')
        end_dt = datetime.strptime(end_date, '%m/%d/%Y')

        # Проверка форматов времени
        datetime.strptime(start_time, '%H:%M:%S')
        datetime.strptime(end_time, '%H:%M:%S')

        conn = get_db_connection()
        cursor = conn.cursor()

        # Запрос для диапазона дат с возможной фильтрацией по времени
        query = '''
        SELECT date, time, temperature, humidity, timestamp
        FROM temperature_data
        WHERE date BETWEEN ? AND ?
        AND time BETWEEN ? AND ?
        ORDER BY timestamp
        '''

        cursor.execute(query, (start_date, end_date, start_time, end_time))
        data = [dict(row) for row in cursor.fetchall()]
        conn.close()

        if not data:
            # Получаем информацию о доступных данных
            available = get_available_data_for_range(start_date, end_date)
            return jsonify({
                "message": "Нет данных для указанного диапазона",
                "requested_range": f"{start_date} - {end_date}",
                "available_dates": available,
                "suggestion": "Используйте даты из списка available_dates"
            }), 404

        return jsonify(data)

    except ValueError as e:
        return jsonify({
            "error": "Неверный формат даты или времени",
            "correct_date_format": "MM/DD/YYYY",
            "correct_time_format": "HH:MM:SS",
            "your_start_date": start_date,
            "your_end_date": end_date,
            "your_start_time": start_time,
            "your_end_time": end_time
        }), 400
    except Exception as e:
        return jsonify({"error": f"Ошибка сервера: {str(e)}"}), 500


def get_available_data_for_range(start_date, end_date):
    """Возвращает доступные даты в запрошенном диапазоне"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT DISTINCT date 
    FROM temperature_data 
    WHERE date BETWEEN ? AND ?
    ORDER BY date
    ''', (start_date, end_date))
    dates = [row['date'] for row in cursor.fetchall()]
    conn.close()
    return dates


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)