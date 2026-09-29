# Minecraft パッチノート運用

初回利用前に、この Workflow と Python スクリプトを `main` と `develop` の両方へ反映する。`develop` は現在の `main` から作成済みだが、作業中の未コミット変更はまだ含まない。

1. 通常開発では作業ブランチから `develop` へPRを出す。利用者に見える変更は同じPRに `changes/pending/<kebab-case>.md` を追加し、`changes/README.md` の形式に従う。通常の編集を `main` へ直接上げない。
2. 変更を `develop` に集約する。`develop` は事前に作成し、継続して管理する。
3. `develop` を確認してから `Prepare Minecraft release` を手動実行する。Workflow は東京の日付と既存 tag / deploy branch から `YYYY-MM-DD.N` を採番し、`deploy/<version>` に完成パッチノートと archived changes をコミットする。
4. 生成された `main` 向け Release PR と `develop` 向け sync PR の両方を確認する。Bot 作成 PR の validation が承認待ちなら、GitHub 上で実行を承認する。
5. デプロイと本番確認を終えてから `main` 向け PR をマージする。Workflow はこの PR が追加したパッチノートだけを公開対象にする。
6. GitHub Release と Discord 投稿を確認する。Discord 投稿結果が不明な場合は Release の `discord-delivery-pending.json` が自動再送を止める。投稿先に何件届いたか確認し、未投稿だと確定できた場合だけ pending asset を削除して同じ Workflow run を再実行する。複数 payload の一部だけ届いていた場合は残りを手動で投稿する。`discord-delivery-sent.json` は送信完了を表す。
7. `develop` 向け sync PR をマージする。`deploy/<version>` ブランチは自動削除しない。

Repository Actions secret `DISCORD_PATCHNOTE_WEBHOOK_URL` が必要。Actions に PR 作成と contents 書き込みを許可し、Ruleset / branch protection で `main` と `develop` のレビュー・必要なチェックを設定する。Release assets を送信状態に使うため、immutable releases は有効化しない。実際の公開は `main` へのマージ後にのみ実行される。
