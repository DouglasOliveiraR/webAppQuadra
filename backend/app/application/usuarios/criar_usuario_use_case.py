from domain.usuarios.repositories import UsuarioRepository
from domain.usuarios.entities import Usuario
from domain.usuarios.enums import StatusUsuario, PerfilUsuario
from domain.eventos.repositories import EventoRepository
from domain.presencas.repositories import PresencaRepository
from domain.presencas.entities import Presenca
from domain.presencas.enums import StatusJogo, Posicao
from domain.eventos.enums import StatusEvento
from core.exceptions import RegraDeNegocioError
from core.security import get_password_hash
from datetime import datetime
import logging

class CriarUsuarioUseCase:
    def __init__(
        self,
        usuario_repo: UsuarioRepository,
        evento_repo: EventoRepository,
        presenca_repo: PresencaRepository
    ):
        self.usuario_repo = usuario_repo
        self.evento_repo = evento_repo
        self.presenca_repo = presenca_repo

    async def executar(self, nome: str, telefone: str, perfil: PerfilUsuario, nota_admin: int, senha: str = None) -> Usuario:
        if perfil == PerfilUsuario.AVULSO:
            # Jogadores avulsos não têm celular real cadastrado; geramos um ID único fictício para respeitar a UNIQUE constraint do SQLite
            timestamp_str = str(datetime.now().timestamp()).replace('.', '')
            telefone = f"AVULSO_{timestamp_str}_{nome.replace(' ', '_')}"
        else:
            if not telefone:
                raise RegraDeNegocioError("O telefone é obrigatório para mensalistas e administradores.")
            
            import re
            telefone = re.sub(r'\D', '', telefone)
            
            existente = await self.usuario_repo.buscar_por_telefone(telefone)
            if existente:
                raise RegraDeNegocioError("Um jogador com este telefone já está cadastrado.")

        if not senha:
            senha = "123456"

        senha_hash = get_password_hash(senha)

        novo_usuario = Usuario(
            id=None,
            nome=nome,
            telefone=telefone,
            senha_hash=senha_hash,
            perfil=perfil,
            status=StatusUsuario.ATIVO,
            nota_admin=nota_admin,
            nota_galera_media=5.0,
            pontos_ranking=0
        )

        usuario_salvo = await self.usuario_repo.salvar(novo_usuario)

        # Se o perfil for avulso, criamos automaticamente a confirmação de presença no evento ativo
        if perfil == PerfilUsuario.AVULSO:
            try:
                eventos = await self.evento_repo.listar_todos()
                if eventos:
                    # Filtra e pega o evento mais recente que não esteja encerrado ou cancelado
                    eventos_ativos = [e for e in eventos if e.status_evento not in [StatusEvento.ENCERRADO, StatusEvento.CANCELADO]]
                    if eventos_ativos:
                        evento_ativo = sorted(eventos_ativos, key=lambda e: e.id, reverse=True)[0]
                        nova_presenca = Presenca(
                            id=None,
                            usuario_id=usuario_salvo.id,
                            evento_id=evento_ativo.id,
                            status_jogo=StatusJogo.VOU,
                            posicao=Posicao.LINHA,
                            vai_churrasco=False,
                            checkin_validado=True,  # Presença validada por padrão
                            falta_penalizada=False
                        )
                        await self.presenca_repo.salvar(nova_presenca)
            except Exception as e:
                # Silencia erros se porventura falhar a criação automática de presença
                logging.error(f"Erro ao cadastrar presença automática de avulso: {e}")

        return usuario_salvo
