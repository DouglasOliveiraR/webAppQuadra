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
            
        from api.db.models import NotaModel, TipoNota
        from sqlalchemy import func
        
        # Nota Galera Media (calculada dinamicamente pois removemos a coluna)
        nota_galera_query = self.session.query(func.avg(NotaModel.nota)).filter(
            NotaModel.avaliado_id == model.id,
            NotaModel.tipo == TipoNota.GALERA
        ).first()
        nota_galera_media_val = float(nota_galera_query[0]) if nota_galera_query and nota_galera_query[0] is not None else 0.0

        return Usuario(
            id=model.id,
            nome=model.nome,
            telefone=model.telefone,
            senha_hash=model.senha_hash,
            perfil=model.perfil,
            status=model.status,
            nota_admin=model.nota_admin,
            nota_galera_media=nota_galera_media_val,
            pontos_ranking=model.pontos_ranking,
            foto_url=model.foto_url,
            criado_em=model.criado_em,
            atualizado_em=model.atualizado_em
        )

    def _to_model(self, entity: Usuario) -> UsuarioModel:
        model = UsuarioModel(
            id=entity.id,
            nome=entity.nome,
            telefone=entity.telefone,
            senha_hash=entity.senha_hash,
            perfil=entity.perfil,
            status=entity.status,
            nota_admin=entity.nota_admin,
            pontos_ranking=entity.pontos_ranking,
            foto_url=entity.foto_url
        )
        if entity.criado_em:
            model.criado_em = entity.criado_em
        if entity.atualizado_em:
            model.atualizado_em = entity.atualizado_em
        return model

    async def buscar_por_id(self, usuario_id: int) -> Optional[Usuario]:
        model = self.session.query(UsuarioModel).filter(UsuarioModel.id == usuario_id).first()
        return self._to_entity(model)

    async def buscar_por_telefone(self, telefone: str) -> Optional[Usuario]:
        model = self.session.query(UsuarioModel).filter(UsuarioModel.telefone == telefone).first()
        return self._to_entity(model)

    async def buscar_por_ids(self, usuario_ids: List[int]) -> List[Usuario]:
        if not usuario_ids:
            return []
        models = self.session.query(UsuarioModel).filter(UsuarioModel.id.in_(usuario_ids)).all()
        return [self._to_entity(m) for m in models]

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
