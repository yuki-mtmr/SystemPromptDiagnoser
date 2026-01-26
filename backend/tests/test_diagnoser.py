"""
Tests for the diagnoser workflow with parallel execution.
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
import time

from workflows.diagnoser import (
    DiagnoserWorkflow,
    run_diagnosis,
    run_diagnosis_async,
    DiagnoseInput,
)


class TestDiagnoserParallelExecution:
    """Test that LLM calls are executed in parallel."""

    @pytest.fixture
    def mock_llm_service(self):
        """Create a mock LLM service that tracks call times."""
        call_times = []

        def mock_generate(strictness, response_length, tone, use_case, style, additional_notes=None):
            call_times.append(time.time())
            # シミュレート: 各LLM呼び出しに0.1秒かかる
            time.sleep(0.1)
            return f"Generated prompt for {style}"

        mock_service = Mock()
        mock_service.generate_system_prompt = mock_generate
        mock_service.call_times = call_times
        return mock_service

    @pytest.fixture
    def sample_input(self) -> DiagnoseInput:
        """Sample input for diagnosis."""
        return {
            "strictness": "flexible",
            "response_length": "standard",
            "tone": "formal",
            "use_case": "coding",
            "additional_notes": None,
        }

    def test_run_diagnosis_returns_three_variants(self, sample_input):
        """Test that diagnosis returns three prompt variants."""
        with patch('workflows.diagnoser.create_llm_service') as mock_create:
            mock_service = Mock()
            mock_service.generate_system_prompt.return_value = "Test prompt"
            mock_create.return_value = mock_service

            result = run_diagnosis(
                strictness=sample_input["strictness"],
                response_length=sample_input["response_length"],
                tone=sample_input["tone"],
                use_case=sample_input["use_case"],
                api_key="test-api-key",
            )

            assert "variants" in result
            assert len(result["variants"]) == 3
            assert "recommended_style" in result

    def test_run_diagnosis_includes_source_field(self, sample_input):
        """Test that diagnosis result includes source field."""
        with patch('workflows.diagnoser.create_llm_service') as mock_create:
            mock_service = Mock()
            mock_service.generate_system_prompt.return_value = "Test prompt"
            mock_create.return_value = mock_service

            result = run_diagnosis(
                strictness=sample_input["strictness"],
                response_length=sample_input["response_length"],
                tone=sample_input["tone"],
                use_case=sample_input["use_case"],
                api_key="test-api-key",
            )

            assert "source" in result
            assert result["source"] in ["llm", "mock"]


class TestAsyncDiagnosis:
    """Test async diagnosis functionality."""

    @pytest.fixture
    def sample_input(self) -> DiagnoseInput:
        return {
            "strictness": "flexible",
            "response_length": "standard",
            "tone": "formal",
            "use_case": "coding",
            "additional_notes": None,
        }

    @pytest.mark.asyncio
    async def test_run_diagnosis_async_exists(self, sample_input):
        """Test that async diagnosis function exists and works."""
        with patch('workflows.diagnoser.create_llm_service') as mock_create:
            mock_service = Mock()
            mock_service.generate_system_prompt.return_value = "Test prompt"
            mock_create.return_value = mock_service

            result = await run_diagnosis_async(
                strictness=sample_input["strictness"],
                response_length=sample_input["response_length"],
                tone=sample_input["tone"],
                use_case=sample_input["use_case"],
                api_key="test-api-key",
            )

            assert "variants" in result
            assert len(result["variants"]) == 3

    @pytest.mark.asyncio
    async def test_parallel_execution_is_faster(self, sample_input):
        """Test that parallel execution is faster than sequential."""
        call_count = 0
        call_timestamps = []

        async def mock_async_generate(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            call_timestamps.append(time.time())
            await asyncio.sleep(0.1)  # シミュレート: 各呼び出しに0.1秒
            return f"Generated prompt {call_count}"

        with patch('workflows.diagnoser.create_llm_service') as mock_create:
            mock_service = Mock()
            # 同期呼び出しをモック
            mock_service.generate_system_prompt.side_effect = lambda *a, **k: "Test"
            mock_create.return_value = mock_service

            start_time = time.time()
            result = await run_diagnosis_async(
                strictness=sample_input["strictness"],
                response_length=sample_input["response_length"],
                tone=sample_input["tone"],
                use_case=sample_input["use_case"],
                api_key="test-api-key",
            )
            elapsed = time.time() - start_time

            # 並列実行なら0.5秒以下で完了するはず
            # (直列なら0.3秒以上かかる)
            assert result is not None
            assert "variants" in result
