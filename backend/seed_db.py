from datetime import date, time
from sqlalchemy.orm import Session
from api.db.database import engine, SessionLocal
from api.db.models import Base, UsuarioModel, EventoModel, PresencaModel
from domain.usuarios.enums import PerfilUsuario, StatusUsuario
from domain.eventos.enums import StatusEvento
from domain.presencas.enums import StatusJogo, Posicao
from core.security import get_password_hash

def seed_db():
    print("Iniciando Seed do Banco de Dados...")
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    # Checar se ja existem usuarios
    if db.query(UsuarioModel).first():
        print("Banco de dados já populado!")
        db.close()
        return

    admin = UsuarioModel(
        nome="Admin Douglas",
        telefone="11999999999",
        senha_hash=get_password_hash("admin123"),
        perfil=PerfilUsuario.ADMIN,
        status=StatusUsuario.ATIVO,
        nota_admin=10.0,
        nota_galera_media=10.0,
        pontos_ranking=50
    )

    jogador1 = UsuarioModel(
        nome="João Artilheiro",
        telefone="11988888888",
        senha_hash=get_password_hash("senha123"),
        perfil=PerfilUsuario.MENSALISTA,
        status=StatusUsuario.ATIVO,
        nota_admin=8.0,
        nota_galera_media=8.5,
        pontos_ranking=20
    )
    
    jogador2 = UsuarioModel(
        nome="Carlos Paredão (Goleiro)",
        telefone="11977777777",
        senha_hash=get_password_hash("senha123"),
        perfil=PerfilUsuario.AVULSO,
        status=StatusUsuario.ATIVO,
        nota_admin=9.0,
        nota_galera_media=9.0,
        pontos_ranking=15
    )

    evento = EventoModel(
        data_jogo=date(2026, 6, 1),
        hora_inicio=time(19, 0),
        hora_fim=time(21, 0),
        status_evento=StatusEvento.PRESENCA_ABERTA,
        flag_churrasco=True,
        valor_churrasco=50.0
    )

    db.add_all([admin, jogador1, jogador2, evento])
    db.commit()

    # Pre-popular algumas presencas
    p1 = PresencaModel(
        usuario_id=admin.id,
        evento_id=evento.id,
        status_jogo=StatusJogo.VOU,
        posicao=Posicao.LINHA,
        vai_churrasco=True,
        checkin_validado=False,
        falta_penalizada=False
    )
    
    p2 = PresencaModel(
        usuario_id=jogador2.id,
        evento_id=evento.id,
        status_jogo=StatusJogo.VOU,
        posicao=Posicao.GOL,
        vai_churrasco=False,
        checkin_validado=False,
        falta_penalizada=False
    )
    
    db.add_all([p1, p2])
    db.commit()

    print("✅ Banco de dados populado com sucesso!")
    print("Use o telefone '11999999999' e senha 'admin123' para logar como Admin.")
    print("Use o telefone '11988888888' e senha 'senha123' para logar como Jogador Comum.")
    
    db.close()

if __name__ == "__main__":
    seed_db()
