from domain.notas.repositories import NotaRepository
from domain.notas.entities import Nota
from domain.usuarios.repositories import UsuarioRepository
from domain.eventos.repositories import EventoRepository
from core.exceptions import RegraDeNegocioError
from typing import Dict

class SalvarNotasGaleraUseCase:
    def __init__(self, nota_repo: NotaRepository, usuario_repo: UsuarioRepository, evento_repo: EventoRepository):
        self.nota_repo = nota_repo
        self.usuario_repo = usuario_repo
        self.evento_repo = evento_repo

    async def executar(self, avaliador_id: int, evento_id: int, notas: Dict[int, int]):
        evento = await self.evento_repo.buscar_por_id(evento_id)
        if not evento:
            raise RegraDeNegocioError("Evento não encontrado")

        avaliador = await self.usuario_repo.buscar_por_id(avaliador_id)
        if not avaliador:
            raise RegraDeNegocioError("Avaliador não encontrado")
            
        from domain.usuarios.enums import PerfilUsuario
        if avaliador.perfil == PerfilUsuario.AVULSO:
            raise RegraDeNegocioError("Jogadores avulsos não podem avaliar a galera")

        notas_entities = []
        for avaliado_id, valor_nota in notas.items():
            if avaliado_id == avaliador_id:
                raise RegraDeNegocioError("Você não pode avaliar a si mesmo")
            
            avaliado = await self.usuario_repo.buscar_por_id(avaliado_id)
            if avaliado and avaliado.perfil == PerfilUsuario.AVULSO:
                raise RegraDeNegocioError("Jogadores avulsos não podem ser avaliados na nota da galera")
            
            if valor_nota < 0 or valor_nota > 10:
                raise RegraDeNegocioError("Notas devem estar entre 0 e 10")
                
            # Verifica se já existe uma nota desse avaliador para esse avaliado no evento
            # O repositório lidaria melhor com uma restrição ou update, mas vamos salvar
            nova_nota = Nota(
                id=None,
                avaliado_id=avaliado_id,
                avaliador_id=avaliador_id,
                evento_id=evento_id,
                nota=valor_nota,
                tipo="GALERA"
            )
            notas_entities.append(nova_nota)

        if notas_entities:
            await self.nota_repo.salvar_em_lote(notas_entities)
        
        return True
