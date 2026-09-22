# Minecraft運用（Paper 26.2）

## 構成

```text
Java TCP 25565 / Bedrock UDP 19132
  -> nginx -> Velocity 4.2.0
                ├ Geyser-Velocity
                ├ Floodgate
                └ LuckPerms
                     │ modern forwarding
                     ▼
                   Paper 26.2 build 126
                     ├ LuckPerms / LuckTags
                     ├ EssentialsX Core / Spawn
                     ├ VaultUnlocked / EssentialsUnlocked
                     ├ EconomyShopGUI Free
                     ├ FancyNpcs
                     ├ squaremap :8123
                     ├ ValhallaMMO
                     ├ SCore / ExecutableItems
                     ├ WorldEdit / CraftBook
                     ├ ImageFrame
                     ├ Better Horses / DualHorse
                     ├ Backpack Plus
                     ├ DeadChest 4.30.0
                     └ FEATO Ancient Coin
Data Packs: Enchants Plus
Web: nginx dynmap.feato.jp -> squaremap :8123
```

対象バージョンは26.2です。`.env`の`MINECRAFT_VERSION`が既定値を上書きするため、デプロイ前に26.2であることを確認してください。

GeyserとFloodgateはVelocityへ配置します。Paper側へFloodgate APIを要求するプラグインは今回ありません。Velocityのオンライン認証、modern forwarding、共有secret、Paperのoffline modeを維持します。Paper、MariaDB、squaremapはホストへ直接公開しません。

## 採用Plugin

Paper側の取得URLは[plugins.txt](java/plugins.txt)、詳細な版・配布元・ハッシュは[versions.md](../deploys/versions.md)で管理します。

- 権限・表示: LuckPerms、LuckTags
- 経済・基本機能: EssentialsX Core / Spawn、VaultUnlocked、EssentialsUnlocked
- 商店・NPC: EconomyShopGUI Free、FancyNpcs
- マップ: squaremap
- RPG・アイテム: ValhallaMMO、SCore、ExecutableItems
- 建築・表示: WorldEdit、CraftBook、ImageFrame
- 馬・収納: Better Horses、DualHorse、Backpack Plus
- 死亡時保護: DeadChest 4.30.0
- 独自機能: FEATO Ancient Coin 0.2.0

DeadChest 4.30.0をPaper 26.2環境で使用します。公式の対応表記は26.1.xまでで、
Paper 26.2での実機テストは未実施です。

旧Vault、XConomy、XConomy_Reload、SetSpawn、Genius Shop、Dynmapは採用しません。既存VolumeからJARが自動削除されるとは限らないため、停止中に退避してください。Dynmapのタイルはバックアップ後に残して構いませんが、squaremapは別形式で再描画します。

## 日本語化

- EssentialsX: `locale: ja`
- EconomyShopGUI: `lang-jp.yml`、通貨ロケール`ja-JP`
- ValhallaMMO: `language: ja-jp`。Gistを原本として追跡
- Backpack Plus: 公式同梱`jpn`ロケール
- Better Horses: 追跡する`language.yml`を日本語化
- AncientCoin: 表示文言はPlugin設定で日本語
- FancyNpcs、squaremap、SCore、ExecutableItems、DualHorseは採用版に公式日本語ロケールがありません

ValhallaMMOの訳は、JAR内英語原本とキー・配列・名前付きプレースホルダーが一致する場合だけ更新します。

```bash
./script/sync_valhallammo_ja.sh /path/to/ValhallaMMO_1.10.3.jar
```

この処理は[日本語Gist](https://gist.github.com/LenTakayama/e8f65dbce8e58baec96c8554a4eba4e5)を一時領域へ取得し、[検証スクリプト](../script/validate_valhallammo_translation.py)を通過してから置換します。

## 経済と通常商店

経済ProviderはEssentialsX、Vault API層はVaultUnlocked、橋渡しはEssentialsUnlockedです。初期残高200G、通貨記号は金額の後ろ、負残高は禁止です。

`/shop`の`feato_shop`に次の商品を設定しています。価格は`minecraft/java/plugins/EconomyShopGUI/shops/feato_shop.yml`で変更します。

| 商品 | 取引 | 数量 | 価格 |
| --- | --- | ---: | ---: |
| Name Tag | 購入 | 1 | 150G |
| Saddle | 購入 | 1 | 200G |
| Lead | 購入 | 2 | 80G |
| Oxidized Copper | 購入 | 16 | 250G |
| Player Head | 購入 | 1 | 200G |
| Poisonous Potato | 売却 | 64以上 | 64個あたり10G |

EconomyShopGUIでは`stack-size`の価格がスタック全体へ適用されます。`min-sell: 64`で64個未満の売却を拒否します。65個以上はPluginの数量計算に従うため、64個単位だけに厳密制限する設定ではありません。

## 緊急帰還札

ExecutableItemsの`emergency_return`を右クリックすると、EssentialsX Spawnで本拠点へ移動し、使用回数を1減らします。販売はEssentialsX kit `return_ticket`で行い、`kit-return_ticket: 100`により100Gを徴収します。一般プレイヤーへ`essentials.spawn`は与えません。

本拠点で管理者が一度`/setspawn`を実行してください。帰還札NPCは、その位置に立って次を実行します。

```text
/npc create return_ticket_vendor
/npc displayname return_ticket_vendor <gold>緊急帰還札</gold>
/npc interaction_cooldown return_ticket_vendor 1s
/npc action return_ticket_vendor RIGHT_CLICK add need_permission essentials.kits.return_ticket
/npc action return_ticket_vendor RIGHT_CLICK add player_command kit return_ticket
```

FancyNpcsの`player_command_as_op`は使用しません。価格徴収、EIアイテム発行、右クリック時の消費はJava版とBedrock版の実プレイヤーで公開前に確認してください。

## FEATO Ancient Coinの換金

AncientCoin 0.2.0は、`minecraft:custom_data={feato_coin:{id:"ancient_coin",schema:1}}`で正規品を識別しますが、換金処理を持ちません。EconomyShopGUI FreeはPDC/custom data照合に対応せず、FancyNpcsにもPDC条件や原子的なアイテム消費・入金処理はありません。このため、偽造防止要件を満たさない古銭10G換金は有効化していません。

安全な実装はAncientCoinへ単一コマンドを追加する方式です。そのコマンド内でメインスレッド上にてPDCを検証し、1枚だけ減らし、Vaultへ10G入金し、入金失敗時はアイテムを復元します。実装後、NPCにはその1コマンドだけを`player_command`として登録します。それまでは案内NPCだけを作成できます。

```text
/npc create ancient_coin_trader
/npc displayname ancient_coin_trader <gold>古銭商</gold>
/npc action ancient_coin_trader RIGHT_CLICK add message <yellow>古銭の換金は現在準備中です。</yellow>
```

## LuckPerms

既存グループ名を`default`と仮定しません。Paperタスクが動くminecraft-dataノードで、一般・管理グループ名を明示して実行します。

```bash
./script/setup_minecraft_permissions.sh <player-group> <admin-group>
```

スクリプトは一般グループへ残高確認、送金、帰還札kit、EIアイテム使用、FEATO商店だけを許可し、一般`/spawn`とEconomyShopGUIの一括売却コマンドを拒否します。管理グループへ経済、spawn、kit、商店編集、NPC作成と必要なaction種別を個別付与します。ワイルドカード権限、prefix、suffix、継承は変更しません。

LuckPermsはVelocity/Paper共通MariaDBを使います。SQL messagingによる反映のため、両側で`/lp info`、Velocityで`/lpv info`を確認します。

## squaremap

squaremap 1.3.15をPaper 26.2用JARで導入し、内部Webサーバーを8123番で起動します。既存の`dynmap.feato.jp`とnginx経路を再利用するためDNS変更は不要です。このホスト名は互換性維持のため残した名称で、表示内容はsquaremapです。

初回公開前に管理者が対象ワールドを指定してfull renderを実行し、CPU、メモリ、ディスク使用量を監視してください。プレイヤー位置、洞窟や非公開領域の表示方針も公開前に確認します。

## デプロイ前後

1. appを停止し、Minecraft/Proxy VolumeとMariaDBを整合した状態でバックアップします。
2. Volume内の旧JARを確認し、旧Vault、XConomy、SetSpawn、Genius Shop、Dynmapと重複版をVolume外へ退避します。
3. 旧Data PackとAncient Coin Data Packを確認し、二重抽選を避けて退避します。
4. Compose/Swarm設定を検証してデプロイします。
5. `setup_minecraft_permissions.sh`を実グループ名で実行し、本拠点で`/setspawn`、NPC作成を行います。
6. Java/Bedrock両方で商店、残高、帰還札、馬、Backpack、AncientCoin drop、squaremap表示を確認します。

ローカルではPaper 26.2 build 126 / Java 25で19 Pluginをすべて有効化し、正常停止まで確認しました。確認できた内容は、設定読込、依存解決、コマンド登録、squaremap 8123起動、ValhallaMMO `ja-jp`、Backpack Plus `jpn`、EI 1アイテム、EconomyShopGUI 1セクション/1ショップ、VaultとEssentialsX Economy連携です。

クライアント操作が必要なJava/Bedrockログイン、NPCクリック、100G徴収、帰還札の消費とteleport、商品売買、馬の二人乗り、各Data Pack、古銭dropは本番公開前の実機確認事項です。Better HorsesはProtocolLibなしでも起動しますが、一部機能が無効になるという通知があります。今回ProtocolLibは追加していません。
