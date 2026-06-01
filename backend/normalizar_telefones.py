import sys
import os
import re

# Adiciona a pasta atual ao path para os imports do Docker funcionarem
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.db.database import SessionLocal
from api.db.models import UsuarioModel

def main():
    db = SessionLocal()
    try:
        usuarios = db.query(UsuarioModel).all()
        atualizados = 0
        
        print("Iniciando a limpeza e normalização dos telefones...")
        
        for u in usuarios:
            # Ignora os jogadores avulsos (que tem um ID fictício no lugar do telefone)
            if u.telefone and not str(u.telefone).startswith("AVULSO_"):
                # Arranca tudo que não for número (espaços, traços, parênteses)
                tel_limpo = re.sub(r'\D', '', str(u.telefone))
                
                # Se o telefone original era diferente do limpo, a gente atualiza
                if tel_limpo != u.telefone:
                    print(f"Corrigindo {u.nome}: '{u.telefone}' -> '{tel_limpo}'")
                    u.telefone = tel_limpo
                    atualizados += 1
                    
        db.commit()
        print(f"\nOperação concluída! {atualizados} telefones foram corrigidos no banco.")
    except Exception as e:
        print(f"Erro durante a normalização: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
