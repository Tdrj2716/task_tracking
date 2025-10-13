# 技術スタック

## Architecture

### システム設計の概要

Kiro Spec-Driven Development は、Claude Code プラットフォーム上で動作するコマンドラインベースのフレームワークです。ファイルシステムをデータストアとして使用し、Markdown と JSON を組み合わせたドキュメントファーストのアーキテクチャを採用しています。

### コアコンポーネント

1. **スラッシュコマンド層** (`.claude/commands/kiro/`)
   - Claude Code のスラッシュコマンドシステムを活用
   - YAML フロントマターで許可ツールとメタデータを定義
   - Markdown ボディでプロンプト/指示を記述

2. **ステアリング層** (`.kiro/steering/`)
   - プロジェクト全体のコンテキストを管理
   - Always/Conditional/Manual の3つのインクルードモード
   - product.md、tech.md、structure.md の3つのコアファイル

3. **スペック層** (`.kiro/specs/[feature-name]/`)
   - 個別機能の要件、設計、タスクを管理
   - spec.json で承認状態とメタデータを追跡
   - 段階的に requirements.md → design.md → tasks.md を生成

## Development Environment

### 必要なツール

- **Claude Code**: VSCode 拡張または CLI
- **ファイルシステムアクセス**: ローカルまたはクラウドストレージ
- **Git** (推奨): バージョン管理とステアリング変更の追跡

### パッケージ管理ツール

- **Backend**: uv（Python パッケージ管理）
- **Frontend**: pnpm（Node.js パッケージ管理）
- **Git Hooks**: lefthook（pre-commit フック管理）

### セットアップ

1. プロジェクトルートに `CLAUDE.md` を配置
2. `.claude/commands/kiro/` にコマンド定義を配置
3. `/kiro:steering` でステアリングドキュメントを初期化
4. uv、pnpm、lefthook をインストール

## Technology Stack

### コマンド定義

- **フォーマット**: Markdown + YAML フロントマター
- **パス**: `.claude/commands/kiro/*.md`
- **命名規則**: `[command-name].md` → `/kiro:[command-name]`

#### 利用可能なコマンド

| コマンド | 説明 | 主要ツール |
|---------|------|-----------|
| `/kiro:steering` | ステアリングドキュメントの作成・更新 | Bash, Read, Write, Edit, Glob, Grep |
| `/kiro:steering-custom` | カスタムステアリングの作成 | Read, Write, Edit, Glob, Grep |
| `/kiro:spec-init` | スペック初期化 | Bash, Read, Write, Glob |
| `/kiro:spec-requirements` | 要件ドキュメント生成 | Read, Write, Edit, Glob, Grep |
| `/kiro:spec-design` | 設計ドキュメント生成 | Read, Write, Edit, Glob, Grep |
| `/kiro:spec-tasks` | タスクリスト生成 | Read, Write, Edit, Glob, Grep |
| `/kiro:spec-impl` | TDD実装フェーズ | Bash, Read, Write, Edit, Glob, Grep |
| `/kiro:spec-status` | 進捗状況確認 | Read |
| `/kiro:validate-design` | 設計品質検証 | Read, Glob, Grep |
| `/kiro:validate-gap` | 実装ギャップ分析 | Read, Glob, Grep |

### データフォーマット

#### spec.json 構造

```json
{
  "feature_name": "機能名",
  "created_at": "作成タイムスタンプ",
  "updated_at": "更新タイムスタンプ",
  "language": "ja",
  "phase": "initialized|requirements|design|tasks|implementation|completed",
  "approvals": {
    "requirements": {
      "generated": false,
      "approved": false
    },
    "design": {
      "generated": false,
      "approved": false
    },
    "tasks": {
      "generated": false,
      "approved": false
    }
  },
  "ready_for_implementation": false
}
```

#### ステアリングファイルの構造

- **product.md**: プロダクト概要、コア機能、ユースケース、価値提案
- **tech.md**: アーキテクチャ、技術スタック、開発環境、コマンド一覧
- **structure.md**: ディレクトリ構造、命名規則、組織パターン、設計原則

## Common Commands

### スペック駆動開発ワークフロー

```bash
# Phase 0: ステアリング作成（オプション）
/kiro:steering

# Phase 1: スペック作成
/kiro:spec-init [詳細な機能説明]
/kiro:spec-requirements [feature-name]
# → requirements.md を確認・承認
/kiro:spec-design [feature-name]
# → design.md を確認・承認
/kiro:spec-tasks [feature-name]
# → tasks.md を確認・承認

# Phase 2: 実装
/kiro:spec-impl [feature-name] [task-numbers]

# Phase 3: 進捗確認
/kiro:spec-status [feature-name]
```

### バリデーション

```bash
# 設計品質の検証
/kiro:validate-design [feature-name]

# 実装ギャップの分析
/kiro:validate-gap [feature-name]
```

## Environment Variables

現在、環境変数は使用していません。すべての設定はファイルベースで管理されます。

## Port Configuration

該当なし（コマンドラインツールのため）

## Language Settings

- **デフォルト言語**: 日本語 (ja)
- **思考プロセス**: 英語
- **出力**: 日本語
- **spec.json の language フィールド**: 出力言語を指定
