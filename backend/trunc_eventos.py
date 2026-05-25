import sqlite3

db_path = r"e:\APP_FUT_V2\backend\pelada.db"
print(f"Connecting to DB at: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Habilita o PRAGMA para que as restrições ON DELETE CASCADE funcionem 
    # (limpando também as presenças e os votos atrelados a esses eventos)
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    cursor.execute("DELETE FROM eventos")
    deleted = cursor.rowcount
    conn.commit()
    print(f"Tabela eventos truncada com sucesso! {deleted} registros deletados (e presenças/votos relacionados foram removidos em cascata).")
except Exception as e:
    print(f"Erro ao truncar a tabela de eventos: {e}")
finally:
    if 'conn' in locals():
        conn.close()
