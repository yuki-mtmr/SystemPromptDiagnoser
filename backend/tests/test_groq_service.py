"""
Tests for Groq LLM service integration.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock


class TestGroqLLMService:
    """Test Groq LLM service functionality."""

    def test_groq_service_can_be_created(self):
        """Test that Groq service can be instantiated."""
        from services.llm_service import LLMService, create_llm_service

        service = create_llm_service(api_key="test-groq-key", provider="groq")
        assert service is not None
        assert service.provider == "groq"

    def test_groq_service_default_timeout(self):
        """Test that Groq service has default 20s timeout."""
        from services.llm_service import LLMService

        service = LLMService(api_key="test-key", provider="groq")
        assert service.timeout == 20

    def test_groq_service_uses_correct_model(self):
        """Test that Groq service uses llama-3.3-70b-versatile model."""
        from services.llm_service import LLMService

        service = LLMService(api_key="test-key", provider="groq")
        assert service.model_name == "llama-3.3-70b-versatile"

    def test_groq_service_generates_prompt(self):
        """Test that Groq service can generate prompts."""
        with patch('services.llm_service.ChatGroq') as mock_groq:
            mock_instance = Mock()
            mock_instance.invoke.return_value = Mock(content="Generated prompt")
            mock_groq.return_value = mock_instance

            from services.llm_service import LLMService

            with patch('services.llm_service.StrOutputParser') as mock_parser:
                mock_parser_instance = Mock()
                mock_parser_instance.__or__ = Mock(return_value=Mock(
                    invoke=Mock(return_value="Generated prompt for Groq")
                ))
                mock_parser.return_value = mock_parser_instance

                service = LLMService(api_key="test-key", provider="groq")
                result = service.generate_system_prompt(
                    strictness="flexible",
                    response_length="standard",
                    tone="formal",
                    use_case="coding",
                    style="short"
                )

                assert result is not None


class TestProviderSelection:
    """Test provider selection between Gemini and Groq."""

    def test_default_provider_is_groq(self):
        """Test that default provider is now Groq."""
        from services.llm_service import LLMService

        service = LLMService(api_key="test-key")
        assert service.provider == "groq"

    def test_can_specify_gemini_provider(self):
        """Test that Gemini can still be specified explicitly."""
        from services.llm_service import LLMService

        service = LLMService(api_key="test-key", provider="gemini")
        assert service.provider == "gemini"

    def test_create_llm_service_accepts_provider(self):
        """Test that create_llm_service accepts provider parameter."""
        from services.llm_service import create_llm_service

        service = create_llm_service(api_key="test-key", provider="groq")
        assert service.provider == "groq"


class TestBackwardCompatibility:
    """Test backward compatibility with existing code."""

    def test_existing_api_still_works(self):
        """Test that existing API calls still work."""
        with patch('services.llm_service.ChatGroq') as mock_groq:
            mock_instance = Mock()
            mock_groq.return_value = mock_instance

            from services.llm_service import create_llm_service

            with patch('services.llm_service.StrOutputParser') as mock_parser:
                mock_parser_instance = Mock()
                mock_parser_instance.__or__ = Mock(return_value=Mock(
                    invoke=Mock(return_value="Test prompt")
                ))
                mock_parser.return_value = mock_parser_instance

                service = create_llm_service(api_key="test-key")
                result = service.generate_system_prompt(
                    strictness="flexible",
                    response_length="standard",
                    tone="formal",
                    use_case="coding",
                    style="standard"
                )

                assert result is not None
