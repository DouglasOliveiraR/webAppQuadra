from typing import List, Optional
from sqlalchemy.orm import Session
from domain.usuarios.entities import Usuario, UsuarioRanking
from domain.usuarios.repositories import UsuarioRepository
from api.db.models import UsuarioModel

class SQLAlchemyUsuarioRepository(UsuarioRepository):
    def __init__(self, session: Session):
        self.session = session

    async def obter_ranking_agrupado(self) -> List[UsuarioRanking]:
        from api.db.models import PremioModel, NotaModel, TipoNota
        from domain.usuarios.enums import StatusUsuario
        from sqlalchemy import func
        from collections import defaultdict

        # 1. Fetch the aggregated data directly using SQLAlchemy
        # Subquery for notes
        subq_notas = self.session.query(
            NotaModel.avaliado_id.label('uid'),
            func.avg(NotaModel.nota).label('media')
        ).filter(NotaModel.tipo == TipoNota.GALERA).group_by(NotaModel.avaliado_id).subquery()

        # Join UsuarioModel with subq_notas
        usuarios_com_notas = self.session.query(
            UsuarioModel,
            subq_notas.c.media
        ).outerjoin(
            subq_notas, UsuarioModel.id == subq_notas.c.uid
        ).filter(
            UsuarioModel.status == StatusUsuario.ATIVO
        ).all()

        if not usuarios_com_notas:
            return []

        # Get the IDs of the active users
        usuarios_ids = [u.UsuarioModel.id for u in usuarios_com_notas]

        # 2. Fetch the aggregated prizes using SQLAlchemy grouping
        premios_agrupados = self.session.query(
            PremioModel.usuario_id,
            PremioModel.categoria,
            func.count(PremioModel.id).label('quantidade')
        ).filter(
            PremioModel.usuario_id.in_(usuarios_ids)
        ).group_by(
            PremioModel.usuario_id, PremioModel.categoria
        ).all()

        # 2.5 Fetch aggregated goals using SQLAlchemy grouping
        from api.db.models import PresencaModel
        gols_agrupados = self.session.query(
            PresencaModel.usuario_id,
            func.sum(PresencaModel.gols).label('total_gols')
        ).filter(
            PresencaModel.usuario_id.in_(usuarios_ids)
        ).group_by(
            PresencaModel.usuario_id
        ).all()

        gols_map = {g.usuario_id: (g.total_gols or 0) for g in gols_agrupados}

        # Build prize map
        premios_map = defaultdict(list)
        for premio in premios_agrupados:
            premios_map[premio.usuario_id].append({
                "categoria": premio.categoria.value,
                "quantidade": premio.quantidade
            })

        # 3. Assemble and sort
        resultado = []
        for u, media in usuarios_com_notas:
            nota_galera = float(media) if media is not None else 0.0

            ranking_obj = UsuarioRanking(
                id=u.id,
                nome=u.nome,
                pontos_ranking=u.pontos_ranking,
                nota_admin=u.nota_admin,
                nota_galera_media=nota_galera,
                foto_url=u.foto_url,
                premios=premios_map.get(u.id, []),
                gols_total=gols_map.get(u.id, 0)
            )
            resultado.append(ranking_obj)

        resultado.sort(key=lambda u: (u.pontos_ranking, u.nota_galera_media), reverse=True)
        return resultado

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
        from domain.usuarios.enums import StatusUsuario
        models = self.session.query(UsuarioModel).filter(UsuarioModel.status != StatusUsuario.INATIVO).all()
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

    async def salvar_lote(self, usuarios: List[Usuario]) -> List[Usuario]:
        if not usuarios:
            return []
        model_list = []
        for usuario in usuarios:
            model = self._to_model(usuario)
            if model.id:
                model = self.session.merge(model)
            else:
                self.session.add(model)
            model_list.append(model)

        # Flush to DB to populate IDs without committing and expiring the models
        self.session.flush()

        # Now we can safely grab the IDs because they are assigned and models are not expired
        model_ids = [m.id for m in model_list if m.id is not None]

        self.session.commit()

        # Avoid N+1 queries by bulk fetching the refreshed models
        if model_ids:
            fetched_models = self.session.query(UsuarioModel).filter(UsuarioModel.id.in_(model_ids)).all()
            model_dict = {m.id: m for m in fetched_models}

            # Maintain the original order, including any potential duplicates from the input
            model_list = [model_dict[model_id] for model_id in model_ids if model_id in model_dict]

        return [self._to_entity(m) for m in model_list]

    async def deletar(self, usuario_id: int) -> bool:
        model = self.session.query(UsuarioModel).filter(UsuarioModel.id == usuario_id).first()
        if model:
            self.session.delete(model)
            self.session.commit()
            return True
        return False

    async def deletar_lote(self, usuario_ids: List[int]) -> bool:
        if not usuario_ids:
            return False
        result = self.session.query(UsuarioModel).filter(UsuarioModel.id.in_(usuario_ids)).delete(synchronize_session=False)
        self.session.commit()
        return result > 0

    async def deletar_por_perfil(self, perfil: 'PerfilUsuario') -> bool:
        result = self.session.query(UsuarioModel).filter(UsuarioModel.perfil == perfil).delete(synchronize_session=False)
        self.session.commit()
        return result > 0
