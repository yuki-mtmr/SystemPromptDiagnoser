import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import { useFetchWithTimeout, TimeoutError } from './useFetchWithTimeout'

// Mock fetch
const mockFetch = vi.fn()
global.fetch = mockFetch

describe('useFetchWithTimeout', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
    vi.clearAllMocks()
  })

  it('should return initial state', () => {
    const { result } = renderHook(() => useFetchWithTimeout())

    expect(result.current.isLoading).toBe(false)
    expect(result.current.error).toBe(null)
    expect(result.current.data).toBe(null)
  })

  it('should set isLoading to true when fetch is called', async () => {
    mockFetch.mockImplementation(() => new Promise(() => {}))

    const { result } = renderHook(() => useFetchWithTimeout())

    act(() => {
      result.current.fetchWithTimeout('/api/test', {})
    })

    expect(result.current.isLoading).toBe(true)
  })

  it('should return data on successful fetch', async () => {
    const mockData = { success: true }
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockData),
    })

    const { result } = renderHook(() => useFetchWithTimeout())

    await act(async () => {
      await result.current.fetchWithTimeout('/api/test', {})
    })

    expect(result.current.data).toEqual(mockData)
    expect(result.current.isLoading).toBe(false)
    expect(result.current.error).toBe(null)
  })

  it('should throw TimeoutError after specified timeout', async () => {
    // fetchが永久に解決しない
    mockFetch.mockImplementation(
      () => new Promise(() => {})
    )

    const { result } = renderHook(() => useFetchWithTimeout({ timeout: 5000 }))

    // fetchを開始（Promise返却）
    let fetchPromise: Promise<unknown>
    act(() => {
      fetchPromise = result.current.fetchWithTimeout('/api/test', {})
    })

    expect(result.current.isLoading).toBe(true)

    // タイマーを進めてタイムアウトを発火させる
    await act(async () => {
      vi.advanceTimersByTime(5000)
      // マイクロタスクを処理
      await vi.runAllTimersAsync()
    })

    // エラー状態を確認
    expect(result.current.error).toBeInstanceOf(TimeoutError)
    expect(result.current.error?.message).toContain('タイムアウト')
    expect(result.current.isLoading).toBe(false)
  }, 10000)

  it('should use default timeout of 60 seconds', async () => {
    mockFetch.mockImplementation(() => new Promise(() => {}))

    const { result } = renderHook(() => useFetchWithTimeout())

    act(() => {
      result.current.fetchWithTimeout('/api/test', {})
    })

    // 59秒経過 - まだタイムアウトしない
    await act(async () => {
      vi.advanceTimersByTime(59000)
      await Promise.resolve()
    })

    expect(result.current.error).toBe(null)
    expect(result.current.isLoading).toBe(true)

    // さらに1秒経過 - タイムアウト
    await act(async () => {
      vi.advanceTimersByTime(1000)
      await vi.runAllTimersAsync()
    })

    expect(result.current.error).toBeInstanceOf(TimeoutError)
  }, 10000)

  it('should clear timeout on successful fetch', async () => {
    const mockData = { success: true }
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockData),
    })

    const clearTimeoutSpy = vi.spyOn(global, 'clearTimeout')

    const { result } = renderHook(() => useFetchWithTimeout())

    await act(async () => {
      await result.current.fetchWithTimeout('/api/test', {})
    })

    expect(clearTimeoutSpy).toHaveBeenCalled()

    clearTimeoutSpy.mockRestore()
  })

  it('should handle fetch error', async () => {
    const errorMessage = 'Network error'
    mockFetch.mockRejectedValueOnce(new Error(errorMessage))

    const { result } = renderHook(() => useFetchWithTimeout())

    await act(async () => {
      await result.current.fetchWithTimeout('/api/test', {})
    })

    expect(result.current.error?.message).toBe(errorMessage)
    expect(result.current.isLoading).toBe(false)
  })
})
