from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from api.schemas.presenca_schemas import PresencaUpdateRequest, PresencaResponse, CheckinRequest
from api.schemas.voto_schemas import VotoRequest, VotoResponse
from application.presencas.use_cases import AtualizarPresencaUseCase, CheckinUseCase
from application.votos.use_cases import RegistrarVotoUseCase, EncerrarVotacaoUseCase
from api.schemas.evento_schemas import EventoRequest, EventoResponse, ChurrascoRequest, SorteioRequest, ChavePixRequest, MensalidadeRequest, CustoQuadraRequest
from application.eventos.use_cases import ObterEventoUseCase, CriarEventoUseCase, ListarEventosUseCase
from application.eventos.iniciar_votacao_use_case import IniciarVotacaoUseCase
from application.eventos.cancelar_votacao_use_case import CancelarVotacaoUseCase
from application.eventos.sorteio_use_case import SorteioUseCase
from application.eventos.atualizar_churrasco_use_case import AtualizarChurrascoUseCase
from application.eventos.atualizar_chave_pix_use_case import AtualizarChavePixUseCase
from application.eventos.atualizar_mensalidade_use_case import AtualizarMensalidadeUseCase
from application.eventos.atualizar_custo_quadra_use_case import AtualizarCustoQuadraUseCase
from application.eventos.cancelar_evento_use_case import CancelarEventoUseCase
from domain.eventos.entities import Evento
from domain.eventos.enums import StatusEvento
from api.v1.deps import (
    get_current_user, get_admin_user, get_atualizar_presenca_use_case,
    get_checkin_use_case, get_registrar_voto_use_case,
    get_encerrar_votacao_use_case, get_obter_evento_use_case,
    get_criar_evento_use_case, get_iniciar_votacao_use_case,
    get_sorteio_use_case, get_atualizar_churrasco_use_case,
    get_atualizar_chave_pix_use_case,
    get_atualizar_mensalidade_use_case,
    get_atualizar_custo_quadra_use_case,
    get_cancelar_evento_use_case, get_listar_eventos_use_case,
    get_cancelar_votacao_use_case, get_db
)
from sqlalchemy.orm import Session
from domain.usuarios.entities import Usuario
from core.exceptions import RegraDeNegocioError, RecursoNaoEncontradoError

router = APIRouter(prefix="/api/eventos", tags=["Eventos"])

@router.post("/", response_model=EventoResponse)
async def criar_evento(
    payload: EventoRequest,
    admin_user: Usuario = Depends(get_admin_user),
    use_case: CriarEventoUseCase = Depends(get_criar_evento_use_case)
):
    try:
        evento = Evento(
            id=None,
            data_jogo=payload.data_jogo,
            hora_inicio=payload.hora_inicio,
            hora_fim=payload.hora_fim,
            status_evento=StatusEvento.PRESENCA_ABERTA,
            flag_churrasco=payload.flag_churrasco,
            valor_churrasco=payload.valor_churrasco,
            endereco=payload.endereco,
            chave_pix=payload.chave_pix,
            valor_mensalidade=payload.valor_mensalidade,
            custo_quadra=payload.custo_quadra
        )
        return await use_case.executar(evento)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.put("/{id}/iniciar-votacao", response_model=EventoResponse)
async def iniciar_votacao(
    id: int,
    admin_user: Usuario = Depends(get_admin_user),
    use_case: IniciarVotacaoUseCase = Depends(get_iniciar_votacao_use_case)
):
    try:
        return await use_case.executar(id)
    except RegraDeNegocioError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.detail)

@router.put("/{id}/cancelar-votacao", response_model=EventoResponse)
async def cancelar_votacao(
    id: int,
    admin_user: Usuario = Depends(get_admin_user),
    use_case: CancelarVotacaoUseCase = Depends(get_cancelar_votacao_use_case)
):
    try:
        return await use_case.executar(id)
    except RegraDeNegocioError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.detail)

@router.put("/{id}/churrasco", response_model=EventoResponse)
async def atualizar_churrasco(
    id: int,
    payload: ChurrascoRequest,
    admin_user: Usuario = Depends(get_admin_user),
    use_case: AtualizarChurrascoUseCase = Depends(get_atualizar_churrasco_use_case)
):
    try:
        return await use_case.executar(id, payload.flag_churrasco, payload.valor_churrasco)
    except RegraDeNegocioError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.detail)

@router.put("/{id}/chave-pix", response_model=EventoResponse)
async def atualizar_chave_pix(
    id: int,
    payload: ChavePixRequest,
    admin_user: Usuario = Depends(get_admin_user),
    use_case: AtualizarChavePixUseCase = Depends(get_atualizar_chave_pix_use_case)
):
    try:
        return await use_case.executar(id, payload.chave_pix)
    except RegraDeNegocioError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.detail)

@router.put("/{id}/mensalidade", response_model=EventoResponse)
async def atualizar_mensalidade(
    id: int,
    payload: MensalidadeRequest,
    admin_user: Usuario = Depends(get_admin_user),
    use_case: AtualizarMensalidadeUseCase = Depends(get_atualizar_mensalidade_use_case)
):
    try:
        return await use_case.executar(id, payload.valor_mensalidade)
    except RegraDeNegocioError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.detail)

@router.put("/{id}/custo-quadra", response_model=EventoResponse)
async def atualizar_custo_quadra(
    id: int,
    payload: CustoQuadraRequest,
    admin_user: Usuario = Depends(get_admin_user),
    use_case: AtualizarCustoQuadraUseCase = Depends(get_atualizar_custo_quadra_use_case)
):
    try:
        return await use_case.executar(id, payload.custo_quadra)
    except RegraDeNegocioError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.detail)

@router.put("/{id}/cancelar", response_model=EventoResponse)
async def cancelar_evento(
    id: int,
    admin_user: Usuario = Depends(get_admin_user),
    use_case: CancelarEventoUseCase = Depends(get_cancelar_evento_use_case)
):
    try:
        return await use_case.executar(id)
    except RegraDeNegocioError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.detail)

@router.post("/{id}/sorteio")
async def sortear_times(
    id: int,
    payload: SorteioRequest,
    admin_user: Usuario = Depends(get_admin_user),
    use_case: SorteioUseCase = Depends(get_sorteio_use_case)
):
    try:
        return await use_case.executar(id, payload.criterio)
    except RegraDeNegocioError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.detail)


@router.put("/{id}/presencas/me", response_model=PresencaResponse)
async def atualizar_presenca(
    id: int,
    payload: PresencaUpdateRequest,
    current_user: Usuario = Depends(get_current_user),
    use_case: AtualizarPresencaUseCase = Depends(get_atualizar_presenca_use_case)
):
    try:
        presenca = await use_case.executar(
            usuario_id=current_user.id,
            evento_id=id,
            status=payload.status,
            posicao=payload.posicao,
            churrasco=payload.churrasco
        )
        return presenca
    except RegraDeNegocioError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.detail)

from pydantic import BaseModel
class GolsRequest(BaseModel):
    delta: int

@router.post("/{id}/presencas/{usuario_id}/gols")
async def ajustar_gols(
    id: int,
    usuario_id: int,
    payload: GolsRequest,
    db: Session = Depends(get_db),
    admin_user: Usuario = Depends(get_admin_user)
):
    from api.db.models import PresencaModel
    from sqlalchemy import select
    
    stmt = select(PresencaModel).where(
        PresencaModel.evento_id == id,
        PresencaModel.usuario_id == usuario_id
    )
    presenca = db.execute(stmt).scalars().first()
    
    if not presenca:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Presença não encontrada")
        
    presenca.gols = (presenca.gols or 0) + payload.delta
    if presenca.gols < 0:
        presenca.gols = 0
        
    db.commit()
    db.refresh(presenca)
    return {"gols": presenca.gols}

@router.post("/{id}/checkin/{usuario_id}", response_model=PresencaResponse)
async def registrar_checkin(
    id: int,
    usuario_id: int,
    payload: CheckinRequest,
    admin_user: Usuario = Depends(get_admin_user),
    use_case: CheckinUseCase = Depends(get_checkin_use_case)
):
    try:
        presenca = await use_case.executar(
            evento_id=id,
            usuario_id=usuario_id,
            chegou=payload.chegou,
            falta_justificada=payload.falta_justificada
        )
        return presenca
    except RegraDeNegocioError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.detail)

@router.post("/{id}/votos", response_model=VotoResponse)
async def registrar_voto(
    id: int,
    payload: VotoRequest,
    current_user: Usuario = Depends(get_current_user),
    use_case: RegistrarVotoUseCase = Depends(get_registrar_voto_use_case)
):
    try:
        voto = await use_case.executar(
            evento_id=id,
            eleitor_id=current_user.id,
            candidato_id=payload.candidato_id,
            categoria=payload.categoria
        )
        return voto
    except RegraDeNegocioError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.detail)

@router.put("/{id}/encerrar")
async def encerrar_votacao(
    id: int,
    use_case: EncerrarVotacaoUseCase = Depends(get_encerrar_votacao_use_case),
    admin_user: Usuario = Depends(get_admin_user)
):
    try:
        return await use_case.executar(id)
    except RegraDeNegocioError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.detail)

@router.get("/{id}")
async def obter_evento(
    id: int,
    current_user: Usuario = Depends(get_current_user),
    use_case: ObterEventoUseCase = Depends(get_obter_evento_use_case)
):
    try:
        return await use_case.executar(id, current_user.id)
    except RecursoNaoEncontradoError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.detail)

@router.get("/", response_model=List[EventoResponse])
async def listar_eventos(
    current_user: Usuario = Depends(get_current_user),
    use_case: ListarEventosUseCase = Depends(get_listar_eventos_use_case)
):
    try:
        return await use_case.executar()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{id}/votos-auditoria")
async def auditoria_votos(
    id: int,
    db: Session = Depends(get_db),
    admin_user: Usuario = Depends(get_admin_user)
):
    from sqlalchemy import select
    from api.db.models import VotoModel, NotaModel, UsuarioModel
    
    # Obter todos os votos do evento
    stmt_votos = select(VotoModel).where(VotoModel.evento_id == id)
    result_votos = db.execute(stmt_votos)
    votos = result_votos.scalars().all()

    # Obter todas as notas do evento
    stmt_notas = select(NotaModel).where(NotaModel.evento_id == id)
    result_notas = db.execute(stmt_notas)
    notas = result_notas.scalars().all()

    # Obter os usuários envolvidos
    usuario_ids = set()
    for v in votos:
        usuario_ids.add(v.eleitor_id)
        usuario_ids.add(v.candidato_id)
    for n in notas:
        usuario_ids.add(n.avaliador_id)
        usuario_ids.add(n.avaliado_id)
        
    if not usuario_ids:
        return []
        
    stmt_usuarios = select(UsuarioModel).where(UsuarioModel.id.in_(usuario_ids))
    usuarios = db.execute(stmt_usuarios).scalars().all()
    mapa_usuarios = {u.id: u.nome for u in usuarios}

    # Estruturar o retorno por eleitor
    auditoria = {}
    for v in votos:
        eleitor_nome = mapa_usuarios.get(v.eleitor_id, "Desconhecido")
        if eleitor_nome not in auditoria:
            auditoria[eleitor_nome] = {"categorias": {}, "notas": {}}
        candidato_nome = mapa_usuarios.get(v.candidato_id, "Desconhecido")
        auditoria[eleitor_nome]["categorias"][v.categoria.value] = candidato_nome
        
    for n in notas:
        eleitor_nome = mapa_usuarios.get(n.avaliador_id, "Desconhecido")
        if eleitor_nome not in auditoria:
            auditoria[eleitor_nome] = {"categorias": {}, "notas": {}}
        candidato_nome = mapa_usuarios.get(n.avaliado_id, "Desconhecido")
        auditoria[eleitor_nome]["notas"][candidato_nome] = n.nota

    # Transformar em lista para o frontend
    resultado = []
    for eleitor, dados in auditoria.items():
        resultado.append({
            "votante": eleitor,
            "categorias": dados["categorias"],
            "notas": dados["notas"]
        })
        
    # Ordenar por nome do votante
    resultado.sort(key=lambda x: x["votante"])
    return resultado
