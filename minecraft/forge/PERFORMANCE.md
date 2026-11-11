# Forge パフォーマンス管理

Forge の起動・Mod 間互換性・実機操作と性能効果は未確認。適用前に既存 Volume とワールドをバックアップし、隔離コピーで確認する。

## JVM

固定 Java 17 HotSpot イメージで MeowIce の G1 フラグを有効にし、Aikar・GraalVM・ZGC 用は無効にする。Forge の JVM_OPTS / JVM_XX_OPTS は別途指定しない。ヒープは 1G〜8G、Swarm 上限は 9G のまま。固定イメージのスクリプトは G1、AlwaysPreTouch、文字列重複排除、400M コードキャッシュ、Large Pages と Transparent Huge Pages を指定する。SoftMaxHeapSize は ZGC 用の分岐だけで設定される。Large Pages の実際の利用はホスト設定に依存する。ネイティブメモリやコードキャッシュも上限内に必要であり、メモリ削減を保証しない。

同イメージの Temurin 17.0.15 で生成フラグと 1G〜8G ヒープによる Java 起動を arm64 の隔離コンテナで確認した。対象ノードの CPU と Huge Pages の状態、Forge の実負荷での OOM・GC は別途確認する。戻す場合は Compose の `USE_MEOWICE_FLAGS` を `FALSE` にし、通常のデプロイ手順を使う。

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

最大ヒープ 8G と Forge の Swarm 上限 9G を維持する。MeowIce OFF/ON と compactFastMap false/true の4構成を、同じワールドの隔離コピー、Mod、人数・活動、計測時間で比較する。Chunky による生成は停止し、導入自体の影響は別途測る。採用候補は両方 ON だが、改善は測定前には確定しない。

ヒープ・GC 後ヒープ、GC 回数と停止時間、コンテナ RSS・Working Set、CPU、TPS、MSPT 平均・P95・P99、起動時間、OOM、Mod エラーを、利用可能な監視と spark で記録する。監視で取得できない項目は未測定とし、数値を推測しない。ホスト全体にも他サービスのための十分なメモリを残す。

## Chunky

[Chunky 1.3.146](https://www.curseforge.com/minecraft/mc-mods/chunky-pregenerator-forge/files/5320028) は Forge 1.20.1 対応として配布される。`CURSEFORGE_FILES` の project 485681 / file 5320028 でサーバーの `/data/mods/` に取得し、共通 Manifest やクライアントには追加しない。Proxy Compatible Forge の `MODS` は維持する。既存 Volume に別経路の Chunky がないか停止・バックアップ後に確認し、重複があれば識別したファイルだけを mods の外に退避する。起動・取得・クライアント接続は未検証。

導入だけでは生成を開始しない。実行の判断は別途行い、管理者コンソールまたは OP のみが操作する。事前にワールドをバックアップし、十分なディスク空き容量を確保して低負荷時間帯に小範囲から始める。CPU、メモリ、TPS、MSPT、ディスクを監視し、OOM や TPS 低下時は停止する。

[公式コマンド](https://github.com/pop4959/Chunky/wiki/Commands)（ゲーム内では先頭に `/`）で対象を確認する。`chunky world <world>` でディメンション、`chunky shape square`、`chunky center <x> <z>`、`chunky radius <blocks>` で範囲を選択し、`chunky selection` で確認する。対象数は形状とブロック範囲から事前に見積もる（正方形なら概算 `(2 × 半径 / 16)²`、境界の端数や既存チャンクを含む）。`chunky start` で開始し、`chunky progress` とコンソールで進捗・完了を確認、`chunky pause` で一時停止、`chunky continue` で再開、`chunky cancel` で中止する。`trim` はチャンク削除なので使用しない。生成済みワールドは Mod の削除では元に戻らない。

Chunky を戻す場合は生成を中止し、停止・バックアップ後に `CURSEFORGE_FILES` を空文字にして管理対象の削除を確認する。固定イメージでの自動削除は未検証のため、残った JAR は実体を特定して `/data/mods/` の外に退避する。設定・タスクデータはバックアップし、再導入時に意図せず再開しないよう個別に確認する。ほかの Mod やワールドは削除しない。
