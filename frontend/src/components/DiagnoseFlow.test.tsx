/**
 * DiagnoseFlow コンポーネントのテスト
 * TDD: まずテストを書き、失敗を確認してから実装する
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { DiagnoseFlow } from './DiagnoseFlow'
import type { DiagnoseV2Result } from '../hooks/useDiagnoseSession'

// fetchをモック
const mockFetch = vi.fn()
global.fetch = mockFetch

describe('DiagnoseFlow', () => {
  const mockOnComplete = vi.fn()
  const mockOnError = vi.fn()

  beforeEach(() => {
    mockFetch.mockReset()
    mockOnComplete.mockReset()
    mockOnError.mockReset()
  })

  const mockResult: DiagnoseV2Result = {
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
      { style: 'short', name: 'Short', prompt: 'Short prompt', description: 'Short desc' },
      { style: 'standard', name: 'Standard', prompt: 'Standard prompt', description: 'Standard desc' },
      { style: 'strict', name: 'Strict', prompt: 'Strict prompt', description: 'Strict desc' },
    ],
    source: 'mock',
  }

  describe('フェーズ1: 初期質問', () => {
    it('初期状態で初期質問を表示する', () => {
      render(<DiagnoseFlow onComplete={mockOnComplete} />)

      // InitialQuestionsが表示されていることを確認
      expect(screen.getByLabelText(/何をしてもらいたい|What would you like/i)).toBeInTheDocument()
    })

    it('フェーズインジケーターを表示する', () => {
      render(<DiagnoseFlow onComplete={mockOnComplete} />)

      expect(screen.getByText(/ステップ|Step/i)).toBeInTheDocument()
    })
  })

  describe('フェーズ遷移', () => {
    it('初期質問送信後にフォローアップ質問を表示する', async () => {
      const user = userEvent.setup()

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          session_id: 'test-session',
          phase: 'followup',
          followup_questions: [
            {
              id: 'fq1',
              question: '使用言語は？',
              type: 'freeform',
              placeholder: '例: Python',
            },
          ],
          result: null,
        }),
      })

      render(<DiagnoseFlow onComplete={mockOnComplete} />)

      // 目的を入力
      const purposeInput = screen.getByLabelText(/何をしてもらいたい|What would you like/i)
      await user.type(purposeInput, 'コードレビュー')

      // 自律性を選択
      const autonomyOption = screen.getByText(/一緒に考える|Collaborate/i)
      await user.click(autonomyOption)

      // 送信
      const submitButton = screen.getByRole('button', { name: /次へ|Next|Submit/i })
      await user.click(submitButton)

      // フォローアップ質問が表示されるまで待機
      await waitFor(() => {
        expect(screen.getByText('使用言語は？')).toBeInTheDocument()
      })
    })

    it('フォローアップなしで直接完了する場合', async () => {
      const user = userEvent.setup()

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          session_id: 'test-session',
          phase: 'complete',
          followup_questions: null,
          result: mockResult,
        }),
      })

      render(<DiagnoseFlow onComplete={mockOnComplete} />)

      // 目的を入力
      const purposeInput = screen.getByLabelText(/何をしてもらいたい|What would you like/i)
      await user.type(purposeInput, 'テスト')

      // 自律性を選択
      const autonomyOption = screen.getByText(/指示に忠実|Follow instructions/i)
      await user.click(autonomyOption)

      // 送信
      const submitButton = screen.getByRole('button', { name: /次へ|Next|Submit/i })
      await user.click(submitButton)

      // onCompleteが呼ばれるまで待機
      await waitFor(() => {
        expect(mockOnComplete).toHaveBeenCalledWith(mockResult)
      })
    })
  })

  describe('ローディング表示', () => {
    it('API呼び出し中はローディングを表示する', async () => {
      const user = userEvent.setup()

      // 遅延レスポンス
      mockFetch.mockImplementation(() =>
        new Promise(resolve =>
          setTimeout(() => resolve({
            ok: true,
            json: () => Promise.resolve({
              session_id: 'test-session',
              phase: 'complete',
              followup_questions: null,
              result: mockResult,
            }),
          }), 500)
        )
      )

      render(<DiagnoseFlow onComplete={mockOnComplete} />)

      // 目的を入力
      const purposeInput = screen.getByLabelText(/何をしてもらいたい|What would you like/i)
      await user.type(purposeInput, 'テスト')

      // 自律性を選択
      const autonomyOption = screen.getByText(/指示に忠実|Follow instructions/i)
      await user.click(autonomyOption)

      // 送信
      const submitButton = screen.getByRole('button', { name: /次へ|Next|Submit/i })
      await user.click(submitButton)

      // ローディング表示を確認
      expect(screen.getByText(/処理中|Loading|分析中/i)).toBeInTheDocument()

      // 完了まで待機
      await waitFor(() => {
        expect(mockOnComplete).toHaveBeenCalled()
      }, { timeout: 2000 })
    })
  })

  describe('エラーハンドリング', () => {
    it('エラー時にonErrorを呼ぶ', async () => {
      const user = userEvent.setup()

      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: () => Promise.resolve({ detail: 'Server error' }),
      })

      render(<DiagnoseFlow onComplete={mockOnComplete} onError={mockOnError} />)

      // 目的を入力
      const purposeInput = screen.getByLabelText(/何をしてもらいたい|What would you like/i)
      await user.type(purposeInput, 'テスト')

      // 自律性を選択
      const autonomyOption = screen.getByText(/指示に忠実|Follow instructions/i)
      await user.click(autonomyOption)

      // 送信
      const submitButton = screen.getByRole('button', { name: /次へ|Next|Submit/i })
      await user.click(submitButton)

      // エラーが報告されるまで待機
      await waitFor(() => {
        expect(mockOnError).toHaveBeenCalled()
      })
    })

    it('エラーメッセージを表示する', async () => {
      const user = userEvent.setup()

      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: () => Promise.resolve({ detail: 'Server error' }),
      })

      render(<DiagnoseFlow onComplete={mockOnComplete} />)

      // 目的を入力
      const purposeInput = screen.getByLabelText(/何をしてもらいたい|What would you like/i)
      await user.type(purposeInput, 'テスト')

      // 自律性を選択
      const autonomyOption = screen.getByText(/指示に忠実|Follow instructions/i)
      await user.click(autonomyOption)

      // 送信
      const submitButton = screen.getByRole('button', { name: /次へ|Next|Submit/i })
      await user.click(submitButton)

      // エラーメッセージが表示されるまで待機
      await waitFor(() => {
        expect(screen.getByText(/エラーが発生しました/i)).toBeInTheDocument()
      })
    })
  })

  describe('リセット', () => {
    it('リセットボタンで最初からやり直せる', async () => {
      const user = userEvent.setup()

      // エラーを発生させてリセットボタンを表示
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: () => Promise.resolve({ detail: 'Error' }),
      })

      render(<DiagnoseFlow onComplete={mockOnComplete} />)

      // 目的を入力
      const purposeInput = screen.getByLabelText(/何をしてもらいたい|What would you like/i)
      await user.type(purposeInput, 'テスト')

      // 自律性を選択
      const autonomyOption = screen.getByText(/指示に忠実|Follow instructions/i)
      await user.click(autonomyOption)

      // 送信
      const submitButton = screen.getByRole('button', { name: /次へ|Next|Submit/i })
      await user.click(submitButton)

      // エラー表示を待つ
      await waitFor(() => {
        expect(screen.getByText(/エラーが発生しました/i)).toBeInTheDocument()
      })

      // リセットボタンをクリック
      const resetButton = screen.getByRole('button', { name: /最初からやり直す|Retry|Reset/i })
      await user.click(resetButton)

      // 初期質問が再表示される
      await waitFor(() => {
        expect(screen.getByLabelText(/何をしてもらいたい|What would you like/i)).toBeInTheDocument()
      })
    })
  })
})
