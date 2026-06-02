from typing import List, Optional
from datetime import datetime, date, time
from sqlalchemy import String, Integer, Float, Boolean, Date, Time, DateTime, Enum as SQLEnum, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from domain.usuarios.enums import PerfilUsuario, StatusUsuario
from domain.eventos.enums import StatusEvento
from domain.presencas.enums import StatusJogo, Posicao
from domain.votos.enums import CategoriaVoto
from domain.financeiro.enums import StatusPagamento
import enum

class TipoNota(str, enum.Enum):
    ADMIN = "ADMIN"
    GALERA = "GALERA"

class Base(DeclarativeBase):
    pass

class UsuarioModel(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String)
    telefone: Mapped[str] = mapped_column(String, unique=True)
    senha_hash: Mapped[str] = mapped_column(String)
    perfil: Mapped[PerfilUsuario] = mapped_column(SQLEnum(PerfilUsuario))
    status: Mapped[StatusUsuario] = mapped_column(SQLEnum(StatusUsuario))
    nota_admin: Mapped[int] = mapped_column(Integer, default=5)
    pontos_ranking: Mapped[int] = mapped_column(Integer)
    foto_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    atualizado_em: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    # Relacionamentos bidirecionais
    presencas: Mapped[List["PresencaModel"]] = relationship(
        back_populates="usuario", cascade="all, delete-orphan", passive_deletes=True
    )
    votos_feitos: Mapped[List["VotoModel"]] = relationship(
        back_populates="eleitor", foreign_keys="[VotoModel.eleitor_id]", cascade="all, delete-orphan", passive_deletes=True
    )
    votos_recebidos: Mapped[List["VotoModel"]] = relationship(
        back_populates="candidato", foreign_keys="[VotoModel.candidato_id]", cascade="all, delete-orphan", passive_deletes=True
    )
    financeiro: Mapped[List["FinanceiroModel"]] = relationship(
        back_populates="usuario", passive_deletes=True
    )
    premios: Mapped[List["PremioModel"]] = relationship(
        back_populates="usuario", cascade="all, delete-orphan", passive_deletes=True
    )
    notas_recebidas: Mapped[List["NotaModel"]] = relationship(
        back_populates="avaliado", foreign_keys="[NotaModel.avaliado_id]", cascade="all, delete-orphan", passive_deletes=True
    )
    notas_dadas: Mapped[List["NotaModel"]] = relationship(
        back_populates="avaliador", foreign_keys="[NotaModel.avaliador_id]", passive_deletes=True
    )
    push_subscriptions: Mapped[List["PushSubscriptionModel"]] = relationship(
        back_populates="usuario", cascade="all, delete-orphan", passive_deletes=True
    )

class PremioModel(Base):
    __tablename__ = "premios"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"))
    evento_id: Mapped[int] = mapped_column(ForeignKey("eventos.id", ondelete="CASCADE"))
    categoria: Mapped[CategoriaVoto] = mapped_column(SQLEnum(CategoriaVoto))
    mes_referencia: Mapped[str] = mapped_column(String)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    usuario: Mapped["UsuarioModel"] = relationship(back_populates="premios")
    evento: Mapped["EventoModel"] = relationship(back_populates="premios")

class NotaModel(Base):
    __tablename__ = "notas"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    avaliado_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"))
    avaliador_id: Mapped[Optional[int]] = mapped_column(ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)
    evento_id: Mapped[Optional[int]] = mapped_column(ForeignKey("eventos.id", ondelete="CASCADE"), nullable=True)
    nota: Mapped[int] = mapped_column(Integer)
    tipo: Mapped[TipoNota] = mapped_column(SQLEnum(TipoNota))
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    avaliado: Mapped["UsuarioModel"] = relationship(back_populates="notas_recebidas", foreign_keys=[avaliado_id])
    avaliador: Mapped[Optional["UsuarioModel"]] = relationship(back_populates="notas_dadas", foreign_keys=[avaliador_id])
    evento: Mapped[Optional["EventoModel"]] = relationship(back_populates="notas")

class EventoModel(Base):
    __tablename__ = "eventos"

    id: Mapped[int] = mapped_column(primary_key=True)
    data_jogo: Mapped[date] = mapped_column(Date)
    hora_inicio: Mapped[time] = mapped_column(Time)
    hora_fim: Mapped[time] = mapped_column(Time)
    status_evento: Mapped[StatusEvento] = mapped_column(SQLEnum(StatusEvento))
    flag_churrasco: Mapped[bool] = mapped_column(Boolean)
    valor_churrasco: Mapped[float] = mapped_column(Float)
    endereco: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    chave_pix: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    valor_mensalidade: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=60.0)
    custo_quadra: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=0.0)
    
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    atualizado_em: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    # Relacionamentos bidirecionais
    presencas: Mapped[List["PresencaModel"]] = relationship(
        back_populates="evento", cascade="all, delete-orphan", passive_deletes=True
    )
    votos: Mapped[List["VotoModel"]] = relationship(
        back_populates="evento", cascade="all, delete-orphan", passive_deletes=True
    )
    premios: Mapped[List["PremioModel"]] = relationship(
        back_populates="evento", cascade="all, delete-orphan", passive_deletes=True
    )
    notas: Mapped[List["NotaModel"]] = relationship(
        back_populates="evento", cascade="all, delete-orphan", passive_deletes=True
    )

class PresencaModel(Base):
    __tablename__ = "presencas"
    __table_args__ = (
        UniqueConstraint("usuario_id", "evento_id", name="uq_presenca_usuario_evento"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"))
    evento_id: Mapped[int] = mapped_column(ForeignKey("eventos.id", ondelete="CASCADE"))
    status_jogo: Mapped[StatusJogo] = mapped_column(SQLEnum(StatusJogo))
    posicao: Mapped[Posicao] = mapped_column(SQLEnum(Posicao))
    vai_churrasco: Mapped[bool] = mapped_column(Boolean)
    checkin_validado: Mapped[bool] = mapped_column(Boolean)
    falta_penalizada: Mapped[bool] = mapped_column(Boolean)
    gols: Mapped[int] = mapped_column(Integer, default=0, server_default='0')
    
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    atualizado_em: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    # Relacionamentos bidirecionais
    usuario: Mapped["UsuarioModel"] = relationship(back_populates="presencas")
    evento: Mapped["EventoModel"] = relationship(back_populates="presencas")

class VotoModel(Base):
    __tablename__ = "votos"
    __table_args__ = (
        UniqueConstraint("evento_id", "eleitor_id", "categoria", name="uq_voto_evento_eleitor_categoria"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    evento_id: Mapped[int] = mapped_column(ForeignKey("eventos.id", ondelete="CASCADE"))
    eleitor_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"))
    candidato_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"))
    categoria: Mapped[CategoriaVoto] = mapped_column(SQLEnum(CategoriaVoto))
    
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    atualizado_em: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    # Relacionamentos bidirecionais
    evento: Mapped["EventoModel"] = relationship(back_populates="votos")
    eleitor: Mapped["UsuarioModel"] = relationship(back_populates="votos_feitos", foreign_keys=[eleitor_id])
    candidato: Mapped["UsuarioModel"] = relationship(back_populates="votos_recebidos", foreign_keys=[candidato_id])

class FinanceiroModel(Base):
    __tablename__ = "financeiro"
    __table_args__ = (
        UniqueConstraint("usuario_id", "tipo", "mes_referencia", name="uq_financeiro_usuario_tipo_mes"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[Optional[int]] = mapped_column(ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)
    tipo: Mapped[str] = mapped_column(String)
    valor: Mapped[float] = mapped_column(Float)
    status_pagamento: Mapped[StatusPagamento] = mapped_column(SQLEnum(StatusPagamento))
    mes_referencia: Mapped[str] = mapped_column(String, default="2026-05")
    
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    atualizado_em: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    # Relacionamentos bidirecionais
    usuario: Mapped[Optional["UsuarioModel"]] = relationship(back_populates="financeiro")

class PushSubscriptionModel(Base):
    __tablename__ = "push_subscriptions"
    __table_args__ = (
        UniqueConstraint("usuario_id", "subscription_json", name="uq_push_subscription"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"))
    subscription_json: Mapped[str] = mapped_column(String)
    
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    # Relacionamentos bidirecionais
    usuario: Mapped["UsuarioModel"] = relationship(back_populates="push_subscriptions")
