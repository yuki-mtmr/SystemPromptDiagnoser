/**
 * useDiagnoseSession フックのテスト
 * TDD: まずテストを書き、失敗を確認してから実装する
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import { useDiagnoseSession } from './useDiagnoseSession'

// fetchをモック
const mockFetch = vi.fn()
global.fetch = mockFetch

describe('useDiagnoseSession', () => {
  beforeEach(() => {
    mockFetch.mockReset()
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  describe('初期状態', () => {
    it('初期状態ではセッションがnull', () => {
      const { result } = renderHook(() => useDiagnoseSession())

      expect(result.current.sessionId).toBeNull()
      expect(result.current.phase).toBeNull()
      expect(result.current.isLoading).toBe(false)
      expect(result.current.error).toBeNull()
    })

    it('初期状態では結果がnull', () => {
      const { result } = renderHook(() => useDiagnoseSession())

      expect(result.current.result).toBeNull()
    })

    it('初期状態ではフォローアップ質問が空配列', () => {
      const { result } = renderHook(() => useDiagnoseSession())

      expect(result.current.followupQuestions).toEqual([])
    })
  })

  describe('startSession', () => {
    it('セッションを開始できる', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          session_id: 'test-session-123',
          phase: 'followup',
          followup_questions: [],
          result: null,
        }),
      })

      const { result } = renderHook(() => useDiagnoseSession())

      await act(async () => {
        await result.current.startSession({
          purpose: 'コードレビュー',
          autonomy: 'collaborative',
        })
      })

      expect(result.current.sessionId).toBe('test-session-123')
      expect(result.current.phase).toBe('followup')
    })

    it('ローディング状態を管理する', async () => {
      mockFetch.mockImplementation(() =>
        new Promise(resolve =>
          setTimeout(() => resolve({
            ok: true,
            json: () => Promise.resolve({
              session_id: 'test-session',
              phase: 'followup',
              followup_questions: [],
              result: null,
            }),
          }), 100)
        )
      )

      const { result } = renderHook(() => useDiagnoseSession())

      expect(result.current.isLoading).toBe(false)

      act(() => {
        result.current.startSession({
          purpose: 'test',
          autonomy: 'obedient',
        })
      })

      expect(result.current.isLoading).toBe(true)

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      })
    })

    it('フォローアップ質問を受け取る', async () => {
      const mockQuestions = [
        {
          id: 'fq1',
          question: 'どのような言語を使用していますか？',
          type: 'freeform',
        },
      ]

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          session_id: 'test-session',
          phase: 'followup',
          followup_questions: mockQuestions,
          result: null,
        }),
      })

      const { result } = renderHook(() => useDiagnoseSession())

      await act(async () => {
        await result.current.startSession({
          purpose: 'coding',
          autonomy: 'collaborative',
        })
      })

      expect(result.current.followupQuestions).toEqual(mockQuestions)
    })

    it('completeフェーズで結果を受け取る', async () => {
      const mockResult = {
        user_profile: {
          primary_use_case: 'coding',
          autonomy_preference: 'collaborative',
          communication_style: 'technical',
          key_traits: ['detail-oriented'],
          detected_needs: ['code review'],
        },
        recommended_style: 'standard',
        recommendation_reason: 'Based on your preferences',
        variants: [
          { style: 'short', name: 'Short', prompt: 'p1', description: 'd1' },
          { style: 'standard', name: 'Standard', prompt: 'p2', description: 'd2' },
          { style: 'strict', name: 'Strict', prompt: 'p3', description: 'd3' },
        ],
        source: 'mock',
      }

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          session_id: 'test-session',
          phase: 'complete',
          followup_questions: null,
          result: mockResult,
        }),
      })

      const { result } = renderHook(() => useDiagnoseSession())

      await act(async () => {
        await result.current.startSession({
          purpose: 'test',
          autonomy: 'obedient',
        })
      })

      expect(result.current.phase).toBe('complete')
      expect(result.current.result).toEqual(mockResult)
    })

    it('エラーを処理する', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: () => Promise.resolve({ detail: 'Internal server error' }),
      })

      const { result } = renderHook(() => useDiagnoseSession())

      await act(async () => {
        await result.current.startSession({
          purpose: 'test',
          autonomy: 'obedient',
        })
      })

      expect(result.current.error).not.toBeNull()
      expect(result.current.isLoading).toBe(false)
    })
  })

  describe('continueSession', () => {
    it('セッションを継続できる', async () => {
      // まずセッションを開始
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          session_id: 'test-session',
          phase: 'followup',
          followup_questions: [{ id: 'fq1', question: 'test?', type: 'freeform' }],
          result: null,
        }),
      })

      const { result } = renderHook(() => useDiagnoseSession())

      await act(async () => {
        await result.current.startSession({
          purpose: 'test',
          autonomy: 'collaborative',
        })
      })

      // 継続
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          session_id: 'test-session',
          phase: 'complete',
          followup_questions: null,
          result: {
            user_profile: {
              primary_use_case: 'test',
              autonomy_preference: 'collaborative',
              communication_style: 'casual',
              key_traits: [],
              detected_needs: [],
            },
            recommended_style: 'standard',
            recommendation_reason: 'reason',
            variants: [
              { style: 'short', name: 'Short', prompt: 'p', description: 'd' },
              { style: 'standard', name: 'Standard', prompt: 'p', description: 'd' },
              { style: 'strict', name: 'Strict', prompt: 'p', description: 'd' },
            ],
            source: 'mock',
          },
        }),
      })

      await act(async () => {
        await result.current.continueSession([
          { question_id: 'fq1', answer: 'test answer' },
        ])
      })

      expect(result.current.phase).toBe('complete')
      expect(result.current.result).not.toBeNull()
    })

    it('セッションなしで継続するとエラー', async () => {
      const { result } = renderHook(() => useDiagnoseSession())

      await act(async () => {
        await result.current.continueSession([])
      })

      expect(result.current.error).not.toBeNull()
    })
  })

  describe('reset', () => {
    it('状態をリセットできる', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          session_id: 'test-session',
          phase: 'followup',
          followup_questions: [],
          result: null,
        }),
      })

      const { result } = renderHook(() => useDiagnoseSession())

      await act(async () => {
        await result.current.startSession({
          purpose: 'test',
          autonomy: 'obedient',
        })
      })

      expect(result.current.sessionId).toBe('test-session')

      act(() => {
        result.current.reset()
      })

      expect(result.current.sessionId).toBeNull()
      expect(result.current.phase).toBeNull()
      expect(result.current.followupQuestions).toEqual([])
      expect(result.current.result).toBeNull()
      expect(result.current.error).toBeNull()
    })
  })

  describe('API URL設定', () => {
    it('baseUrlを設定できる', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          session_id: 'test',
          phase: 'complete',
          followup_questions: null,
          result: {
            user_profile: {
              primary_use_case: 'test',
              autonomy_preference: 'obedient',
              communication_style: 'casual',
              key_traits: [],
              detected_needs: [],
            },
            recommended_style: 'short',
            recommendation_reason: 'reason',
            variants: [
              { style: 'short', name: 'Short', prompt: 'p', description: 'd' },
              { style: 'standard', name: 'Standard', prompt: 'p', description: 'd' },
              { style: 'strict', name: 'Strict', prompt: 'p', description: 'd' },
            ],
            source: 'mock',
          },
        }),
      })

      const { result } = renderHook(() =>
        useDiagnoseSession({ baseUrl: 'http://custom-api:8000' })
      )

      await act(async () => {
        await result.current.startSession({
          purpose: 'test',
          autonomy: 'obedient',
        })
      })

      expect(mockFetch).toHaveBeenCalledWith(
        'http://custom-api:8000/api/v2/diagnose/start',
        expect.any(Object)
      )
    })
  })

  describe('APIキー設定', () => {
    it('APIキーをヘッダーに含める', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          session_id: 'test',
          phase: 'complete',
          followup_questions: null,
          result: {
            user_profile: {
              primary_use_case: 'test',
              autonomy_preference: 'obedient',
              communication_style: 'casual',
              key_traits: [],
              detected_needs: [],
            },
            recommended_style: 'short',
            recommendation_reason: 'reason',
            variants: [
              { style: 'short', name: 'Short', prompt: 'p', description: 'd' },
              { style: 'standard', name: 'Standard', prompt: 'p', description: 'd' },
              { style: 'strict', name: 'Strict', prompt: 'p', description: 'd' },
            ],
            source: 'mock',
          },
        }),
      })

      const { result } = renderHook(() =>
        useDiagnoseSession({ apiKey: 'test-api-key' })
      )

      await act(async () => {
        await result.current.startSession({
          purpose: 'test',
          autonomy: 'obedient',
        })
      })

      expect(mockFetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            'X-API-Key': 'test-api-key',
          }),
        })
      )
    })
  })
})
