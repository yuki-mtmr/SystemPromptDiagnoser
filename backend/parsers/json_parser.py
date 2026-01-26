"""
会話JSONパーサー

ChatGPT、Claude などの会話エクスポートJSONをパース
"""
import json
from typing import Any, Literal

from pydantic import BaseModel, Field


class ConversationMessage(BaseModel):
    """会話メッセージ"""

    role: Literal["user", "assistant", "system"] = Field(..., description="メッセージの役割")
    content: str = Field(..., description="メッセージ内容")


class ParsedConversation(BaseModel):
    """パースされた会話"""

    messages: list[ConversationMessage] = Field(
        default_factory=list, description="メッセージリスト"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="会話メタデータ"
    )

    def to_context_string(self, max_messages: int = 20) -> str:
        """
        コンテキスト文字列に変換

        Args:
            max_messages: 最大メッセージ数

        Returns:
            コンテキスト文字列
        """
        lines = []
        for msg in self.messages[:max_messages]:
            role_label = "User" if msg.role == "user" else "Assistant"
            lines.append(f"{role_label}: {msg.content}")

        return "\n\n".join(lines)


class ConversationParser:
    """
    会話パーサー

    複数のフォーマット（ChatGPT、Claude）に対応
    """

    def detect_format(self, content: str) -> str:
        """
        フォーマットを自動検出

        Args:
            content: 会話データ文字列

        Returns:
            検出されたフォーマット
        """
        try:
            data = json.loads(content)

            # ChatGPT形式: mapping キーが存在
            if "mapping" in data:
                return "chatgpt_json"

            # Claude形式: chat_messages キーが存在
            if "chat_messages" in data:
                return "claude_json"

            # その他のJSON形式
            return "unknown"

        except json.JSONDecodeError:
            # マークダウンの可能性
            if "User:" in content or "Assistant:" in content:
                return "markdown"
            return "unknown"

    def parse(
        self,
        content: str,
        format: Literal["chatgpt_json", "claude_json", "markdown", "auto"] = "auto",
    ) -> ParsedConversation:
        """
        会話をパース

        Args:
            content: 会話データ文字列
            format: フォーマット指定

        Returns:
            ParsedConversation: パースされた会話
        """
        if format == "auto":
            format = self.detect_format(content)

        if format == "chatgpt_json":
            return self._parse_chatgpt(content)
        elif format == "claude_json":
            return self._parse_claude(content)
        elif format == "markdown":
            return self._parse_markdown(content)
        else:
            # フォールバック: 空の会話を返す
            return ParsedConversation()

    def _parse_chatgpt(self, content: str) -> ParsedConversation:
        """
        ChatGPTエクスポート形式をパース

        ChatGPTの会話エクスポートは以下の構造:
        {
            "title": "...",
            "mapping": {
                "node_id": {
                    "message": {
                        "author": {"role": "user" | "assistant"},
                        "content": {"parts": ["メッセージ内容"]}
                    }
                }
            }
        }
        """
        data = json.loads(content)
        messages = []
        metadata = {"title": data.get("title", "")}

        mapping = data.get("mapping", {})
        for node_id, node in mapping.items():
            message_data = node.get("message")
            if not message_data:
                continue

            author = message_data.get("author", {})
            role = author.get("role", "")
            if role not in ["user", "assistant"]:
                continue

            content_data = message_data.get("content", {})
            parts = content_data.get("parts", [])
            if not parts:
                continue

            # パーツを結合
            text = "".join(str(p) for p in parts if isinstance(p, str))
            if text.strip():
                messages.append(ConversationMessage(role=role, content=text.strip()))

        return ParsedConversation(messages=messages, metadata=metadata)

    def _parse_claude(self, content: str) -> ParsedConversation:
        """
        Claudeエクスポート形式をパース

        Claudeの会話エクスポートは以下の構造:
        {
            "uuid": "...",
            "name": "...",
            "chat_messages": [
                {"sender": "human" | "assistant", "text": "メッセージ内容"}
            ]
        }
        """
        data = json.loads(content)
        messages = []
        metadata = {
            "uuid": data.get("uuid", ""),
            "name": data.get("name", ""),
        }

        chat_messages = data.get("chat_messages", [])
        for msg in chat_messages:
            sender = msg.get("sender", "")
            text = msg.get("text", "")

            if sender == "human":
                role = "user"
            elif sender == "assistant":
                role = "assistant"
            else:
                continue

            if text.strip():
                messages.append(ConversationMessage(role=role, content=text.strip()))

        return ParsedConversation(messages=messages, metadata=metadata)

    def _parse_markdown(self, content: str) -> ParsedConversation:
        """
        マークダウン形式をパース

        想定フォーマット:
        User: メッセージ
        Assistant: 応答
        """
        messages = []
        current_role = None
        current_content = []

        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("User:"):
                if current_role and current_content:
                    messages.append(ConversationMessage(
                        role=current_role,
                        content=" ".join(current_content)
                    ))
                current_role = "user"
                current_content = [line[5:].strip()]
            elif line.startswith("Assistant:"):
                if current_role and current_content:
                    messages.append(ConversationMessage(
                        role=current_role,
                        content=" ".join(current_content)
                    ))
                current_role = "assistant"
                current_content = [line[10:].strip()]
            elif line and current_role:
                current_content.append(line)

        # 最後のメッセージを追加
        if current_role and current_content:
            messages.append(ConversationMessage(
                role=current_role,
                content=" ".join(current_content)
            ))

        return ParsedConversation(messages=messages)
