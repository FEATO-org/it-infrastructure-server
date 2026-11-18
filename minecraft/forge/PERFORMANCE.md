# Forge パフォーマンス管理

Forge の起動・Mod 間互換性・実機操作と性能効果は未確認。適用前に既存 Volume とワールドをバックアップし、隔離コピーで確認する。

## JVM

固定 Java 17 HotSpot イメージで MeowIce の G1 フラグを有効にし、Aikar・GraalVM・ZGC 用は無効にする。Forge の JVM_OPTS は JMX Agent のみに使い、JVM_XX_OPTS は別途指定しない。ヒープは 1G〜8G のまま、Swarm 上限は 9G から 10G に変更する。固定イメージのスクリプトは G1、AlwaysPreTouch、文字列重複排除、400M コードキャッシュ、Large Pages と Transparent Huge Pages を指定する。SoftMaxHeapSize は ZGC 用の分岐だけで設定される。Large Pages の実際の利用はホスト設定に依存する。ネイティブメモリやコードキャッシュも上限内に必要であり、メモリ削減を保証しない。

同イメージの Temurin 17.0.15 で生成フラグと 1G〜8G ヒープによる Java 起動を arm64 の隔離コンテナで確認した。対象ノードの CPU と Huge Pages の状態、Forge の実負荷での OOM・GC は別途確認する。戻す場合は Compose の `USE_MEOWICE_FLAGS` を `FALSE` にし、通常のデプロイ手順を使う。

コンテナ上限だけを戻す場合は Forge の `deploy.resources.limits.memory` を `9G` に戻す。いずれの上限でも、データノードに他サービスと OS のための余裕を確保し、実使用量を監視する。

## FerriteCore の既存 Volume への反映

`prepare-forge.sh` は `/forge-config/config/` の設定を `/data/config/` に、存在しないファイルだけコピーする。Git の値の変更は既存 Volume に反映されない。

1. 対象サービス・Volume・データノードを確認し、通常の手順で Forge を停止する。
2. 既存のバックアップ手順に従い Volume 全体をバックアップする。加えて `/data/config/ferritecore-mixin.toml` の実物を別名でバックアップし、復元できるよう保管する。
3. 実物を確認し、`compactFastMap = false` の行だけを `compactFastMap = true` に変更する。他の項目や権限・所有者を保持する。既に true の場合は変更不要。対象行が重複・存在しない場合は作業を止めて調査する。
4. 差分が対象行だけであることを確認する。通常の手順で起動後、Volume 上の同ファイルの値と起動ログのエラーを確認する。値がファイルに存在することだけでは mixin 適用や互換性の証明にはならない。
5. 戻す場合は停止後に現在の設定をバックアップし、対象行だけを false に戻すか、変更前の設定ファイルを復元する。所有者と権限を確認して起動する。

Create を含む Mod との互換性、メモリ削減効果と MSPT への影響は未検証。

## spark 診断

Manifest には spark 361579 / 4738952 が登録されている。明示除外リストにはないが、サーバーへの実配置とコマンドは未検証。管理者コンソールまたは権限のある管理者のみで実行し、一般プレイヤーに分析権限を付与しない。

- 状態: `/spark tps`、`/spark health show --memory`。
- CPU: `/spark profiler start`、必要な時間だけ計測して `/spark profiler stop --save-to-file`。サーバースレッドを中心に高負荷処理を確認する。
- 割当: `/spark profiler start --alloc`、計測後に `/spark profiler stop --save-to-file`。CPU プロファイルとは別に実施する。対応 profiler の利用可否は実環境で確認する。
- 中止: `/spark profiler cancel`。常時長時間の計測は行わない。

コマンドの動作は導入版で未検証。出力には内部構成やプレイヤーに関する情報が含まれる可能性がある。結果は管理者のみが扱い、外部サービスへのアップロードや URL の共有は公開範囲を確認してから行う。参照: [spark コマンド](https://spark.lucko.me/docs/Command-Usage)。

## 性能比較

最大ヒープ 8G と Forge の Swarm 上限 10G に統一する。旧設定との比較では 9G からの上限変更も記録する。MeowIce OFF/ON と compactFastMap false/true の4構成を、同じワールドの隔離コピー、Mod、人数・活動、計測時間で比較する。Chunky による生成は停止し、導入自体の影響は別途測る。採用候補は両方 ON だが、改善は測定前には確定しない。

ヒープ・GC 後ヒープ、GC 回数と停止時間、コンテナ RSS・Working Set、CPU、TPS、MSPT 平均・P95・P99、起動時間、OOM、Mod エラーを、利用可能な監視と spark で記録する。監視で取得できない項目は未測定とし、数値を推測しない。ホスト全体にも他サービスのための十分なメモリを残す。

## Chunky

[Chunky 1.3.146](https://www.curseforge.com/minecraft/mc-mods/chunky-pregenerator-forge/files/5320028) は Forge 1.20.1 対応として配布される。`CURSEFORGE_FILES` の project 485681 / file 5320028 でサーバーの `/data/mods/` に取得し、共通 Manifest やクライアントには追加しない。Proxy Compatible Forge の `MODS` は維持する。既存 Volume に別経路の Chunky がないか停止・バックアップ後に確認し、重複があれば識別したファイルだけを mods の外に退避する。起動・取得・クライアント接続は未検証。

導入だけでは生成を開始しない。実行の判断は別途行い、管理者コンソールまたは OP のみが操作する。事前にワールドをバックアップし、十分なディスク空き容量を確保して低負荷時間帯に小範囲から始める。CPU、メモリ、TPS、MSPT、ディスクを監視し、OOM や TPS 低下時は停止する。

[公式コマンド](https://github.com/pop4959/Chunky/wiki/Commands)（ゲーム内では先頭に `/`）で対象を確認する。`chunky world <world>` でディメンション、`chunky shape square`、`chunky center <x> <z>`、`chunky radius <blocks>` で範囲を選択し、`chunky selection` で確認する。対象数は形状とブロック範囲から事前に見積もる（正方形なら概算 `(2 × 半径 / 16)²`、境界の端数や既存チャンクを含む）。`chunky start` で開始し、`chunky progress` とコンソールで進捗・完了を確認、`chunky pause` で一時停止、`chunky continue` で再開、`chunky cancel` で中止する。`trim` はチャンク削除なので使用しない。生成済みワールドは Mod の削除では元に戻らない。

Chunky を戻す場合は生成を中止し、停止・バックアップ後に `CURSEFORGE_FILES` から `485681:5320028` だけを外し、他の指定を維持して管理対象の削除を確認する。固定イメージでの自動削除は未検証のため、残った JAR は実体を特定して `/data/mods/` の外に退避する。設定・タスクデータはバックアップし、再導入時に意図せず再開しないよう個別に確認する。ほかの Mod やワールドは削除しない。

## サーバー専用の最適化 Mod 3件

`CURSEFORGE_FILES` に [Radium Re-Reforged 0.15.0](https://www.curseforge.com/minecraft/mc-mods/radium-re-reforged/files/9434151)（1649038:9434151）、[AegisNetworking 0.1.2](https://www.curseforge.com/minecraft/mc-mods/aegisnetworking/files/9380443)（1773519:9380443）、[AllTheLeaks 1.1.6](https://www.curseforge.com/minecraft/mc-mods/alltheleaks/files/9640602)（1091339:9640602）を固定する。Chunky と Proxy Compatible Forge は維持し、共通 manifest に追加しない。取得した JAR のメタデータでは Radium の ID は `radium`、AegisNetworking の表示名と ID は `RatNetworking` / `ratnetworking`。Aegis の JAR は通常の通信では片側導入可能とする一方、バニラ上限を超えるパケットの受信側には RatNetworking または Packet Fixer が必要と記載する。

固定 JAR を Curse Maven から取得して依存宣言を確認した。Aegis は Forge 47 以降、AllTheLeaks は Forge 47.2.0 以降と Minecraft 1.20.1 を要求し、現行 Forge 47.4.28 は範囲内。AllTheLeaks は GeckoLib 4.4.8 以降を任意依存として宣言し、manifest の [4.8.4](https://www.curseforge.com/minecraft/mc-mods/geckolib/files/8285794) は範囲内。Radium の loader 宣言は `*` で、Minecraft / Forge のバージョン範囲は明示されていない。AllTheLeaks の JAR には ModernFix 関連コードが含まれるが、競合の有無は未確認。既存 manifest と管理対象の追加取得先に旧 Radium、Krypton 系、VMP、Packet Fixer、Connectivity の登録は見当たらない。永続 Volume の手動配置分は別途確認する。FerriteCore と Radium の自動互換性制御、および ModernFix・AllTheLeaks・Aegis 間の Mixin 共存は実行時に確認する。推測による設定変更は行わない。

本番適用前に Forge を正常停止し、world、playerdata、mods、config、tacz と同期管理状態を含む Volume 全体をバックアップして復元可能性を確認する。Auto CurseForge の管理対象と手動配置を区別し、3件の重複 JAR がないか確認する。本番 Volume をマウントしない隔離環境で取得・起動・Mod 認識・停止・再起動を試し、新規 Mod の Mixin / クラスロードエラーと既知の Frontline の Mixin エラーを区別する。FerriteCore の互換性制御、Aegis と AllTheLeaks の初期化を確認する。Velocity 経由の Forge ハンドシェイク、ログイン・切断・再接続、大きな Mod パケット、チャンク送信と Entity Tracking を確認する。圧縮設定 `-1` は維持する。起動・接続・性能効果は未検証で、同条件の spark による TPS・MSPT・CPU・メモリ比較も未測定。

障害時は停止・バックアップ後、3件の project:file 指定だけを外して Chunky を維持し、管理対象からの削除を確認する。自動削除は未検証のため、残存 JAR を実体と ID で特定して対象だけを `/data/mods/` 外へ退避する。他 Mod やワールドを一括削除しない。必要なら更新前の整合した Volume バックアップと旧 revision を復元する。

## Forge JVM 監視

JMX Exporter 1.7.0 Java Agent を `content.lock` の公式 URL と SHA-256 で `/data/monitoring/` に同期する。`prepare-forge.sh` は Forge の `run.sh` 実行前に同期し、専用 overlay の alias `forge-jvm-target` の経路から自タスクの送信元 IP を求め、生成済み `user_jvm_args.txt` の Agent 待受先に設定する。IP を決められなければ起動を中止する。固定イメージでは JVM flags と Xms/Xmx の生成後に pre-start を実行し、Forge の `run.sh` が同ファイルを読む。既存の global Fluent Bit に専用 overlay を追加し、Swarm の templated config で選択ノードだけ JVM の input/output を有効にする。`deploy_swarm.sh` は `minecraft-data=true` が1台ならその node ID を選ぶ。複数台なら `FORGE_JVM_SCRAPE_NODE_ID` に対象の完全な node ID を指定する。60秒間隔（`FORGE_JVM_SCRAPE_INTERVAL=120s` で変更可）で remote write する。既存監視の2分間隔は変えない。60秒は初期観測用であり契約上の許容量を保証しない。

Agent 組み込み JVM メトリクスと exporter 自身の状態を出力する。別の JMX collector は対象 ObjectName を限定し、任意の Mod MBean を出力しない。Java 17 の隔離確認で以下を観測した。単位は bytes、GC count は回数、GC sum は秒。その他に JVM thread、class、buffer、process と exporter の状態系列がある。

- `jvm_memory_used_bytes` / `jvm_memory_committed_bytes` / `jvm_memory_max_bytes`（`area="heap"` または `area="nonheap"`）
- `jvm_memory_pool_used_bytes`、`jvm_memory_pool_collection_used_bytes`（`pool` 別、Metaspace を含む）
- `jvm_gc_collection_seconds_count`、`jvm_gc_collection_seconds_sum`（`gc` 別の累積回数と累積秒）

Grafana Explore の Prometheus データソースで `{monitor="forge-jvm",app_mode="<環境>"}` を各式に付ける。例（環境を実値に置換）:

```promql
jvm_memory_used_bytes{monitor="forge-jvm",app_mode="<環境>",area="heap"}
jvm_memory_committed_bytes{monitor="forge-jvm",app_mode="<環境>",area="heap"}
jvm_memory_max_bytes{monitor="forge-jvm",app_mode="<環境>",area="heap"}
jvm_memory_used_bytes{monitor="forge-jvm",app_mode="<環境>",area="heap"} / jvm_memory_max_bytes{monitor="forge-jvm",app_mode="<環境>",area="heap"}
rate(jvm_gc_collection_seconds_count{monitor="forge-jvm",app_mode="<環境>"}[10m])
rate(jvm_gc_collection_seconds_sum{monitor="forge-jvm",app_mode="<環境>"}[10m])
jvm_memory_pool_used_bytes{monitor="forge-jvm",app_mode="<環境>"}
jvm_memory_used_bytes{monitor="forge-jvm",app_mode="<環境>",area="nonheap"}
```

Heap 比率はその時点の使用量 / 最大値であり GC 後の生存量ではない。Pool の collection 値は JVM がその Pool の GC 後に更新した値で、未対応の Pool は存在しない場合がある。G1 の Young/Old ごとに更新条件が異なり、全 Heap の同時点の生存量とは限らない。GC sum は累積時間であり停止時間分布や P95/P99 ではない。最大値の `-1` は未定義を示す。cAdvisor のコンテナメモリと比較する際は Forge のコンテナを既存ラベルで特定し、Heap に加え native、Non-Heap、ページキャッシュ等を含む差に注意する。

Explore で `count({monitor="forge-jvm",app_mode="<環境>"})` を確認し、概算 DPM は系列数 × 60 / scrape秒数。Grafana Cloud の使用量画面で実際の Active Series / DPM と契約枠を確認し、超過が懸念される場合は120秒に変更する。Agent 自身の `jmx_scrape_duration_seconds` / `jmx_scrape_error` と Forge の CPU・メモリ、および Fluent Bit の CPU・メモリを導入前後の同条件で比較する。scrape 時間は全オーバーヘッドではない。

起動失敗時は Forge service logs の同期失敗、ハッシュ不一致、DNS/route、Agent YAML、ポート bind を順に調査する。改変済み・管理外ファイルは上書きされず、手動削除もしない。Minecraft が起動済みで系列がない場合は `system_fluent-bit` の選択ノードの logs で scrape DNS/接続、`jmx_scrape_error`、remote write の TLS・認証・応答を切り分ける。認証値を表示・共有しない。通信障害と JVM 起動障害は別に扱う。

ロールバックは Forge の `JVM_OPTS` の Agent 指定をまず削除して通常のデプロイ手順で再起動する（設定の除去だけでは既存プロセスに反映されない）。Agent の取得自体が障害の場合は同時に `content.lock` の Agent 行も外し、同期失敗で起動が止まらないようにする。必要に応じて JVM 用 include、両 Compose の overlay 参照と config 宣言、config ハッシュ対象と外部ネットワーク作成を戻し、対応スタックを再デプロイする。既存 global Fluent Bit のログ・他メトリクス設定は維持する。未使用 config/network は参照を確認して運用者が整理する。管理済み JAR は Volume から削除しない。本作業では本番適用を行っていない。

複数ノード運用では選択ノードの障害時に自動切替しないため、監視欠落を確認し `FORGE_JVM_SCRAPE_NODE_ID` を別の `minecraft-data=true` ノードへ切り替えて再デプロイする。切替時に旧・新ノードの Scrape が重ならないよう、先に `FORGE_JVM_SCRAPE_NODE_ID=disabled` でデプロイし、全 `system_fluent-bit` タスクの更新完了と JVM 収集停止を確認してから新 ID を指定して再デプロイする。未選択ノードでは他の収集は継続する。テンプレート config の選択と実際の Remote Write は Swarm 実機で要確認。
