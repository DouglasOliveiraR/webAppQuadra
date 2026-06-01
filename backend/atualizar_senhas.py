import sys
import os

# Adiciona a pasta app ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.db.database import SessionLocal
from api.db.models import UsuarioModel
from domain.usuarios.enums import PerfilUsuario
from core.security import get_password_hash
from datetime import date

def main():
    db = SessionLocal()
    try:
        print("Gerando nova hash segura para '123456'...")
        nova_hash = get_password_hash("123456")
        
        hoje = date.today()
        usuarios = db.query(UsuarioModel).all()
        
        atualizados = 0
        print(f"Buscando usuários cadastrados hoje ({hoje})...")
        for u in usuarios:
            # Se a data de criação for hoje, atualizamos a senha
            # Ignoramos o perfil ADMIN apenas por precaução, a não ser que você queira
            if u.criado_em.date() == hoje and u.perfil != PerfilUsuario.ADMIN:
                u.senha_hash = nova_hash
                atualizados += 1
                print(f"✅ Senha resetada para o jogador: {u.nome} (Celular: {u.telefone})")
                
        db.commit()
        print(f"\nSucesso! {atualizados} jogadores tiveram a senha atualizada para '123456'.")
    except Exception as e:
        print(f"Erro ao processar: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
