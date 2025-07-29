import psycopg2

# Подключаемся к серверу PostgreSQL к существующей базе (например, стандартной postgres)
conn = psycopg2.connect(dbname="postgres", user="postgres", password="1234", host="localhost")
conn.autocommit = True  # Включаем автокоммит для создания БД вне транзакции

cursor = conn.cursor()

# Создаем базу данных mydatabase
cursor.execute("CREATE DATABASE mydatabase;")

cursor.close()
conn.close()

print("База данных успешно создана")
