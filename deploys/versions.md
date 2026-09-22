# バージョン確認（2026-09-22）

公式リリース一覧・APIで安定版を確認し、Minecraft本体・プロキシ以外のコンテナは固定タグを指定しています。
nginxはMainlineではなくStable系列です。

| 対象 | 採用版 | 確認先 |
| --- | --- | --- |
| MariaDB | 13.0.2（Stable、rolling系列） | https://mariadb.org/mariadb/all-releases/ |
| nginx | 1.30.5（Stable） | https://nginx.org/en/download.html |
| Fluent Bit | 5.1.2 | https://github.com/fluent/fluent-bit/releases/tag/v5.1.2 |
| cAdvisor | 0.60.5（変更なし） | https://github.com/google/cadvisor/releases/tag/v0.60.5 |
| mc-monitor | 0.17.1 | https://github.com/itzg/mc-monitor/releases/tag/0.17.1 |
| Portainer Server / Agent | 2.45.1 | https://github.com/portainer/portainer/releases/tag/2.45.1 |
| cloudflared | 2026.9.1 | https://github.com/cloudflare/cloudflared/releases/tag/2026.9.1 |
| Certbot / DNS Cloudflare | 5.8.0（変更なし） | https://github.com/certbot/certbot/releases/tag/v5.8.0 |
| Minecraft server image | itzg/minecraft-server:java25-graalvm（公式イメージ） | https://docker-minecraft-server.readthedocs.io/en/latest/versions/java/ |
| Minecraft proxy image | itzg/mc-proxy:java25（公式HotSpotイメージ） | https://github.com/itzg/docker-mc-proxy/blob/main/README.md |
| Paper / Minecraft | 26.2 build 126（STABLE）、Java 25 | https://fill.papermc.io/v3/projects/paper/versions/26.2/builds/latest |

GitHub Release採用品は`releases/latest`の`prerelease=false`を確認しています。EssentialsXは26.2対応を優先し、公式CIの固定development buildを採用します。
Docker HubでMariaDB・nginx・Portainer・itzgの採用タグの存在も確認しました。
Java 25の要件: https://docs.papermc.io/paper/getting-started/

独自Bot `support-feato-system` は公開Releaseがないため既存の`main`を維持しています。
Velocity、Geyser、Floodgateは既存の公式イメージ取得方式を維持します。
Pluginのstable分類、26.2対応表、Java要件は下記で別々に記録します。

`.env`の`MINECRAFT_VERSION`は26.2の既定値より優先されます。
本番のサービス名は`minecraft-server`です。
既存の`minecraft_server_data` volume名は維持しています。
本番のMariaDB上限は1G、Minecraft上限は7G、最大ヒープは6Gです。

既存DBを11.4から更新する場合はバックアップと公式アップグレード手順が必要です。
既存ワールドも26.2への更新前にバックアップしてください。コンテナのロールバックだけでは
更新済みのDB・ワールドのデータ形式は元に戻りません。

Minecraftのjava25タグは更新されるため、再取得時にイメージの内容が変わります。

## GraalVM設定

本体は公式の`itzg/minecraft-server:java25-graalvm`を既定にし、自前ビルドは不要です。
プロキシは公式の`itzg/mc-proxy:java25`とG1GC最適化を使います。
Oracle版を使うのはMeowIceのGraalVMフラグがenterpriseコンパイラ設定を要求するためです。
https://www.graalvm.org/jdk25/getting-started/

公式のJavaバージョン表にはjava25-graalvmが掲載されていますが、images.jsonでは
`deprecated: true`です。タグの存在と継続的な更新は別のため、取得したイメージの
JavaバージョンとJVMフラグの動作をデプロイ前に確認してください。
https://docker-minecraft-server.readthedocs.io/en/latest/versions/java/
https://raw.githubusercontent.com/itzg/docker-minecraft-server/master/images.json

自前で更新版GraalVMを導入する必要がある場合だけ、`.env`に
`MINECRAFT_SERVER_IMAGE=it-infrastructure/minecraft-server:java25-graalvm`を指定し、
`./script/build_minecraft_graalvm.sh`を実行します。
複数ノードでは各ノードからpullできるレジストリのイメージ名を指定してビルドし、
本体のイメージをpushしてください。ビルドスクリプトは自動push・デプロイしません。

本体はAikarを無効にし、`USE_MEOWICE_FLAGS`と`USE_MEOWICE_GRAALVM_FLAGS`を有効化。
プロキシはこれらの変数をサポートしないため、`JVM_XX_OPTS`でG1GC、並列参照処理、
ヒープの事前確保、明示的GCの抑制、GC停止時間の目標200msを指定します。
小さい1Gヒープには本体用の16Mリージョン設定を流用せず、JVMの自動調整を使います。
両方ともメモリ上限とヒープの上限は従来値を維持します。
https://docker-minecraft-server.readthedocs.io/en/latest/configuration/jvm-options/#enable-meowices-flags
https://github.com/itzg/docker-mc-proxy/blob/main/README.md

公式イメージの更新時は再取得してください。性能向上は未計測のため、デプロイ後に
TPS/MSPT、GC停止時間、コンテナメモリとOOMの有無を比較してください。

本体のMeowIce設定に含まれるUseFastUnorderedTimeStampsとUseNUMAは、
VPSのハードウェア特性に依存するためJVM_OPTSで無効化します。
以前のローカル検証は自前ビルド（GraalVM 25.0.4、Graal Enterpriseコンパイラ）を対象とし、
本体のイメージ内スクリプトが生成するMeowIce/GraalVMフラグでのJVM起動を確認しました。
公式イメージでの起動確認と、上限内の実負荷検証はVPSで行います。

## プロキシのJava 25メモリ最適化

MeowIceの資料にはVelocity専用の設定はありません。
そのうち標準HotSpotのJava 25で使える`-XX:+UseCompactObjectHeaders`を追加し、
オブジェクトヘッダーのメモリ使用量を削減します。1Gヒープと自動リージョンサイズは維持します。
実際の削減量と処理速度はオブジェクトの構成・負荷に依存します。
Graal専用設定、400Mのコードキャッシュ、16Mリージョン、NUMA、HugePages、
CPU命令の強制指定はこのプロキシには適用しません。

https://github.com/MeowIce/meowice-flags
https://docs.oracle.com/en/java/javase/25/docs/specs/man/java.html

公式itzg/mc-proxy:java25でJVM起動とPrintFlagsFinalの
UseCompactObjectHeaders=trueを確認しています。実トラフィックでの性能は未計測です。
問題が出た場合はこのフラグを削除してプロキシを再デプロイしてください。

## Minecraft確定構成（2026-09-20）

Modrinth/GitHub/Paper公式APIでrelease、対応版、配置先loaderを確認し、GETしたJAR/ZIPのSHA-512を照合しました。
Java列は同梱クラスの最大バージョンに基づきます。Java 25起動、外部依存と組合せ互換性は
すべて Requires runtime verification。配布metadataの対応表と実際の動作保証は別です。

| Plugin名 | Version | Distribution | Platform | Minecraft | Stability | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| LuckPerms | v5.5.71-bukkit | [固定URL](https://cdn.modrinth.com/data/Vebnzrzj/versions/b0mk8uS6/LuckPerms-Bukkit-5.5.71.jar) | Paper | 26.2（配布metadata） | stable | 同梱Java 11以上; Requires runtime verification |
| LuckPerms | v5.5.71-velocity | [固定URL](https://cdn.modrinth.com/data/Vebnzrzj/versions/tamnmXad/LuckPerms-Velocity-5.5.71.jar) | Velocity | 26.2（配布metadata） | stable | 同梱Java 11以上; Requires runtime verification |
| LuckTags | 1.4 | [固定URL](https://cdn.modrinth.com/data/riEl5GDK/versions/mMmIwg51/lucktags-1.4.jar) | Paper | 26.2（配布metadata） | stable | 同梱Java 21以上; Requires runtime verification |
| ValhallaMMO | 1.10.3 | [固定URL](https://cdn.modrinth.com/data/rxrgsoud/versions/GkeSDJSq/ValhallaMMO_1.10.3.jar) | Paper | 26.2（配布metadata） | stable | 同梱Java 21以上; Requires runtime verification |
| Magic | 11.2.4 | [固定URL](https://mediafilez.forgecdn.net/files/8375/702/Magic-11.2.4.jar) | Paper | 26.2（公式配布対象） | stable | 公式ValhallaMMO integrationを使用; Requires runtime verification |
| SCore | 5.26.9.17 | [固定URL](https://cdn.modrinth.com/data/ZfcV7L06/versions/EHLoQYh8/SCore-5.26.9.17.jar) | Paper | 26.2（配布metadata） | stable | 同梱Java 8以上; Requires runtime verification |
| ExecutableItems | 7.26.9.17 | [固定URL](https://cdn.modrinth.com/data/g8Zwnnmn/versions/XrhxAt8x/ExecutableItems-7.26.9.17.jar) | Paper | 26.2（配布metadata） | stable | 同梱Java 8以上; Requires runtime verification |
| WorldEdit | 7.4.5 | [固定URL](https://cdn.modrinth.com/data/1u6JkXh5/versions/F5ea2ov3/worldedit-bukkit-7.4.5.jar) | Paper | 26.2（配布metadata） | stable | 同梱Java 25以上; Requires runtime verification |
| CraftBook | 3.10.13 | [固定URL](https://cdn.modrinth.com/data/jrO7z7l7/versions/6kl3GQSJ/craftbook-3.10.13.jar) | Paper | 26.2（配布metadata） | stable | 同梱Java 21以上; Requires runtime verification |
| ImageFrame | 2026.1.4 | [固定URL](https://cdn.modrinth.com/data/lJFOpcEj/versions/nt0GWT1y/ImageFrame-2026.1.4.0.jar) | Paper | 26.2（配布metadata） | stable | 同梱Java 21以上; Requires runtime verification |
| Backpack Plus | 3.2.0 | [固定URL](https://cdn.modrinth.com/data/lDAFcnRN/versions/vsRfbexG/BackpackPlus-3.2.0-all.jar) | Paper | 26.2（配布metadata） | stable | 同梱Java 21以上; Requires runtime verification |
| Enchants Plus | 1.6 | [固定URL](https://cdn.modrinth.com/data/N72bKhby/versions/oeMySJjE/Enchants%2B%20v1.6%201.21%20-%201.21.11.zip) | Data Pack | 26.2（配布metadata） | stable | Requires runtime verification |
| DeadChest | 4.30.0 | [固定URL](https://cdn.modrinth.com/data/pKqnV03Y/versions/mBSgqYZH/dead-chest-4.30.0.jar) | Paper | 配布metadataは26.1.2まで | stable | Paper 26.2で使用、実機テスト未実施; Requires runtime verification |
| Better Horses | 6.3 | [作者配布](https://www.spigotmc.org/resources/better-horses.124223/) | Paper | 26.2（作者tested一覧、起動確認） | stable | Spiget resource 124223から動的取得。ProtocolLibなしでは一部機能無効 |
| EssentialsX Core / Spawn | 2.22.1-dev+24-49a2f10（公式CI build 1829） | [Core](https://ci.ender.zone/job/EssentialsX/1829/artifact/jars/EssentialsX-2.22.1-dev+24-49a2f10.jar) / [Spawn](https://ci.ender.zone/job/EssentialsX/1829/artifact/jars/EssentialsXSpawn-2.22.1-dev+24-49a2f10.jar) | Paper | 26.2（現行公式support一覧） | development | 2.22.0 stableは26.1.2まで。Paper 26.2で起動確認 |
| VaultUnlocked | 2.20.3 | [固定URL](https://cdn.modrinth.com/data/ayRaM8J7/versions/qZgRzoYs/VaultUnlocked-2.20.3.jar) | Paper | 26.2（配布metadata） | stable | plugin名は`Vault`。Paper 26.2で起動確認 |
| EssentialsUnlocked | 1.0.0.1 | [固定URL](https://cdn.modrinth.com/data/gPLRdl3T/versions/fUaoKCyT/EssentialsUnlocked-1.0.0.1.jar) | Paper | 26.2（配布metadata） | stable | manifest versionは1.0.0.0。Paper 26.2で起動確認 |
| EconomyShopGUI Free | 7.2.1 | [作者配布](https://www.spigotmc.org/resources/economyshopgui.69927/) | Paper | 26.2（作者tested一覧） | stable | Paper 26.2でEssentialsX Economyへの接続確認。Spiget CDNは動的URL |
| FEATO Ancient Coin | 1.0.0 | [固定Release](https://github.com/FEATO-org/feato_ancient_coin/releases/tag/v1.0.0) | Paper | 26.2（plugin api-version） | stable release | GitHub latest release（draft=false、prerelease=false）。Paper 26.2で起動確認 |
| FEATO Coin Exchange | 1.1.0 | [公開予定Release](https://github.com/FEATO-org/feato-coin-exchange/releases/tag/v1.1.0) | Paper | 26.2（plugin api-version） | release pending | `FEATO-Coin-Exchange-1.1.0.jar`を取得対象として事前設定。data folderは`FEATOCoinExchange`、`exchange-value: 10.0` |
| FancyNpcs | 2.12.0 | [固定URL](https://cdn.modrinth.com/data/EeyAn23L/versions/53lykMXY/FancyNpcs-2.12.0.jar) | Paper | 26.2（配布metadata、起動確認） | stable | 依存なし。帰還札はplayer_command、古銭換金はconsole_command 1回を使用し、一時OPは禁止 |
| squaremap | 1.3.15 | [固定Release](https://github.com/jpenilla/squaremap/releases/tag/v1.3.15) | Paper | 26.2（api-version、起動確認） | stable | 内部Webサーバー8123、既存dynmap.feato.jp経路を再利用 |
| DualHorse | 1.5.4 | [固定URL](https://cdn.modrinth.com/data/mgoLZ3st/versions/9jTb2KHl/DualHorse-1.5.4.jar) | Paper | 配布metadataは26.1.2まで、26.2で起動確認 | stable | 26.2の実プレイヤー二人乗りとBetter Horses併用は要確認 |
| Velocity | 4.2.0 build 30 | [公式配布](https://papermc.io/downloads/velocity) | Velocity | 接続を実機検証 | stable（公式API STABLE） | VELOCITY_VERSIONとBUILD_IDで固定。JAR GETは403、Requires runtime verification |
| Geyser | 既存latest | [公式配布](https://download.geysermc.org/) | Velocity | 接続を実機検証 | 取得build要確認 | 既存方式維持、Requires runtime verification |
| Floodgate | 既存latest | [公式配布](https://download.geysermc.org/) | Velocity | 接続を実機検証 | 取得build要確認 | 既存UUID・username-prefix維持、Requires runtime verification |
| EmoteOffhand | latest（確認時 build 3） | [公式Downloads API](https://download.geysermc.org/v2/projects/emoteoffhand/versions/latest/builds/latest/downloads/emoteoffhand) | Geyser Extension（Velocity上のGeyser） | Geyser latest | dynamic build | `DOWNLOAD_EXTRA_CONFIGS`で`plugins/Geyser-Velocity/extensions`へ取得。Velocity Pluginとしては配置しない |
| Hurricane | latest（確認時 build 4） | [公式Downloads API](https://download.geysermc.org/v2/projects/hurricane/versions/latest/builds/latest/downloads/spigot) | Paper | 公式README表記は26.1まで | dynamic build | bamboo / pointed dripstone collisionのみ。Paper 26.2ではRequires runtime verification |

### GET検証済みSHA-512

| Distribution | SHA-512 |
| --- | --- |
| LuckPerms-Bukkit-5.5.71.jar | `188a91f0a543d23bfda32385fca6db63d61e49c8a422bd452a260bd9cbc6a7d7fe45071199e9fca8f3ce43c2b41ee84fd315bd15464577028ff3951a7d4fab27` |
| LuckPerms-Velocity-5.5.71.jar | `a619da8804727bed7b2b2ee5383974329a3c09181a67745484fdffd0f4b6c5b13c44aa88e0d2b30d13f3068d9b0f3e26863abba9855f80a7eb5f9455ca6c40d4` |
| lucktags-1.4.jar | `1052d2ea814da732d5e39447384df0427fd14c2e1f206441b3d71a5a65b10733bf30db983cc92e21079503687c9097310d43b237e388db7d8d1129fc56989855` |
| ValhallaMMO_1.10.3.jar | `e04a1e8f39e009e141fe8f07dd1eea85ad06c5850e63e5518618c316e3b4822179ab5bab571f1a5fc6ccf35c17de4baaae07c86e7fd9b374b6eb1f6cedd528a6` |
| Magic-11.2.4.jar | `4eb13cba74a534f6f58ef4dd4a301cac20f58299b4606ff2488c7fa7c4fc6dac69781449669acbef12a30b378771d474fdd58b9e4fa33defa59e9061aeed9e32` |
| SCore-5.26.9.17.jar | `7d023fa5973ca88acce406581eeb8378b2c14de9a77545d04f87ff79b3049de296f1d67eb0b442977b2e6b4fb5665ec344b8c274b7ccbda942fcc87fa72f57ee` |
| ExecutableItems-7.26.9.17.jar | `4d96fe9d62f8936fa9a471d118eaf4d18cee491da8f4a42bc438be8b2a85bd85a3d3508350dea48e92f2f99aae4f4602522117fea8329c802ebaef3b7e8be04d` |
| worldedit-bukkit-7.4.5.jar | `a383492fac6bfb4d43a257dfa7b5fc076aae503a71151b463de4fe80e6f3d5fc11209eaf4097baa115f3febf0adc40ca0a1ecda227b8439b429d0a4ba3a63a4f` |
| craftbook-3.10.13.jar | `04ff7ae4ddaf732951a882096e9d0744626e0449b6d6c24c2fa4f5af02ac5241b45c8992dcf4814153c5d1a3d01051a7bb6a42bd8102fea192ca93c8513addb3` |
| ImageFrame-2026.1.4.0.jar | `2a510fa5906e26331351fb69da6b19ca08d82ffb3ea34781cde8de44eed25a18e43862e6144a3bcbc8bf2184ee3a975fe65ee10689ff07039d23076fda35f58a` |
| BackpackPlus-3.2.0-all.jar | `e2385aab904864957ec1063f4faa9c553ad8e68604cb719a74b8a3a03c7459b628f82b10e7f4a56768ee77511129a0884bda7d4168074d26cec10448ce80ff5f` |
| EssentialsX-2.22.1-dev+24-49a2f10.jar | `11564dd426f55738507fe776dbc6cf644243f37289eb34e4cb6ac83960e1b565c93f0212332bea93d1a24990c88cfc0d94e23b0cf1dafbce0a27bde38605f7b8` |
| EssentialsXSpawn-2.22.1-dev+24-49a2f10.jar | `f634b55517cc3ee9d191a275bb9093552e3312aa5f54d1c35dfddd8f90c3f92f32c10cce9049b93e4d635fa0dfe986377e507b3f7b15e59e35f56d0a7035eef7` |
| VaultUnlocked-2.20.3.jar | `0eedea1591459e7e327315b43afa834a173c8c2ae31b3b235586d31963df29a4a6c0ef4b8f3fdc746e15afd47ee50c1ff93584543b5c2ef7c2a80135dba1136a` |
| EssentialsUnlocked-1.0.0.1.jar | `c271923c87e2a1e85011e3784141f50b848c4717f9c04c9279cc03d7aaafd79ddcf73abadfdb6aac0d964be818065ee510737365feed07a2309687aa533c85b9` |
| EconomyShopGUI-7.2.1.jar | `178c3d5e0d051be27008a5bf9ef2b69c74bf1be7a37f40f4b63046f6d520c4f886e7b94502dfc01893b97262feb56d674c4e8100352a36fa4fa6058409bf9114` |
| FEATO-Ancient-Coin-1.0.0.jar | `d4e7608d9d1f2614a6e420f3ee7e02a84b96e8c638cc9f5c6fa17f554aaaa99ef6af3d54a180a7002f0b87959ff249420c255a6bd48bfe8f81017d44e106e238` |
| FEATO-Coin-Exchange-1.1.0.jar | Release公開後にGitHub Release asset digestを記録 |
| FancyNpcs-2.12.0.jar | `f7a52c7e44d004e4235c12bf8d6936b25188ae7259b375d8b310b56538e724452805173e3781f9326c8fa794802f329c18416cbafccf5b5fab5016a628027399` |
| squaremap-paper-mc26.2-1.3.15.jar | `a6f00e0ea57268ed30b4aa2246b8ea3424f1210daab01bd47b217ec334199e792605f9419b7cfed7ed07cac20ad125593ddaf181c0ee72a129255563c75ab11e` |
| DualHorse-1.5.4.jar | `fd70684e9b3263bfc4edb9bde54a5fc1cc08c9f2ca4577434e2517dd7a3e5958029ebb0fd4090faa0545ae957531608cafe5452cb30d87f67344b28ac30e75d2` |
| BetterHorses-6.3.jar | `d54e921e073eec52dbe81542f0d06713bf1c217a645c4644caf410fcc08ebfa27723866d7de3803a2be7c3d4143c61943849dd9e959f312f8d465426d863e704` |
| Enchants+ v1.6 1.21 - 1.21.11.zip | `93e507c428287d7e8562a2ddd5a6488e47fcd76282426d683621c947f4fa8dda6a0ed605d458a1fed659ac5aa0909f01c8adb32994664788abe35fce0411083b` |
| dead-chest-4.30.0.jar | `1cc61288c1c530e0839f7060bd0f670a5b54b18dd70399ca50207ff973ad1f1b5a1effa5da52a18b9f6944ec784913b2798f59ea9b208d3f31643992681e1b9d` |

## 26.2追加構成の起動検証（2026-09-21）

Hurricane追加前に、Paper 26.2 build 126 / Java 25で全19 Pluginを同時に有効化し、正常停止を確認しました。FancyNpcs 2.12.0、squaremap 1.3.15、DualHorse 1.5.4、Better Horses 6.3を含みます。squaremapは8123番で起動し、ValhallaMMOはja-jp、Backpack Plusはjpn、EconomyShopGUIはlang-jp.ymlを読み込みました。ExecutableItemsはemergency_returnを含む追跡アイテム1件を読み込み、EconomyShopGUIはfeato_shop 1セクション/1ショップとEssentialsX Economy接続を確認しました。Hurricaneは公式READMEの対応表記が26.1までのため、Paper 26.2での起動ログと両collision workaroundの実機動作は未検証です。

Better HorsesはProtocolLibなしでも起動しますが一部機能を無効化します。DualHorseの配布metadataは26.1.2までのため、26.2では起動確認に加えて実プレイヤーで二人乗り、再接続、馬データ保存、Better Horsesとの併用を確認してください。NPCクリック、帰還札の100G徴収・1回消費・teleport、Java/Bedrock接続はクライアント試験が必要です。
