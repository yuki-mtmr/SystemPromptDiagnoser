"""
Tests for LLM service with timeout functionality.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import time

from services.llm_service import LLMService, create_llm_service, LLMTimeoutError


class TestLLMServiceTimeout:
    """Test LLM service timeout functionality."""

    def test_llm_service_has_timeout_parameter(self):
        """Test that LLM service accepts timeout parameter."""
        service = LLMService(api_key="test-key", timeout=10)
        assert service.timeout == 10

    def test_llm_service_default_timeout_is_20_seconds(self):
        """Test that default timeout is 20 seconds."""
        service = LLMService(api_key="test-key")
        assert service.timeout == 20

    def test_create_llm_service_accepts_timeout(self):
        """Test that create_llm_service accepts timeout parameter."""
        service = create_llm_service(api_key="test-key", timeout=15)
        assert service.timeout == 15

    def test_timeout_error_is_raised_on_timeout(self):
        """Test that LLMTimeoutError is raised when timeout occurs."""
        # _generate_prompt_internal をモックして遅延をシミュレート
        with patch.object(LLMService, '_generate_prompt_internal') as mock_generate:
            def slow_generate(*args, **kwargs):
                time.sleep(1)  # タイムアウトより長い
                return "Generated prompt"

            mock_generate.side_effect = slow_generate

            service = LLMService(api_key="test-key", timeout=0.1)

            with pytest.raises(LLMTimeoutError):
                service.generate_system_prompt(
                    strictness="flexible",
                    response_length="standard",
                    tone="formal",
                    use_case="coding",
                    style="short"
                )

    def test_successful_call_within_timeout(self):
        """Test that calls within timeout succeed."""
        # Default provider is now Groq, so mock ChatGroq
        with patch('services.llm_service.ChatGroq') as mock_chat:
            mock_instance = Mock()
            mock_instance.invoke.return_value = Mock(content="Generated prompt")
            mock_chat.return_value = mock_instance

            service = LLMService(api_key="test-key", timeout=10)

            # StrOutputParserもモックする必要がある
            with patch('services.llm_service.StrOutputParser') as mock_parser:
                mock_parser_instance = Mock()
                mock_parser_instance.__or__ = Mock(return_value=Mock(
                    invoke=Mock(return_value="Generated prompt")
                ))
                mock_parser.return_value = mock_parser_instance

                result = service.generate_system_prompt(
                    strictness="flexible",
                    response_length="standard",
                    tone="formal",
                    use_case="coding",
                    style="short"
                )

                assert result is not None


class TestLLMTimeoutError:
    """Test LLMTimeoutError exception."""

    def test_timeout_error_is_exception(self):
        """Test that LLMTimeoutError is an Exception."""
        error = LLMTimeoutError("Test timeout")
        assert isinstance(error, Exception)

    def test_timeout_error_message(self):
        """Test that LLMTimeoutError has correct message."""
        error = LLMTimeoutError("Custom message")
        assert str(error) == "Custom message"
