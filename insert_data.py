import sqlite3
import csv
import os
from datetime import datetime

def create_database():
    """Создает SQLite базу данных и таблицы (если их нет)"""
    conn = sqlite3.connect('sensor_data.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS temperature_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        time TEXT NOT NULL,
        temperature REAL,
        humidity REAL,
        timestamp DATETIME,
        UNIQUE(date, time)
    )
    ''')

    conn.commit()
    return conn

def parse_csv_file(file_path, conn):
    """Парсит CSV файл и добавляет данные в базу"""
    cursor = conn.cursor()

    with open(file_path, 'r', encoding='utf-8') as f:
        # Пропускаем первые 37 строк
        for _ in range(38):
            next(f)

        # Читаем оставшиеся строки как CSV
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 3:
                continue

            date = row[0].strip()
            time = row[1].strip()
            temp = row[2].strip().replace(' ', '')

            try:
                temperature = float(temp) if temp != '--' else None
                humidity = float(row[3].strip()) if len(row) > 3 and row[3].strip() != '--' else None

                dt_str = f"{date} {time}"
                timestamp = datetime.strptime(dt_str, '%m/%d/%Y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')

                cursor.execute('''
                INSERT OR IGNORE INTO temperature_data 
                (date, time, temperature, humidity, timestamp)
                VALUES (?, ?, ?, ?, ?)
                ''', (date, time, temperature, humidity, timestamp))

            except ValueError as e:
                print(f"Ошибка обработки строки {row}: {e}")
                continue

    conn.commit()

def print_sorted_data(conn):
    """Выводит данные, отсортированные по времени"""
    cursor = conn.cursor()

    cursor.execute('''
    SELECT date, time, temperature, humidity 
    FROM temperature_data 
    ORDER BY timestamp
    ''')

    print("\nДанные, отсортированные по времени:")
    print("----------------------------------")
    print("Дата        | Время     | Температура | Влажность")
    print("----------------------------------")

    for row in cursor.fetchall():
        date, time, temp, hum = row
        temp_str = f"{temp:.1f}°C" if temp is not None else "N/A"
        hum_str = f"{hum}%" if hum is not None else "N/A"
        print(f"{date:10} | {time:8} | {temp_str:11} | {hum_str}")

if __name__ == '__main__':
    db_conn = create_database()
    parse_csv_file('2-TZ0324074843.csv', db_conn)

    cursor = db_conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM temperature_data")
    print(f"Всего записей в базе: {cursor.fetchone()[0]}")

    print_sorted_data(db_conn)
    db_conn.close()