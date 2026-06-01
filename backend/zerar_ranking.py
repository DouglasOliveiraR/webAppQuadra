import sys
import os

# Adiciona a pasta atual ao path para os imports do Docker funcionarem
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.db.database import SessionLocal
from api.db.models import UsuarioModel

def main():
    db = SessionLocal()
    try:
        usuarios = db.query(UsuarioModel).all()
        atualizados = 0
        
        print("Iniciando o zeramento do ranking para todos os usuários...")
        
        for u in usuarios:
            # Só atualiza quem tem ponto maior ou menor que zero (para otimizar o banco)
            if u.pontos_ranking != 0:
                u.pontos_ranking = 0
                atualizados += 1
                
        db.commit()
        print(f"\nSucesso absoluto! O ranking de {atualizados} jogadores foi resetado para 0 pontos.")
    except Exception as e:
        print(f"Erro ao processar o reset do ranking: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
