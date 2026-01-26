"""
セッション管理サービスのテスト
TDD: まずテストを書き、失敗を確認してから実装する
"""
import pytest
import time
from datetime import datetime, timedelta

from services.session_service import (
    SessionService,
    SessionData,
    SessionNotFoundError,
    SessionExpiredError,
)


class TestSessionService:
    """SessionServiceのテスト"""

    def test_create_session_returns_session_id(self):
        """セッション作成時にセッションIDが返される"""
        service = SessionService()
        session_id = service.create_session()

        assert session_id is not None
        assert isinstance(session_id, str)
        assert len(session_id) > 0

    def test_create_session_returns_unique_ids(self):
        """セッションIDは一意である"""
        service = SessionService()
        session_ids = [service.create_session() for _ in range(100)]

        assert len(set(session_ids)) == 100  # 全て一意

    def test_get_session_returns_session_data(self):
        """セッションIDでセッションデータを取得できる"""
        service = SessionService()
        session_id = service.create_session()

        session = service.get_session(session_id)

        assert session is not None
        assert isinstance(session, SessionData)
        assert session.session_id == session_id

    def test_get_session_raises_error_for_invalid_id(self):
        """存在しないセッションIDでエラーが発生する"""
        service = SessionService()

        with pytest.raises(SessionNotFoundError):
            service.get_session("invalid-session-id")

    def test_update_session_stores_data(self):
        """セッションデータを更新できる"""
        service = SessionService()
        session_id = service.create_session()

        test_data = {"phase": 1, "answers": {"q1": "test answer"}}
        service.update_session(session_id, test_data)

        session = service.get_session(session_id)
        assert session.data == test_data

    def test_update_session_merges_data(self):
        """セッションデータの更新はマージされる"""
        service = SessionService()
        session_id = service.create_session()

        service.update_session(session_id, {"phase": 1})
        service.update_session(session_id, {"answers": {"q1": "test"}})

        session = service.get_session(session_id)
        assert session.data == {"phase": 1, "answers": {"q1": "test"}}

    def test_update_session_raises_error_for_invalid_id(self):
        """存在しないセッションIDで更新するとエラー"""
        service = SessionService()

        with pytest.raises(SessionNotFoundError):
            service.update_session("invalid-id", {"test": "data"})

    def test_delete_session_removes_session(self):
        """セッションを削除できる"""
        service = SessionService()
        session_id = service.create_session()

        service.delete_session(session_id)

        with pytest.raises(SessionNotFoundError):
            service.get_session(session_id)

    def test_delete_session_raises_error_for_invalid_id(self):
        """存在しないセッションIDで削除するとエラー"""
        service = SessionService()

        with pytest.raises(SessionNotFoundError):
            service.delete_session("invalid-id")

    def test_session_has_created_at_timestamp(self):
        """セッションは作成時刻を持つ"""
        service = SessionService()
        before = datetime.now()
        session_id = service.create_session()
        after = datetime.now()

        session = service.get_session(session_id)

        assert session.created_at is not None
        assert before <= session.created_at <= after

    def test_session_has_updated_at_timestamp(self):
        """セッションは更新時刻を持つ"""
        service = SessionService()
        session_id = service.create_session()

        session = service.get_session(session_id)
        initial_updated_at = session.updated_at

        time.sleep(0.01)  # わずかに待機
        service.update_session(session_id, {"test": "data"})

        session = service.get_session(session_id)
        assert session.updated_at > initial_updated_at

    def test_session_default_expiry_is_one_hour(self):
        """セッションのデフォルト有効期限は1時間"""
        service = SessionService()
        session_id = service.create_session()

        session = service.get_session(session_id)
        expected_expiry = session.created_at + timedelta(hours=1)

        # 誤差1秒以内
        assert abs((session.expires_at - expected_expiry).total_seconds()) < 1

    def test_custom_expiry_time(self):
        """カスタム有効期限を設定できる"""
        service = SessionService(default_expiry_minutes=30)
        session_id = service.create_session()

        session = service.get_session(session_id)
        expected_expiry = session.created_at + timedelta(minutes=30)

        assert abs((session.expires_at - expected_expiry).total_seconds()) < 1

    def test_expired_session_raises_error(self):
        """期限切れセッションにアクセスするとエラー"""
        service = SessionService(default_expiry_minutes=0)  # 即時期限切れ
        session_id = service.create_session()

        time.sleep(0.01)  # わずかに待機して期限切れに

        with pytest.raises(SessionExpiredError):
            service.get_session(session_id)

    def test_cleanup_expired_sessions(self):
        """期限切れセッションをクリーンアップできる"""
        service = SessionService(default_expiry_minutes=0)
        session_id1 = service.create_session()
        session_id2 = service.create_session()

        time.sleep(0.01)

        # 新しいセッションを作成（期限切れではない）
        service_with_longer_expiry = SessionService(default_expiry_minutes=60)
        # 内部ストアを共有するためインスタンスを再利用
        service._default_expiry_minutes = 60
        session_id3 = service.create_session()

        cleaned = service.cleanup_expired_sessions()

        assert cleaned >= 2  # 少なくとも2つの期限切れセッションが削除

        with pytest.raises((SessionNotFoundError, SessionExpiredError)):
            service.get_session(session_id1)

    def test_session_data_is_isolated(self):
        """異なるセッションのデータは分離されている"""
        service = SessionService()
        session_id1 = service.create_session()
        session_id2 = service.create_session()

        service.update_session(session_id1, {"user": "alice"})
        service.update_session(session_id2, {"user": "bob"})

        session1 = service.get_session(session_id1)
        session2 = service.get_session(session_id2)

        assert session1.data["user"] == "alice"
        assert session2.data["user"] == "bob"


class TestSessionData:
    """SessionDataのテスト"""

    def test_session_data_initialization(self):
        """SessionDataの初期化"""
        now = datetime.now()
        expires = now + timedelta(hours=1)

        session = SessionData(
            session_id="test-id",
            created_at=now,
            updated_at=now,
            expires_at=expires,
            data={"test": "data"}
        )

        assert session.session_id == "test-id"
        assert session.created_at == now
        assert session.updated_at == now
        assert session.expires_at == expires
        assert session.data == {"test": "data"}

    def test_session_data_default_empty_data(self):
        """SessionDataのデフォルトデータは空辞書"""
        now = datetime.now()
        expires = now + timedelta(hours=1)

        session = SessionData(
            session_id="test-id",
            created_at=now,
            updated_at=now,
            expires_at=expires
        )

        assert session.data == {}

    def test_session_is_expired(self):
        """セッションの期限切れ判定"""
        past = datetime.now() - timedelta(hours=1)
        future = datetime.now() + timedelta(hours=1)

        expired_session = SessionData(
            session_id="expired",
            created_at=past,
            updated_at=past,
            expires_at=past
        )

        valid_session = SessionData(
            session_id="valid",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            expires_at=future
        )

        assert expired_session.is_expired() is True
        assert valid_session.is_expired() is False
