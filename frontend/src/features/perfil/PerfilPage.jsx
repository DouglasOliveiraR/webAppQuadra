import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import api, { API_URL, getFotoUrl } from '../../services/api';
import { showToast } from '../../components/ui/Toast';
import Cropper from 'react-easy-crop';
import { getCroppedImg } from './cropImage';
import { usePushNotifications } from '../../hooks/usePushNotifications';

export function PerfilPage() {
  const navigate = useNavigate();
  const [meusDados, setMeusDados] = useState(null);
  const [loading, setLoading] = useState(true);

  // States para o modal de alterar senha
  const [showSenhaModal, setShowSenhaModal] = useState(false);
  const [senhaAtual, setSenhaAtual] = useState('');
  const [novaSenha, setNovaSenha] = useState('');
  const [confirmarNovaSenha, setConfirmarNovaSenha] = useState('');
  const [loadingSenha, setLoadingSenha] = useState(false);
  const [erroSenhaAtual, setErroSenhaAtual] = useState('');

  // Refs e states para upload de foto
  const fileInputRef = useRef(null);
  const [uploadingFoto, setUploadingFoto] = useState(false);
  const [imageSrc, setImageSrc] = useState(null);
  const [crop, setCrop] = useState({ x: 0, y: 0 });
  const [zoom, setZoom] = useState(1);
  const [croppedAreaPixels, setCroppedAreaPixels] = useState(null);

  const { isSupported, permission, subscribeToPush, loading: loadingPush } = usePushNotifications();

  const handleAbrirModalSenha = () => {
    setSenhaAtual('');
    setNovaSenha('');
    setConfirmarNovaSenha('');
    setErroSenhaAtual('');
    setShowSenhaModal(true);
  };

  // Extract info from token
  const token = localStorage.getItem('token');
  let currentUserId = null;
  let nomeBase = 'Jogador';
  let perfilTipo = 'AVULSO';

  if (token) {
    try {
      const payloadBase64 = token.split('.')[1];
      const decodedPayload = JSON.parse(atob(payloadBase64));
      currentUserId = parseInt(decodedPayload.sub);
      nomeBase = decodedPayload.nome || 'Jogador';
      perfilTipo = decodedPayload.perfil || 'AVULSO';
    } catch (e) {
      console.error(e);
    }
  }

  useEffect(() => {
    const fetchMe = async () => {
      try {
        // Fetch ranking to get points and stats as a workaround for MVP
        const { data } = await api.get('/ranking');
        const eu = data.find(u => u.id === currentUserId);
        if (eu) {
          setMeusDados(eu);
        }
      } catch (err) {
        console.error('Erro ao buscar meus dados', err);
      } finally {
        setLoading(false);
      }
    };
    fetchMe();
  }, [currentUserId]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
    showToast('Logout realizado com sucesso', 'success');
  };

  const handleAlterarSenha = async (e) => {
    e.preventDefault();
    if (!senhaAtual.trim() || !novaSenha.trim() || !confirmarNovaSenha.trim()) {
      showToast('Todos os campos são obrigatórios.', 'error');
      return;
    }
    if (novaSenha !== confirmarNovaSenha) {
      showToast('A nova senha e a confirmação não conferem.', 'error');
      return;
    }
    if (novaSenha.length < 6) {
      showToast('A nova senha deve ter pelo menos 6 caracteres.', 'error');
      return;
    }

    setLoadingSenha(true);
    setErroSenhaAtual('');
    try {
      await api.put('/usuarios/me/senha', {
        senha_atual: senhaAtual,
        nova_senha: novaSenha
      });
      showToast('Senha alterada com sucesso!');
      setShowSenhaModal(false);
      setSenhaAtual('');
      setNovaSenha('');
      setConfirmarNovaSenha('');
    } catch (err) {
      const msg = err.response?.data?.detail || 'Erro ao alterar senha. Verifique se a senha atual está correta.';
      if (msg === "Senha atual incorreta.") {
        setErroSenhaAtual(msg);
      } else {
        showToast(msg, 'error');
      }
    } finally {
      setLoadingSenha(false);
    }
  };

  const handleFotoSelect = async (e) => {
    let file = e.target.files?.[0];
    if (!file) return;

    const isHeic = file.type === 'image/heic' || file.type === 'image/heif' || file.name.toLowerCase().endsWith('.heic') || file.name.toLowerCase().endsWith('.heif');

    if (!file.type.startsWith('image/') && !isHeic) {
      showToast('Apenas arquivos de imagem são permitidos.', 'error');
      return;
    }

    if (isHeic) {
      setUploadingFoto(true);
      try {
        const heic2any = (await import('heic2any')).default;
        const convertedBlob = await heic2any({
          blob: file,
          toType: "image/jpeg",
          quality: 0.8
        });
        
        // Se a conversão retornar um array (múltiplas imagens no heic), pega a primeira
        const finalBlob = Array.isArray(convertedBlob) ? convertedBlob[0] : convertedBlob;
        file = new File([finalBlob], file.name.replace(/\.heic|\.heif/i, '.jpg'), { type: 'image/jpeg' });
      } catch (err) {
        console.error("Erro ao converter HEIC", err);
        showToast("Formato de imagem da Apple não suportado.", "error");
        setUploadingFoto(false);
        return;
      }
      setUploadingFoto(false);
    }

    const reader = new FileReader();
    reader.addEventListener('load', () => {
      setImageSrc(reader.result);
    });
    reader.readAsDataURL(file);
  };

  const handleFotoConfirm = async () => {
    if (!imageSrc || !croppedAreaPixels) return;

    setUploadingFoto(true);
    try {
      const croppedImageBlob = await getCroppedImg(imageSrc, croppedAreaPixels);
      const file = new File([croppedImageBlob], 'perfil.jpg', { type: 'image/jpeg' });
      
      const formData = new FormData();
      formData.append('file', file);

      const response = await api.post('/usuarios/me/foto', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      showToast('Foto de perfil atualizada com sucesso!');
      localStorage.setItem('foto_timestamp', Date.now().toString());
      const updatedUser = response.data;
      setMeusDados(prev => prev ? { ...prev, foto_url: updatedUser.foto_url } : null);
      
      // Limpa os estados do Cropper
      setImageSrc(null);
      setZoom(1);
      setCrop({ x: 0, y: 0 });
    } catch (err) {
      console.error(err);
      const msg = err.response?.data?.detail || 'Erro ao realizar upload e recorte da imagem.';
      showToast(msg, 'error');
    } finally {
      setUploadingFoto(false);
    }
  };

  const senhasNaoConferem = confirmarNovaSenha && novaSenha !== confirmarNovaSenha;
  const senhaNovaCurta = novaSenha && novaSenha.length < 6;

  const isMensalista = perfilTipo === 'MENSALISTA' || perfilTipo === 'ADMIN';

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-background">
        <div className="animate-spin rounded-full h-10 w-10 border-4 border-primary border-t-transparent"></div>
      </div>
    );
  }

  return (
    <div className="flex flex-col w-full pb-8">
      {/* Header */}
      <header className="flex items-center justify-center py-4 relative mb-6">
        <h2 className="font-headline-md text-headline-md text-primary font-bold text-[20px]">Meu Perfil</h2>
        <button className="absolute right-0 text-primary p-2 rounded-full focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary" aria-label="Notificações">
          <span className="material-symbols-outlined" aria-hidden="true">notifications</span>
        </button>
      </header>

      {/* Avatar & Info */}
      <section className="flex flex-col items-center mb-8">
        <div className="relative mb-4">
          <div className="w-24 h-24 rounded-full bg-surface-variant flex items-center justify-center text-on-surface-variant text-4xl font-bold border-4 border-surface shadow-sm overflow-hidden">
            {uploadingFoto ? (
              <div className="animate-spin rounded-full h-8 w-8 border-4 border-primary border-t-transparent"></div>
            ) : meusDados?.foto_url ? (
              <img 
                src={getFotoUrl(meusDados.foto_url)} 
                alt={nomeBase} 
                className="w-full h-full object-cover animate-fade-in" 
              />
            ) : (
              nomeBase.charAt(0)
            )}
          </div>
          <button 
            onClick={() => fileInputRef.current?.click()}
            disabled={uploadingFoto}
            aria-label="Alterar foto de perfil"
            className="absolute bottom-0 right-0 w-8 h-8 bg-primary rounded-full flex items-center justify-center text-on-primary shadow-md border-2 border-surface hover:bg-primary/90 transition-colors disabled:opacity-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
          >
            <span className="material-symbols-outlined text-[16px]" aria-hidden="true">photo_camera</span>
          </button>
          <input 
            type="file" 
            ref={fileInputRef} 
            onChange={handleFotoSelect} 
            accept="image/jpeg, image/png, image/webp" 
            className="hidden" 
          />
        </div>
        
        <h1 className="font-headline-lg text-headline-lg text-on-surface mb-2">{nomeBase}</h1>
        
        <div className={`px-3 py-1 rounded-full flex items-center gap-1 font-label-bold text-label-bold ${isMensalista ? 'bg-primary text-on-primary' : 'bg-surface-variant text-on-surface-variant'}`}>
          <span className="material-symbols-outlined text-[14px]">verified</span>
          {isMensalista ? 'Mensalista' : 'Avulso'}
        </div>
      </section>

      {/* Trophy Room */}
      <section className="mb-8">
        <h3 className="font-headline-md text-headline-md text-on-surface mb-4">Minha Sala de Troféus</h3>
        
        <div className="grid grid-cols-2 gap-4">
          <div className="glass-panel rounded-xl p-4 flex flex-col items-center justify-center text-center shadow-ambient-1 hover:shadow-ambient-2 transition-shadow">
            <div className="w-12 h-12 rounded-full bg-[#FEF3C7] flex items-center justify-center mb-3">
              <img src="/assets/golden_ball_3d.png" alt="Bola Cheia" className="w-8 h-8 object-contain" />
            </div>
            <span className="font-headline-md text-headline-md font-bold mb-1" aria-hidden="true">{meusDados?.premios?.find(p => p.categoria === 'BOLA_CHEIA')?.quantidade || 0}x</span>
            <span className="font-body-sm text-body-sm text-on-surface-variant" aria-hidden="true">Bola Cheia</span>
            <span className="sr-only">Prêmio Bola Cheia: {meusDados?.premios?.find(p => p.categoria === 'BOLA_CHEIA')?.quantidade || 0} vezes</span>
          </div>

          <div className="glass-panel rounded-xl p-4 flex flex-col items-center justify-center text-center shadow-ambient-1 hover:shadow-ambient-2 transition-shadow">
            <div className="w-12 h-12 rounded-full bg-[#DCFCE7] flex items-center justify-center mb-3">
              <img src="/assets/top_corner_goal_3d.png" alt="Gol Mais Bonito" className="w-8 h-8 object-contain" />
            </div>
            <span className="font-headline-md text-headline-md font-bold mb-1" aria-hidden="true">{meusDados?.premios?.find(p => p.categoria === 'GOL_BONITO')?.quantidade || 0}x</span>
            <span className="font-body-sm text-body-sm text-on-surface-variant" aria-hidden="true">Gol + Bonito</span>
            <span className="sr-only">Prêmio Gol Mais Bonito: {meusDados?.premios?.find(p => p.categoria === 'GOL_BONITO')?.quantidade || 0} vezes</span>
          </div>

          <div className="glass-panel rounded-xl p-4 flex flex-col items-center justify-center text-center shadow-ambient-1 hover:shadow-ambient-2 transition-shadow">
            <div className="w-12 h-12 rounded-full bg-[#FFE4E6] flex items-center justify-center mb-3">
              <img src="/assets/deflated_ball_3d.png" alt="Bola Murcha" className="w-8 h-8 object-contain" />
            </div>
            <span className="font-headline-md text-headline-md font-bold mb-1" aria-hidden="true">{meusDados?.premios?.find(p => p.categoria === 'BOLA_MURCHA')?.quantidade || 0}x</span>
            <span className="font-body-sm text-body-sm text-on-surface-variant" aria-hidden="true">O Bagre</span>
            <span className="sr-only">Prêmio O Bagre: {meusDados?.premios?.find(p => p.categoria === 'BOLA_MURCHA')?.quantidade || 0} vezes</span>
          </div>

          <div className="glass-panel rounded-xl p-4 flex flex-col items-center justify-center text-center shadow-ambient-1 hover:shadow-ambient-2 transition-shadow">
            <div className="w-12 h-12 rounded-full bg-[#FCE7F3] flex items-center justify-center mb-3">
              <img src="/assets/cry_face_3d.png" alt="Lafon Chorão" className="w-8 h-8 object-contain" />
            </div>
            <span className="font-headline-md text-headline-md font-bold mb-1" aria-hidden="true">{meusDados?.premios?.find(p => p.categoria === 'LAFON')?.quantidade || 0}x</span>
            <span className="font-body-sm text-body-sm text-on-surface-variant" aria-hidden="true">Lafon (Chorão)</span>
            <span className="sr-only">Prêmio Lafon Chorão: {meusDados?.premios?.find(p => p.categoria === 'LAFON')?.quantidade || 0} vezes</span>
          </div>

          <div className="glass-panel rounded-xl p-4 flex flex-col items-center justify-center text-center shadow-ambient-1 hover:shadow-ambient-2 transition-shadow">
            <div className="w-12 h-12 rounded-full bg-blue-500/20 text-blue-500 flex items-center justify-center mb-3">
              <span className="material-symbols-outlined text-[24px]" aria-hidden="true">sports</span>
            </div>
            <span className="font-headline-md text-headline-md font-bold mb-1" aria-hidden="true">{meusDados?.gols_total || 0}</span>
            <span className="font-body-sm text-body-sm text-on-surface-variant" aria-hidden="true">Gols Marcados</span>
            <span className="sr-only">Total de Gols Marcados: {meusDados?.gols_total || 0}</span>
          </div>

          <div className="glass-panel rounded-xl p-4 flex flex-col items-center justify-center text-center shadow-ambient-1 hover:shadow-ambient-2 transition-shadow">
            <div className="w-12 h-12 rounded-full bg-green-500/20 text-green-500 flex items-center justify-center mb-3">
              <span className="material-symbols-outlined text-[24px]" aria-hidden="true">trending_up</span>
            </div>
            <span className="font-headline-md text-headline-md font-bold mb-1" aria-hidden="true">{meusDados?.nota_galera_media ? parseFloat(meusDados.nota_galera_media).toFixed(1) : '-'}</span>
            <span className="font-body-sm text-body-sm text-on-surface-variant" aria-hidden="true">Média da Galera</span>
            <span className="sr-only">Média de Nota da Galera: {meusDados?.nota_galera_media ? parseFloat(meusDados.nota_galera_media).toFixed(1) : 'Sem nota'}</span>
          </div>

          <div className="col-span-2 bg-primary/10 border border-primary/20 rounded-xl p-4 flex flex-col items-center justify-center text-center shadow-ambient-1 hover:shadow-ambient-2 transition-shadow">
            <div className="w-12 h-12 rounded-full bg-primary/20 text-primary flex items-center justify-center mb-3">
              <span className="material-symbols-outlined text-[24px]" aria-hidden="true">emoji_events</span>
            </div>
            <span className="font-headline-md text-headline-md font-bold mb-1 text-primary" aria-hidden="true">{meusDados?.pontos_ranking || 0}</span>
            <span className="font-body-sm text-body-sm text-primary" aria-hidden="true">Total de Pontos</span>
            <span className="sr-only">Total de Pontos no Ranking: {meusDados?.pontos_ranking || 0}</span>
          </div>
        </div>
      </section>

      {/* Actions */}
      <section className="flex flex-col gap-3">
        <button 
          onClick={handleAbrirModalSenha}
          className="flex items-center justify-between glass-panel rounded-xl p-4 shadow-ambient-1 hover:bg-surface-container-low transition-colors text-left w-full"
        >
          <div className="flex items-center gap-3 text-on-surface">
            <span className="material-symbols-outlined">lock</span>
            <span className="font-body-md text-body-md font-medium">Trocar Minha Senha</span>
          </div>
          <span className="material-symbols-outlined text-on-surface-variant">chevron_right</span>
        </button>

        {isSupported && (!permission || permission === 'default' || permission === 'prompt') && (
          <button 
            onClick={subscribeToPush}
            disabled={loadingPush}
            className="flex items-center justify-between bg-primary/10 border border-primary/20 text-primary rounded-xl p-4 shadow-ambient-1 hover:bg-primary/20 transition-colors mb-3 disabled:opacity-50"
          >
            <div className="flex items-center gap-3">
              <span className="material-symbols-outlined">notifications_active</span>
              <div className="flex flex-col text-left">
                <span className="font-body-md text-body-md font-bold">Ativar Notificações</span>
                <span className="font-body-sm text-body-sm text-primary/80">Receba avisos de pelada e votações</span>
              </div>
            </div>
            {loadingPush ? (
              <div className="animate-spin rounded-full h-5 w-5 border-2 border-primary border-t-transparent"></div>
            ) : (
              <span className="material-symbols-outlined">chevron_right</span>
            )}
          </button>
        )}

        {isSupported && permission === 'denied' && (
          <div className="flex items-center justify-between bg-surface-variant border border-outline-variant/30 text-on-surface-variant rounded-xl p-4 mb-3 shadow-ambient-1">
            <div className="flex items-center gap-3">
              <span className="material-symbols-outlined text-error">notifications_off</span>
              <div className="flex flex-col text-left">
                <span className="font-body-md text-body-md font-bold">Notificações Bloqueadas</span>
                <span className="font-body-sm text-body-sm opacity-80">Permita nas configurações do navegador</span>
              </div>
            </div>
          </div>
        )}

        {isSupported && permission === 'granted' && (
          <div className="flex items-center justify-between bg-surface-container-low border border-outline-variant/30 text-on-surface-variant rounded-xl p-4 mb-3">
            <div className="flex items-center gap-3">
              <span className="material-symbols-outlined text-green-500">notifications_active</span>
              <span className="font-body-md text-body-md font-medium">Notificações Ativas</span>
            </div>
            <span className="material-symbols-outlined text-green-500">check_circle</span>
          </div>
        )}

        <button 
          onClick={handleLogout}
          className="flex items-center gap-3 bg-error/10 border border-error/20 text-error rounded-xl p-4 shadow-ambient-1 hover:bg-error/20 transition-colors w-full text-left"
        >
          <span className="material-symbols-outlined">logout</span>
          <span className="font-body-md text-body-md font-medium">Sair do Aplicativo</span>
        </button>
      </section>

      {/* Modal de Alterar Senha */}
      {showSenhaModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[100] flex items-center justify-center p-4 animate-fade-in">
          <div className="bg-surface dark:bg-surface-dim rounded-2xl w-full max-w-sm p-6 shadow-2xl border border-outline-variant/30 animate-scale-up space-y-4">
            <div className="flex justify-between items-center border-b border-outline-variant/20 pb-3">
              <div className="flex items-center gap-2">
                <span className="material-symbols-outlined text-[24px] text-primary">lock_reset</span>
                <h3 className="font-headline-sm text-headline-sm text-on-surface font-bold">Trocar Senha</h3>
              </div>
              <button 
                onClick={() => setShowSenhaModal(false)}
                className="w-8 h-8 rounded-full bg-surface-container-low flex items-center justify-center text-on-surface-variant hover:bg-surface-variant transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
                aria-label="Fechar"
              >
                <span className="material-symbols-outlined text-[20px]" aria-hidden="true">close</span>
              </button>
            </div>

            <form onSubmit={handleAlterarSenha} className="space-y-4">
              <div className="space-y-1">
                <label className="block font-label-bold text-label-bold text-on-surface-variant uppercase tracking-wider text-[11px]">Senha Atual</label>
                <input 
                  type="password" 
                  value={senhaAtual}
                  onChange={(e) => {
                    setSenhaAtual(e.target.value);
                    if (erroSenhaAtual) setErroSenhaAtual('');
                  }}
                  placeholder="Sua senha atual"
                  className={`block w-full px-3 py-3 bg-[#F1F5F9] dark:bg-surface-lowest border rounded-lg focus:ring-2 transition-all font-body-md text-on-surface ${erroSenhaAtual ? 'border-error focus:ring-error/20' : 'border-transparent focus:border-primary focus:ring-primary/20'}`}
                  autoFocus
                />
                {erroSenhaAtual && (
                  <p className="text-error text-body-sm mt-1 flex items-center gap-1 font-medium">
                    <span className="material-symbols-outlined text-[16px]">error</span>
                    {erroSenhaAtual}
                  </p>
                )}
              </div>

              <div className="space-y-1">
                <label className="block font-label-bold text-label-bold text-on-surface-variant uppercase tracking-wider text-[11px]">Nova Senha</label>
                <input 
                  type="password" 
                  value={novaSenha}
                  onChange={(e) => setNovaSenha(e.target.value)}
                  placeholder="No mínimo 6 caracteres"
                  className={`block w-full px-3 py-3 bg-[#F1F5F9] dark:bg-surface-lowest border rounded-lg focus:ring-2 transition-all font-body-md text-on-surface ${senhaNovaCurta ? 'border-error focus:ring-error/20' : 'border-transparent focus:border-primary focus:ring-primary/20'}`}
                />
                {senhaNovaCurta && (
                  <p className="text-error text-body-sm mt-1 flex items-center gap-1 font-medium">
                    <span className="material-symbols-outlined text-[16px]">error</span>
                    A nova senha deve ter pelo menos 6 caracteres.
                  </p>
                )}
              </div>

              <div className="space-y-1">
                <label className="block font-label-bold text-label-bold text-on-surface-variant uppercase tracking-wider text-[11px]">Confirmar Nova Senha</label>
                <input 
                  type="password" 
                  value={confirmarNovaSenha}
                  onChange={(e) => setConfirmarNovaSenha(e.target.value)}
                  placeholder="Repita a nova senha"
                  className={`block w-full px-3 py-3 bg-[#F1F5F9] dark:bg-surface-lowest border rounded-lg focus:ring-2 transition-all font-body-md text-on-surface ${senhasNaoConferem ? 'border-error focus:ring-error/20' : 'border-transparent focus:border-primary focus:ring-primary/20'}`}
                />
                {senhasNaoConferem && (
                  <p className="text-error text-body-sm mt-1 flex items-center gap-1 font-medium">
                    <span className="material-symbols-outlined text-[16px]">error</span>
                    As senhas não coincidem.
                  </p>
                )}
              </div>

              <div className="flex gap-3 pt-2">
                <button 
                  type="button"
                  onClick={() => setShowSenhaModal(false)}
                  className="flex-1 py-3 border-2 border-outline-variant text-on-surface rounded-xl font-label-bold text-label-bold hover:bg-surface-variant/50 transition-colors"
                >
                  Cancelar
                </button>
                <button 
                  type="submit"
                  disabled={loadingSenha}
                  className="flex-1 py-3 bg-primary text-on-primary rounded-xl font-label-bold text-label-bold hover:bg-primary/90 transition-colors flex justify-center items-center gap-2"
                >
                  {loadingSenha ? 'Salvando...' : 'Confirmar'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal de Recorte (Cropper) */}
      {imageSrc && (
        <div className="fixed inset-0 bg-black/85 backdrop-blur-sm z-[105] flex flex-col items-center justify-center p-4 animate-fade-in">
          <div className="bg-surface dark:bg-surface-dim rounded-2xl w-full max-w-md p-6 shadow-2xl border border-outline-variant/30 animate-scale-up space-y-6">
            <div className="flex justify-between items-center border-b border-outline-variant/20 pb-3">
              <div className="flex items-center gap-2">
                <span className="material-symbols-outlined text-[24px] text-primary">crop_free</span>
                <h3 className="font-headline-sm text-headline-sm text-on-surface font-bold">Ajustar Foto</h3>
              </div>
              <button 
                onClick={() => {
                  setImageSrc(null);
                  setZoom(1);
                  setCrop({ x: 0, y: 0 });
                }}
                className="w-8 h-8 rounded-full bg-surface-container-low flex items-center justify-center text-on-surface-variant hover:bg-surface-variant transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
                aria-label="Fechar"
              >
                <span className="material-symbols-outlined text-[20px]" aria-hidden="true">close</span>
              </button>
            </div>

            {/* Container do Cropper */}
            <div className="relative w-full h-64 md:h-80 bg-black rounded-lg overflow-hidden border border-outline-variant/20">
              <Cropper
                image={imageSrc}
                crop={crop}
                zoom={zoom}
                aspect={1}
                cropShape="round"
                showGrid={false}
                onCropChange={setCrop}
                onZoomChange={setZoom}
                onCropComplete={(croppedArea, croppedAreaPixels) => setCroppedAreaPixels(croppedAreaPixels)}
              />
            </div>

            {/* Slider de Zoom */}
            <div className="space-y-2">
              <div className="flex justify-between text-body-sm text-on-surface-variant">
                <span>Zoom</span>
                <span>{zoom.toFixed(1)}x</span>
              </div>
              <input
                type="range"
                value={zoom}
                min={1}
                max={3}
                step={0.1}
                aria-label="Zoom"
                onChange={(e) => setZoom(parseFloat(e.target.value))}
                className="w-full h-2 bg-[#E2E8F0] dark:bg-surface-lowest rounded-lg appearance-none cursor-pointer accent-primary"
              />
            </div>

            {/* Ações */}
            <div className="flex gap-3 pt-2">
              <button 
                type="button"
                onClick={() => {
                  setImageSrc(null);
                  setZoom(1);
                  setCrop({ x: 0, y: 0 });
                }}
                disabled={uploadingFoto}
                className="flex-1 py-3 border-2 border-outline-variant text-on-surface rounded-xl font-label-bold text-label-bold hover:bg-surface-variant/50 transition-colors disabled:opacity-50"
              >
                Cancelar
              </button>
              <button 
                type="button"
                onClick={handleFotoConfirm}
                disabled={uploadingFoto}
                className="flex-1 py-3 bg-primary text-on-primary rounded-xl font-label-bold text-label-bold hover:bg-primary/90 transition-colors flex justify-center items-center gap-2 disabled:opacity-50"
              >
                {uploadingFoto ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-2 border-on-primary border-t-transparent"></div>
                    Enviando...
                  </>
                ) : (
                  'Confirmar e Salvar'
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
