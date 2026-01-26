/**
 * v2診断セッション管理フック
 *
 * 動的診断フローのセッション状態管理とAPI呼び出しを行う
 */
import { useState, useCallback } from 'react'

// 型定義
export interface InitialAnswers {
  purpose: string
  autonomy: 'obedient' | 'collaborative' | 'autonomous'
}

export interface FollowupAnswer {
  question_id: string
  answer: string
}

export interface QuestionChoice {
  value: string
  label: string
  description?: string
}

export interface Question {
  id: string
  question: string
  type: 'freeform' | 'choice' | 'multi_choice'
  placeholder?: string
  suggestions?: string[]
  choices?: QuestionChoice[]
}

export interface UserProfile {
  primary_use_case: string
  autonomy_preference: string
  communication_style: string
  key_traits: string[]
  detected_needs: string[]
}

export interface PromptVariant {
  style: 'short' | 'standard' | 'strict'
  name: string
  prompt: string
  description: string
}

export interface DiagnoseV2Result {
  user_profile: UserProfile
  recommended_style: 'short' | 'standard' | 'strict'
  recommendation_reason: string
  variants: PromptVariant[]
  source: 'llm' | 'mock'
}

interface DiagnoseV2StartResponse {
  session_id: string
  phase: 'followup' | 'complete'
  followup_questions: Question[] | null
  result: DiagnoseV2Result | null
}

interface DiagnoseV2ContinueResponse {
  session_id: string
  phase: 'followup' | 'complete'
  followup_questions: Question[] | null
  result: DiagnoseV2Result | null
}

// プロバイダー型
export type Provider = 'openai' | 'groq' | 'gemini'

// フックのオプション
export interface UseDiagnoseSessionOptions {
  baseUrl?: string
  apiKey?: string
  provider?: Provider
  timeout?: number
}

// フックの戻り値
export interface UseDiagnoseSessionReturn {
  sessionId: string | null
  phase: 'followup' | 'complete' | null
  isLoading: boolean
  error: Error | null
  followupQuestions: Question[]
  result: DiagnoseV2Result | null
  startSession: (answers: InitialAnswers) => Promise<void>
  continueSession: (answers: FollowupAnswer[]) => Promise<void>
  reset: () => void
}

const DEFAULT_BASE_URL = ''
const DEFAULT_TIMEOUT = 60000

/**
 * v2診断セッション管理フック
 *
 * @param options.baseUrl - APIのベースURL
 * @param options.apiKey - APIキー（オプション）
 * @param options.timeout - タイムアウト時間（ミリ秒）
 */
export const useDiagnoseSession = (
  options: UseDiagnoseSessionOptions = {}
): UseDiagnoseSessionReturn => {
  const {
    baseUrl = DEFAULT_BASE_URL,
    apiKey,
    provider,
    timeout = DEFAULT_TIMEOUT,
  } = options

  // 状態
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [phase, setPhase] = useState<'followup' | 'complete' | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)
  const [followupQuestions, setFollowupQuestions] = useState<Question[]>([])
  const [result, setResult] = useState<DiagnoseV2Result | null>(null)

  // リセット
  const reset = useCallback(() => {
    setSessionId(null)
    setPhase(null)
    setIsLoading(false)
    setError(null)
    setFollowupQuestions([])
    setResult(null)
  }, [])

  // 共通のfetch処理
  const fetchWithTimeout = useCallback(async <T>(
    url: string,
    body: object
  ): Promise<T> => {
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), timeout)

    try {
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      }

      if (apiKey) {
        headers['X-API-Key'] = apiKey
      }

      if (provider) {
        headers['X-Provider'] = provider
      }

      const response = await fetch(url, {
        method: 'POST',
        headers,
        body: JSON.stringify(body),
        signal: controller.signal,
      })

      clearTimeout(timeoutId)

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `リクエストに失敗しました: ${response.status}`)
      }

      return await response.json() as T
    } finally {
      clearTimeout(timeoutId)
    }
  }, [apiKey, provider, timeout])

  // セッション開始
  const startSession = useCallback(async (answers: InitialAnswers) => {
    setIsLoading(true)
    setError(null)

    try {
      const response = await fetchWithTimeout<DiagnoseV2StartResponse>(
        `${baseUrl}/api/v2/diagnose/start`,
        {
          initial_answers: answers,
        }
      )

      setSessionId(response.session_id)
      setPhase(response.phase)

      if (response.followup_questions) {
        setFollowupQuestions(response.followup_questions)
      } else {
        setFollowupQuestions([])
      }

      if (response.result) {
        setResult(response.result)
      }
    } catch (err) {
      setError(err instanceof Error ? err : new Error('予期しないエラーが発生しました'))
    } finally {
      setIsLoading(false)
    }
  }, [baseUrl, fetchWithTimeout])

  // セッション継続
  const continueSession = useCallback(async (answers: FollowupAnswer[]) => {
    if (!sessionId) {
      setError(new Error('セッションが開始されていません'))
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      const response = await fetchWithTimeout<DiagnoseV2ContinueResponse>(
        `${baseUrl}/api/v2/diagnose/continue`,
        {
          session_id: sessionId,
          answers,
        }
      )

      setPhase(response.phase)

      if (response.followup_questions) {
        setFollowupQuestions(response.followup_questions)
      } else {
        setFollowupQuestions([])
      }

      if (response.result) {
        setResult(response.result)
      }
    } catch (err) {
      setError(err instanceof Error ? err : new Error('予期しないエラーが発生しました'))
    } finally {
      setIsLoading(false)
    }
  }, [baseUrl, sessionId, fetchWithTimeout])

  return {
    sessionId,
    phase,
    isLoading,
    error,
    followupQuestions,
    result,
    startSession,
    continueSession,
    reset,
  }
}
