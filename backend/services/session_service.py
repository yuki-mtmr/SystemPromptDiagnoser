"""
セッション管理サービス
インメモリでのセッションストア、有効期限管理を提供
"""
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any


class SessionNotFoundError(Exception):
    """セッションが見つからない場合のエラー"""

    pass


class SessionExpiredError(Exception):
    """セッションが期限切れの場合のエラー"""

    pass


@dataclass
class SessionData:
    """セッションデータを保持するデータクラス"""

    session_id: str
    created_at: datetime
    updated_at: datetime
    expires_at: datetime
    data: dict[str, Any] = field(default_factory=dict)

    def is_expired(self) -> bool:
        """セッションが期限切れかどうかを判定"""
        return datetime.now() > self.expires_at


class SessionService:
    """
    インメモリセッション管理サービス

    セッションの作成、取得、更新、削除、期限管理を行う
    """

    def __init__(self, default_expiry_minutes: int = 60):
        """
        セッションサービスを初期化

        Args:
            default_expiry_minutes: セッションのデフォルト有効期限（分）
        """
        self._sessions: dict[str, SessionData] = {}
        self._default_expiry_minutes = default_expiry_minutes

    def create_session(self) -> str:
        """
        新しいセッションを作成

        Returns:
            セッションID
        """
        session_id = str(uuid.uuid4())
        now = datetime.now()
        expires_at = now + timedelta(minutes=self._default_expiry_minutes)

        session = SessionData(
            session_id=session_id,
            created_at=now,
            updated_at=now,
            expires_at=expires_at,
            data={},
        )

        self._sessions[session_id] = session
        return session_id

    def get_session(self, session_id: str) -> SessionData:
        """
        セッションを取得

        Args:
            session_id: セッションID

        Returns:
            セッションデータ

        Raises:
            SessionNotFoundError: セッションが存在しない場合
            SessionExpiredError: セッションが期限切れの場合
        """
        if session_id not in self._sessions:
            raise SessionNotFoundError(f"Session not found: {session_id}")

        session = self._sessions[session_id]

        if session.is_expired():
            del self._sessions[session_id]
            raise SessionExpiredError(f"Session expired: {session_id}")

        return session

    def update_session(self, session_id: str, data: dict[str, Any]) -> None:
        """
        セッションデータを更新（マージ）

        Args:
            session_id: セッションID
            data: 更新データ（既存データにマージされる）

        Raises:
            SessionNotFoundError: セッションが存在しない場合
        """
        if session_id not in self._sessions:
            raise SessionNotFoundError(f"Session not found: {session_id}")

        session = self._sessions[session_id]
        session.data.update(data)
        session.updated_at = datetime.now()

    def delete_session(self, session_id: str) -> None:
        """
        セッションを削除

        Args:
            session_id: セッションID

        Raises:
            SessionNotFoundError: セッションが存在しない場合
        """
        if session_id not in self._sessions:
            raise SessionNotFoundError(f"Session not found: {session_id}")

        del self._sessions[session_id]

    def cleanup_expired_sessions(self) -> int:
        """
        期限切れセッションをクリーンアップ

        Returns:
            削除されたセッション数
        """
        expired_ids = [
            sid for sid, session in self._sessions.items() if session.is_expired()
        ]

        for sid in expired_ids:
            del self._sessions[sid]

        return len(expired_ids)


# グローバルセッションサービスインスタンス（シングルトン）
_session_service: SessionService | None = None


def get_session_service() -> SessionService:
    """
    セッションサービスのシングルトンインスタンスを取得

    Returns:
        SessionService インスタンス
    """
    global _session_service
    if _session_service is None:
        _session_service = SessionService()
    return _session_service
