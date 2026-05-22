from sqlalchemy.orm import configure_mappers
from api.db.models import (
    Base, UsuarioModel, EventoModel, PresencaModel, VotoModel, FinanceiroModel
)

def test_models_mapper_configuration():
    # Isso levanta erro se houver falhas no mapeamento das foreign keys ou relacionamentos no SQLAlchemy
    try:
        configure_mappers()
        mappers_configured = True
    except Exception as e:
        mappers_configured = False
        assert False, f"Falha na configuração do SQLAlchemy Mapper: {str(e)}"
    
    assert mappers_configured is True

def test_models_have_correct_table_names():
    assert UsuarioModel.__tablename__ == "usuarios"
    assert EventoModel.__tablename__ == "eventos"
    assert PresencaModel.__tablename__ == "presencas"
    assert VotoModel.__tablename__ == "votos"
    assert FinanceiroModel.__tablename__ == "financeiro"
