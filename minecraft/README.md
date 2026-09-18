# Minecraft運用（2026-09-18）

## Architecture

```text
Internet (Java TCP 25565 / Bedrock UDP 19132)
  -> nginx -> Velocity :25577
                ├ Geyser-Velocity
                ├ Floodgate (既存 username-prefix: b-)
                └ LuckPerms ───────────┐
                     │ modern forwarding
                     ▼                │
                   Paper :25565       │
                     ├ LuckPerms ─────┴-> MariaDB / luckperms
                     ├ LuckTags
                     ├ ValhallaMMO (Alchemy含む)
                     ├ SCore / ExecutableItems
                     ├ WorldEdit / CraftBook
                     ├ ImageFrame
                     ├ Better Horses (取得検証後に有効化)
                     └ Backpack Plus
Data Packs: Enchants Plus / KETKET'S Graves
Web: nginx dynmap.feato.jp -> Paper :8123 (対応Dynmapを待機)
```

Velocityは認証とJava/Bedrock接続、Paperはゲーム処理を担当します。
Geyser/FloodgateはVelocityだけに配置します。API依存が確認されていないため
PaperへFloodgateを追加しません。Velocity online-mode=true、modern forwarding、
forwarding secret、backend routing、Paperのoffline-modeを維持します。
Paper・MariaDB・Dynmapの直接publishはありません。既存暗号化overlay、Volumeを維持し、
DB接続のためVelocity/Paperだけdatabase-networkへ追加します。

**この変更は確定構成の対応確認済み部分です。ショップ、帰還札、Dynmap、DualHorse、Better Horsesは未稼働です。**
安定版と26.2、Java 25を別々に確認した結果は[versions.md](../deploys/versions.md)を参照してください。
Vault / XConomyは26.2未確認、Genius Shopはbeta、SetSpawn 3.2はJava 26必須、
Dynmapは26.2対応stable未確認、DualHorse 1.5.4は26.1までのため自動取得に含めません。

## LuckPerms / Database / Secrets

Velocity/Paperは共通DB `luckperms`、専用ユーザー `luckperms`、同じtable-prefixを参照します。
SQL messagingとauto-pushを双方に設定し、Redisを追加しません。
反映はSQL pollingによるためゼロ遅延保証ではありません。両コンソールで `/lp info` と
変更後の権限反映を確認します。Velocityでは `/lpv info` を使用します。
DB権限は当該DB内のSELECT/INSERT/UPDATE/DELETE/CREATE/ALTER/INDEX/DROPのみです。
rootや既存appアカウントをPluginへ渡しません。

managerで追加secretを一度作成します（実値を引数・Gitへ保存しない）。

```bash
openssl rand -base64 48 | docker secret create luckperms_db_password -
```

itzg公式のconfig sync/interpolationと`CFG_LUCKPERMS_PASSWORD_FILE`を使用します。
置換先はVolume内だけです。LuckPermsに直接secretファイルを解釈させる設定ではありません。
Volume内の置換済み設定とバックアップも秘密情報を含むためアクセスを制限してください。
secretの変更だけでは既存DBユーザーのpasswordは更新されません。再実行は既存ユーザーを
上書きしません。rotationはDB/secret/両サービスの整合を別途計画してください。

## Deploy前の移行

本番deploymentはこの作業では実行していません。
最初にappを停止し、Minecraft/Proxy VolumeとMariaDBの整合したバックアップを取得します。
既存LuckPermsを使っていた場合は権限データのexport/importが必要です。
world、playerdata、whitelist、ban、ops、stats、advancements、Floodgate key、Dynmap tiles、
MariaDBデータは削除しません。

既存Volume内の旧JARは、URLやSPIGET_RESOURCESを変更しても必ずしも削除されません。
停止中に `/data/plugins` と `/server/plugins` のJARを一覧し、採用一覧以外を
Volume外の保護されたバックアップ先へ移動してください。同名旧版JARも退避し、
同じPluginを複数取得しないでください。旧Pluginのユーザーデータは保存してください。
旧DeadChestの未回収チェストは撤去前に回収/復旧してください。

旧Data Packもworld内のdatapacksへコピー済みの場合は自動削除されません。
停止中にworld/datapacksを確認し、FTMC Bullet Cart / Speedometer / Railway Builder、
extended-enchants / higherenchantsと採用外Packを退避してください。独自Data Packは
今回開発しません。ignoredな既存アセット自体はローカルに保存したままです。
今後の追加mountは `minecraft/java/datapacks/` に変更し、旧アセットを再導入しません。

全minecraft-dataノードとdatabase-dataノードへリポジトリを同じ絶対pathで配置します。
DBノードにもinitスクリプトのbind mountが必要です。
既存[deploy手順](../deploys/README.md)で環境変数とTLS_STATE_FILEを読み込み、
先にsystemだけを更新して新secretとinitスクリプトをMariaDBへmountします。
この更新にはMariaDBの再起動が伴います。DBイメージupgradeは今回行わず、既存採用版を維持します。

```bash
# manager: 既存.envとTLS状態を読み込んだ環境で実行
export DEPLOY_ROOT=/opt/it-infrastructure-server
docker compose -f deploys/system/compose.yml config --quiet
docker stack config -c deploys/system/compose.yml >/dev/null
docker stack deploy -c deploys/system/compose.yml --with-registry-auth system
```

新規DB Volumeではinitdbが専用DB/userを作成します。
既存DB Volumeではinitdbが走らないため、MariaDBのタスクが動くdatabase-dataノードで
healthを確認後、明示的に実行します。データの削除/upgradeを行わずDB/userを追加します。

```bash
container_id=$(docker ps -q --filter label=com.docker.swarm.service.name=system_mariadb)
# 1タスクだけ存在することを確認して実行
test -n "$container_id"
docker exec "$container_id" bash /docker-entrypoint-initdb.d/20-luckperms.sh
```

DB準備後、managerから既存の `./script/deploy_swarm.sh` を実行します。
secret、ComposeとSwarm stack configを検査してから既存3スタックを更新します。
通常デプロイがappから始まるため、上記のsystem先行とDB作成を省略しないでください。
ゲームクライアントへ公開する前に以下のRuntime checklistを確認してください。

## Plugin / Data Packの更新

Paperの固定URLは `minecraft/java/plugins.txt`、VelocityのLuckPermsはapp composeです。
Better Horsesは取得検証後に `.env` へ `BETTER_HORSES_SPIGET_RESOURCE=124223` を設定し、
作者Spigot resource 124223を既存Spiget経由で取得します。既定では取得を無効化しています。
調査時点6.3ですがGETは403でmanifest未検証、公開ソース6.2はJava 21です。
デプロイ前に公式配布から取得してversionとJava 25、任意依存を確認してください。
取得不能なら非公式mirrorを使わず、そのPluginを保留してください。
Velocity 4.2.0 build 30を固定し、Geyser/Floodgateは既存公式latest方式を維持します。
調査時点Geyser 2.11.3 build 1245、Floodgate 2.2.5 build 141（promoted=false）です。
これらをstableと断定せず、更新時に取得channel、クライアント対応、起動を再確認します。

Data Packはapp composeの `DATAPACKS` の固定ZIP URLからitzgが取得します。
Enchants Plus 1.6とKETKET'S Graves 2.4を改変せず使います。
ZIP名に古いMinecraft版が含まれますが配布metadataは26.2を含みます。
pack.mcmetaはEnchants Plusが48–9999とversion別overlay、Gravesが94.1–107.1を宣言しています。
ZIP内部のmanifest/function配置は確認済みですが、26.2でのロードと挙動は実機確認してください。
更新時は取得URL、対応表、stable、Java要件、hash、依存を再確認してversions.mdも更新します。
動的JAR/ZIP、runtime DB、world、logs、cache、backup、生成tilesをGitへ追加しません。
追加のローカルZIP/mcpack転送には `REMOTE_HOST` と必要なら `REMOTE_DEPLOY_ROOT` を設定して
`script/copy_plugins_to_remote.sh` を使用します。転送先directoryは先に用意してください。
旧resources/datapacksは転送しません。

## Economy / 緊急帰還札（対応版待機）

XConomyの待機templateは `minecraft/templates/XConomy/` に置き、mountしません。
初期残高200G、通貨G、UUID-mode=Default、単一PaperのためSyncData無効です。
Floodgateの既存prefix `b-` を維持します。prefixが空の場合のSemiOnlineは使いません。
導入時は専用DB/user `xconomy` と `xconomy_db_password` を追加し、既存app/LP資格情報を
共有しないでください。現時点ではXConomy DB/user/secretは作成しません。

Genius Shopは管理者の限定ショップとし、一般資源の大量販売や万能ショップは作りません。
目標は商品ID `emergency_return`、ExecutableItems item ID `emergency_return`、価格100G、
購入1回につき公式 `ei give <player> emergency_return 1` コマンドで1個配布です。
現在このitemは存在せず、このテストコマンドは後続の有効化後だけ使用します。

帰還札はright click/useでSetSpawnの本拠点へ移動し、**転送成功時だけ1個消費**します。
単純な `spawn` コマンドとEI usage消費の連結では、spawn未設定/権限拒否/転送失敗時も
消費する恐れがあり、公式で成功判定できる方法を確認するまで実行設定を作りません。
購入成功・失敗時の引落しと配布も二重処理/無料配布がないことを検証してから販売開始します。
cooldown、teleport delay、cast time、damage/movement cancel、combat restrictionは追加しません。

SetSpawn対応版の導入後、管理者が帰還先で `/setspawn` を実行します。
座標はGitで決めません。公式configの `cooldown-time` と `countdown-time` を0にし、
座標を含む生成config全体を毎起動上書きせず、必要なキーのみ変更します。
`/spawn` とベッド死亡respawnを別々に確認し、全員を本拠点へ強制respawnさせません。
Java/Bedrock両方で残高200G→購入100G→札1個→使用→成功時だけ札0個を確認します。
100G未満、spawn未設定、権限拒否、転送失敗、連続use、満杯inventoryもテストします。

## 権限 / その他設定

LuckTagsはPaperだけでprefix/suffixを表示します。`[村長]` は役職表示であり管理権限ではありません。
役職metaとpermissionを分離し、今回特定ユーザーへ付与しません。
ValhallaMMOは公式defaultを使い、追加Potion Pluginや独自翻訳を作成しません。
CraftBookはElevator/Bridge/Gate/MinecartBooster/MinecartSpeedModifiers/Pipesだけ有効にし、
Chairsと全機能有効化は行いません。BrakeはMinecartSpeedModifiersの公式設定を確認します。
基本Redstone ICは対象ICを管理者が確認後に有効化するTODOです。ProtocolLibは追加しません。

Backpack Plusは旧生成configを外し公式defaultへ戻します。容量/recipeは未確定です。
既存Volume内configは自動削除しないのでバックアップし、新版defaultと差分を確認してください。
容量・recipeは生成configと `/backpack settings <tier>`、`/backpack crafting` で管理します。
Bedrock resource pack/mappingは公式提供・対応確認後に既存Geyser packsへ統合するTODOです。
独自変換pipelineは作成しません。

Dynmapは既存configuration/templatesとnginx/web-ingress経路を保存します。
対応stableを導入するまでは https://dynmap.feato.jp は稼働保証できません。
player marker/location、cave map、hidden/visibility、map detailは現状維持で変更は管理者TODOです。

## Runtime checklist / rollback

すべて Requires runtime verification:

- Velocity/Paper起動、依存errorなし、forwarding、backend登録、Geyser/Floodgate load
- Java/Bedrock login、Floodgate UUID/prefix/再接続・link時のidentity
- LuckPerms DB接続、両側権限同期、LuckTags prefixと管理権限の分離
- XConomy残高、Java/Bedrock間 `/pay`、再接続で残高維持（対応版導入後）
- Genius Shop購入、帰還札購入/use/失敗時非消費、bed spawn維持（対応版導入後）
- Dynmap nginx公開（対応版導入後）、ImageFrame Bedrock rendering
- Backpack Plus Bedrock UI/mapping、既存backpackデータ保持
- Better Horses + DualHorse二人乗り/育成/保存（DualHorse対応版導入後）
- ValhallaMMO combat/mining/farming/smithing/alchemy、Enchants Plusとの組合せ
- KETKET'S Graves死亡/回収/次元移動、旧DeadChestからの移行
- CraftBook Elevator/Bridge/Gate/Pipes/Minecart booster/brake

公開情報だけではValhallaMMOとEnchants Plus、Better HorsesとDualHorse、Bedrock custom item等の
組合せ互換性を保証しません。競合する場合はworld/DBを保全して対象機能を停止してください。
CoreProtect、Cart Speed、BulletCart、FEATO Ancient Coinは導入しません。
Backpack容量/recipe、Dynmap visibility、一般商品、村長予算、古銭、追加ICは未決定のままです。

rollbackは旧Git設定/イメージ/JAR/Packと秘密情報を揃え、停止中に整合したVolume/DB backupから
復元します。`docker service rollback` だけでは変更済みDB、world、Plugin dataは戻りません。
追加DB/user/secretは自動削除せず、旧secretも復旧用に保持してください。


## 実装時のValidation

- 全対象YAML/TOML parse、3スタックCompose parseとSwarm stack config: PASS
- secret/network/volume/mount参照、非公開配置、共有DB、旧config整理、重複URL: PASS
- 固定JAR/ZIPをGET、SHA-512照合、Plugin manifestと同梱Java class major確認: PASS
- Paper/Velocity公式イメージのsecretファイル置換: network=none・架空値でPASS
- 専用DB初期化/再実行、必要DDL/DML、system DB/global CREATE拒否: PASS
  （MariaDB 12.0.2、network=none、架空値。本番13.0.2の起動は未検証）
- Velocity固定版: 公式APIで4.2.0 build 30/channel STABLE確認、JAR GETは403で未検証
- Bash構文、git diff --check: PASS
- Better HorsesのGET: 403、manifestは未検証
- Plugin起動テスト: 自動承認レビューがネットワーク下の外部Plugin実行を拒否したため未実行
- 本番deployment、DNS変更、既存DB migration: 未実行

Swarm config検証はローカル旧CLIに当該コマンドがないため、公式Docker CLI 29.8.0を
一時directoryから使用しました。インストール済みDockerは変更していません。

## 変更ファイル一覧

- `.gitignore`
- `README.md`
- `deploys/README.md`
- `deploys/app/compose.yml`
- `deploys/system/compose.yml`
- `deploys/system/mariadb/init-luckperms.sh`
- `deploys/versions.md`
- `minecraft/README.md`
- `minecraft/java/plugins.txt`
- `minecraft/java/plugins/CraftBook/config.yml`
- `minecraft/java/plugins/LuckPerms/config.yml`
- `minecraft/templates/XConomy/config.yml`
- `minecraft/templates/XConomy/database.yml`
- `minecraft-proxy/config/plugins/LuckPerms/config.yml`
- `minecraft-proxy/plugins/Geyser-Velocity/config.yml`
- `script/deploy_swarm.sh`
- `script/copy_plugins_to_remote.sh`

削除/移動元:

- `minecraft/java/plugins/BackpackPlus/config.yml`
- `minecraft/java/plugins/BetterChairs/config.yml`
- `minecraft/java/plugins/BetterChairs/messages.yml`
- `minecraft/java/plugins/DeadChest/config.yml`
- `minecraft/java/plugins/HorseEnhancer/config.yml`
- `minecraft/java/plugins/NewGods/config.yml`
- `minecraft/java/plugins/SimplyFarming/config.yml`
- `minecraft-proxy/plugins/Geyser-Spigot/config.yml`（Geyser-Velocityへ内容保持して移動）
