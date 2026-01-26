import { useState, useCallback, useRef } from 'react'

export class TimeoutError extends Error {
  constructor(message: string = 'リクエストがタイムアウトしました') {
    super(message)
    this.name = 'TimeoutError'
  }
}

interface UseFetchWithTimeoutOptions {
  timeout?: number  // ミリ秒
}

interface FetchState<T> {
  isLoading: boolean
  error: Error | null
  data: T | null
}

interface UseFetchWithTimeoutReturn<T> extends FetchState<T> {
  fetchWithTimeout: (url: string, options: RequestInit) => Promise<T | null>
  reset: () => void
}

const DEFAULT_TIMEOUT = 60000  // 60秒

/**
 * タイムアウト機能付きfetchフック
 *
 * @param options.timeout タイムアウト時間（ミリ秒）。デフォルト60秒
 */
export const useFetchWithTimeout = <T = unknown>(
  options: UseFetchWithTimeoutOptions = {}
): UseFetchWithTimeoutReturn<T> => {
  const { timeout = DEFAULT_TIMEOUT } = options

  const [state, setState] = useState<FetchState<T>>({
    isLoading: false,
    error: null,
    data: null,
  })

  const timeoutIdRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const abortControllerRef = useRef<AbortController | null>(null)

  const reset = useCallback(() => {
    setState({
      isLoading: false,
      error: null,
      data: null,
    })
  }, [])

  const fetchWithTimeout = useCallback(async (
    url: string,
    fetchOptions: RequestInit
  ): Promise<T | null> => {
    // 前回のリクエストをキャンセル
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
    }
    if (timeoutIdRef.current) {
      clearTimeout(timeoutIdRef.current)
    }

    abortControllerRef.current = new AbortController()

    setState({
      isLoading: true,
      error: null,
      data: null,
    })

    // タイムアウト処理
    const timeoutPromise = new Promise<never>((_, reject) => {
      timeoutIdRef.current = setTimeout(() => {
        abortControllerRef.current?.abort()
        reject(new TimeoutError('接続がタイムアウトしました。サーバーが応答していない可能性があります。'))
      }, timeout)
    })

    try {
      const response = await Promise.race([
        fetch(url, {
          ...fetchOptions,
          signal: abortControllerRef.current.signal,
        }),
        timeoutPromise,
      ])

      // タイムアウトをクリア
      if (timeoutIdRef.current) {
        clearTimeout(timeoutIdRef.current)
        timeoutIdRef.current = null
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `リクエストに失敗しました: ${response.status}`)
      }

      const data = await response.json() as T

      setState({
        isLoading: false,
        error: null,
        data,
      })

      return data
    } catch (error) {
      // タイムアウトをクリア
      if (timeoutIdRef.current) {
        clearTimeout(timeoutIdRef.current)
        timeoutIdRef.current = null
      }

      const err = error instanceof Error ? error : new Error('予期しないエラーが発生しました')

      setState({
        isLoading: false,
        error: err,
        data: null,
      })

      return null
    }
  }, [timeout])

  return {
    ...state,
    fetchWithTimeout,
    reset,
  }
}
