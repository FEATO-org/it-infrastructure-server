# Ultimate Sleep 運用

Paper 26.2用 Ultimate Sleep 1.3.1を `plugins.txt` から取得する。追跡する
`UltimateSleep/config.yml` は `/plugins` から `/data/plugins/UltimateSleep/config.yml` に
起動時同期される。再起動時はGitの設定が正本で、ゲーム内 `/usleep set` や
sleep-adminの変更は次回同期で戻り得る。永続設定を変更したらGitにも反映する。
旧バージョンの `ultimate-sleep-*.jar` は起動前の既存JAR整理で削除される。

## 適用前の必須確認

1. Paperを正常停止し、ワールド全体と `/data/plugins` の設定を別の安全な場所にバックアップする。Gitに保存しない。
2. 導入前の稼働中に、対象オーバーワールドで `/gamerule minecraft:players_sleeping_percentage` を読み取り、ワールド名と**実測値**をバックアップとともに記録する。複数の通常ワールドがある場合は各ワールドを確認する。現時点の `20` は未確認の暫定値である。
3. 実測値が20と異なる場合、適用前に `config.yml` の `required_sleep_percentage` を実測値に変更し、Git管理と配布設定を一致させる。元の値を推測しない。
4. 実際にロードされる通常ワールドが1つであることを確認する。公式実装は起動時に全通常ワールドを101にする一方、最初の通常ワールドだけで時刻を制御する。複数存在する場合は導入しない。リポジトリだけでは本番Volume内のワールド構成を確定できない。
5. 隔離環境で以下の受入試験を実施し、問題を解決してから適用する。特にAFK・報酬・既存効果とコマンド競合は静的確認だけでは保証できない。

追跡設定 `minecraft/java/plugins/UltimateSleep/config.yml` は `/plugins` から起動時に `/data/plugins/UltimateSleep/config.yml` へ同期される。ゲーム内の `/usleep set` や sleep-admin 追加は再デプロイ時に追跡設定で上書きされ得るため、既存設定をバックアップし、必要な変更は次のデプロイ前にGitへ取り込む。

## 動作と制約

- SIMPLE / ACCELERATE / SLOWを設定し、再生能力Iを1分、移動速度上昇Iを3分とする。金のニンジン、成長補正、自動睡眠、投票は使わない。公式実装の速度20%はamplifier 0（Speed I）。
- 必要人数は全ディメンションのオンライン非観戦者から独自AFKを除外し `max(1, ceil(人数 × 割合 / 100))`。20%なら1人・5人は1人、6人は2人。別ディメンションも分母に入る。100 tick以上の睡眠者が最低1人必要。加速開始後は人数条件を再評価しない。
- SLOWは約10秒を目標とするが、実装は時刻23459を超えた時点で加速を終了する。100 tickの待機、実際のTPS、開始時刻、途中参加可能時間を実機で確認する。
- AFKはUltimate Sleep独自の操作履歴（既定180秒）および `/usleep afk` による。EssentialsXのAFK状態とは連携しない。両Pluginが `/afk` を登録するため、実際の優先順位と `/essentials:afk`、`/ultimatesleep:afk` を確認する。
- 報酬判定は一次ワールドの暗→明の境界直前に眠っていたプレイヤーに基づき、自然な夜明けや管理者の時刻変更でも発生し得る。既存の再生・速度効果との競合、ValhallaMMO・Magicとの併用は未検証。
- 管理権限 `ultimatesleep.set` / `ultimatesleep.admin` は既定でOPのみ。一般プレイヤーに付与しない。GSitの `/lay` 用 `lay-rest: false` / `lay-night-skip: false` とCraftBook Chairsの既存設定は維持する。

## 適用後の受入と復旧

- 起動ログと `/usleep query` で有効・割合・設定を確認し、対象ワールドのゲームルールが101になったことを確認する。101はPlugin動作中のバニラ睡眠抑止値で、元の割合ではない。
- JavaとGeyser経由のBedrockそれぞれ一般権限で、1人・5人・6人、AFK、ネザー/エンド滞在、途中入床・離床、朝通知・報酬、管理者時刻変更、既存PotionEffect、GSit `/lay` とChairs、権限・`/afk` を確認する。加速時間と正常停止後の値も測定する。
- ロールバックはPaperを正常停止し、導入前のmanifest・設定へ戻してUltimate Sleep JARを永続Volumeから撤去する。バックアップを保持して起動し、各ワールドでゲームルールが導入前の**記録値**に戻ったことを確認する。異なる場合（101を含む）は対象ワールドで `/gamerule minecraft:players_sleeping_percentage <記録値>` を実行して確認する。無条件に100へ戻さない。
- 異常終了後に101が残る場合、Pluginは次回起動時に元値を100とみなす実装である。復旧時は正常停止・JAR撤去後に各ワールドを確認して記録値へ戻す。再起動後に正常停止しただけで元の値が保たれたと判断しない。

本番適用・実プレイヤー試験は未実施。

2026-10-31、隔離localhostのPaper 26.2 build 126 / GraalVM Java 25.0.4 / Ultimate Sleep単体でenable、`/usleep query`による設定、ゲームルール20→101、正常停止・JAR撤去後の再起動で20への復元を確認した。既存Pluginとの同時起動、配布コンテナ上の同期、睡眠・報酬・実プレイヤー操作は未確認。
