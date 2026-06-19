import pytest
from unittest.mock import AsyncMock
from application.usuarios.criar_usuario_use_case import CriarUsuarioUseCase
from domain.usuarios.entities import Usuario
from domain.usuarios.enums import PerfilUsuario, StatusUsuario
from core.exceptions import RegraDeNegocioError

@pytest.mark.asyncio
async def test_criar_usuario_telefone_duplicado_erro():
    usuario_repo = AsyncMock()
    evento_repo = AsyncMock()
    presenca_repo = AsyncMock()

    # Mocks de dados
    existente = Usuario(
        id=1,
        nome="Usuario Existente",
        telefone="11999999999",
        senha_hash="",
        perfil=PerfilUsuario.MENSALISTA,
        status=StatusUsuario.ATIVO,
        nota_admin=8,
        nota_galera_media=8.0,
        pontos_ranking=0
    )

    usuario_repo.buscar_por_telefone.return_value = existente

    use_case = CriarUsuarioUseCase(usuario_repo, evento_repo, presenca_repo)

    with pytest.raises(RegraDeNegocioError, match="Um jogador com este telefone já está cadastrado."):
        await use_case.executar(
            nome="Novo Usuario",
            telefone="11999999999",
            perfil=PerfilUsuario.MENSALISTA,
            nota_admin=8,
            senha="senha"
        )

@pytest.mark.asyncio
async def test_criar_usuario_sucesso():
    usuario_repo = AsyncMock()
    evento_repo = AsyncMock()
    presenca_repo = AsyncMock()

    usuario_repo.buscar_por_telefone.return_value = None

    def mock_salvar(usuario):
        usuario.id = 1
        return usuario

    usuario_repo.salvar.side_effect = mock_salvar

    use_case = CriarUsuarioUseCase(usuario_repo, evento_repo, presenca_repo)

    usuario = await use_case.executar(
        nome="Novo Usuario",
        telefone="11999999999",
        perfil=PerfilUsuario.MENSALISTA,
        nota_admin=8,
        senha="senha"
    )

    assert usuario.nome == "Novo Usuario"
    assert usuario.telefone == "11999999999"
    assert usuario.perfil == PerfilUsuario.MENSALISTA
    usuario_repo.salvar.assert_called_once()
