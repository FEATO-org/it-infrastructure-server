# Minecraft運用（2026-09-20）

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
                     ├ Backpack Plus
                     ├ EssentialsX / EssentialsX Spawn
                     ├ VaultUnlocked / EssentialsUnlocked
                     ├ EconomyShopGUI Free
                     └ FEATO Ancient Coin
Data Packs: Enchants Plus / KETKET'S Graves
Web: nginx dynmap.feato.jp -> Paper :8123 (対応Dynmapを待機)
```

Velocityは認証とJava/Bedrock接続、Paperはゲーム処理を担当します。
Geyser/FloodgateはVelocityだけに配置します。API依存が確認されていないため
PaperへFloodgateを追加しません。Velocity online-mode=true、modern forwarding、
forwarding secret、backend routing、Paperのoffline-modeを維持します。
Paper・MariaDB・Dynmapの直接publishはありません。既存暗号化overlay、Volumeを維持し、
DB接続のためVelocity/Paperだけdatabase-networkへ追加します。

**Paper 26.2で経済・spawn基盤とFEATO Ancient Coinを導入します。帰還札販売、古銭換金、Dynmap、DualHorse、Better Horsesは未稼働です。**
Paper 26.2 build 126（STABLE）と採用Pluginの起動をローカルで確認しました。採用版と対応範囲は[versions.md](../deploys/versions.md)を参照してください。

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

## Economy / Spawn / FEATO Ancient Coin

Economy ProviderはEssentialsXへ統一し、Vault API層にVaultUnlocked、橋渡しに
EssentialsUnlockedを使用します。XConomy / XConomy_Reload、旧Vault、SetSpawn、
Genius Shopは採用しません。初期残高は200G、通貨記号は金額の後ろに`G`を表示し、
負残高を禁止します。既存XConomy残高が本番Volumeや外部DBに存在する場合は削除せず、
旧環境でexportしてから移行表を作り、EssentialsXの`eco set`で管理者が反映してください。
自動変換処理はありません。

一般プレイヤーへ許可するEssentialsX権限は次の3つだけです。aliasも同じ権限ノードで制御されます。
`essentials.*`は付与しません。

```bash
lp group default permission set essentials.balance true
lp group default permission set essentials.pay true
lp group default permission set essentials.spawn true
```

`home`、`sethome`、`back`、`tpa`、`tpahere`、`tpaccept`、`tpdeny`、`tpacancel`、
`warp`、`setwarp`、`kit`、`nick`、`sudo`はEssentialsX設定でも無効化しています。
管理者の経済操作とspawn設定は必要な管理グループへ個別付与します。

```bash
lp group <admin-group> permission set essentials.balance.others true
lp group <admin-group> permission set essentials.eco true
lp group <admin-group> permission set essentials.setspawn true
```

EssentialsX Spawnの死亡respawn listenerは`none`、`spawn-on-join`は`false`です。
通常死亡はvanillaのbed / respawn anchorを使い、`/spawn`だけが管理者の
`/setspawn`で設定した本拠点へ移動します。初回導入後、本拠点で`/setspawn`を1回実行してください。

EssentialsXは公式の`ja`、EconomyShopGUIは同梱の`lang-jp.yml`と`ja-JP`を指定します。
Ancient Coinには言語設定がなく、SCore / ExecutableItemsの配布版にも日本語ロケールはありません。

EconomyShopGUI Free 7.2.1はVault APIを明示指定し、一般資源を含まない空の
`feato_exchange`だけを追跡します。Plugin既定ではsell系権限がtrueのため、
LuckPermsで明示的に拒否し、交換所だけを許可します。

```bash
lp group default permission set economyshopgui.sellall false
lp group default permission set economyshopgui.sellallitem false
lp group default permission set economyshopgui.sellallhand false
lp group default permission set economyshopgui.sellgui false
lp group default permission set economyshopgui.shop true
lp group default permission set economyshopgui.shop.all false
lp group default permission set economyshopgui.shop.feato_exchange true
```

FEATO Ancient Coin v0.2.0をPaper backendへ導入し、公式既定drop率を
`plugins/AncientCoin/config.yml`で管理します。v0.2.0は`api-version: 26.2`を宣言し、
Paper 26.2で起動確認済みです。古銭はGold Nuggetをbaseに、
`minecraft:custom_data={feato_coin:{id:"ancient_coin",schema:1}}`で識別されます。
Plugin自身は経済・換金・GUIを実装しません。旧Ancient Coin Data Packがworld内に存在する場合は、
二重抽選を避けるため停止中に退避してください。Enchants Plusは別Packなので維持します。

EconomyShopGUI Freeでは`components`/NBT、外部custom item provider、
`buy-commands`/`sell-commands`がPremium限定です。無料版のMaterial、name、Loreだけでは
通常Gold Nuggetや同名/Lore模倣品を安全に排除できないため、古銭の10G換金は設定しません。
安全に実現するには、AncientCoin Plugin自身がcustom dataを検証して1枚を消費し、
VaultUnlocked economyへ10Gを入金する換金処理を実装する案があります。設計変更は未実施です。

同じ制約により、EconomyShopGUI FreeからExecutableItemsの`emergency_return`を正しく配布する
custom item連携と購入時commandは利用できません。100Gの緊急帰還札商品は作らず、
名前だけ同じ無効アイテムの販売も行いません。ExecutableItems側に既存item設定はありません。
後続実装時はプレイヤー自身の`/spawn`権限で実行し、temp OPやconsole権限昇格を使わず、
価格100G、消費1個、cooldown/cast time 0、成功時だけ消費を検証してください。

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
- EssentialsX残高、初期200G、Java/Bedrock間 `/pay`、再接続で残高維持
- `/spawn`とvanilla bed/respawn anchorの分離
- EconomyShopGUIのVaultUnlocked接続と空の交換所、sell系権限拒否
- FEATO Ancient Coin drop、custom data維持、既存lootとの共存
- 帰還札購入/useと古銭10G換金（安全な実装追加後）
- Dynmap nginx公開（対応版導入後）、ImageFrame Bedrock rendering
- Backpack Plus Bedrock UI/mapping、既存backpackデータ保持
- Better Horses + DualHorse二人乗り/育成/保存（DualHorse対応版導入後）
- ValhallaMMO combat/mining/farming/smithing/alchemy、Enchants Plusとの組合せ
- KETKET'S Graves死亡/回収/次元移動、旧DeadChestからの移行
- CraftBook Elevator/Bridge/Gate/Pipes/Minecart booster/brake

公開情報だけではValhallaMMOとEnchants Plus、Better HorsesとDualHorse、Bedrock custom item等の
組合せ互換性を保証しません。競合する場合はworld/DBを保全して対象機能を停止してください。
CoreProtect、Cart Speed、BulletCartは導入しません。
Backpack容量/recipe、Dynmap visibility、一般商品、村長予算、古銭の安全な換金、帰還札販売、追加ICは未決定のままです。

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
- Plugin起動テスト: Paper 26.2 build 126で対象9 Pluginを有効化し、ERROR/Exceptionなし。AncientCoin 0.2.0、EssentialsX ja、EconomyShopGUI lang-jp.yml、Vault連携を確認: PASS
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
- `minecraft/java/plugins/AncientCoin/config.yml`
- `minecraft/java/plugins/EconomyShopGUI/config.yml`
- `minecraft/java/plugins/EconomyShopGUI/sections/feato_exchange.yml`
- `minecraft/java/plugins/EconomyShopGUI/shops/feato_exchange.yml`
- `minecraft/java/plugins/Essentials/config.yml`
- `minecraft/java/plugins/CraftBook/config.yml`
- `minecraft/java/plugins/LuckPerms/config.yml`
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
- `minecraft/templates/XConomy/config.yml`
- `minecraft/templates/XConomy/database.yml`
