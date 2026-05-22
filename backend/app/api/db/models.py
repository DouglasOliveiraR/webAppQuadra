from typing import List, Optional
from datetime import date, time
from sqlalchemy import String, Integer, Float, Boolean, Date, Time, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from domain.usuarios.enums import PerfilUsuario, StatusUsuario
from domain.eventos.enums import StatusEvento
from domain.presencas.enums import StatusJogo, Posicao
from domain.votos.enums import CategoriaVoto
from domain.financeiro.enums import StatusPagamento

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
    nota_admin: Mapped[float] = mapped_column(Float)
    nota_galera_media: Mapped[float] = mapped_column(Float)
    pontos_ranking: Mapped[int] = mapped_column(Integer)

    # Relacionamentos bidirecionais
    presencas: Mapped[List["PresencaModel"]] = relationship(back_populates="usuario")
    votos_feitos: Mapped[List["VotoModel"]] = relationship(
        back_populates="eleitor", foreign_keys="[VotoModel.eleitor_id]"
    )
    votos_recebidos: Mapped[List["VotoModel"]] = relationship(
        back_populates="candidato", foreign_keys="[VotoModel.candidato_id]"
    )
    financeiro: Mapped[List["FinanceiroModel"]] = relationship(back_populates="usuario")

class EventoModel(Base):
    __tablename__ = "eventos"

    id: Mapped[int] = mapped_column(primary_key=True)
    data_jogo: Mapped[date] = mapped_column(Date)
    hora_inicio: Mapped[time] = mapped_column(Time)
    hora_fim: Mapped[time] = mapped_column(Time)
    status_evento: Mapped[StatusEvento] = mapped_column(SQLEnum(StatusEvento))
    flag_churrasco: Mapped[bool] = mapped_column(Boolean)
    valor_churrasco: Mapped[float] = mapped_column(Float)

    # Relacionamentos bidirecionais
    presencas: Mapped[List["PresencaModel"]] = relationship(back_populates="evento")
    votos: Mapped[List["VotoModel"]] = relationship(back_populates="evento")

class PresencaModel(Base):
    __tablename__ = "presencas"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    evento_id: Mapped[int] = mapped_column(ForeignKey("eventos.id"))
    status_jogo: Mapped[StatusJogo] = mapped_column(SQLEnum(StatusJogo))
    posicao: Mapped[Posicao] = mapped_column(SQLEnum(Posicao))
    vai_churrasco: Mapped[bool] = mapped_column(Boolean)
    checkin_validado: Mapped[bool] = mapped_column(Boolean)
    falta_penalizada: Mapped[bool] = mapped_column(Boolean)

    # Relacionamentos bidirecionais
    usuario: Mapped["UsuarioModel"] = relationship(back_populates="presencas")
    evento: Mapped["EventoModel"] = relationship(back_populates="presencas")

class VotoModel(Base):
    __tablename__ = "votos"

    id: Mapped[int] = mapped_column(primary_key=True)
    evento_id: Mapped[int] = mapped_column(ForeignKey("eventos.id"))
    eleitor_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    candidato_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    categoria: Mapped[CategoriaVoto] = mapped_column(SQLEnum(CategoriaVoto))

    # Relacionamentos bidirecionais
    evento: Mapped["EventoModel"] = relationship(back_populates="votos")
    eleitor: Mapped["UsuarioModel"] = relationship(back_populates="votos_feitos", foreign_keys=[eleitor_id])
    candidato: Mapped["UsuarioModel"] = relationship(back_populates="votos_recebidos", foreign_keys=[candidato_id])

class FinanceiroModel(Base):
    __tablename__ = "financeiro"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[Optional[int]] = mapped_column(ForeignKey("usuarios.id"), nullable=True)
    tipo: Mapped[str] = mapped_column(String)
    valor: Mapped[float] = mapped_column(Float)
    status_pagamento: Mapped[StatusPagamento] = mapped_column(SQLEnum(StatusPagamento))

    # Relacionamentos bidirecionais
    usuario: Mapped[Optional["UsuarioModel"]] = relationship(back_populates="financeiro")
