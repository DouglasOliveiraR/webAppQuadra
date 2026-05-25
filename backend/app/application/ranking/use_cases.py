from typing import List, Dict
from domain.usuarios.repositories import UsuarioRepository
from domain.premios.repositories import PremioRepository
from collections import Counter

class ListarRankingUseCase:
    def __init__(self, usuario_repo: UsuarioRepository, premio_repo: PremioRepository):
        self.usuario_repo = usuario_repo
        self.premio_repo = premio_repo

    async def executar(self) -> List[Dict]:
        usuarios = await self.usuario_repo.listar_todos()
        
        # Obter todos os prêmios para não sobrecarregar com queries
        todos_premios = await self.premio_repo.listar_todos()
        
        # Agrupar prêmios por usuário e categoria
        premios_por_usuario = {}
        for p in todos_premios:
            if p.usuario_id not in premios_por_usuario:
                premios_por_usuario[p.usuario_id] = []
            premios_por_usuario[p.usuario_id].append(p.categoria.value)

        # Ordenar os usuários
        usuarios_ordenados = sorted(
            usuarios, 
            key=lambda u: (u.pontos_ranking, u.nota_galera_media), 
            reverse=True
        )
        
        resultado = []
        for u in usuarios_ordenados:
            categorias_ganhas = premios_por_usuario.get(u.id, [])
            contagem = Counter(categorias_ganhas)
            premios_list = [{"categoria": k, "quantidade": v} for k, v in contagem.items()]
            
            resultado.append({
                "id": u.id,
                "nome": u.nome,
                "pontos_ranking": u.pontos_ranking,
                "nota_admin": u.nota_admin,
                "nota_galera_media": u.nota_galera_media,
                "foto_url": u.foto_url,
                "premios": premios_list
            })
            
        return resultado
