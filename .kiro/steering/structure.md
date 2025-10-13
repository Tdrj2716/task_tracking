# プロジェクト構造

## Root Directory Organization

```
.
├── .claude/              # Claude Code 設定
│   └── commands/        # スラッシュコマンド定義
│       └── kiro/        # Kiro 関連コマンド
├── .kiro/               # Kiro データディレクトリ
│   ├── steering/        # ステアリングドキュメント
│   └── specs/           # スペックドキュメント
│       └── [feature]/   # 個別機能のスペック
└── CLAUDE.md            # プロジェクト設定・ドキュメント
```

### ディレクトリ別の責務

- **`.claude/commands/kiro/`**: スラッシュコマンドの定義ファイル（Markdown）
- **`.kiro/steering/`**: プロジェクト全体のコンテキスト（常に読み込まれる）
- **`.kiro/specs/`**: 個別機能のスペック（feature-name ディレクトリ単位）
- **`CLAUDE.md`**: プロジェクトのメインドキュメント、開発ガイドライン

## Subdirectory Structures

### `.claude/commands/kiro/` 構造

スラッシュコマンド定義ファイルを格納。各ファイルは `/kiro:[command-name]` として実行可能。

```
.claude/commands/kiro/
├── steering.md              # /kiro:steering
├── steering-custom.md       # /kiro:steering-custom
├── spec-init.md            # /kiro:spec-init
├── spec-requirements.md    # /kiro:spec-requirements
├── spec-design.md          # /kiro:spec-design
├── spec-tasks.md           # /kiro:spec-tasks
├── spec-impl.md            # /kiro:spec-impl
├── spec-status.md          # /kiro:spec-status
├── validate-design.md      # /kiro:validate-design
└── validate-gap.md         # /kiro:validate-gap
```

### `.kiro/steering/` 構造

プロジェクト全体のコンテキストを管理。3つのコアファイルは常に読み込まれる。

```
.kiro/steering/
├── product.md          # プロダクト概要（Always）
├── tech.md            # 技術スタック（Always）
├── structure.md       # プロジェクト構造（Always）
└── [custom].md        # カスタムステアリング（Conditional/Manual）
```

#### インクルードモード

- **Always**: すべてのインタラクションで読み込み（product.md、tech.md、structure.md）
- **Conditional**: 特定ファイルパターンにマッチする場合のみ読み込み
- **Manual**: `@filename.md` 構文で明示的に参照

### `.kiro/specs/[feature-name]/` 構造

個別機能のスペックを管理。feature-name ディレクトリ単位で分離。

```
.kiro/specs/[feature-name]/
├── spec.json           # メタデータ・承認状態
├── requirements.md     # 要件ドキュメント
├── design.md          # 設計ドキュメント
└── tasks.md           # タスクリスト
```

#### ライフサイクル

1. **初期化**: `/kiro:spec-init` で spec.json と requirements.md テンプレートを作成
2. **要件**: `/kiro:spec-requirements` で requirements.md を生成
3. **設計**: `/kiro:spec-design` で design.md を作成（要件承認後）
4. **タスク**: `/kiro:spec-tasks` で tasks.md を作成（設計承認後）
5. **実装**: `/kiro:spec-impl` で TDD ベースの実装を実行

## Code Organization Patterns

### コマンド定義ファイルの構造

各コマンド定義ファイル（`.claude/commands/kiro/*.md`）は以下の構造に従います：

```markdown
---
description: コマンドの説明
allowed-tools: 許可されたツール（カンマ区切り）
argument-hint: <引数のヒント>（オプション）
---

# コマンド名

コマンドの詳細な説明とタスク定義

## Task: メインタスク

実行する具体的なタスク

### セクション1

詳細な指示

### セクション2

追加の指示

## Instructions

実行手順のリスト

## Output Format

期待される出力形式
```

### ステアリングドキュメントの構造

各ステアリングファイルは以下のセクションを含みます：

- **product.md**: Product Overview、Core Features、Target Use Case、Key Value Proposition
- **tech.md**: Architecture、Technology Stack、Development Environment、Common Commands
- **structure.md**: Root Directory Organization、Subdirectory Structures、Code Organization Patterns、File Naming Conventions

### スペックドキュメントの構造

#### requirements.md

```markdown
# Requirements Document

## Project Description (Input)
[初期の機能説明]

## Requirements
[自動生成された要件リスト]
```

#### design.md

```markdown
# Technical Design

## Overview
[設計概要]

## Architecture
[アーキテクチャ設計]

## Implementation Details
[実装詳細]
```

#### tasks.md

```markdown
# Implementation Tasks

## Task List

### Task 1: [タスク名]
- Status: pending/in_progress/completed
- Description: [説明]
- Implementation: [実装方針]
```

## File Naming Conventions

### コマンドファイル

- **形式**: `[command-name].md`
- **例**: `spec-init.md`、`steering-custom.md`
- **命名ルール**: ハイフン区切り、小文字のみ

### ステアリングファイル

- **コアファイル**: `product.md`、`tech.md`、`structure.md`（固定）
- **カスタムファイル**: 自由な命名（`.md` 拡張子必須）
- **推奨**: 目的を明確にする名前（例: `testing.md`、`security.md`）

### スペックディレクトリ

- **形式**: `[feature-name]/`
- **生成ルール**: プロジェクト説明から自動生成（ハイフン区切り、小文字）
- **重複回避**: 既存の feature-name と重複する場合は数字サフィックス（例: `feature-name-2`）

### スペック内ファイル

- **固定名**: `spec.json`、`requirements.md`、`design.md`、`tasks.md`
- **拡張不可**: カスタムファイルは追加不可（構造を統一）

## Import Organization

該当なし（インポートシステムは使用していません）

### ファイル参照の方法

- **Claude Code の @ 構文**: `@CLAUDE.md`、`@.kiro/steering/product.md`
- **相対パス**: スラッシュコマンド内で相対パスを使用
- **ステアリングの自動読み込み**: Always モードのファイルは明示的な参照不要

## Key Architectural Principles

### 1. ドキュメントファースト

すべての情報は Markdown または JSON ファイルとして保存され、バージョン管理可能です。データベースは使用しません。

### 2. 段階的承認ワークフロー

要件 → 設計 → タスク の各フェーズで人間による承認を必須とし、品質を担保します。

### 3. 単一責任原則

- ステアリング: プロジェクト全体のコンテキスト
- スペック: 個別機能の詳細
- コマンド: 特定のタスクの実行

各レイヤーは明確に分離され、責務が重複しません。

### 4. 自動化と柔軟性のバランス

- 小規模な機能追加: ステアリングをスキップ可能
- 大規模な機能開発: 完全なワークフローを推奨
- カスタマイズ: ステアリングファイルの手動編集を尊重

### 5. 永続的なプロジェクトメモリ

ステアリングドキュメントにより、AI との会話が終了してもプロジェクトコンテキストが保存され、次回のセッションで継続できます。

### 6. 明示的な状態管理

spec.json により、各スペックの現在フェーズと承認状態を明示的に追跡し、曖昧さを排除します。

### 7. コンポーザビリティ

スラッシュコマンドは独立して実行可能で、必要に応じて組み合わせて使用できます。特定の順序を強制しますが、柔軟性も維持します。
