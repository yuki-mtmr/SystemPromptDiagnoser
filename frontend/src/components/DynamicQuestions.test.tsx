/**
 * DynamicQuestions コンポーネントのテスト
 * TDD: まずテストを書き、失敗を確認してから実装する
 */
import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { DynamicQuestions } from './DynamicQuestions'
import type { Question } from '../hooks/useDiagnoseSession'

describe('DynamicQuestions', () => {
  const mockOnSubmit = vi.fn()

  beforeEach(() => {
    mockOnSubmit.mockReset()
  })

  const freeformQuestion: Question = {
    id: 'fq1',
    question: 'どのような言語を使用していますか？',
    type: 'freeform',
    placeholder: '例: Python, JavaScript',
  }

  const choiceQuestion: Question = {
    id: 'fq2',
    question: 'フィードバックの形式は？',
    type: 'choice',
    choices: [
      { value: 'detailed', label: '詳細', description: '詳しい説明付き' },
      { value: 'brief', label: '簡潔', description: '要点のみ' },
    ],
  }

  describe('レンダリング', () => {
    it('質問が表示される', () => {
      render(
        <DynamicQuestions
          questions={[freeformQuestion]}
          onSubmit={mockOnSubmit}
        />
      )

      expect(screen.getByText(freeformQuestion.question)).toBeInTheDocument()
    })

    it('複数の質問を表示できる', () => {
      render(
        <DynamicQuestions
          questions={[freeformQuestion, choiceQuestion]}
          onSubmit={mockOnSubmit}
        />
      )

      expect(screen.getByText(freeformQuestion.question)).toBeInTheDocument()
      expect(screen.getByText(choiceQuestion.question)).toBeInTheDocument()
    })

    it('freeform質問にはテキスト入力が表示される', () => {
      render(
        <DynamicQuestions
          questions={[freeformQuestion]}
          onSubmit={mockOnSubmit}
        />
      )

      expect(screen.getByPlaceholderText(/Python|JavaScript/i)).toBeInTheDocument()
    })

    it('choice質問には選択肢が表示される', () => {
      render(
        <DynamicQuestions
          questions={[choiceQuestion]}
          onSubmit={mockOnSubmit}
        />
      )

      expect(screen.getByText('詳細')).toBeInTheDocument()
      expect(screen.getByText('簡潔')).toBeInTheDocument()
    })

    it('送信ボタンを表示する', () => {
      render(
        <DynamicQuestions
          questions={[freeformQuestion]}
          onSubmit={mockOnSubmit}
        />
      )

      expect(screen.getByRole('button', { name: /次へ|Next|Submit|回答する|送信/i })).toBeInTheDocument()
    })
  })

  describe('入力', () => {
    it('freeformに入力できる', async () => {
      const user = userEvent.setup()
      render(
        <DynamicQuestions
          questions={[freeformQuestion]}
          onSubmit={mockOnSubmit}
        />
      )

      const input = screen.getByPlaceholderText(/Python|JavaScript/i)
      await user.type(input, 'TypeScript')

      expect(input).toHaveValue('TypeScript')
    })

    it('choiceを選択できる', async () => {
      const user = userEvent.setup()
      render(
        <DynamicQuestions
          questions={[choiceQuestion]}
          onSubmit={mockOnSubmit}
        />
      )

      const option = screen.getByText('詳細')
      await user.click(option)

      const radio = screen.getByRole('radio', { name: /詳細/i })
      expect(radio).toBeChecked()
    })
  })

  describe('送信', () => {
    it('freeform回答を送信できる', async () => {
      const user = userEvent.setup()
      render(
        <DynamicQuestions
          questions={[freeformQuestion]}
          onSubmit={mockOnSubmit}
        />
      )

      const input = screen.getByPlaceholderText(/Python|JavaScript/i)
      await user.type(input, 'TypeScript')

      const submitButton = screen.getByRole('button', { name: /次へ|Next|Submit|回答する|送信/i })
      await user.click(submitButton)

      expect(mockOnSubmit).toHaveBeenCalledWith([
        { question_id: 'fq1', answer: 'TypeScript' },
      ])
    })

    it('choice回答を送信できる', async () => {
      const user = userEvent.setup()
      render(
        <DynamicQuestions
          questions={[choiceQuestion]}
          onSubmit={mockOnSubmit}
        />
      )

      const option = screen.getByText('詳細')
      await user.click(option)

      const submitButton = screen.getByRole('button', { name: /次へ|Next|Submit|回答する|送信/i })
      await user.click(submitButton)

      expect(mockOnSubmit).toHaveBeenCalledWith([
        { question_id: 'fq2', answer: 'detailed' },
      ])
    })

    it('複数の回答を送信できる', async () => {
      const user = userEvent.setup()
      render(
        <DynamicQuestions
          questions={[freeformQuestion, choiceQuestion]}
          onSubmit={mockOnSubmit}
        />
      )

      // freeformに入力
      const input = screen.getByPlaceholderText(/Python|JavaScript/i)
      await user.type(input, 'Rust')

      // choiceを選択
      const option = screen.getByText('簡潔')
      await user.click(option)

      // 送信
      const submitButton = screen.getByRole('button', { name: /次へ|Next|Submit|回答する|送信/i })
      await user.click(submitButton)

      expect(mockOnSubmit).toHaveBeenCalledWith([
        { question_id: 'fq1', answer: 'Rust' },
        { question_id: 'fq2', answer: 'brief' },
      ])
    })
  })

  describe('スキップ', () => {
    it('スキップボタンがある', () => {
      render(
        <DynamicQuestions
          questions={[freeformQuestion]}
          onSubmit={mockOnSubmit}
          allowSkip={true}
        />
      )

      expect(screen.getByRole('button', { name: /スキップ|Skip/i })).toBeInTheDocument()
    })

    it('スキップすると空の回答で送信される', async () => {
      const user = userEvent.setup()
      render(
        <DynamicQuestions
          questions={[freeformQuestion]}
          onSubmit={mockOnSubmit}
          allowSkip={true}
        />
      )

      const skipButton = screen.getByRole('button', { name: /スキップ|Skip/i })
      await user.click(skipButton)

      expect(mockOnSubmit).toHaveBeenCalledWith([])
    })
  })

  describe('ローディング状態', () => {
    it('ローディング中は送信ボタンが無効', () => {
      render(
        <DynamicQuestions
          questions={[freeformQuestion]}
          onSubmit={mockOnSubmit}
          isLoading={true}
        />
      )

      const submitButton = screen.getByRole('button', { name: /次へ|Next|Submit|回答する|送信|処理中|Loading/i })
      expect(submitButton).toBeDisabled()
    })
  })

  describe('空の質問', () => {
    it('質問がない場合はメッセージを表示', () => {
      render(
        <DynamicQuestions
          questions={[]}
          onSubmit={mockOnSubmit}
        />
      )

      expect(screen.getByText(/質問がありません|No questions/i)).toBeInTheDocument()
    })
  })
})
