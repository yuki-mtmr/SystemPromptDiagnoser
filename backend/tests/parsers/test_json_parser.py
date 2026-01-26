"""
会話パーサーのテスト
TDD: RED - まずテストを書き、失敗を確認してから実装
"""
import pytest
import json

from parsers.json_parser import ConversationParser, ParsedConversation
from schemas.conversation import ConversationUploadRequest


class TestConversationParser:
    """ConversationParser のテスト"""

    def test_parse_chatgpt_export_format(self):
        """ChatGPTエクスポート形式をパース"""
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
                        "content": {"parts": ["I'm doing well, thank you!"]}
                    }
                }
            }
        }

        parser = ConversationParser()
        result = parser.parse(json.dumps(chatgpt_data), format="chatgpt_json")

        assert isinstance(result, ParsedConversation)
        assert len(result.messages) >= 1

    def test_parse_claude_export_format(self):
        """Claudeエクスポート形式をパース"""
        claude_data = {
            "uuid": "test-uuid",
            "name": "Test Conversation",
            "chat_messages": [
                {"sender": "human", "text": "Can you help me?"},
                {"sender": "assistant", "text": "Of course! What do you need?"}
            ]
        }

        parser = ConversationParser()
        result = parser.parse(json.dumps(claude_data), format="claude_json")

        assert isinstance(result, ParsedConversation)
        assert len(result.messages) >= 1

    def test_extract_user_messages(self):
        """ユーザーメッセージを抽出"""
        chatgpt_data = {
            "title": "Test",
            "mapping": {
                "node1": {
                    "message": {
                        "author": {"role": "user"},
                        "content": {"parts": ["User message 1"]}
                    }
                },
                "node2": {
                    "message": {
                        "author": {"role": "assistant"},
                        "content": {"parts": ["Assistant response"]}
                    }
                },
                "node3": {
                    "message": {
                        "author": {"role": "user"},
                        "content": {"parts": ["User message 2"]}
                    }
                }
            }
        }

        parser = ConversationParser()
        result = parser.parse(json.dumps(chatgpt_data), format="chatgpt_json")

        user_messages = [m for m in result.messages if m.role == "user"]
        assert len(user_messages) == 2

    def test_detect_format_automatically(self):
        """フォーマットを自動検出"""
        chatgpt_data = {
            "title": "Test",
            "mapping": {"node1": {"message": {"author": {"role": "user"}, "content": {"parts": ["Hi"]}}}}
        }

        parser = ConversationParser()
        detected = parser.detect_format(json.dumps(chatgpt_data))

        assert detected == "chatgpt_json"

    def test_detect_claude_format(self):
        """Claude形式を自動検出"""
        claude_data = {
            "uuid": "test",
            "chat_messages": [{"sender": "human", "text": "Hi"}]
        }

        parser = ConversationParser()
        detected = parser.detect_format(json.dumps(claude_data))

        assert detected == "claude_json"

    def test_parse_with_auto_format(self):
        """auto形式でパース"""
        chatgpt_data = {
            "title": "Test",
            "mapping": {"node1": {"message": {"author": {"role": "user"}, "content": {"parts": ["Test"]}}}}
        }

        parser = ConversationParser()
        result = parser.parse(json.dumps(chatgpt_data), format="auto")

        assert isinstance(result, ParsedConversation)

    def test_to_context_string(self):
        """コンテキスト文字列に変換"""
        chatgpt_data = {
            "title": "Test",
            "mapping": {
                "node1": {"message": {"author": {"role": "user"}, "content": {"parts": ["Hello"]}}},
                "node2": {"message": {"author": {"role": "assistant"}, "content": {"parts": ["Hi there!"]}}}
            }
        }

        parser = ConversationParser()
        result = parser.parse(json.dumps(chatgpt_data), format="chatgpt_json")
        context = result.to_context_string()

        assert "User:" in context or "user" in context.lower()
        assert "Hello" in context


class TestConversationUploadRequest:
    """ConversationUploadRequest スキーマのテスト"""

    def test_has_content_field(self):
        """contentフィールドを持つ"""
        request = ConversationUploadRequest(
            content='{"test": "data"}',
            format="auto"
        )
        assert request.content == '{"test": "data"}'

    def test_has_format_field(self):
        """formatフィールドを持つ"""
        request = ConversationUploadRequest(
            content='{}',
            format="chatgpt_json"
        )
        assert request.format == "chatgpt_json"

    def test_format_defaults_to_auto(self):
        """formatのデフォルトはauto"""
        request = ConversationUploadRequest(content='{}')
        assert request.format == "auto"


class TestParsedConversation:
    """ParsedConversation モデルのテスト"""

    def test_has_messages(self):
        """messagesフィールドを持つ"""
        from parsers.json_parser import ConversationMessage

        conv = ParsedConversation(
            messages=[ConversationMessage(role="user", content="Test")]
        )
        assert len(conv.messages) == 1

    def test_has_optional_metadata(self):
        """オプションのmetadataを持つ"""
        conv = ParsedConversation(
            messages=[],
            metadata={"title": "Test Conversation"}
        )
        assert conv.metadata["title"] == "Test Conversation"
