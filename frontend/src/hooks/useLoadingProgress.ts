import { useState, useEffect, useRef, useCallback } from 'react'

export type LoadingPhase = 'connecting' | 'generating' | 'finishing'

interface LoadingProgress {
  phase: LoadingPhase
  message: string
}

const PROGRESS_MESSAGES: Record<LoadingPhase, string> = {
  connecting: 'サーバーに接続中...',
  generating: 'プロンプト生成中...',
  finishing: 'まもなく完了...',
}

const PHASE_THRESHOLDS = {
  generating: 10000,  // 10秒
  finishing: 30000,   // 30秒
}

/**
 * ローディング中のプログレス表示を管理するフック
 *
 * @param isLoading ローディング中かどうか
 * @returns 現在のフェーズとメッセージ
 */
export const useLoadingProgress = (isLoading: boolean): LoadingProgress => {
  const [phase, setPhase] = useState<LoadingPhase>('connecting')
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const startTimeRef = useRef<number | null>(null)

  const updatePhase = useCallback(() => {
    if (startTimeRef.current === null) return

    const elapsed = Date.now() - startTimeRef.current

    if (elapsed >= PHASE_THRESHOLDS.finishing) {
      setPhase('finishing')
    } else if (elapsed >= PHASE_THRESHOLDS.generating) {
      setPhase('generating')
    }
  }, [])

  useEffect(() => {
    if (isLoading) {
      // ローディング開始
      startTimeRef.current = Date.now()
      setPhase('connecting')

      // 1秒ごとにフェーズを更新
      timerRef.current = setInterval(updatePhase, 1000)
    } else {
      // ローディング終了 - タイマーをクリア
      if (timerRef.current) {
        clearInterval(timerRef.current)
        timerRef.current = null
      }
      startTimeRef.current = null
      setPhase('connecting')
    }

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current)
        timerRef.current = null
      }
    }
  }, [isLoading, updatePhase])

  return {
    phase,
    message: PROGRESS_MESSAGES[phase],
  }
}
