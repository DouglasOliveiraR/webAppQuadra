import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from api.db.database import SessionLocal
from api.db.models import EventoModel, PresencaModel, VotoModel, FinanceiroModel, UsuarioModel

def run():
    db = SessionLocal()
    try:
        print("Zerando pontos de ranking e médias dos usuários...")
        db.query(UsuarioModel).update({
            UsuarioModel.pontos_ranking: 0,
            UsuarioModel.nota_galera_media: 0.0
        })
        
        print("Limpando Votos...")
        db.query(VotoModel).delete()
        
        print("Limpando Presencas...")
        db.query(PresencaModel).delete()
        
        print("Limpando Eventos...")
        db.query(EventoModel).delete()
        
        print("Limpando Financeiro...")
        db.query(FinanceiroModel).delete()
        
        db.commit()
        print("Ranking resetado e tabelas limpas com sucesso!")
    except Exception as e:
        db.rollback()
        print(f"Erro ao resetar: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run()
