# バージョン確認（2026-09-20）

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
| SCore | 5.26.9.17 | [固定URL](https://cdn.modrinth.com/data/ZfcV7L06/versions/EHLoQYh8/SCore-5.26.9.17.jar) | Paper | 26.2（配布metadata） | stable | 同梱Java 8以上; Requires runtime verification |
| ExecutableItems | 7.26.9.17 | [固定URL](https://cdn.modrinth.com/data/g8Zwnnmn/versions/XrhxAt8x/ExecutableItems-7.26.9.17.jar) | Paper | 26.2（配布metadata） | stable | 同梱Java 8以上; Requires runtime verification |
| WorldEdit | 7.4.5 | [固定URL](https://cdn.modrinth.com/data/1u6JkXh5/versions/F5ea2ov3/worldedit-bukkit-7.4.5.jar) | Paper | 26.2（配布metadata） | stable | 同梱Java 25以上; Requires runtime verification |
| CraftBook | 3.10.13 | [固定URL](https://cdn.modrinth.com/data/jrO7z7l7/versions/6kl3GQSJ/craftbook-3.10.13.jar) | Paper | 26.2（配布metadata） | stable | 同梱Java 21以上; Requires runtime verification |
| ImageFrame | 2026.1.4 | [固定URL](https://cdn.modrinth.com/data/lJFOpcEj/versions/nt0GWT1y/ImageFrame-2026.1.4.0.jar) | Paper | 26.2（配布metadata） | stable | 同梱Java 21以上; Requires runtime verification |
| Backpack Plus | 3.2.0 | [固定URL](https://cdn.modrinth.com/data/lDAFcnRN/versions/vsRfbexG/BackpackPlus-3.2.0-all.jar) | Paper | 26.2（配布metadata） | stable | 同梱Java 21以上; Requires runtime verification |
| Enchants Plus | 1.6 | [固定URL](https://cdn.modrinth.com/data/N72bKhby/versions/oeMySJjE/Enchants%2B%20v1.6%201.21%20-%201.21.11.zip) | Data Pack | 26.2（配布metadata） | stable | Requires runtime verification |
| KETKET'S Graves | 2.4 | [固定URL](https://cdn.modrinth.com/data/bYcfmIoG/versions/KL6JT1nQ/graves-v2.4.zip) | Data Pack | 26.2（配布metadata） | stable | Requires runtime verification |
| Better Horses | 未採用（候補6.3、取得は動的） | [作者配布](https://www.spigotmc.org/resources/better-horses.124223/) | Paper | 26.2（作者tested一覧） | stable | 確認後にBETTER_HORSES_SPIGET_RESOURCE=124223。固定release assetなし、GETは403。公開ソース6.2はJava 21、6.3のmanifestとJava 25をデプロイ前に確認 |
| EssentialsX Core / Spawn | 2.22.1-dev+24-49a2f10（公式CI build 1829） | [Core](https://ci.ender.zone/job/EssentialsX/1829/artifact/jars/EssentialsX-2.22.1-dev+24-49a2f10.jar) / [Spawn](https://ci.ender.zone/job/EssentialsX/1829/artifact/jars/EssentialsXSpawn-2.22.1-dev+24-49a2f10.jar) | Paper | 26.2（現行公式support一覧） | development | 2.22.0 stableは26.1.2まで。Paper 26.2で起動確認 |
| VaultUnlocked | 2.20.3 | [固定URL](https://cdn.modrinth.com/data/ayRaM8J7/versions/qZgRzoYs/VaultUnlocked-2.20.3.jar) | Paper | 26.2（配布metadata） | stable | plugin名は`Vault`。Paper 26.2で起動確認 |
| EssentialsUnlocked | 1.0.0.1 | [固定URL](https://cdn.modrinth.com/data/gPLRdl3T/versions/fUaoKCyT/EssentialsUnlocked-1.0.0.1.jar) | Paper | 26.2（配布metadata） | stable | manifest versionは1.0.0.0。Paper 26.2で起動確認 |
| EconomyShopGUI Free | 7.2.1 | [作者配布](https://www.spigotmc.org/resources/economyshopgui.69927/) | Paper | 26.2（作者tested一覧） | stable | Paper 26.2でEssentialsX Economyへの接続確認。Spiget CDNは動的URL |
| FEATO Ancient Coin | 0.2.0 | [固定Release](https://github.com/FEATO-org/feato_ancient_coin/releases/tag/v0.2.0) | Paper | 26.2（plugin api-version） | stable release | draft=false、prerelease=false。Paper 26.2で起動確認 |
| Dynmap | 未採用 | [公式release](https://github.com/webbukkit/dynmap/releases) | Paper | 26.2未確認 | 対応stable未確認 | [対応PR #4271](https://github.com/webbukkit/dynmap/pull/4271)は未マージ。設定・nginx経路維持 |
| DualHorse | 未採用（候補1.5.4） | [公式配布](https://modrinth.com/plugin/dualhorse/versions) | Paper | 26.1–26.1.2 | stable | 26.2未確認。Better Horsesとの併用は Requires runtime verification |
| Velocity | 4.2.0 build 30 | [公式配布](https://papermc.io/downloads/velocity) | Velocity | 接続を実機検証 | stable（公式API STABLE） | VELOCITY_VERSIONとBUILD_IDで固定。JAR GETは403、Requires runtime verification |
| Geyser | 既存latest | [公式配布](https://download.geysermc.org/) | Velocity | 接続を実機検証 | 取得build要確認 | 既存方式維持、Requires runtime verification |
| Floodgate | 既存latest | [公式配布](https://download.geysermc.org/) | Velocity | 接続を実機検証 | 取得build要確認 | 既存UUID・username-prefix維持、Requires runtime verification |

### GET検証済みSHA-512

| Distribution | SHA-512 |
| --- | --- |
| LuckPerms-Bukkit-5.5.71.jar | `188a91f0a543d23bfda32385fca6db63d61e49c8a422bd452a260bd9cbc6a7d7fe45071199e9fca8f3ce43c2b41ee84fd315bd15464577028ff3951a7d4fab27` |
| LuckPerms-Velocity-5.5.71.jar | `a619da8804727bed7b2b2ee5383974329a3c09181a67745484fdffd0f4b6c5b13c44aa88e0d2b30d13f3068d9b0f3e26863abba9855f80a7eb5f9455ca6c40d4` |
| lucktags-1.4.jar | `1052d2ea814da732d5e39447384df0427fd14c2e1f206441b3d71a5a65b10733bf30db983cc92e21079503687c9097310d43b237e388db7d8d1129fc56989855` |
| ValhallaMMO_1.10.3.jar | `e04a1e8f39e009e141fe8f07dd1eea85ad06c5850e63e5518618c316e3b4822179ab5bab571f1a5fc6ccf35c17de4baaae07c86e7fd9b374b6eb1f6cedd528a6` |
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
| FEATO-Ancient-Coin-0.2.0.jar | `b48305f6918df47070e6b6ceea1e4326a120a18f713f2bd221f4e75db71b047b5c0f3bf08c247aa671ef8eb2be1dc5db641146dd768537d3c98a398652e5a183` |
| Enchants+ v1.6 1.21 - 1.21.11.zip | `93e507c428287d7e8562a2ddd5a6488e47fcd76282426d683621c947f4fa8dda6a0ed605d458a1fed659ac5aa0909f01c8adb32994664788abe35fce0411083b` |
| graves-v2.4.zip | `ec11eb415c3108fa2741d32331a35328122a1d0f34eafb7885ca7cee8d93606d2c65c44b7f93fea02b57eb6bfe00f3fb96bc526c343d8329e65050e351819b8b` |
