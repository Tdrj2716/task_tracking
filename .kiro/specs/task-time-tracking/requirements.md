# Requirements Document

## Project Description (Input)
タスクのタイムトラッキングができるWebアプリを作成したい

## Introduction
タスクタイムトラッキングWebアプリは、ユーザーが日常のタスクに費やした時間を記録・管理するためのシステムです。このアプリにより、ユーザーは作業時間の可視化、生産性の分析、プロジェクトごとの時間配分の把握が可能になります。

## Requirements

### Requirement 1: タスク管理
**Objective:** As a ユーザー, I want タスクの作成・編集・削除を行う機能, so that 時間を記録する対象のタスクを管理できる

#### Acceptance Criteria

1. WHEN ユーザーがタスク作成フォームにタスク名を入力して送信する THEN Time Tracking App SHALL 新しいタスクを作成してタスク一覧に表示する
2. WHEN ユーザーが既存のタスクを選択して編集ボタンをクリックする THEN Time Tracking App SHALL タスクの編集フォームを表示する
3. WHEN ユーザーがタスク編集フォームでタスク名を変更して保存する THEN Time Tracking App SHALL タスク情報を更新してタスク一覧に反映する
4. WHEN ユーザーがタスクの削除ボタンをクリックして確認する THEN Time Tracking App SHALL タスクと関連する時間記録を削除する
5. WHERE タスク作成フォーム THE Time Tracking App SHALL タスク名の入力を必須とする

### Requirement 2: 時間記録
**Objective:** As a ユーザー, I want タスクに対する作業時間を記録する機能, so that どのタスクにどれだけ時間を費やしたか追跡できる

#### Acceptance Criteria

1. WHEN ユーザーがタスクを選択してスタートボタンをクリックする THEN Time Tracking App SHALL タイマーを開始して経過時間の計測を始める
2. WHEN ユーザーがタスクを選択せずにスタートボタンをクリックする THEN Time Tracking App SHALL タスク未指定のままタイマーを開始して経過時間の計測を始める
3. WHILE タイマーが動作している THE Time Tracking App SHALL リアルタイムで経過時間を表示する
4. WHEN ユーザーがストップボタンをクリックする THEN Time Tracking App SHALL タイマーを停止して作業時間を記録として保存する
5. WHEN ユーザーが手動で時間記録を追加する（開始時刻・終了時刻を指定） THEN Time Tracking App SHALL 指定された時間範囲を時間記録として保存する
6. WHEN ユーザーがタスク未指定で手動時間記録を追加する THEN Time Tracking App SHALL タスクなしの時間記録として保存する
7. IF ユーザーが既に別のタスクのタイマーを実行中である THEN Time Tracking App SHALL 新しいタスクのタイマー開始時に前のタイマーを自動的に停止する
8. WHERE 時間記録 THE Time Tracking App SHALL タスク（オプショナル）、開始時刻、終了時刻、経過時間を含む情報を保存する

### Requirement 3: 時間記録の編集・削除
**Objective:** As a ユーザー, I want 記録した時間エントリーを修正または削除する機能, so that 誤った記録を訂正できる

#### Acceptance Criteria

1. WHEN ユーザーが時間記録を選択して編集ボタンをクリックする THEN Time Tracking App SHALL 時間記録の編集フォーム（開始時刻・終了時刻）を表示する
2. WHEN ユーザーが時間記録の開始時刻または終了時刻を変更して保存する THEN Time Tracking App SHALL 時間記録を更新して経過時間を再計算する
3. WHEN ユーザーが時間記録の削除ボタンをクリックして確認する THEN Time Tracking App SHALL 時間記録を削除する
4. IF ユーザーが編集フォームで終了時刻を開始時刻より前に設定する THEN Time Tracking App SHALL エラーメッセージを表示して保存を拒否する

### Requirement 4: 時間記録の表示と一覧
**Objective:** As a ユーザー, I want 記録した時間エントリーを一覧表示する機能, so that 過去の作業履歴を確認できる

#### Acceptance Criteria

1. WHEN ユーザーが時間記録一覧ページにアクセスする THEN Time Tracking App SHALL すべての時間記録を新しい順に表示する
2. WHERE 時間記録一覧 THE Time Tracking App SHALL タスク名、開始時刻、終了時刻、経過時間を表示する
3. WHEN ユーザーが日付フィルターを適用する THEN Time Tracking App SHALL 指定された日付範囲の時間記録のみを表示する
4. WHEN ユーザーがタスクフィルターを適用する THEN Time Tracking App SHALL 指定されたタスクの時間記録のみを表示する

### Requirement 5: 時間統計とレポート
**Objective:** As a ユーザー, I want タスクごとや期間ごとの作業時間の集計を確認する機能, so that 時間の使い方を分析できる

#### Acceptance Criteria

1. WHEN ユーザーが統計ページにアクセスする THEN Time Tracking App SHALL 各タスクの合計作業時間を表示する
2. WHEN ユーザーが日次レポートを選択する THEN Time Tracking App SHALL 指定された日の各タスクの作業時間を表示する
3. WHEN ユーザーが週次レポートを選択する THEN Time Tracking App SHALL 指定された週の各タスクの作業時間を日ごとに表示する
4. WHEN ユーザーが月次レポートを選択する THEN Time Tracking App SHALL 指定された月の各タスクの作業時間を日ごとに表示する
5. WHERE 統計表示 THE Time Tracking App SHALL 各タスクの作業時間を時間と分の形式で表示する

### Requirement 6: ユーザーインターフェース
**Objective:** As a ユーザー, I want 直感的で使いやすいインターフェース, so that スムーズに時間記録を行える

#### Acceptance Criteria

1. WHERE メインダッシュボード THE Time Tracking App SHALL 現在実行中のタイマー、タスク一覧、最近の時間記録を一画面で表示する
2. WHEN ユーザーが操作を実行する THEN Time Tracking App SHALL 処理の成功・失敗を通知メッセージで表示する
3. IF ユーザーがタイマー実行中にページを離れようとする THEN Time Tracking App SHALL 確認ダイアログを表示する
4. WHERE すべてのフォーム THE Time Tracking App SHALL 入力エラーがある場合に具体的なエラーメッセージを表示する

### Requirement 7: データの永続化
**Objective:** As a ユーザー, I want 記録したデータが保存される機能, so that ブラウザを閉じても情報が失われない

#### Acceptance Criteria

1. WHEN ユーザーがタスクや時間記録を作成・編集する THEN Time Tracking App SHALL データをストレージに永続化する
2. WHEN ユーザーがアプリケーションを再度開く THEN Time Tracking App SHALL 保存されたタスクと時間記録を復元して表示する
3. IF ブラウザのストレージが利用できない THEN Time Tracking App SHALL エラーメッセージを表示する

### Requirement 8: ユーザー認証
**Objective:** As a ユーザー, I want Googleアカウントでログインする機能, so that 複数デバイス間でデータを同期できる

#### Acceptance Criteria

1. WHEN ユーザーがログインページにアクセスする THEN Time Tracking App SHALL Googleログインボタンを表示する
2. WHEN ユーザーがGoogleログインボタンをクリックする THEN Time Tracking App SHALL Google OAuth認証フローを開始する
3. WHEN Google認証が成功する THEN Time Tracking App SHALL ユーザー情報を取得してログイン状態にする
4. WHEN ユーザーがログインした状態でアプリケーションにアクセスする THEN Time Tracking App SHALL ユーザー固有のタスクと時間記録を表示する
5. WHEN ユーザーがログアウトボタンをクリックする THEN Time Tracking App SHALL ログアウト処理を実行してログインページにリダイレクトする
6. IF ユーザーが未ログイン状態でアプリケーションにアクセスする THEN Time Tracking App SHALL ログインページにリダイレクトする
7. WHERE ユーザーデータ THE Time Tracking App SHALL ログインしたユーザーごとにタスクと時間記録を分離して管理する

### Requirement 9: タスク階層構造
**Objective:** As a ユーザー, I want タスクに子タスクを追加して階層化する機能, so that 大きなタスクを小さな作業単位に分割して管理できる

#### Acceptance Criteria

1. WHEN ユーザーがタスクに子タスクを追加する THEN Time Tracking App SHALL 親タスクの配下に子タスクを作成する
2. WHEN ユーザーが子タスクにさらに子タスク（孫タスク）を追加する THEN Time Tracking App SHALL 子タスクの配下に孫タスクを作成する
3. IF ユーザーが孫タスクにさらに子タスクを追加しようとする THEN Time Tracking App SHALL エラーメッセージを表示して作成を拒否する
4. WHERE タスク階層 THE Time Tracking App SHALL 親・子・孫の最大3階層までのタスク構造を許可する
5. WHEN ユーザーがタスク一覧を表示する THEN Time Tracking App SHALL タスクを階層構造で表示し、親タスクの展開/折りたたみを可能にする
6. WHEN ユーザーが親タスクを削除する THEN Time Tracking App SHALL 配下の子タスク・孫タスクもすべて削除する
7. WHEN ユーザーが時間記録を作成する際にタスクを選択する THEN Time Tracking App SHALL すべての階層のタスク（親・子・孫）を選択可能にする

### Requirement 10: プロジェクト管理
**Objective:** As a ユーザー, I want タスクをプロジェクトで分類する機能, so that 関連するタスクをまとめて管理できる

#### Acceptance Criteria

1. WHEN ユーザーがプロジェクトを作成する THEN Time Tracking App SHALL 新しいプロジェクトを作成してプロジェクト一覧に表示する
2. WHEN ユーザーがタスクを作成または編集する THEN Time Tracking App SHALL プロジェクト選択ドロップダウンを表示する
3. WHEN ユーザーがタスクにプロジェクトを設定する THEN Time Tracking App SHALL タスクを指定されたプロジェクトに関連付ける
4. IF ユーザーがタスクにプロジェクトを設定しない THEN Time Tracking App SHALL タスクを "Inbox" プロジェクトに自動的に関連付ける
5. WHERE タスクのプロジェクト設定 THE Time Tracking App SHALL 1つのタスクに対して1つのプロジェクトのみ設定を許可する
6. WHEN ユーザーがプロジェクトを削除する THEN Time Tracking App SHALL 関連するタスクを "Inbox" プロジェクトに移動する
7. WHEN ユーザーがプロジェクト別レポートを表示する THEN Time Tracking App SHALL 各プロジェクトの合計作業時間を表示する
8. WHERE システム THE Time Tracking App SHALL "Inbox" という名前のデフォルトプロジェクトを自動作成し、削除を禁止する

### Requirement 11: タグ管理
**Objective:** As a ユーザー, I want タスクに複数のタグを設定する機能, so that タスクを柔軟に分類・フィルタリングできる

#### Acceptance Criteria

1. WHEN ユーザーがタグを作成する THEN Time Tracking App SHALL 新しいタグを作成してタグ一覧に表示する
2. WHEN ユーザーがタスクを作成または編集する THEN Time Tracking App SHALL タグ選択インターフェース（マルチセレクト）を表示する
3. WHEN ユーザーがタスクに複数のタグを設定する THEN Time Tracking App SHALL タスクに指定されたすべてのタグを関連付ける
4. WHEN ユーザーがタスク一覧でタグフィルターを適用する THEN Time Tracking App SHALL 指定されたタグを持つタスクのみを表示する
5. WHEN ユーザーが複数のタグでフィルターする THEN Time Tracking App SHALL すべての指定されたタグを持つタスクのみを表示する（AND条件）
6. WHEN ユーザーがタグを削除する THEN Time Tracking App SHALL タスクからそのタグの関連付けを削除する
7. WHERE タグ表示 THE Time Tracking App SHALL タスク一覧で各タスクに設定されたタグを表示する
8. WHEN ユーザーがタグ別レポートを表示する THEN Time Tracking App SHALL 各タグの合計作業時間を表示する
