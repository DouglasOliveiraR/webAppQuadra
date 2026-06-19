import { renderHook, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import api from '../../services/api';
import * as Toast from '../../components/ui/Toast';

vi.mock('../../services/api', () => ({
  default: {
    get: vi.fn(),
    put: vi.fn(),
  }
}));

vi.mock('../../components/ui/Toast', () => ({
  showToast: vi.fn(),
}));

describe('useFinanceiro Hook', () => {
  beforeEach(async () => {
    vi.clearAllMocks();
    vi.useFakeTimers();
    // Use resetModules to ensure module-level cache is cleared between tests
    vi.resetModules();
  });

  afterEach(() => {
    vi.restoreAllMocks();
    vi.useRealTimers();
  });

  it('deve buscar dados financeiros do jogador na inicialização', async () => {
    const { useFinanceiro } = await import('../useFinanceiro');
    const mockData = [{ id: 1, valor: 50 }];
    api.get.mockResolvedValueOnce({ data: mockData });

    const { result } = renderHook(() => useFinanceiro());

    expect(result.current.loading).toBe(true);
    expect(result.current.pendencias).toEqual([]);

    await act(async () => {
      await vi.runAllTimersAsync();
    });

    expect(api.get).toHaveBeenCalledWith('/financeiro/me', { params: {} });
    expect(result.current.loading).toBe(false);
    expect(result.current.pendencias).toEqual(mockData);
  });

  it('deve usar o cache para chamadas subsequentes sem force', async () => {
    const { useFinanceiro } = await import('../useFinanceiro');
    const mockData = [{ id: 2, valor: 60 }];
    api.get.mockResolvedValueOnce({ data: mockData });

    const { result } = renderHook(() => useFinanceiro());

    await act(async () => {
      await vi.runAllTimersAsync();
    });

    expect(api.get).toHaveBeenCalledTimes(1);

    const { result: result2 } = renderHook(() => useFinanceiro());

    await act(async () => {
      await vi.runAllTimersAsync();
    });

    expect(api.get).toHaveBeenCalledTimes(1);
    expect(result2.current.pendencias).toEqual(mockData);
  });

  it('deve ignorar cache com force=true', async () => {
    const { useFinanceiro } = await import('../useFinanceiro');
    const mockData1 = [{ id: 1, valor: 50 }];
    const mockData2 = [{ id: 1, valor: 100 }];

    api.get.mockResolvedValueOnce({ data: mockData1 });
    const { result } = renderHook(() => useFinanceiro());
    await act(async () => {
      await vi.runAllTimersAsync();
    });

    expect(api.get).toHaveBeenCalledTimes(1);

    api.get.mockResolvedValueOnce({ data: mockData2 });
    await act(async () => {
      await result.current.refetch();
    });

    expect(api.get).toHaveBeenCalledTimes(2);
    expect(api.get).toHaveBeenLastCalledWith('/financeiro/me', {
      params: expect.objectContaining({ _t: expect.any(Number) })
    });
    expect(result.current.pendencias).toEqual(mockData2);
  });

  it('deve lidar com erro ao buscar dados financeiros do jogador', async () => {
    const { useFinanceiro } = await import('../useFinanceiro');
    api.get.mockRejectedValueOnce(new Error('Network Error'));

    const { result } = renderHook(() => useFinanceiro());

    await act(async () => {
      await vi.runAllTimersAsync();
    });

    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBe('Erro ao buscar seus dados financeiros.');
  });

  it('deve buscar dados financeiros do admin', async () => {
    const { useFinanceiro } = await import('../useFinanceiro');
    const mockAdminData = [{ id: 3, valor: 100 }];
    api.get.mockResolvedValueOnce({ data: [] }); // Initial fetch
    api.get.mockResolvedValueOnce({ data: mockAdminData }); // Admin fetch

    const { result } = renderHook(() => useFinanceiro());

    await act(async () => {
      await vi.runAllTimersAsync();
    });

    await act(async () => {
      await result.current.refetchAdmin('2023-10');
    });

    expect(api.get).toHaveBeenCalledWith('/financeiro/admin', expect.objectContaining({
      params: expect.objectContaining({ mes: '2023-10', _t: expect.any(Number) })
    }));
    expect(result.current.loadingAdmin).toBe(false);
    expect(result.current.pendenciasAdmin).toEqual(mockAdminData);
  });

  it('deve dar baixa no pagamento do jogador com sucesso', async () => {
    const { useFinanceiro } = await import('../useFinanceiro');
    const mockData = [{ id: 1, status: 'pago' }];
    api.get.mockResolvedValueOnce({ data: [] }); // Initial
    api.put.mockResolvedValueOnce({});
    api.get.mockResolvedValueOnce({ data: mockData }); // Refetch after

    const { result } = renderHook(() => useFinanceiro());

    await act(async () => {
      await vi.runAllTimersAsync();
    });

    await act(async () => {
      await result.current.baixarPagamento(1, '2023-10');
    });

    expect(api.put).toHaveBeenCalledWith('/financeiro/1/baixar');
    expect(api.get).toHaveBeenCalledWith('/financeiro/me', expect.objectContaining({
      params: expect.objectContaining({ mes: '2023-10', _t: expect.any(Number) })
    }));
    expect(Toast.showToast).toHaveBeenCalledWith('Status do pagamento atualizado!');
  });

  it('deve lidar com erro ao dar baixa no pagamento do jogador', async () => {
    const { useFinanceiro } = await import('../useFinanceiro');
    api.get.mockResolvedValueOnce({ data: [] }); // initial
    api.put.mockRejectedValueOnce({ response: { data: { detail: 'Pagamento já baixado' } } });

    const { result } = renderHook(() => useFinanceiro());

    await act(async () => {
      await vi.runAllTimersAsync();
    });

    await act(async () => {
      await result.current.baixarPagamento(1);
    });

    expect(api.put).toHaveBeenCalledWith('/financeiro/1/baixar');
    expect(result.current.error).toBe('Pagamento já baixado');
    expect(Toast.showToast).toHaveBeenCalledWith('Pagamento já baixado', 'error');
  });

  it('deve dar baixa no pagamento do admin com sucesso', async () => {
    const { useFinanceiro } = await import('../useFinanceiro');
    const mockData = [{ id: 1, status: 'pago' }];
    api.get.mockResolvedValueOnce({ data: [] }); // initial
    api.put.mockResolvedValueOnce({});
    api.get.mockResolvedValueOnce({ data: mockData }); // RefetchAdmin after

    const { result } = renderHook(() => useFinanceiro());

    await act(async () => {
      await vi.runAllTimersAsync();
    });

    await act(async () => {
      await result.current.baixarPagamentoAdmin(2, '2023-10');
    });

    expect(api.put).toHaveBeenCalledWith('/financeiro/2/baixar');
    expect(api.get).toHaveBeenCalledWith('/financeiro/admin', expect.objectContaining({
      params: expect.objectContaining({ mes: '2023-10', _t: expect.any(Number) })
    }));
    expect(Toast.showToast).toHaveBeenCalledWith('Status do pagamento atualizado!');
  });

});
