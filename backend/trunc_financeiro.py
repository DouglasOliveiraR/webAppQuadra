import sqlite3

db_path = r"e:\APP_FUT_V2\backend\pelada.db"
print(f"Connecting to DB at: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM financeiro")
    deleted = cursor.rowcount
    conn.commit()
    print(f"Tabela financeiro truncada com sucesso! {deleted} registros deletados.")
except Exception as e:
    print(f"Erro ao truncar a tabela: {e}")
finally:
    if 'conn' in locals():
        conn.close()
