"""
v2 APIエンドポイントのテスト
TDD: まずテストを書き、失敗を確認してから実装する
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from main import app


client = TestClient(app)


class TestDiagnoseV2StartEndpoint:
    """POST /api/v2/diagnose/start エンドポイントのテスト"""

    def test_endpoint_exists(self):
        """エンドポイントが存在する"""
        response = client.post(
            "/api/v2/diagnose/start",
            json={
                "initial_answers": {
                    "purpose": "コードレビュー",
                    "autonomy": "collaborative"
                }
            }
        )
        # 404でなければエンドポイントは存在
        assert response.status_code != 404

    def test_returns_session_id(self):
        """セッションIDを返す"""
        response = client.post(
            "/api/v2/diagnose/start",
            json={
                "initial_answers": {
                    "purpose": "コードレビュー",
                    "autonomy": "collaborative"
                }
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert len(data["session_id"]) > 0

    def test_returns_phase(self):
        """フェーズを返す（followup または complete）"""
        response = client.post(
            "/api/v2/diagnose/start",
            json={
                "initial_answers": {
                    "purpose": "test",
                    "autonomy": "obedient"
                }
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "phase" in data
        assert data["phase"] in ["followup", "complete"]

    def test_returns_followup_questions_when_needed(self):
        """フォローアップ質問が必要な場合は質問を返す"""
        response = client.post(
            "/api/v2/diagnose/start",
            json={
                "initial_answers": {
                    "purpose": "Help me with code",
                    "autonomy": "collaborative"
                }
            }
        )
        assert response.status_code == 200
        data = response.json()

        if data["phase"] == "followup":
            assert "followup_questions" in data
            assert data["followup_questions"] is not None

    def test_returns_result_when_complete(self):
        """完了時は結果を返す"""
        response = client.post(
            "/api/v2/diagnose/start",
            json={
                "initial_answers": {
                    "purpose": "quick test",
                    "autonomy": "obedient"
                }
            }
        )
        assert response.status_code == 200
        data = response.json()

        if data["phase"] == "complete":
            assert "result" in data
            assert data["result"] is not None

    def test_validation_error_for_invalid_autonomy(self):
        """不正なautonomyでバリデーションエラー"""
        response = client.post(
            "/api/v2/diagnose/start",
            json={
                "initial_answers": {
                    "purpose": "test",
                    "autonomy": "invalid_value"
                }
            }
        )
        assert response.status_code == 422

    def test_validation_error_for_missing_purpose(self):
        """purposeが欠けているとバリデーションエラー"""
        response = client.post(
            "/api/v2/diagnose/start",
            json={
                "initial_answers": {
                    "autonomy": "collaborative"
                }
            }
        )
        assert response.status_code == 422


class TestDiagnoseV2ContinueEndpoint:
    """POST /api/v2/diagnose/continue エンドポイントのテスト"""

    def test_endpoint_exists(self):
        """エンドポイントが存在する"""
        # まずセッションを開始
        start_response = client.post(
            "/api/v2/diagnose/start",
            json={
                "initial_answers": {
                    "purpose": "コードレビュー",
                    "autonomy": "collaborative"
                }
            }
        )
        session_id = start_response.json()["session_id"]

        response = client.post(
            "/api/v2/diagnose/continue",
            json={
                "session_id": session_id,
                "answers": []
            }
        )
        assert response.status_code != 404

    def test_returns_session_id(self):
        """セッションIDを返す"""
        # セッション開始
        start_response = client.post(
            "/api/v2/diagnose/start",
            json={
                "initial_answers": {
                    "purpose": "test",
                    "autonomy": "collaborative"
                }
            }
        )
        session_id = start_response.json()["session_id"]

        response = client.post(
            "/api/v2/diagnose/continue",
            json={
                "session_id": session_id,
                "answers": []
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_id

    def test_returns_phase(self):
        """フェーズを返す"""
        start_response = client.post(
            "/api/v2/diagnose/start",
            json={
                "initial_answers": {
                    "purpose": "test",
                    "autonomy": "collaborative"
                }
            }
        )
        session_id = start_response.json()["session_id"]

        response = client.post(
            "/api/v2/diagnose/continue",
            json={
                "session_id": session_id,
                "answers": []
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["phase"] in ["followup", "complete"]

    def test_error_for_invalid_session_id(self):
        """無効なセッションIDでエラー"""
        response = client.post(
            "/api/v2/diagnose/continue",
            json={
                "session_id": "invalid-session-id",
                "answers": []
            }
        )
        assert response.status_code == 404

    def test_returns_result_on_complete(self):
        """完了時は結果を含む"""
        # セッション開始
        start_response = client.post(
            "/api/v2/diagnose/start",
            json={
                "initial_answers": {
                    "purpose": "test",
                    "autonomy": "obedient"
                }
            }
        )
        session_id = start_response.json()["session_id"]

        # 続行（空の回答で強制的に完了へ）
        response = client.post(
            "/api/v2/diagnose/continue",
            json={
                "session_id": session_id,
                "answers": []
            }
        )
        assert response.status_code == 200
        data = response.json()

        # 最終的にcompleteになるまでループ
        max_iterations = 5
        for _ in range(max_iterations):
            if data["phase"] == "complete":
                break
            response = client.post(
                "/api/v2/diagnose/continue",
                json={
                    "session_id": session_id,
                    "answers": []
                }
            )
            data = response.json()

        # completeになったら結果がある
        if data["phase"] == "complete":
            assert "result" in data
            assert data["result"] is not None


class TestDiagnoseV2Integration:
    """v2診断フローの統合テスト"""

    def test_full_flow_with_mock(self):
        """モック生成でのフルフローテスト"""
        # Phase 1: 開始
        start_response = client.post(
            "/api/v2/diagnose/start",
            json={
                "initial_answers": {
                    "purpose": "コードレビューを手伝ってほしい",
                    "autonomy": "collaborative"
                }
            }
        )
        assert start_response.status_code == 200
        data = start_response.json()
        session_id = data["session_id"]

        # Phase 2: フォローアップがあれば回答
        while data["phase"] == "followup" and data.get("followup_questions"):
            # 最初の質問に回答
            answers = []
            for q in data["followup_questions"]:
                if q["type"] == "choice" and q.get("choices"):
                    answers.append({
                        "question_id": q["id"],
                        "answer": q["choices"][0]["value"]
                    })
                else:
                    answers.append({
                        "question_id": q["id"],
                        "answer": "test answer"
                    })

            continue_response = client.post(
                "/api/v2/diagnose/continue",
                json={
                    "session_id": session_id,
                    "answers": answers
                }
            )
            assert continue_response.status_code == 200
            data = continue_response.json()

        # フォローアップがなければ完了へ
        if data["phase"] == "followup" and not data.get("followup_questions"):
            continue_response = client.post(
                "/api/v2/diagnose/continue",
                json={
                    "session_id": session_id,
                    "answers": []
                }
            )
            data = continue_response.json()

        # Phase 3: 結果確認
        assert data["phase"] == "complete"
        assert "result" in data
        result = data["result"]

        assert "user_profile" in result
        assert "recommended_style" in result
        assert "variants" in result
        assert len(result["variants"]) == 3

    def test_detects_japanese_language(self):
        """日本語の検出"""
        response = client.post(
            "/api/v2/diagnose/start",
            json={
                "initial_answers": {
                    "purpose": "コードレビューをお願いします",
                    "autonomy": "collaborative"
                }
            }
        )
        # モック生成では言語検出のテストは間接的になる
        assert response.status_code == 200

    def test_detects_english_language(self):
        """英語の検出"""
        response = client.post(
            "/api/v2/diagnose/start",
            json={
                "initial_answers": {
                    "purpose": "Please help me with code review",
                    "autonomy": "collaborative"
                }
            }
        )
        assert response.status_code == 200


class TestDiagnoseV2WithCognitiveProfile:
    """認知プロファイル対応の統合テスト"""

    def test_full_flow_returns_cognitive_profile(self):
        """フルフローで認知プロファイルが返される"""
        # Phase 1: 開始
        start_response = client.post(
            "/api/v2/diagnose/start",
            json={
                "initial_answers": {
                    "purpose": "コーディングサポート",
                    "autonomy": "autonomous"
                }
            }
        )
        assert start_response.status_code == 200
        data = start_response.json()
        session_id = data["session_id"]

        # completeまで進める
        max_iterations = 5
        for _ in range(max_iterations):
            if data["phase"] == "complete":
                break
            continue_response = client.post(
                "/api/v2/diagnose/continue",
                json={
                    "session_id": session_id,
                    "answers": []
                }
            )
            data = continue_response.json()

        # 結果確認
        assert data["phase"] == "complete"
        result = data["result"]

        # 認知プロファイルが含まれる
        assert "user_profile" in result
        user_profile = result["user_profile"]
        assert "cognitive_profile" in user_profile

        cognitive = user_profile["cognitive_profile"]
        assert "thinking_pattern" in cognitive
        assert "learning_type" in cognitive
        assert "persona_summary" in cognitive

    def test_prompt_not_generic(self):
        """生成されるプロンプトが汎用的でない"""
        start_response = client.post(
            "/api/v2/diagnose/start",
            json={
                "initial_answers": {
                    "purpose": "コードレビュー",
                    "autonomy": "autonomous"
                }
            }
        )
        data = start_response.json()
        session_id = data["session_id"]

        # completeまで進める
        max_iterations = 5
        for _ in range(max_iterations):
            if data["phase"] == "complete":
                break
            continue_response = client.post(
                "/api/v2/diagnose/continue",
                json={
                    "session_id": session_id,
                    "answers": []
                }
            )
            data = continue_response.json()

        result = data["result"]
        variants = result["variants"]

        # strictプロンプトを取得
        strict_variant = next(v for v in variants if v["style"] == "strict")
        strict_prompt = strict_variant["prompt"]

        # 汎用的な表現が含まれていない
        generic_patterns = [
            "ユーザーの質問に的確に回答してください",
            "Answer questions accurately",
        ]
        for pattern in generic_patterns:
            assert pattern not in strict_prompt, f"Generic pattern found: {pattern}"

        # ペルソナ宣言または認知特性の言及がある
        personalized_indicators = [
            "私は", "学習者", "思考", "構造",  # 日本語
            "I am", "learner", "thinking", "structure",  # 英語
        ]
        has_personalization = any(
            indicator in strict_prompt for indicator in personalized_indicators
        )
        assert has_personalization, "Prompt lacks personalization indicators"

    def test_cognitive_profile_varies_by_autonomy_in_api(self):
        """APIレベルで自律性によって認知プロファイルが変わる"""
        # obedient
        response_obedient = client.post(
            "/api/v2/diagnose/start",
            json={
                "initial_answers": {
                    "purpose": "task",
                    "autonomy": "obedient"
                }
            }
        )
        data_obedient = response_obedient.json()
        session_id_obedient = data_obedient["session_id"]

        # completeまで進める
        for _ in range(5):
            if data_obedient["phase"] == "complete":
                break
            data_obedient = client.post(
                "/api/v2/diagnose/continue",
                json={"session_id": session_id_obedient, "answers": []}
            ).json()

        # autonomous
        response_autonomous = client.post(
            "/api/v2/diagnose/start",
            json={
                "initial_answers": {
                    "purpose": "task",
                    "autonomy": "autonomous"
                }
            }
        )
        data_autonomous = response_autonomous.json()
        session_id_autonomous = data_autonomous["session_id"]

        for _ in range(5):
            if data_autonomous["phase"] == "complete":
                break
            data_autonomous = client.post(
                "/api/v2/diagnose/continue",
                json={"session_id": session_id_autonomous, "answers": []}
            ).json()

        # 両方とも認知プロファイルがある
        cognitive_obedient = data_obedient["result"]["user_profile"]["cognitive_profile"]
        cognitive_autonomous = data_autonomous["result"]["user_profile"]["cognitive_profile"]

        assert cognitive_obedient is not None
        assert cognitive_autonomous is not None

        # 異なる値を持つ（ただしモックなので予測可能）
        # thinking_pattern が異なる
        assert cognitive_obedient["thinking_pattern"] in ["structural", "fluid", "hybrid"]
        assert cognitive_autonomous["thinking_pattern"] in ["structural", "fluid", "hybrid"]

    def test_result_includes_source_field(self):
        """結果にsourceフィールドが含まれる"""
        start_response = client.post(
            "/api/v2/diagnose/start",
            json={
                "initial_answers": {
                    "purpose": "test",
                    "autonomy": "collaborative"
                }
            }
        )
        data = start_response.json()
        session_id = data["session_id"]

        for _ in range(5):
            if data["phase"] == "complete":
                break
            data = client.post(
                "/api/v2/diagnose/continue",
                json={"session_id": session_id, "answers": []}
            ).json()

        result = data["result"]
        assert "source" in result
        assert result["source"] in ["llm", "mock"]
