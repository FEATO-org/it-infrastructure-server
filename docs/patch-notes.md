# Minecraft パッチノート運用

初回利用前に、この Workflow と Python スクリプトを `main` と `develop` の両方へ反映する。初期導入は `main` から `codex/bootstrap-minecraft-release` を作り、リリース用Workflow・`scripts/patchnotes/`・運用文書・保存先の `.gitkeep` だけを反映する。未リリースのMinecraft設定や `changes/pending/` は持ち込まない。この導入PRはリリースPRではなく、パッチノートの公開も行わない。

1. 通常開発では作業ブランチから `develop` へPRを出す。利用者に見える変更は同じPRに `changes/pending/<kebab-case>.md` を追加し、`changes/README.md` の形式に従う。通常の編集を `main` へ直接上げない。
2. 変更を `develop` に集約する。`develop` は事前に作成し、継続して管理する。
3. `develop` を確認してから、実行ブランチに `develop` を選び `Prepare Minecraft release` を手動実行する。Workflow は東京の日付と既存 tag / deploy branch から `YYYY-MM-DD.N` を採番し、`deploy/<version>` に完成パッチノートと archived changes をコミットする。Discord用payloadも生成して文字数制限を検証し、生成済みパッチノートは上書きしない。
4. 生成された `main` 向け Release PR と `develop` 向け sync PR の両方を確認する。PR作成には下記のPATを使うため、`GITHUB_TOKEN`による作成時のCI承認待ちを避けられる。レビューとマージは手動で行う。
5. デプロイと本番確認を終えてから `main` 向け PR をマージする。Workflow はこの PR が追加したパッチノートだけを公開対象にする。
6. GitHub Release と Discord 投稿を確認する。Discord 投稿結果が不明な場合は Release の `discord-delivery-pending.json` が自動再送を止める。未投稿だと確定できた場合だけ、下記の手動復旧を使う。複数 payload の一部だけ届いていた場合は残りを手動で投稿する。`discord-delivery-sent.json` は送信完了を表す。
7. `develop` 向け sync PR をマージする。`deploy/<version>` ブランチは自動削除しない。

Repository Actions secret `DISCORD_PATCHNOTE_WEBHOOK_URL` と `RELEASE_PR_TOKEN` が必要。ブランチ作成とpushにはWorkflowの `GITHUB_TOKEN`（contents: write）、PR作成にはPATを使う。Ruleset / branch protection で `main` と `develop` のレビュー・必要なチェックを設定する。Release assets を送信状態に使うため、immutable releases は有効化しない。実際の公開は `main` へのマージ後にのみ実行される。

## PR作成用PATの登録

1. GitHubの [Fine-grained personal access tokens](https://github.com/settings/personal-access-tokens) でtokenを作成する。Resource ownerは `FEATO-org`、Repository accessは `Only select repositories` → `it-infrastructure-server` に限定する。
2. Repository permissionsに `Contents: Read-only`（GitHub CLIのリポジトリ参照用）と `Pull requests: Read and write` を設定する。`Metadata: Read-only` は自動付与される。token所有者自身も、このリポジトリでPRを作成できる権限が必要。
3. 有効期限を設定し、Organizationの承認が必要なら承認を完了する。
4. リポジトリの [Settings → Secrets and variables → Actions](https://github.com/FEATO-org/it-infrastructure-server/settings/secrets/actions) に、名前 `RELEASE_PR_TOKEN` で登録する。期限前に更新し、同じSecretを差し替える。

Resource ownerに `FEATO-org` が出ない場合は、ブラウザのログインアカウントがOrganizationのMember / Ownerか、招待を承諾済みかを確認する。リポジトリだけのoutside collaboratorはfine-grained PATでOrganizationを指定できない。所属済みでもOrganizationがfine-grained PATを禁止していると候補に出ないため、Organization Settings → Personal access tokens → Settings → Fine-grained tokensのポリシーをOwnerが確認する。

PATは準備Workflowのtoken確認と2本のPR作成でだけ使用し、PRの作成者はPAT所有者になる。未登録の場合は最初のstepで停止し、対象リポジトリへのAPIアクセスもブランチ作成前に確認する。承認待ちの `GITHUB_TOKEN` に自動で戻す処理は設けない。tokenの期限切れ、Organization承認、PR書き込み権限も実行前に確認する。既存の承認待ちrunは自動解除されないので、必要ならそのPRで承認する。

GitHubの認証仕様は [GITHUB_TOKEN](https://docs.github.com/en/actions/concepts/security/github_token)、PATの発行手順は [Managing your personal access tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) を参照する。

公開処理は、今回のpushで追加されたパッチノートと、そのcommitをマージした `deploy/<version> → main` PRが一致する場合だけ動作する。GitHub APIがエラーになった場合は、Releaseやtagが存在しないと推測して作成を続けず停止する。既存Releaseの本文が異なる場合やdraft / prereleaseの場合も停止する。

Discordへの送信はAPI指定形式の `User-Agent` を付ける。HTTPエラー時はステータスと、JSONで返された数値のAPIエラーコードだけを記録し、レスポンス本文やWebhook URLは出力しない。403だけではURL・権限の問題とCloudflareによる拒否を確定できない。送信コードを修正した場合、過去のrunを再実行しても元のcommitのコードが使われるため、修正済みコードを使う復旧手順が必要になる。

## Discord送信の手動復旧

1. 投稿先で対象バージョンが1件も投稿されていないことを確認する。一部投稿済み・結果不明なら、この手順で全文を再送しない。
2. 必要なコード修正を `main` に反映する。過去runのRe-runではなく、Actionsの `Publish Minecraft release` で `Run workflow` を選ぶ。
3. 実行ブランチに `main`、`version` に既存のバージョン（例: `2026-10-03.2`）を指定し、`confirm_no_delivery` にチェックを入れて実行する。
4. Workflowが成功し、Discord全文投稿とReleaseの `discord-delivery-sent.json` を確認する。

復旧は既存tagがmainにマージ済みの対応するリリースPRのcommitを指し、正式Releaseが存在する場合だけ可能。保存済みchangeから生成した本文とRelease本文の一致も検証する。未投稿の確認を受けた復旧実行だけがpending assetを置き換えて送信を再開し、Releaseやtagは新規作成しない。送信済みなら何も投稿しない。通常の自動公開ではpending assetによる再送停止を維持する。

## ブランチ保護と復旧

`main` と `develop` はPR経由の更新と `validate` チェックを必須にし、管理者にも適用する。force pushとブランチ削除を許可しない。`validate` は変更記録とパッチノート用テストに加え、PRの向きも確認する。通常の作業PRは `develop` 向け、`main` 向けは `deploy/YYYY-MM-DD.N` のリリースPRだけとする。上記の初期導入ブランチは対象ファイルを制限した例外とする。

誤って `main` に未リリース機能を入れた場合は、履歴を書き換えず取り消しPRで本番基準へ戻す。機能を維持する `develop` に取り消しコミットを単独でcherry-pickしない。`develop` から復旧作業ブランチを作って `main` をmergeし、設定と未リリースの変更記録が意図どおり維持されていることを確認して、`develop` 向けPRで履歴を同期する。初期導入PRのマージ後も同様に `main` を同期する。

作業ブランチは対象PRへの取り込みと追加コミットがないことを確認して削除する。`main` の復旧専用ブランチは `develop` に未マージでも、復旧PRが `main` にマージ済みなら削除できる。`main`・`develop`・`deploy/<version>` は削除しない。

リリースの前に `DISCORD_PATCHNOTE_WEBHOOK_URL` と `RELEASE_PR_TOKEN` の登録、PATの有効性と権限、両ブランチの保護設定を確認する。Secret値はログや文書へ書かない。未設定のSecretや未実施の本番確認を、静的検証で完了扱いにしない。
