import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useLoadingProgress } from './useLoadingProgress'

describe('useLoadingProgress', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('should return "connecting" phase initially', () => {
    const { result } = renderHook(() => useLoadingProgress(true))

    expect(result.current.phase).toBe('connecting')
    expect(result.current.message).toBe('サーバーに接続中...')
  })

  it('should return "generating" phase after 10 seconds', () => {
    const { result } = renderHook(() => useLoadingProgress(true))

    // 10秒経過
    act(() => {
      vi.advanceTimersByTime(10000)
    })

    expect(result.current.phase).toBe('generating')
    expect(result.current.message).toBe('プロンプト生成中...')
  })

  it('should return "finishing" phase after 30 seconds', () => {
    const { result } = renderHook(() => useLoadingProgress(true))

    // 30秒経過
    act(() => {
      vi.advanceTimersByTime(30000)
    })

    expect(result.current.phase).toBe('finishing')
    expect(result.current.message).toBe('まもなく完了...')
  })

  it('should reset to "connecting" when loading stops', () => {
    const { result, rerender } = renderHook(
      ({ isLoading }) => useLoadingProgress(isLoading),
      { initialProps: { isLoading: true } }
    )

    // 15秒経過 (generating フェーズ)
    act(() => {
      vi.advanceTimersByTime(15000)
    })

    expect(result.current.phase).toBe('generating')

    // ローディング終了
    rerender({ isLoading: false })

    expect(result.current.phase).toBe('connecting')
  })

  it('should clear timer when loading stops', () => {
    const clearIntervalSpy = vi.spyOn(global, 'clearInterval')

    const { rerender } = renderHook(
      ({ isLoading }) => useLoadingProgress(isLoading),
      { initialProps: { isLoading: true } }
    )

    // ローディング終了
    rerender({ isLoading: false })

    expect(clearIntervalSpy).toHaveBeenCalled()

    clearIntervalSpy.mockRestore()
  })

  it('should not update phase when not loading', () => {
    const { result } = renderHook(() => useLoadingProgress(false))

    act(() => {
      vi.advanceTimersByTime(30000)
    })

    expect(result.current.phase).toBe('connecting')
  })
})
