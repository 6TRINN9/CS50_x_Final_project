import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        port=5433,
        database="cinema_db",
        user="cinema",
        password="cinema",
    )
    print("✅ Подключение успешно!")
    conn.close()
except Exception as e:
    print(f"❌ Ошибка: {e}")
