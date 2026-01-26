/**
 * ApiKeyInput コンポーネントのテスト
 * TDD: テストを先に書き、失敗を確認してから実装する
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { ApiKeyInput, getStoredApiKey, getStoredProvider, Provider, PROVIDER_CONFIG } from './ApiKeyInput'

// sessionStorageをモック
const mockSessionStorage: Record<string, string> = {}
const sessionStorageMock = {
  getItem: vi.fn((key: string) => mockSessionStorage[key] || null),
  setItem: vi.fn((key: string, value: string) => {
    mockSessionStorage[key] = value
  }),
  removeItem: vi.fn((key: string) => {
    delete mockSessionStorage[key]
  }),
  clear: vi.fn(() => {
    Object.keys(mockSessionStorage).forEach((key) => delete mockSessionStorage[key])
  }),
}

Object.defineProperty(window, 'sessionStorage', {
  value: sessionStorageMock,
  writable: true,
})

describe('ApiKeyInput', () => {
  beforeEach(() => {
    sessionStorageMock.clear()
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  describe('Provider Selection', () => {
    it('デフォルトプロバイダーはgroq', () => {
      const onApiKeyChange = vi.fn()
      render(<ApiKeyInput onApiKeyChange={onApiKeyChange} />)

      // ドロップダウンの現在の値がGroqであることを確認
      const providerSelect = screen.getByRole('combobox')
      expect(providerSelect).toHaveValue('groq')
    })

    it('プロバイダー選択がsessionStorageに保存される', () => {
      const onApiKeyChange = vi.fn()
      const onProviderChange = vi.fn()
      render(
        <ApiKeyInput
          onApiKeyChange={onApiKeyChange}
          onProviderChange={onProviderChange}
        />
      )

      const providerSelect = screen.getByRole('combobox')
      fireEvent.change(providerSelect, { target: { value: 'openai' } })

      expect(sessionStorageMock.setItem).toHaveBeenCalledWith('llm_provider', 'openai')
    })

    it('getStoredProvider()が保存されたプロバイダーを返す', () => {
      mockSessionStorage['llm_provider'] = 'gemini'

      const result = getStoredProvider()
      expect(result).toBe('gemini')
    })

    it('プロバイダー変更時にonProviderChangeが呼ばれる', () => {
      const onApiKeyChange = vi.fn()
      const onProviderChange = vi.fn()
      render(
        <ApiKeyInput
          onApiKeyChange={onApiKeyChange}
          onProviderChange={onProviderChange}
        />
      )

      const providerSelect = screen.getByRole('combobox')
      fireEvent.change(providerSelect, { target: { value: 'openai' } })

      expect(onProviderChange).toHaveBeenCalledWith('openai')
    })

    it('保存されたプロバイダーが初期値として使用される', () => {
      mockSessionStorage['llm_provider'] = 'gemini'

      const onApiKeyChange = vi.fn()
      render(<ApiKeyInput onApiKeyChange={onApiKeyChange} />)

      const providerSelect = screen.getByRole('combobox')
      expect(providerSelect).toHaveValue('gemini')
    })
  })

  describe('Provider UI', () => {
    it('プロバイダードロップダウンが表示される', () => {
      const onApiKeyChange = vi.fn()
      render(<ApiKeyInput onApiKeyChange={onApiKeyChange} />)

      const providerSelect = screen.getByRole('combobox')
      expect(providerSelect).toBeInTheDocument()

      // 全プロバイダーがオプションとして存在する
      expect(screen.getByRole('option', { name: /OpenAI/i })).toBeInTheDocument()
      expect(screen.getByRole('option', { name: /Groq/i })).toBeInTheDocument()
      expect(screen.getByRole('option', { name: /Gemini/i })).toBeInTheDocument()
    })

    it('OpenAI選択時にプレースホルダーが"sk-..."に変わる', () => {
      const onApiKeyChange = vi.fn()
      render(<ApiKeyInput onApiKeyChange={onApiKeyChange} />)

      // まずAPIキー入力ボタンをクリック
      const setKeyButton = screen.getByText('APIキーを設定')
      fireEvent.click(setKeyButton)

      // プロバイダーをOpenAIに変更
      const providerSelect = screen.getByRole('combobox')
      fireEvent.change(providerSelect, { target: { value: 'openai' } })

      // 入力フィールドのプレースホルダーを確認
      const input = screen.getByPlaceholderText('sk-...')
      expect(input).toBeInTheDocument()
    })

    it('Groq選択時にプレースホルダーが"gsk_..."に変わる', () => {
      const onApiKeyChange = vi.fn()
      render(<ApiKeyInput onApiKeyChange={onApiKeyChange} />)

      // APIキー入力ボタンをクリック
      const setKeyButton = screen.getByText('APIキーを設定')
      fireEvent.click(setKeyButton)

      // プロバイダーをGroqに（デフォルト）
      const providerSelect = screen.getByRole('combobox')
      fireEvent.change(providerSelect, { target: { value: 'groq' } })

      // 入力フィールドのプレースホルダーを確認
      const input = screen.getByPlaceholderText('gsk_...')
      expect(input).toBeInTheDocument()
    })

    it('Gemini選択時にプレースホルダーが"AI..."に変わる', () => {
      const onApiKeyChange = vi.fn()
      render(<ApiKeyInput onApiKeyChange={onApiKeyChange} />)

      // APIキー入力ボタンをクリック
      const setKeyButton = screen.getByText('APIキーを設定')
      fireEvent.click(setKeyButton)

      // プロバイダーをGeminiに変更
      const providerSelect = screen.getByRole('combobox')
      fireEvent.change(providerSelect, { target: { value: 'gemini' } })

      // 入力フィールドのプレースホルダーを確認
      const input = screen.getByPlaceholderText('AI...')
      expect(input).toBeInTheDocument()
    })

    it('プロバイダー変更時にヘルプリンクが更新される', () => {
      const onApiKeyChange = vi.fn()
      render(<ApiKeyInput onApiKeyChange={onApiKeyChange} />)

      // OpenAIに変更
      const providerSelect = screen.getByRole('combobox')
      fireEvent.change(providerSelect, { target: { value: 'openai' } })

      // OpenAIのリンクが表示されることを確認
      const link = screen.getByRole('link')
      expect(link).toHaveAttribute('href', PROVIDER_CONFIG.openai.url)
    })
  })

  describe('PROVIDER_CONFIG', () => {
    it('各プロバイダーの設定が正しく定義されている', () => {
      expect(PROVIDER_CONFIG.openai).toEqual({
        name: 'OpenAI',
        modelInfo: 'GPT-4o',
        placeholder: 'sk-...',
        url: 'https://platform.openai.com/api-keys',
      })

      expect(PROVIDER_CONFIG.groq).toEqual({
        name: 'Groq',
        modelInfo: 'Llama 3.3',
        placeholder: 'gsk_...',
        url: 'https://console.groq.com/keys',
      })

      expect(PROVIDER_CONFIG.gemini).toEqual({
        name: 'Gemini',
        modelInfo: 'Gemini 2.0',
        placeholder: 'AI...',
        url: 'https://aistudio.google.com/apikey',
      })
    })
  })

  describe('APIキー保存', () => {
    it('APIキーを保存できる', () => {
      const onApiKeyChange = vi.fn()
      render(<ApiKeyInput onApiKeyChange={onApiKeyChange} />)

      // APIキー入力ボタンをクリック
      const setKeyButton = screen.getByText('APIキーを設定')
      fireEvent.click(setKeyButton)

      // APIキーを入力
      const input = screen.getByPlaceholderText('gsk_...')
      fireEvent.change(input, { target: { value: 'gsk_test_key' } })

      // 保存ボタンをクリック
      const saveButton = screen.getByText('保存')
      fireEvent.click(saveButton)

      expect(sessionStorageMock.setItem).toHaveBeenCalledWith('llm_api_key', 'gsk_test_key')
      expect(onApiKeyChange).toHaveBeenCalledWith(true)
    })

    it('getStoredApiKey()が保存されたAPIキーを返す', () => {
      mockSessionStorage['llm_api_key'] = 'test_api_key'

      const result = getStoredApiKey()
      expect(result).toBe('test_api_key')
    })
  })
})
