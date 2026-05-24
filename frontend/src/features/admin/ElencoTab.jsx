import React, { useState, useEffect } from 'react';
import api from '../../services/api';
import { showToast } from '../../components/ui/Toast';

export function ElencoTab() {
  const [jogadores, setJogadores] = useState([]);
  const [loading, setLoading] = useState(true);
  const [busca, setBusca] = useState('');
  
  // Modal states
  const [modalOpen, setModalOpen] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  
  // Form states
  const [idEdicao, setIdEdicao] = useState(null);
  const [nome, setNome] = useState('');
  const [telefone, setTelefone] = useState('');
  const [perfil, setPerfil] = useState('AVULSO');
  const [statusJogador, setStatusJogador] = useState('ATIVO');
  const [notaAdmin, setNotaAdmin] = useState(5);

  const fetchElenco = async () => {
    try {
      const response = await api.get('/usuarios');
      setJogadores(response.data);
    } catch (err) {
      console.error('Erro ao buscar elenco', err);
      showToast('Erro ao carregar lista de jogadores.', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchElenco();
  }, []);

  const handleNovoJogador = () => {
    setIsEditing(false);
    setIdEdicao(null);
    setNome('');
    setTelefone('');
    setPerfil('AVULSO');
    setStatusJogador('ATIVO');
    setNotaAdmin(5);
    setModalOpen(true);
  };

  const handleEditarJogador = (jogador) => {
    setIsEditing(true);
    setIdEdicao(jogador.id);
    setNome(jogador.nome);
    setTelefone(jogador.telefone || '');
    setPerfil(jogador.perfil || 'AVULSO');
    setStatusJogador(jogador.status || 'ATIVO');
    setNotaAdmin(jogador.nota_admin ?? 5);
    setModalOpen(true);
  };

  const handleSalvarJogador = async () => {
    if (!nome.trim() || !telefone.trim()) {
      showToast('Nome e Telefone são obrigatórios.', 'error');
      return;
    }

    try {
      const payload = {
        nome,
        telefone,
        perfil,
        nota_admin: notaAdmin
      };

      if (isEditing) {
        await api.put(`/usuarios/${idEdicao}`, {
          ...payload,
          status: statusJogador
        });
        showToast('Jogador atualizado com sucesso!');
      } else {
        await api.post('/usuarios', payload);
        showToast('Jogador cadastrado com sucesso!');
      }
      
      setModalOpen(false);
      fetchElenco();
    } catch (err) {
      const msg = err.response?.data?.detail || 'Erro ao salvar jogador.';
      showToast(msg, 'error');
    }
  };

  const filteredJogadores = jogadores.filter(j => 
    j.nome.toLowerCase().includes(busca.toLowerCase())
  );

  const ativos = filteredJogadores.filter(j => j.status === 'ATIVO');
  const inativos = filteredJogadores.filter(j => j.status === 'INATIVO');

  if (loading) {
    return <div className="py-10 flex justify-center"><div className="animate-spin rounded-full h-8 w-8 border-4 border-primary border-t-transparent"></div></div>;
  }

  return (
    <div className="space-y-6 fade-in">
      <button 
        onClick={handleNovoJogador}
        className="w-full py-4 bg-primary text-on-primary rounded-xl font-headline-md text-headline-md shadow-lg hover:bg-primary/90 active:scale-95 transition-all flex items-center justify-center gap-2"
      >
        <span className="material-symbols-outlined">person_add</span>
        + Cadastrar Novo Jogador
      </button>

      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-on-surface-variant">
          <span className="material-symbols-outlined">search</span>
        </div>
        <input 
          type="text" 
          placeholder="Buscar jogador..." 
          value={busca}
          onChange={(e) => setBusca(e.target.value)}
          className="block w-full pl-10 pr-3 py-3 bg-surface-container-low border border-outline-variant/30 rounded-lg focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all font-body-md text-on-surface"
        />
      </div>

      <div>
        <h3 className="font-label-bold text-label-bold text-tertiary mb-3 uppercase tracking-wider">Jogadores Ativos</h3>
        <div className="space-y-3">
          {ativos.map(jogador => (
            <div key={jogador.id} className="glass-panel rounded-xl p-4 flex justify-between items-center shadow-ambient-1 border border-outline-variant/30 hover:border-primary/50 transition-colors">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-full bg-surface-variant flex items-center justify-center text-on-surface-variant font-bold text-lg shrink-0">
                  {jogador.nome.charAt(0)}
                </div>
                <div>
                  <h4 className="font-headline-md text-[16px] text-on-surface">{jogador.nome}</h4>
                  <div className="flex items-center gap-2 text-[12px] font-bold text-primary mt-1">
                    <span className="w-2 h-2 rounded-full bg-primary"></span>
                    {jogador.perfil}
                  </div>
                  <div className="text-[11px] text-tertiary mt-0.5">
                    Nota Técnica: <span className="font-bold text-primary">{jogador.nota_admin}</span>
                  </div>
                </div>
              </div>
              <button 
                onClick={() => handleEditarJogador(jogador)}
                className="w-8 h-8 rounded-full flex items-center justify-center text-on-surface-variant hover:bg-surface-variant/50 transition-colors"
              >
                <span className="material-symbols-outlined">edit_note</span>
              </button>
            </div>
          ))}
          {ativos.length === 0 && <p className="text-body-sm text-tertiary">Nenhum jogador ativo encontrado.</p>}
        </div>
      </div>

      <div>
        <h3 className="font-label-bold text-label-bold text-tertiary mb-3 mt-8 uppercase tracking-wider">Lesionados / Inativos</h3>
        <div className="space-y-3">
          {inativos.map(jogador => (
            <div key={jogador.id} className="glass-panel rounded-xl p-4 flex justify-between items-center shadow-ambient-1 border border-outline-variant/30 hover:border-error/50 transition-colors bg-surface-container-low/50">
              <div className="flex items-center gap-3 opacity-70">
                <div className="w-12 h-12 rounded-full bg-surface-variant flex items-center justify-center text-on-surface-variant font-bold text-lg shrink-0 grayscale filter">
                  {jogador.nome.charAt(0)}
                </div>
                <div>
                  <h4 className="font-headline-md text-[16px] text-on-surface">{jogador.nome}</h4>
                  <div className="flex items-center gap-2 text-[12px] font-bold text-error mt-1">
                    <span className="w-2 h-2 rounded-full bg-error"></span>
                    {jogador.perfil} • Inativo
                  </div>
                </div>
              </div>
              <button 
                onClick={() => handleEditarJogador(jogador)}
                className="w-8 h-8 rounded-full flex items-center justify-center text-on-surface-variant hover:bg-surface-variant/50 transition-colors"
              >
                <span className="material-symbols-outlined">edit_note</span>
              </button>
            </div>
          ))}
          {inativos.length === 0 && <p className="text-body-sm text-tertiary">Nenhum jogador inativo encontrado.</p>}
        </div>
      </div>

      {/* Modal de Cadastro e Edição de Jogador */}
      {modalOpen && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[100] flex items-center justify-center p-4 animate-fade-in">
          <div className="bg-surface dark:bg-surface-dim rounded-2xl w-full max-w-sm p-6 shadow-2xl border border-outline-variant/30 animate-scale-up space-y-4 max-h-[90vh] overflow-y-auto">
            {/* Header */}
            <div className="flex justify-between items-center border-b border-outline-variant/20 pb-3">
              <div className="flex items-center gap-2">
                <span className="material-symbols-outlined text-[24px] text-primary">
                  {isEditing ? 'edit_note' : 'person_add'}
                </span>
                <h3 className="font-headline-sm text-headline-sm text-on-surface font-bold">
                  {isEditing ? 'Editar Jogador' : 'Novo Jogador'}
                </h3>
              </div>
              <button 
                onClick={() => setModalOpen(false)}
                className="w-8 h-8 rounded-full bg-surface-container-low flex items-center justify-center text-on-surface-variant hover:bg-surface-variant transition-colors"
              >
                <span className="material-symbols-outlined text-[20px]">close</span>
              </button>
            </div>

            {/* Form */}
            <div className="space-y-4">
              <div className="space-y-1">
                <label className="block font-label-bold text-label-bold text-on-surface-variant uppercase tracking-wider text-[11px]">Nome</label>
                <input 
                  type="text" 
                  value={nome}
                  onChange={(e) => setNome(e.target.value)}
                  placeholder="Nome do Jogador"
                  className="block w-full px-3 py-3 bg-[#F1F5F9] dark:bg-surface-lowest border-transparent rounded-lg focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all font-body-md text-on-surface"
                />
              </div>

              <div className="space-y-1">
                <label className="block font-label-bold text-label-bold text-on-surface-variant uppercase tracking-wider text-[11px]">Telefone</label>
                <input 
                  type="text" 
                  value={telefone}
                  onChange={(e) => setTelefone(e.target.value)}
                  placeholder="Ex: 11999999999"
                  className="block w-full px-3 py-3 bg-[#F1F5F9] dark:bg-surface-lowest border-transparent rounded-lg focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all font-body-md text-on-surface"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="block font-label-bold text-label-bold text-on-surface-variant uppercase tracking-wider text-[11px]">Perfil</label>
                  <select 
                    value={perfil} 
                    onChange={(e) => setPerfil(e.target.value)}
                    className="block w-full px-3 py-3 bg-[#F1F5F9] dark:bg-surface-lowest border-transparent rounded-lg focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all font-body-md text-on-surface"
                  >
                    <option value="AVULSO">Avulso</option>
                    <option value="MENSALISTA">Mensalista</option>
                    <option value="ADMIN">Admin</option>
                  </select>
                </div>

                <div className="space-y-1">
                  <label className="block font-label-bold text-label-bold text-on-surface-variant uppercase tracking-wider text-[11px]">Status</label>
                  <select 
                    value={statusJogador} 
                    disabled={!isEditing}
                    onChange={(e) => setStatusJogador(e.target.value)}
                    className="block w-full px-3 py-3 bg-[#F1F5F9] dark:bg-surface-lowest border-transparent rounded-lg focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all font-body-md text-on-surface disabled:opacity-50"
                  >
                    <option value="ATIVO">Ativo</option>
                    <option value="INATIVO">Inativo</option>
                  </select>
                </div>
              </div>

              {/* Slider de Nota Secreta */}
              <div className="space-y-1 pt-2 border-t border-outline-variant/10">
                <div className="flex justify-between items-center mb-1">
                  <label className="block font-label-bold text-label-bold text-on-surface-variant uppercase tracking-wider text-[11px]">Nota Técnica Secreta</label>
                  <span className="text-[20px] font-bold text-primary">{notaAdmin}</span>
                </div>
                <input 
                  type="range" 
                  min="0" 
                  max="10" 
                  step="1" 
                  value={notaAdmin}
                  onChange={(e) => setNotaAdmin(parseInt(e.target.value))}
                  className="w-full h-2 bg-surface-variant rounded-lg appearance-none cursor-pointer accent-primary"
                  style={{
                    background: `linear-gradient(to right, var(--color-primary) ${(notaAdmin / 10) * 100}%, var(--color-surface-variant) ${(notaAdmin / 10) * 100}%)`
                  }}
                />
                <div className="flex justify-between text-[10px] font-bold text-on-surface-variant/70 mt-1">
                  <span>Perna de Pau (0)</span>
                  <span>Craque (10)</span>
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-3 pt-3">
              <button 
                onClick={() => setModalOpen(false)}
                className="flex-1 py-3 border-2 border-outline-variant text-on-surface rounded-xl font-label-bold text-label-bold hover:bg-surface-variant/50 transition-colors"
              >
                Cancelar
              </button>
              <button 
                onClick={handleSalvarJogador}
                className="flex-1 py-3 bg-primary text-on-primary rounded-xl font-label-bold text-label-bold hover:bg-primary/90 transition-colors"
              >
                Salvar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
