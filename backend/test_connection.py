from app.database import get_connection


try:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT current_database();")
    database_name = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM public.sofa_dataset;")
    sofa_count = cursor.fetchone()[0]

    print("PostgreSQL connection successful!")
    print("Database:", database_name)
    print("Sofa records:", sofa_count)

    cursor.close()
    conn.close()

except Exception as e:
    print("Connection failed:")
    print(e)