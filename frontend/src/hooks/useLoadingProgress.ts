import { useState, useEffect, useRef, useCallback } from 'react'

export type LoadingPhase = 'analyzing' | 'extracting' | 'building' | 'generating' | 'optimizing' | 'finishing'

interface LoadingProgress {
  phase: LoadingPhase
  message: string
  icon: string
  tip: string
  progress: number
}

interface PhaseConfig {
  message: string
  icon: string
  progress: number
}

const PHASE_CONFIGS: Record<LoadingPhase, PhaseConfig> = {
  analyzing: { message: '回答を分析中...', icon: '🔍', progress: 15 },
  extracting: { message: '認知特性を抽出中...', icon: '🧩', progress: 35 },
  building: { message: 'プロファイルを構築中...', icon: '📐', progress: 55 },
  generating: { message: 'プロンプトを生成中...', icon: '✍️', progress: 75 },
  optimizing: { message: '最適化を実行中...', icon: '🎯', progress: 90 },
  finishing: { message: 'まもなく完了...', icon: '✨', progress: 95 },
}

const PHASE_THRESHOLDS: Record<LoadingPhase, number> = {
  analyzing: 0,
  extracting: 3000,
  building: 6000,
  generating: 9000,
  optimizing: 12000,
  finishing: 15000,
}

const LOADING_TIPS = [
  '豆知識: 構造型思考の人は見出しと箇条書きを好みます',
  '生成されたプロンプトは自由にカスタマイズできます',
  '認知特性に基づいて最適なフォーマットを選択中...',
  '豆知識: 詳細志向度は情報量の好みを表します',
  '3種類のプロンプト（Short/Standard/Strict）を準備中...',
  'ヒント: Strictは専門的な作業に最適です',
  '豆知識: 学習タイプによって好みの説明形式が異なります',
  'ヒント: 生成後、推奨スタイル以外も試してみてください',
]

/**
 * ローディング中のプログレス表示を管理するフック
 *
 * @param isLoading ローディング中かどうか
 * @returns 現在のフェーズ、メッセージ、アイコン、Tips、進捗率
 */
export const useLoadingProgress = (isLoading: boolean): LoadingProgress => {
  const [phase, setPhase] = useState<LoadingPhase>('analyzing')
  const [tipIndex, setTipIndex] = useState(0)
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const tipTimerRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const startTimeRef = useRef<number | null>(null)

  const updatePhase = useCallback(() => {
    if (startTimeRef.current === null) return

    const elapsed = Date.now() - startTimeRef.current
    const phases: LoadingPhase[] = ['analyzing', 'extracting', 'building', 'generating', 'optimizing', 'finishing']

    // 経過時間に基づいて適切なフェーズを選択
    for (let i = phases.length - 1; i >= 0; i--) {
      if (elapsed >= PHASE_THRESHOLDS[phases[i]]) {
        setPhase(phases[i])
        break
      }
    }
  }, [])

  useEffect(() => {
    if (isLoading) {
      // ローディング開始
      startTimeRef.current = Date.now()
      setPhase('analyzing')
      setTipIndex(0)

      // 500msごとにフェーズを更新（スムーズな遷移）
      timerRef.current = setInterval(updatePhase, 500)

      // 3秒ごとにTipsを更新
      tipTimerRef.current = setInterval(() => {
        setTipIndex(prev => (prev + 1) % LOADING_TIPS.length)
      }, 3000)
    } else {
      // ローディング終了 - タイマーをクリア
      if (timerRef.current) {
        clearInterval(timerRef.current)
        timerRef.current = null
      }
      if (tipTimerRef.current) {
        clearInterval(tipTimerRef.current)
        tipTimerRef.current = null
      }
      startTimeRef.current = null
      setPhase('analyzing')
    }

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current)
        timerRef.current = null
      }
      if (tipTimerRef.current) {
        clearInterval(tipTimerRef.current)
        tipTimerRef.current = null
      }
    }
  }, [isLoading, updatePhase])

  const config = PHASE_CONFIGS[phase]

  return {
    phase,
    message: config.message,
    icon: config.icon,
    tip: LOADING_TIPS[tipIndex],
    progress: config.progress,
  }
}
