---
name: implement-minecraft-server-changes
description: Implement an established plan in this Minecraft server repository, validate and record the changes, and open a pull request to develop. Use for Paper plugins, configuration, data packs, and infrastructure after requirements or a fix plan have been supplied; do not use to redesign requirements from scratch.
---

# Implement Minecraft server changes

確定した要件・実装計画・修正方針をこのリポジトリへ反映し、検証、必要な利用者向け変更記録、`develop` 向けPR作成までを一続きの作業として完了する。ユーザーが「ローカル修正のみ」など成果物や外部操作の範囲を限定した場合は、その指定を優先する。

## Scope and implementation

1. ルートから対象ディレクトリまでの `AGENTS.md` を読み、このSkillより優先する。変更記録は [changes/README.md](../../../changes/README.md) に従う。
2. 作業ツリーと現在のブランチ、既存PRを確認する。同じ作業の進行中のブランチ・PRがあれば継続し、新規作業は最新の `origin/develop` から `codex/<descriptive-name>` を作る。ユーザーの未コミット変更を保全し、依頼外の変更をPRに含めない。
3. 修正対象、近接する実装、使用中のAPI・設定方式、関連する検証方法を確認する。計画で確定した内容を再調査せず、不足分だけ補う。
4. 既存の構成と運用上の読み込み先を踏まえて実装する。関連する設定・配布手順・運用文書の食い違いは依頼範囲で整合を取る。

既存の命名や設定方式を守り、保守性を優先する。広範なリファクタリングや不要な抽象化を加えない。計画と現状が矛盾する場合は根拠を確認し、利用者から見た仕様が変わる解釈はユーザーに確認する。合理的に決められる実装詳細は自律的に決め、確認待ちの間も独立して進められる作業を続ける。

Git管理の配布元、永続データ、実行時の読み込み先を区別する。PR作成までの依頼を、本番への適用・デプロイ・実サーバー操作の許可と解釈しない。実施する場合は依頼範囲、対象、権限を確認する。

## Validation and change records

- ユーザー指定の検証条件を優先し、既存のテスト・ビルド方法と変更リスクに応じて検証する。シェル・Composeの検証方法は `AGENTS.md`、実機確認の方法は関連する運用手順に従う。静的検証を本番確認と呼ばない。
- ファイル種別ではなく最終的な利用者体験で影響を判定し、必要なら `changes/pending/<descriptive-name>.md` を追加する。原則として利用者にとって独立した変更ごとに1ファイルとする。判定基準、書式、許容値は `changes/README.md` を参照し、通常開発では完成パッチノートの生成や `changes/released/` への移動を行わない。
- `change` は観測できる具体的事実を書く。`reason` は必要な場合だけ確認できた理由を書き、技術的事情をユーザーの意図した理由として補作しない。利用者への変更内容や必要な理由を確定できない場合は確認する。単純な追加・修正など理由が不要な場合は、確認せず省略する。
- `git diff --check` と対象の差分、未追跡・ステージ済みファイルを確認する。秘密情報やプレイヤーデータ、DB・Worldのバックアップ、依頼外の変更をコミットやPRに含めない。

## Pull request

検証と差分確認を終えたら、対象ファイルを明示してコミットし、作業ブランチをpushして `develop` 向けPRを作成する。必要な変更記録は同じPRに含める。同じ作業のPRが既にあれば追加コミットで更新し、重複PRを作らない。

PRのタイトル・本文は最終的な変更を表し、解決する問題、変更後の挙動、実施した検証と結果、未確認の本番動作を簡潔に記載する。PR作成後はURL、向き先、差分を確認する。Codexの `attach_artifact` が利用できる場合はPRをこのチャットに添付する。

認証・権限不足や検証失敗で先へ進めない場合は、解消できる範囲を対応してから、完了した作業と残る障害を報告する。pushやPR作成の成否が不明な場合はリモートの状態を確認してから再試行する。未作成のPRを作成済みとせず、ユーザーの指示なくマージや自動マージを行わない。

## Completion

指定範囲の実装、検証、必要な変更記録、最終差分の確認を終え、コミットを含む `develop` 向けPRが作成・更新されていることを完了条件とする。ユーザーが範囲を限定した場合や障害が残る場合は、達成した範囲を明示する。

完了報告はPRのURLを先に示し、変更内容、検証結果、追加した変更記録、未解決事項を簡潔に伝える。利用者影響なしで記録しなかった場合と、本番動作が未確認の場合はその旨を明記する。
