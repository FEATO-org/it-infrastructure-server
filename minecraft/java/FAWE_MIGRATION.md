# WorldEdit → FAWE移行・検証（2026-10-09）

## 採用版と目的

WorldEdit 7.4.5をFastAsyncWorldEdit **2.16.0 Paper版**へ置換する。
BUILDING高レベル能力で、Survival inventory消費を伴う制限付き大規模施工を
安全に実装できる編集基盤を用意するため。BUILDING / Architectは未実装。

- [公式Release](https://github.com/IntellectualSites/FastAsyncWorldEdit/releases/tag/2.16.0): 2026-10-04公開、`prerelease: false`。
- [公式Paper metadata](https://api.modrinth.com/v2/version/U2dcKa9T): `version_type: release`、Paper / 26.2を列挙。
- 固定URL: https://cdn.modrinth.com/data/z4HZZnLr/versions/U2dcKa9T/FastAsyncWorldEdit-Paper-2.16.0.jar
- SHA-256（取得JARから計算）: `1a3cf8178f22d97fe78db100c7d50ebe57acdb59f3df1a972c29761ebba6f0cd`
- SHA-512（取得JARとmetadata一致）: `add46c57209e95c700cbda1c4b25d58d4e39826cd5cbc23bfbc678e145d3424283020317544ec05587972d2a133e43715dc24dd26d51593bb3b0c4e28b7c9c4b`
- JARのmain: `com.sk89q.worldedit.bukkit.WorldEditPlugin`、`provides: [WorldEdit]`、version: `2.16.0+bd5705d`。

第一候補2.15.4より新しいstableで26.2対応を維持し、clipboard保存時のentity座標修正と
block/item ID定数の明示化を含む2.16.0を採用した。snapshot/devは使用しない。
CraftBook 3.10.13は`depend: [WorldEdit]`をFAWEのprovidesで解決する。
配布JAR内のCraftBook表記は`3.10.13-SNAPSHOT;no_git_id`だが、既存の固定配布物を変更しない。

## 永続Volume・データ移行

`PLUGINS_FILE: /extras/plugins.txt`から`/data/plugins`へJARを取得する。
Git追跡設定はComposeの`/plugins`から`/data/plugins`へ同期される。
今回、FAWEの設定seedや一般向けWorldEdit権限は追加しない。CraftBookの設定・mechanicsも変更しない。

1. `minecraft-data`ラベルのPaper稼働ノードを確認し、正常停止する。停止したVolumeの
   WorldEdit / FastAsyncWorldEdit / CraftBookの設定・schematics・sessions、必要ならWorldをバックアップする。
2. `/data/plugins`と`update/`を確認する。既存`REMOVE_OLD_MODS_INCLUDE`に
   `worldedit-bukkit-*.jar`を追加したため、通常取得前に旧WorldEditを除去する。
   `prepare-paper-plugins.sh`も起動直前に以下の**JARだけ**を除去する。
   - `/data/plugins/worldedit-bukkit-*.jar`
   - `/data/plugins/update/worldedit-bukkit-*.jar`
   - `/data/plugins/.paper-remapped/worldedit-bukkit-*.jar`
   既存のDeadChest staged-JAR cleanupも同じループで維持する。
   FAWE / CraftBook / 他PluginのJAR、WorldEditの設定やschematicは除去しない。
   独自リネームされたWorldEdit JARはパターン外なので、descriptorを確認してVolume外へ退避する。
3. 追跡設定にWorldEditディレクトリやschematicの利用実績は見つからなかった。
   本番Volumeの内容は未調査。不要データとは判断せず、旧ディレクトリを保持する。
   FAWEの隔離起動で生成された読み込み先は
   `/data/plugins/FastAsyncWorldEdit/config.yml`（FAWE設定）、
   `worldedit-config.yml`（WorldEdit互換設定）、`schematics/`、`sessions/`。
   旧`WorldEdit/config.yml`があれば、FAWEが生成した`worldedit-config.yml`とキー単位で比較して
   必要な設定だけ移す。FAWEでは一部WorldEdit limitsが無視されるため、丸ごとの上書きはしない。
   旧`WorldEdit/schematics/`の必要なファイルは同名衝突を確認してFAWEの`schematics/`へコピーし、
   管理者で読み込みを確認する。旧設定・schematic・historyの自動移行成功は未確認。
4. 通常デプロイでmanifestと起動前処理を同時に反映し、完全再起動する。
   WorldEdit本体JARなし、FAWEのJARは1版だけ、全対象Pluginのenableをログとdescriptorで確認する。
   Paperが起動時に再生成するFAWEのremap cacheは2つ目のインストールとは数えない。
   コピーだけで有効化と判断せず、実際の読み込み先と起動ログを確認する。

ロールバックはPaperを正常停止して、旧plugins.txt / cleanup設定を戻す。
FAWEのJAR（`update/`とremap cacheも）をVolume外へ退避し、WorldEdit 7.4.5だけを戻す。
設定・World変更があれば同時点のバックアップへ戻して完全再起動する。FAWEとWorldEditを同居させない。

## 隔離起動結果

Paper **26.2 build 126** / Oracle GraalVM **Java 25.0.4**、localhost `127.0.0.1:25587`、
新規検証Worldで現行`plugins.txt`の全JARと固定ProtocolLibを起動した。
本番の秘密鍵・DB・プレイヤーデータはコピーせず、LuckPermsは隔離H2、Valhalla等は隔離SQLiteを使用。
Gun Core 1.0.15 / Modern Guns 1.9.3 / Bridge 0.3.0を含む現行`datapacks.txt`も配置した。
全対象Pluginのenable、`Done`、`stop`による正常停止（exit 0）を確認した。

| 対象 | 結果 |
| --- | --- |
| FAWE 2.16.0 | enable、Paper 26.2 adapter使用、WorldEdit本体なし |
| CraftBook 3.10.13 | enable、WorldEdit依存解決、永続YAML読み込み・保存 |
| ValhallaMMO 1.10.3 / Magic 11.2.4 | enable、Magicのデータ読み込み完了 |
| SCore / ExecutableItems / ImageFrame | enable |
| BreweryX / EssentialsX Core・Spawn / squaremap | enable |
| FancyNpcs / FancyHolograms | enable |
| FEATO Gun-Valhalla Bridge 0.3.0 | enable、Data Pack marker確認後FIREARMS登録 |
| FEATO Horsemanship 0.3.0 | enable、専用Skill/Profile登録 |
| FEATO Ancient Coin 1.1.0 / Coin Exchange 1.0.0 | enable、Vault Economy連携 |

CraftBookを含め、ClassNotFoundException / NoSuchMethodError / WorldEdit dependency missingは検出しなかった。
ただしenableだけでmechanicsの実操作互換性は確定しない。以下の手動項目は未確認。

検証環境の初回不備として、Data PackなしのBridge起動失敗、未ロードの仮想Playerに対する
LuckPerms/Vault lookup例外が出た。Data Pack配置とテストUUIDの事前loadで解消した。
最終試験ではPoC例外やBridge停止は解消し、以下の残存ログを調査した。

- Modern Guns由来`gbg:target` predicateの`minecraft:type`解析ERRORは、同じData Packを使う
  **旧WorldEdit 7.4.5の対照起動でも再現**した。FAWE置換由来ではない。修正は今回の対象外。
- Magicの`bubble`式評価とYAML duplicate keys、MineGamesのduplicate keys、
  EssentialsUnlocked版の不一致、BreweryXの未知のMinecraft版警告も旧WorldEdit対照で再現。
- 初回にFancyAnalyticsの外部event送信ERROR（HTTP status 200）があり、後続起動では再現しなかった。
  FancyNpcs / FancyHologramsはenableしたが、外部analyticsの成功は保証しない。
- localhostのoffline-mode、新規環境のresource pack host / MineSkin API keyなし、
  NPC / hologramデータなしの警告は隔離条件による。本番の接続経路や既存データの確認とは分ける。

最終PoCは全5ケースの消費・設置数・History・undoで`FAWE_INVENTORY_PROBE_SUCCESS`。
`stop`でexit 0、全World保存を確認した。起動ログ・生成データは隔離一時領域だけに保持する。

静的検証は`sh -n`（起動前処理・PoC build）、cleanupの実ループを使う
`python3 script/test_fawe_cleanup.py`（旧版のみ削除・データ保持・再実行）、
`docker compose --file deploys/app/compose.yml config --quiet`と
`docker stack config --compose-file deploys/app/compose.yml >/dev/null`、
変更記録validator、`git diff --check`を通過。Composeは検証用の環境変数を使い、秘密値は出力しない。

## Inventory API PoC

[`tests/fawe-inventory/`](tests/fawe-inventory/)に再実行可能な検証ソースを保持する。
本番manifestには追加せず、汎用コマンド・権限ノードは持たない。
明示的JVM opt-inと`fawe-test` Worldがない場合は自動的にdisableする。

実FAWE / 実Paper World / 実Bukkit ItemStackを使い、Bukkit Player / PlayerInventoryのみ
メモリ配列を使うtest doubleとした。接続中の実プレイヤー、packet反映、inventory競合は未検証。
一般プレイヤー同様に`isOp=false`のActorを使用し、LuckPermsへテストUUIDを事前loadする。
自前の資材徴収や数量事前判定を行わず、FAWEの`BukkitPlayerBlockBag`だけで消費させる。

- `BukkitAdapter.adapt(player)` → Actor、`actor.getInventoryBlockBag()` → Player由来BlockBag。
- `FaweLimit.MAX.copy()`を検証の基準にし、`INVENTORY_MODE = 2`と有限`MAX_CHANGES`を指定する。
  後続の本番実装では既存Actor limitをコピーし、有限上限・許可領域を施工条件に合わせて制限する。
- builderへ`.actor(actor).limit(limit).blockBag(bag).fastMode(false).changeSet(false, uuid)`を渡す。
  Historyが`BlockBagChangeSet`として有効であることをassertする。
- `.maxBlocks(n)`も指定するが、この版のFAWEでは**`limit.MAX_CHANGES`での制限が必要**。
  WorldEdit互換builderの`maxBlocks`だけに依存しない。
- `EditSession.close()`でqueueを完了し、`bag.flushChanges()`でinventoryへ反映する。
  `.combineStages(false)`を明示。fast mode / NullChangeSet / bypassHistory経由で消費を迂回しない。
- 設置後のWorld、残数、Historyの件数をassertする。Historyからのundoも別sessionで確認する。

| 所持STONE_BRICKS | 要求 / 上限 | 残数 | 実設置・History件数 |
| --- | --- | ---: | ---: |
| 64 | 10 / 10 | 54 | 10 |
| 64 + 32 | 80 / 80 | 16 | 80 |
| 5 | 10 / 10 | 0 | 5（不足時に停止） |
| 0 | 10 / 10 | 0 | 0 |
| 64 | 10 / 3 | 61 | 3（上限で停止） |

全ケース通過。無料設置は発生せず、History有効・有限上限の実効性を確認。
資材不足は全量rollbackではなく**所持数までの部分施工**になる。
後続BUILDINGでは部分施工の扱い、実Playerでのmain-thread inventory読取・flush、
施工中のinventory変更防止、session終了・例外時flushを実装・実機検証する。
全体設定の`inventory-mode`を変更せずsession単位で2を指定するため、CraftBookの施工消費仕様は変更しない。

再実行は停止した隔離Paperディレクトリに対し、Java 25で行う。

```sh
sh minecraft/java/tests/fawe-inventory/build.sh /absolute/isolated-paper /absolute/isolated-paper/plugins/FAWEInventoryProbe.jar
# server.properties: server-ip=127.0.0.1, level-name=fawe-test
# 起動先は本番WorldやVolumeを含まない隔離環境のみ
cd /absolute/isolated-paper
java -Dfeato.fawe.inventory-probe=true -Dterminal.jline=false -Dterminal.ansi=false -Xmx3G -jar paper.jar --nogui
# FAWE_INVENTORY_PROBE_SUCCESSを確認してconsoleからstop
```

PoC JARは試験後に隔離環境から取り外す。JAR、生成World、DB、ログはGitへ追加しない。

## 公開前の実機確認（未実施）

既存権限の管理者とSurvivalのテストPlayerを使い、バックアップ済み検証区域で行う。
一般グループの権限を変更せず、PoCや管理操作を本番の汎用コマンドとして公開しない。

| 項目 | 操作と確認 |
| --- | --- |
| WorldEdit互換 | 管理者で`//wand`、2点selection、`//set stone_bricks`、`//undo`。選択範囲・設置数・undo後のWorldを照合 |
| Survival inventory | 後続のPlayer接続用試験ハーネスで上記5ケースを実行。64→54、96→16、資材不足の部分施工、無料設置なしをinventoryとWorld双方で照合。Creative/OP bypassで済ませない |
| Bridge | 既存仕様の看板で作成、資材補充、開く・閉じる、Redstone両方向。資材数と復元ブロックを照合 |
| Gate | 作成、資材補充、開く・閉じる、Redstone両方向。資材数と復元ブロックを照合 |
| Chairs | 看板条件・着席・降りる・休憩回復が既存設定どおり |
| Elevator | 既存の上下階看板で往復し、移動先と権限を確認 |
| Pipes | 既存の吸入口・出口・filterを使って搬送し、資材消失・増殖なしを確認 |
| Minecart | Booster、Deposit、Elevator、Reverser、SpeedModifiers、Stationを既存路線で個別確認 |
| BetterPlants | 既存の栽培動作と権限を確認 |
| 他Plugin | Java/Bedrockログイン、MagicとValhallaスキル、EIアイテム、NPC・ホログラム、地図、経済連携を確認 |

Door / ToggleArea / Cauldron等のdisabled mechanicsは有効化しない。
本番反映・既存schematicのロード・実プレイヤー操作は未確認。
重大なFAWE置換由来の非互換は隔離検証で検出していないため、後続実装はGO。
公開時のruntime verificationは上表を別途完了させる。
