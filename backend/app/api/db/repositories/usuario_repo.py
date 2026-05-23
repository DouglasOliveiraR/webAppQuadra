from typing import List, Optional
from sqlalchemy.orm import Session
from domain.usuarios.entities import Usuario
from domain.usuarios.repositories import UsuarioRepository
from api.db.models import UsuarioModel

class SQLAlchemyUsuarioRepository(UsuarioRepository):
    def __init__(self, session: Session):
        self.session = session

    def _to_entity(self, model: UsuarioModel) -> Usuario:
        if not model:
            return None
        return Usuario(
            id=model.id,
            nome=model.nome,
            telefone=model.telefone,
            senha_hash=model.senha_hash,
            perfil=model.perfil,
            status=model.status,
            nota_admin=model.nota_admin,
            nota_galera_media=model.nota_galera_media,
            pontos_ranking=model.pontos_ranking
        )

    def _to_model(self, entity: Usuario) -> UsuarioModel:
        return UsuarioModel(
            id=entity.id,
            nome=entity.nome,
            telefone=entity.telefone,
            senha_hash=entity.senha_hash,
            perfil=entity.perfil,
            status=entity.status,
            nota_admin=entity.nota_admin,
            nota_galera_media=entity.nota_galera_media,
            pontos_ranking=entity.pontos_ranking
        )

    async def buscar_por_id(self, usuario_id: int) -> Optional[Usuario]:
        model = self.session.query(UsuarioModel).filter(UsuarioModel.id == usuario_id).first()
        return self._to_entity(model)

    async def buscar_por_telefone(self, telefone: str) -> Optional[Usuario]:
        model = self.session.query(UsuarioModel).filter(UsuarioModel.telefone == telefone).first()
        return self._to_entity(model)

    async def listar_todos(self) -> List[Usuario]:
        models = self.session.query(UsuarioModel).all()
        return [self._to_entity(m) for m in models]

    async def salvar(self, usuario: Usuario) -> Usuario:
        model = self._to_model(usuario)
        if model.id:
            model = self.session.merge(model)
        else:
            self.session.add(model)
        
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    async def deletar(self, usuario_id: int) -> bool:
        model = self.session.query(UsuarioModel).filter(UsuarioModel.id == usuario_id).first()
        if model:
            self.session.delete(model)
            self.session.commit()
            return True
        return False

    async def atualizar_lote(self, usuarios: List[Usuario]) -> bool:
        if not usuarios:
            return True

        models = [self._to_model(u) for u in usuarios]
        for model in models:
            if model.id:
                self.session.merge(model)
            else:
                self.session.add(model)

        self.session.commit()
        return True
