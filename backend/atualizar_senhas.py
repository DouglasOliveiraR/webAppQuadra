import sys
import os
import logging
import secrets

# Adiciona a pasta app ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.db.database import SessionLocal
from api.db.models import UsuarioModel
from domain.usuarios.enums import PerfilUsuario
from core.security import get_password_hash
from datetime import date

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    db = SessionLocal()
    try:
        hoje = date.today()
        usuarios = db.query(UsuarioModel).all()
        
        atualizados = 0
        logger.info(f"Buscando usuários cadastrados hoje ({hoje})...")
        for u in usuarios:
            # Se a data de criação for hoje, atualizamos a senha
            # Ignoramos o perfil ADMIN apenas por precaução, a não ser que você queira
            if u.criado_em.date() == hoje and u.perfil != PerfilUsuario.ADMIN:
                nova_senha = secrets.token_urlsafe(8)
                u.senha_hash = get_password_hash(nova_senha)
                atualizados += 1
                logger.info(f"✅ Senha resetada para o jogador: {u.nome} (Celular: {u.telefone}) - Nova Senha: {nova_senha}")
                
        db.commit()
        logger.info(f"Sucesso! {atualizados} jogadores tiveram a senha atualizada com senhas seguras.")
    except Exception as e:
        logger.exception(f"Erro ao processar: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
