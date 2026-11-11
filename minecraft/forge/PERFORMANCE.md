# Forge パフォーマンス管理（作業中）

この文書は隔離起動・実機操作未確認。PR の Compose 変更が完了するまでは MeowIce や Chunky が導入済みとは扱わない。

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

最大ヒープ 8G と Forge の Swarm 上限 10G を予定する。Compose に 10G が入るまでは現行の上限を記録する。MeowIce OFF/ON と compactFastMap false/true の4構成を、同じワールドの隔離コピー、Mod、人数・活動、計測時間で比較する。Chunky による生成は停止し、導入自体の影響は別途測る。採用候補は両方 ON だが、改善は測定前には確定しない。

ヒープ・GC 後ヒープ、GC 回数と停止時間、コンテナ RSS・Working Set、CPU、TPS、MSPT 平均・P95・P99、起動時間、OOM、Mod エラーを、利用可能な監視と spark で記録する。監視で取得できない項目は未測定とし、数値を推測しない。ホスト全体にも他サービスのための十分なメモリを残す。
