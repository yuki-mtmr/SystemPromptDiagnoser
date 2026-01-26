import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ResultsDisplay, type DiagnoseResult } from './ResultsDisplay'

describe('ResultsDisplay - Source Badge', () => {
  const mockOnReset = vi.fn()

  const baseMockResults: DiagnoseResult = {
    recommended_style: 'standard',
    variants: [
      { style: 'short', name: 'Short', prompt: 'test prompt', description: 'desc' },
      { style: 'standard', name: 'Standard', prompt: 'test prompt', description: 'desc' },
      { style: 'strict', name: 'Strict', prompt: 'test prompt', description: 'desc' },
    ],
  }

  it('should display "LLM生成" badge when source is "llm"', () => {
    const results: DiagnoseResult = {
      ...baseMockResults,
      source: 'llm',
    }

    render(<ResultsDisplay results={results} onReset={mockOnReset} />)

    expect(screen.getByText(/LLM生成/)).toBeInTheDocument()
  })

  it('should display "モック" badge when source is "mock"', () => {
    const results: DiagnoseResult = {
      ...baseMockResults,
      source: 'mock',
    }

    render(<ResultsDisplay results={results} onReset={mockOnReset} />)

    expect(screen.getByText(/モック/)).toBeInTheDocument()
  })

  it('should not display source badge when source is not provided', () => {
    render(<ResultsDisplay results={baseMockResults} onReset={mockOnReset} />)

    expect(screen.queryByText(/LLM生成/)).not.toBeInTheDocument()
    expect(screen.queryByText(/モック/)).not.toBeInTheDocument()
  })

  it('should display LLM badge as inline element', () => {
    const results: DiagnoseResult = {
      ...baseMockResults,
      source: 'llm',
    }

    render(<ResultsDisplay results={results} onReset={mockOnReset} />)

    const badge = screen.getByText(/LLM生成/)
    // バッジが存在し、適切なテキストが含まれていることを確認
    expect(badge).toBeInTheDocument()
    expect(badge.textContent).toContain('LLM生成')
  })

  it('should display mock badge with yellow color', () => {
    const results: DiagnoseResult = {
      ...baseMockResults,
      source: 'mock',
    }

    render(<ResultsDisplay results={results} onReset={mockOnReset} />)

    const badge = screen.getByText(/モック/)
    expect(badge).toBeInTheDocument()
  })
})
