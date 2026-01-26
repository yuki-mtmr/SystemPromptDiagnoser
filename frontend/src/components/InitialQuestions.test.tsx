/**
 * InitialQuestions コンポーネントのテスト
 * TDD: まずテストを書き、失敗を確認してから実装する
 */
import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { InitialQuestions } from './InitialQuestions'

describe('InitialQuestions', () => {
  const mockOnSubmit = vi.fn()

  beforeEach(() => {
    mockOnSubmit.mockReset()
  })

  describe('レンダリング', () => {
    it('目的の入力フィールドを表示する', () => {
      render(<InitialQuestions onSubmit={mockOnSubmit} />)

      expect(screen.getByLabelText(/何をしてもらいたい|What would you like/i)).toBeInTheDocument()
    })

    it('自律性の選択肢を表示する', () => {
      render(<InitialQuestions onSubmit={mockOnSubmit} />)

      expect(screen.getByText(/指示に忠実|Follow instructions/i)).toBeInTheDocument()
      expect(screen.getByText(/一緒に考える|Collaborate/i)).toBeInTheDocument()
      expect(screen.getByText(/自律的|Autonomous/i)).toBeInTheDocument()
    })

    it('サジェストチップを表示する', () => {
      render(<InitialQuestions onSubmit={mockOnSubmit} />)

      // サジェストチップが表示されていることを確認
      expect(screen.getByRole('button', { name: /コーディング|Coding/i })).toBeInTheDocument()
    })

    it('送信ボタンを表示する', () => {
      render(<InitialQuestions onSubmit={mockOnSubmit} />)

      expect(screen.getByRole('button', { name: /次へ|Next|Submit/i })).toBeInTheDocument()
    })
  })

  describe('入力', () => {
    it('目的を入力できる', async () => {
      const user = userEvent.setup()
      render(<InitialQuestions onSubmit={mockOnSubmit} />)

      const input = screen.getByLabelText(/何をしてもらいたい|What would you like/i)
      await user.type(input, 'コードレビューをしてほしい')

      expect(input).toHaveValue('コードレビューをしてほしい')
    })

    it('サジェストチップをクリックすると入力に追加される', async () => {
      const user = userEvent.setup()
      render(<InitialQuestions onSubmit={mockOnSubmit} />)

      const chip = screen.getByRole('button', { name: /コーディング|Coding/i })
      await user.click(chip)

      const input = screen.getByLabelText(/何をしてもらいたい|What would you like/i) as HTMLTextAreaElement
      // 値にコーディングが含まれていることを確認
      expect(input.value).toContain('コーディング')
    })

    it('自律性を選択できる', async () => {
      const user = userEvent.setup()
      render(<InitialQuestions onSubmit={mockOnSubmit} />)

      const collaborativeOption = screen.getByText(/一緒に考える|Collaborate/i)
      await user.click(collaborativeOption)

      // 選択されたことを確認（aria-checkedまたはdata-selected）
      const radio = screen.getByRole('radio', { name: /一緒に考える|Collaborate/i })
      expect(radio).toBeChecked()
    })
  })

  describe('バリデーション', () => {
    it('目的が空の場合は送信できない', async () => {
      const user = userEvent.setup()
      render(<InitialQuestions onSubmit={mockOnSubmit} />)

      // 自律性を選択
      const option = screen.getByText(/一緒に考える|Collaborate/i)
      await user.click(option)

      // 送信ボタンをクリック
      const submitButton = screen.getByRole('button', { name: /次へ|Next|Submit/i })
      await user.click(submitButton)

      expect(mockOnSubmit).not.toHaveBeenCalled()
    })

    it('自律性が未選択の場合は送信できない', async () => {
      const user = userEvent.setup()
      render(<InitialQuestions onSubmit={mockOnSubmit} />)

      // 目的を入力
      const input = screen.getByLabelText(/何をしてもらいたい|What would you like/i)
      await user.type(input, 'test')

      // 送信ボタンをクリック
      const submitButton = screen.getByRole('button', { name: /次へ|Next|Submit/i })
      await user.click(submitButton)

      expect(mockOnSubmit).not.toHaveBeenCalled()
    })
  })

  describe('送信', () => {
    it('有効な入力で送信できる', async () => {
      const user = userEvent.setup()
      render(<InitialQuestions onSubmit={mockOnSubmit} />)

      // 目的を入力
      const input = screen.getByLabelText(/何をしてもらいたい|What would you like/i)
      await user.type(input, 'コードレビュー')

      // 自律性を選択
      const option = screen.getByText(/一緒に考える|Collaborate/i)
      await user.click(option)

      // 送信
      const submitButton = screen.getByRole('button', { name: /次へ|Next|Submit/i })
      await user.click(submitButton)

      expect(mockOnSubmit).toHaveBeenCalledWith({
        purpose: 'コードレビュー',
        autonomy: 'collaborative',
      })
    })
  })

  describe('ローディング状態', () => {
    it('ローディング中は送信ボタンが無効', () => {
      render(<InitialQuestions onSubmit={mockOnSubmit} isLoading={true} />)

      const submitButton = screen.getByRole('button', { name: /次へ|Next|Submit|処理中|Loading/i })
      expect(submitButton).toBeDisabled()
    })
  })
})
