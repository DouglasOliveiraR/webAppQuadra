from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from api.schemas.presenca_schemas import PresencaUpdateRequest, PresencaResponse, CheckinRequest
from api.schemas.voto_schemas import VotoRequest, VotoResponse
from application.presencas.use_cases import AtualizarPresencaUseCase, CheckinUseCase
from application.votos.use_cases import RegistrarVotoUseCase, EncerrarVotacaoUseCase
from api.schemas.evento_schemas import EventoRequest, EventoResponse, ChurrascoRequest, SorteioRequest, ChavePixRequest, MensalidadeRequest, CustoQuadraRequest
from application.eventos.use_cases import ObterEventoUseCase, CriarEventoUseCase, ListarEventosUseCase
from application.eventos.iniciar_votacao_use_case import IniciarVotacaoUseCase
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
    get_cancelar_evento_use_case, get_listar_eventos_use_case
)
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
