# 実装計画 - フェーズ 1: 基本UI実装

## 目標
Docker環境の準備と並行して、Reactを使用したフロントエンドの基本UIコンポーネント（ヘッダー、フッター、アンケートフォーム）を実装し、アプリの見た目の基盤を作ります。「プレミアムなデザイン」のガイドラインに従います。

## ユーザーレビューが必要な事項
- 特になし。

## 変更内容

### 設定
#### [MODIFY] [task.md](file:///C:/Users/240154/.gemini/antigravity/brain/f5aaf363-81cc-4cae-bb8d-25170efba2a2/task.md)
- UI実装のタスクを更新。

### フロントエンド (`frontend/src/`)
機能的なCSSとReactコンポーネントを使用してコアレイアウトを実装します。

#### [NEW] [Header.tsx](file:///c:/Users/240154/Desktop/projects/SystemPromptDiagnoser/frontend/src/components/Header.tsx)
- アプリタイトルとダークモード切り替え（将来用）を含むシンプルなヘッダー。

#### [NEW] [Footer.tsx](file:///c:/Users/240154/Desktop/projects/SystemPromptDiagnoser/frontend/src/components/Footer.tsx)
- コピーライトとリンク。

#### [NEW] [Questionnaire.tsx](file:///c:/Users/240154/Desktop/projects/SystemPromptDiagnoser/frontend/src/components/Questionnaire.tsx)
- ユーザー入力用のフォームコンポーネント（期初はモック）。ガラスモーフィズム等のデザイン適用。

#### [MODIFY] [App.tsx](file:///c:/Users/240154/Desktop/projects/SystemPromptDiagnoser/frontend/src/App.tsx)
- ヘッダー、フッター、メインコンテンツエリアの統合。

## 検証計画
### 自動テスト
-   Dockerが動作するようになったら:
    -   `docker-compose up -d`
    -   `http://localhost:5173` にアクセスしてUIのレンダリングを確認。

### 手動検証
-   ブラウザで開き、グラデーションやガラスモーフィズムなどのデザインが適用されているかを目視確認。
