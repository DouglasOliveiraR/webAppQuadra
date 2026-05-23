import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from api.db.database import SessionLocal
from api.db.models import EventoModel, PresencaModel, VotoModel, FinanceiroModel

def run():
    db = SessionLocal()
    print("Limpando Financeiro...")
    db.query(FinanceiroModel).delete()
    print("Limpando Votos...")
    db.query(VotoModel).delete()
    print("Limpando Presencas...")
    db.query(PresencaModel).delete()
    print("Limpando Eventos...")
    db.query(EventoModel).delete()
    db.commit()
    print("Tabelas limpas com sucesso (exceto usuarios).")
    db.close()

if __name__ == "__main__":
    run()
