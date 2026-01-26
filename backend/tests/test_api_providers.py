"""
API プロバイダー関連エンドポイントのテスト
TDD: RED - まずテストを書き、失敗を確認してから実装
"""
import pytest
from fastapi.testclient import TestClient
import json


class TestProvidersEndpoint:
    """GET /api/providers エンドポイントのテスト"""

    def test_get_providers_returns_list(self, client):
        """プロバイダー一覧を取得"""
        response = client.get("/api/providers")
        assert response.status_code == 200
        data = response.json()
        assert "providers" in data
        assert isinstance(data["providers"], list)

    def test_get_providers_includes_openai(self, client):
        """OpenAIが含まれる"""
        response = client.get("/api/providers")
        data = response.json()
        providers = [p["id"] for p in data["providers"]]
        assert "openai" in providers

    def test_get_providers_includes_groq(self, client):
        """Groqが含まれる"""
        response = client.get("/api/providers")
        data = response.json()
        providers = [p["id"] for p in data["providers"]]
        assert "groq" in providers

    def test_get_providers_includes_gemini(self, client):
        """Geminiが含まれる"""
        response = client.get("/api/providers")
        data = response.json()
        providers = [p["id"] for p in data["providers"]]
        assert "gemini" in providers

    def test_provider_has_default_model(self, client):
        """各プロバイダーにデフォルトモデルがある"""
        response = client.get("/api/providers")
        data = response.json()
        for provider in data["providers"]:
            assert "default_model" in provider
            assert len(provider["default_model"]) > 0


class TestUploadConversationEndpoint:
    """POST /api/v2/diagnose/upload-conversation エンドポイントのテスト"""

    def test_upload_conversation_chatgpt_format(self, client):
        """ChatGPT形式の会話をアップロード"""
        chatgpt_data = {
            "title": "Test Conversation",
            "mapping": {
                "node1": {
                    "message": {
                        "author": {"role": "user"},
                        "content": {"parts": ["Hello, how are you?"]}
                    }
                },
                "node2": {
                    "message": {
                        "author": {"role": "assistant"},
                        "content": {"parts": ["I'm doing well!"]}
                    }
                }
            }
        }

        response = client.post(
            "/api/v2/diagnose/upload-conversation",
            json={"content": json.dumps(chatgpt_data), "format": "chatgpt_json"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message_count"] >= 1

    def test_upload_conversation_claude_format(self, client):
        """Claude形式の会話をアップロード"""
        claude_data = {
            "uuid": "test-uuid",
            "name": "Test Conversation",
            "chat_messages": [
                {"sender": "human", "text": "Can you help me?"},
                {"sender": "assistant", "text": "Of course!"}
            ]
        }

        response = client.post(
            "/api/v2/diagnose/upload-conversation",
            json={"content": json.dumps(claude_data), "format": "claude_json"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message_count"] >= 1

    def test_upload_conversation_auto_detect(self, client):
        """フォーマット自動検出"""
        chatgpt_data = {
            "title": "Test",
            "mapping": {
                "node1": {
                    "message": {
                        "author": {"role": "user"},
                        "content": {"parts": ["Test message"]}
                    }
                }
            }
        }

        response = client.post(
            "/api/v2/diagnose/upload-conversation",
            json={"content": json.dumps(chatgpt_data), "format": "auto"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["detected_format"] == "chatgpt_json"

    def test_upload_conversation_returns_context_preview(self, client):
        """コンテキストプレビューを返す"""
        chatgpt_data = {
            "title": "Test",
            "mapping": {
                "node1": {
                    "message": {
                        "author": {"role": "user"},
                        "content": {"parts": ["Hello, this is a test message"]}
                    }
                }
            }
        }

        response = client.post(
            "/api/v2/diagnose/upload-conversation",
            json={"content": json.dumps(chatgpt_data), "format": "auto"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "context_preview" in data
        assert len(data["context_preview"]) > 0


class TestXProviderHeader:
    """X-Provider ヘッダーのテスト"""

    def test_x_provider_header_openai(self, client):
        """X-Provider: openai を使用"""
        response = client.get(
            "/api/status",
            headers={"X-Provider": "openai", "X-API-Key": "test-key"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["provider"] == "openai"

    def test_x_provider_header_groq(self, client):
        """X-Provider: groq を使用"""
        response = client.get(
            "/api/status",
            headers={"X-Provider": "groq", "X-API-Key": "test-key"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["provider"] == "groq"

    def test_x_provider_header_gemini(self, client):
        """X-Provider: gemini を使用"""
        response = client.get(
            "/api/status",
            headers={"X-Provider": "gemini", "X-API-Key": "test-key"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["provider"] == "gemini"

    def test_x_provider_defaults_to_groq(self, client):
        """X-Provider 未指定時はgroqをデフォルト"""
        response = client.get(
            "/api/status",
            headers={"X-API-Key": "test-key"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["provider"] == "groq"


@pytest.fixture
def client():
    """テストクライアントを作成"""
    from main import app
    return TestClient(app)
