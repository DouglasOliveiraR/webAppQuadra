import sqlite3

try:
    conn = sqlite3.connect('e:/APP_FUT_V2/backend/app/pelada.db')
    cursor = conn.cursor()
    cursor.execute("ALTER TABLE presencas ADD COLUMN gols INTEGER DEFAULT 0")
    conn.commit()
    print("Coluna gols adicionada com sucesso!")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e).lower():
        print("Coluna já existe.")
    else:
        print(f"Erro: {e}")
finally:
    conn.close()
