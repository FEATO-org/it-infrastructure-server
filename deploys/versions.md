# バージョン確認（2026-09-22）

## CraftBook Chairs有効化（2026-10-04）

CraftBook 3.10.13 / WorldEdit 7.4.5は変更せず、Chairsを有効化します。
3.10.13の[公式Chairソース](https://github.com/EngineHub/CraftBook/blob/3.10.13/src/main/java/com/sk89q/craftbook/mechanics/Chair.java)と
固定配布JARで、`mechanics.Chairs`の7キー、`craftbook.mech.chair.use`、
20 tickごとの回復処理と最大HP上限を確認しました。回復量は既定1.0から0.5にし、看板を必須にします。
`blocks`はpatchせず、既存値またはCraftBook自身の既定一覧を維持します。

ProtocolLibは追加済みの公式5.5.0-SNAPSHOT / asset ID `608298575`を維持します。
[公式Development Build](https://github.com/dmulloy2/ProtocolLib/releases/tag/dev-build)の
26.2対応（#3642）・Java 25修正（#3566）を再確認し、公式asset metadataのSHA-256も
既存の固定値と一致しました。配布元と起動前取得方式は下記「Plugin運用整理」のとおりです。
同節の隔離Paper 26.2 / Java 25起動確認は既存の記録です。今回のChairsの起動・
クライアント操作・本番確認は未実施です。設定保持方式と手動確認項目は
[Minecraft運用](../minecraft/README.md#craftbook-chairs休憩)を参照してください。

## Plugin運用整理（2026-10-04）

- DeadChest 4.31.0: [作者公式配布](https://modrinth.com/plugin/dead-chest/version/ej8X4AM4)はPaper / 26.2を列挙。GETしたJARのSHA-512は公式metadataと一致しました。旧`dead-chest-*.jar`は既存の起動前除去対象に追加し、`plugins/update/`の同名パターンも除去します。DeadChest 4.31.0を継続使用し、`prepare-paper-plugins.sh`で運用設定の`updates.auto-check`と旧形式`auto-update`をfalseへpatchします。同じ起動時patchで`/data/plugins/DeadChest/config.yml`の`chest.duration-seconds`を全ロス防止のため`0`（無期限）に固定し、死亡チェストは時間経過では期限切れにしません。その他の死亡保護設定（`chest.max-per-player`を含む）は既存値を保持します。無期限化の本番動作・プレイヤー操作は未確認です。
- ProtocolLib: [公式dev changelog](https://github.com/dmulloy2/ProtocolLib/releases/tag/dev-build)は26.2対応（#3642）とJava 25修正（#3566）を含みます。stable 5.4.0の対応は1.21.8までなのでdevelopment版を採用。2026-10-03T18:20:42Z作成の`ProtocolLib-Spigot.jar`（JAR表記5.5.0-SNAPSHOT、asset ID `608298575`）を固定し、可変`dev-build`ダウンロードURLは使いません。`plugins.txt`には管理対象と固定取得元をコメントで記録し、Acceptヘッダーが必要なため起動前スクリプトで`mc-image-helper get --accept application/octet-stream`を実行します。SHA-256 `a4ef57c36e27adec56b3a7935b7930fd1e366b310b9b698949e7f3320c84a8f9`で検証してから配置します。公式asset削除・ハッシュ不一致時は起動を中止します。既存JARがハッシュ一致なら再取得しません。
- PlaceholderAPI: [公式2.12.3 Release](https://github.com/PlaceholderAPI/PlaceholderAPI/releases/tag/2.12.3)は26.2対応を明記していますが、Paper版はexperimentalとされています。ここではReleaseのBukkit/Spigot JARを固定し、Java 25でenableを確認。SHA-256 `fde03259f5af6938f3c33eeb4d814000a1adabf1d2304ce14970be81f609a437`は公式asset digestと一致しました。eCloud・外部Expansionは導入していません（既存Plugin自身の内部placeholder登録は発生します）。
- Magic 11.2.4: [upstream修正](https://github.com/elBukkit/MagicPlugin/commit/10d3665616efe71f3431a2434ff8124d0aeeebc7)に沿って`vengeance.variables: bubble`を追跡設定へ追加。本体版と0.4/0.6/0.8の式は維持。ただし、この版でのローカル起動では3段階の式評価警告が残りました。
- MineGames 1.0.5: 外部configのRoulette / Slotsの重複6行を削除し、同じ文言を各1定義に統一。ただしJAR同梱configにも重複があり、既定設定読み込み時の警告は残ります。本体変更は今回行っていません。
- GhastMaster: 履歴`ec6bcf3`にSpiget resource `126304`の追加、`18c1ce5`に取得失敗による削除がありましたが、どちらも版は記録されていません。手元の配布JARにも運用版を特定できるものがなく、本体の管理化は未実施。別版への移行は行いません。`ghastmaster.share`のみ一般グループの許可一覧へ追加しました。本番適用は未実施です。

隔離Paper 26.2 build 126 / Oracle GraalVM Java 25.0.4でMagic、MineGames、DeadChest、ProtocolLib、PlaceholderAPI、BetterHorses（6.4）と既存依存Pluginを同時にenableし、正常停止を確認しました。DeadChestのAmbiguous plugin name、BetterHorsesのProtocolLib未導入警告はありません。Magicのbubble警告とMineGames既定YAMLのduplicate keys警告は残存。全Plugin・Data Packとの組合せ、本番、プレイヤー操作は未確認です。ValhallaMMO等の別タスクの修正は含みません。

## BreweryX追加（2026-10-04）

[BreweryX 3.7.1公式Release](https://github.com/BreweryTeam/BreweryX/releases/tag/3.7.1)が案内する
[Modrinth版XmLbPZhp](https://modrinth.com/plugin/breweryx/version/XmLbPZhp)を採用します。
固定取得URL: https://cdn.modrinth.com/data/gvXaGv1n/versions/XmLbPZhp/BreweryX-3.7.1.jar

公式metadataはPaperを含み、Minecraft 1.20.2〜26.2の列挙に現行26.2も含まれます。
公式ソースtagは`3.7.1`（Release commit `343872c`）です。
配布JARの`plugin.yml`は`3.7.1;master`、`api-version: 1.13`と表記されています。
GETした公式JARのSHA-512はmetadataと一致:

`e1ccd1958e614b130762e2a6ff5fe7f9eff9702e63e89b7d4db458a5b8f9c9050b52829b742deac9088ceef25d4ffe550e04b3ec9e4eff02d0af67ae6715159b`

隔離したPaper 26.2 build 126 / Java 25で初回起動・日本語設定での再起動、
`Using language: ja.yml`、SQLite、enable、Consoleの日本語ヘルプ、正常停止を確認しました。
本体のバージョン判定は26.2を`Unknown`と警告するため、対応metadataと起動確認だけで
全挙動の互換性を保証しません。既存全Pluginとの同時起動、クライアント表示、
コーヒーの実製造・飲用、樽・蒸留・飲酒演出、Java/Bedrock操作、本番は未検証です。
Paper、権限設定、外部DBは変更していません。詳細と手動確認は
[BreweryX運用手順](../minecraft/java/plugins/BreweryX/README.md)を参照してください。

## 既存構成（2026-09-22確認）

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
| Paper / Minecraft | 26.2 build 126（STABLE）、Java 25 | https://fill.papermc.io/v3/projects/paper/versions/26.2/builds/126 |

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
| FEATO Gun-Valhalla Bridge Plugin | 0.3.0 | [固定JAR](https://github.com/FEATO-org/feato-gun-valhalla-bridge/releases/download/v0.3.0/feato-gun-valhalla-bridge-plugin-0.3.0.jar) | Paper | 26.2 build 126（Bridge固定対象） | 公開Release（Phase 1 PoC） | Java 25、ValhallaMMO 1.10.3必須。release ID 4 / protocol 1。config reload対応。0.3.0の実機起動・reloadは未確認 |
| FEATO Gun-Valhalla Bridge Datapack | 0.3.0 | [固定ZIP](https://github.com/FEATO-org/feato-gun-valhalla-bridge/releases/download/v0.3.0/feato-gun-valhalla-bridge-datapack-0.3.0.zip) | Data Pack | 26.2（pack format 107.1） | 公開Release（Phase 1 PoC） | 同版Pluginと対で配置。Gun Core 1.0.15 / Modern Guns 1.9.3。release ID 4 / protocol 1。0.3.0は実機未確認 |
| FEATO Horsemanship | 0.3.0 | [固定JAR](https://github.com/FEATO-org/feato_horsemanship/releases/download/v0.3.0/feato-horsemanship-0.3.0.jar) / [Skill設定](https://github.com/FEATO-org/feato_horsemanship/releases/download/v0.3.0/horsemanship.yml) | Paper | 26.2 build 126（配布元対象、api-version 26.2） | stable release（draft=false、prerelease=false） | Java 25、ValhallaMMO 1.10.3必須。専用Java Skill/Profile登録。旧Custom Skill退避と完全再起動が必要。公開アセット・設定の一致を確認、v0.3.0実機確認は下記参照。本番・プレイヤー操作は未確認 |
| Magic | 11.2.4 | [固定URL](https://mediafilez.forgecdn.net/files/8375/702/Magic-11.2.4.jar) | Paper | 26.2（公式配布対象） | stable | 公式ValhallaMMO integrationを使用; Requires runtime verification |
| SCore | 5.26.9.17 | [固定URL](https://cdn.modrinth.com/data/ZfcV7L06/versions/EHLoQYh8/SCore-5.26.9.17.jar) | Paper | 26.2（配布metadata） | stable | 同梱Java 8以上; Requires runtime verification |
| ExecutableItems | 7.26.9.17 | [固定URL](https://cdn.modrinth.com/data/g8Zwnnmn/versions/XrhxAt8x/ExecutableItems-7.26.9.17.jar) | Paper | 26.2（配布metadata） | stable | 同梱Java 8以上; Requires runtime verification |
| WorldEdit | 7.4.5 | [固定URL](https://cdn.modrinth.com/data/1u6JkXh5/versions/F5ea2ov3/worldedit-bukkit-7.4.5.jar) | Paper | 26.2（配布metadata） | stable | 同梱Java 25以上; Requires runtime verification |
| CraftBook | 3.10.13 | [固定URL](https://cdn.modrinth.com/data/jrO7z7l7/versions/6kl3GQSJ/craftbook-3.10.13.jar) | Paper | 26.2（配布metadata） | stable | 同梱Java 21以上; Requires runtime verification |
| ImageFrame | 2026.1.4 | [固定URL](https://cdn.modrinth.com/data/lJFOpcEj/versions/nt0GWT1y/ImageFrame-2026.1.4.0.jar) | Paper | 26.2（配布metadata） | stable | 同梱Java 21以上; Requires runtime verification |
| Backpack Plus | 3.2.0 | [固定URL](https://cdn.modrinth.com/data/lDAFcnRN/versions/vsRfbexG/BackpackPlus-3.2.0-all.jar) | Paper | 26.2（配布metadata） | stable | 同梱Java 21以上; Requires runtime verification |
| Enchants Plus | 1.6 | [固定URL](https://cdn.modrinth.com/data/N72bKhby/versions/oeMySJjE/Enchants%2B%20v1.6%201.21%20-%201.21.11.zip) | Data Pack | 26.2（配布metadata） | stable | Requires runtime verification |
| DeadChest | 4.31.0 | [固定URL](https://cdn.modrinth.com/data/pKqnV03Y/versions/ej8X4AM4/dead-chest-4.31.0.jar) | Paper | 26.2（公式metadata） | stable | Java 25 / Paper 26.2 build 126でenable・正常停止確認。死亡・回収操作と本番は未確認 |
| ProtocolLib | 5.5.0-SNAPSHOT（asset 608298575） | [固定公式asset](https://api.github.com/repos/dmulloy2/ProtocolLib/releases/assets/608298575) | Paper（Spigot artifact） | 26.2（公式dev changelog #3642） | development | Java 25対応修正 #3566を含む。Java 25 / Paper 26.2 build 126でenableとBetterHorses接続確認 |
| PlaceholderAPI | 2.12.3 | [固定公式Release](https://github.com/PlaceholderAPI/PlaceholderAPI/releases/download/2.12.3/PlaceholderAPI-2.12.3.jar) | Paper | 26.2（公式Release） | release（Paper版はexperimental表記） | Java 25 / Paper 26.2 build 126でenable確認。追加Expansionなし |
| Better Horses | 6.4（検証時、動的取得） | [作者配布](https://www.spigotmc.org/resources/better-horses.124223/) | Paper | 26.2（6.4でローカル起動確認） | dynamic author release | Spiget resource 124223の取得方式を維持。2026-10-04に馬術との同時起動確認、プレイヤー操作は未確認。ProtocolLibなしでは一部機能無効 |
| EssentialsX Core / Spawn | 2.22.1-dev+24-49a2f10（公式CI build 1829） | [Core](https://ci.ender.zone/job/EssentialsX/1829/artifact/jars/EssentialsX-2.22.1-dev+24-49a2f10.jar) / [Spawn](https://ci.ender.zone/job/EssentialsX/1829/artifact/jars/EssentialsXSpawn-2.22.1-dev+24-49a2f10.jar) | Paper | 26.2（現行公式support一覧） | development | 2.22.0 stableは26.1.2まで。Paper 26.2で起動確認 |
| VaultUnlocked | 2.20.3 | [固定URL](https://cdn.modrinth.com/data/ayRaM8J7/versions/qZgRzoYs/VaultUnlocked-2.20.3.jar) | Paper | 26.2（配布metadata） | stable | plugin名は`Vault`。Paper 26.2で起動確認 |
| EssentialsUnlocked | 1.0.0.1 | [固定URL](https://cdn.modrinth.com/data/gPLRdl3T/versions/fUaoKCyT/EssentialsUnlocked-1.0.0.1.jar) | Paper | 26.2（配布metadata） | stable | manifest versionは1.0.0.0。Paper 26.2で起動確認 |
| MineGames | 1.0.5 | [Modrinth公式Release](https://cdn.modrinth.com/data/YAetfB2l/versions/457fwbAR/minegames-1.0.5.jar) | Paper | 26.2（配布metadata） | stable | Slotsのみ初期利用。Vault Economyへ接続。実機確認待ち |
| EconomyShopGUI Free | 7.3.2 | [作者公式Release](https://www.curseforge.com/minecraft/bukkit-plugins/economyshopgui/files/9031004) / [取得URL](https://cdn.spiget.org/file/spiget-resources/69927.jar) | Paper | 26.2（公式配布対象、JARにv26_2実装あり） | stable release（公式配布Type: Release） | 標準Bedrock Formsを全Bedrock端末で使用、Java GUIは従来通り。Spiget resource 69927は動的URL。7.3.2の起動・Geyser/Floodgateとの実クライアント動作はRequires runtime verification |
| FEATO Ancient Coin | 1.0.0 | [固定Release](https://github.com/FEATO-org/feato_ancient_coin/releases/tag/v1.0.0) | Paper | 26.2（plugin api-version） | stable release | GitHub latest release（draft=false、prerelease=false）。Paper 26.2で起動確認 |
| FEATO Coin Exchange | 1.1.0 | [公開予定Release](https://github.com/FEATO-org/feato-coin-exchange/releases/tag/v1.1.0) | Paper | 26.2（plugin api-version） | release pending | `FEATO-Coin-Exchange-1.1.0.jar`を取得対象として事前設定。data folderは`FEATOCoinExchange`、`exchange-value: 10.0` |
| FancyNpcs | 2.12.0 | [固定URL](https://cdn.modrinth.com/data/EeyAn23L/versions/53lykMXY/FancyNpcs-2.12.0.jar) | Paper | 26.2（配布metadata、起動確認） | stable | 依存なし。帰還札はplayer_command、古銭換金はconsole_command 1回を使用し、一時OPは禁止 |
| FancyHolograms | 2.12.0 | [固定URL](https://mediafilez.forgecdn.net/files/8887/168/FancyHolograms-2.12.0.jar) | Paper Plugin | Paper 26.2対象（build 126、実起動未確認） | stable Release | Java 25で運用予定。必須追加dependencyなし。PlaceholderAPI / FancyNpcsはoptional integration。JAR GET・metadata・ZIP整合性のみ確認。本番動作・Java / Bedrock client表示は未確認 |
| squaremap | 1.3.15 | [固定Release](https://github.com/jpenilla/squaremap/releases/tag/v1.3.15) | Paper | 26.2（api-version、起動確認） | stable | 内部Webサーバー8123、既存dynmap.feato.jp経路を再利用 |
| DualHorse | 1.5.4 | [固定URL](https://cdn.modrinth.com/data/mgoLZ3st/versions/9jTb2KHl/DualHorse-1.5.4.jar) | Paper | 配布metadataは26.1.2まで、26.2で起動確認 | stable | 26.2の実プレイヤー二人乗りとBetter Horses併用は要確認 |
| Velocity | 4.2.0 build 30 | [公式配布](https://papermc.io/downloads/velocity) | Velocity | 接続を実機検証 | stable（公式API STABLE） | VELOCITY_VERSIONとBUILD_IDで固定。JAR GETは403、Requires runtime verification |
| Geyser | 既存latest | [公式配布](https://download.geysermc.org/) | Velocity | 接続を実機検証 | 取得build要確認 | 既存方式維持、Requires runtime verification |
| Floodgate | 既存latest | [公式配布](https://download.geysermc.org/) | Velocity | 接続を実機検証 | 取得build要確認 | 既存UUID維持、username-prefixは`.`へ変更、Requires runtime verification |
| EmoteOffhand | Version ID: YiejycoE | [Modrinth](https://modrinth.com/plugin/pVsz9nZm/version/YiejycoE) | Geyser Extension（Velocity上のGeyser） | 1.21.11（配布metadata） | fixed artifact | Source: Modrinth。Project ID: pVsz9nZm。`resources/minecraft/geyser/extensions/EmoteOffhand.jar` を管理側で用意し、更新時のみ `script/copy_plugins_to_remote.sh` で配布。通常deploy時に再取得しない。Velocity Pluginとしては配置しない |
| Hurricane | latest（確認時 build 4） | [公式Downloads API](https://download.geysermc.org/v2/projects/hurricane/versions/latest/builds/latest/downloads/spigot) | Paper | 公式README表記は26.1まで | dynamic build | bamboo / pointed dripstone collisionのみ。Paper 26.2ではRequires runtime verification |

### FancyHolograms 2.12.0追加（2026-10-07）

CurseForge Project ID `1480051` / File ID `8887168` の固定URLをHTTP GETし、
JARのZIP整合性と `paper-plugin.yml` の `name: FancyHolograms` / `version: 2.12.0` を確認しました。
`PLUGINS_FILE` の既存導入経路を使用し、設定seedは作らず、初回起動時にupstream defaultを永続Volumeの `/data/plugins/FancyHolograms/` へ生成させます。
取得した2.12.0 JARの `BrightnessCMD` を `javap -c -p` で局所確認したところ、個別permission checkがないため `fancyholograms.hologram.edit.brightness` は付与一覧から除外しています。
`see_trough` は指定の綴りを維持し、ホログラムごとの `fancyholograms.viewhologram.<hologram-name>` は必要時に個別設定します。
Paper 26.2 build 126 / Java 25での起動、操作・保存、任意連携とJava / Bedrock表示は未確認です。
公開前の受入確認は [LuckPerms運用](../minecraft/README.md#luckperms) を参照してください。

### EconomyShopGUI 7.3.2確認（2026-10-03）

`plugins.txt`の既存Spiget resource 69927 URLをHTTP GETし、JAR（1,896,195 bytes）の`plugin.yml`で`version: 7.3.2`、ZIP整合性、`versions/v26_2/`の同梱実装を確認しました。公式配布名は`EconomyShopGUI-7.3.2.jar`で、[作者公式配布metadata](https://www.curseforge.com/minecraft/bukkit-plugins/economyshopgui/files/9031004)はRelease・26.2対応です。取得方式は維持し、再取得時には動的URLのJAR版と下記SHA-512を再確認してください。

[7.3.0公式更新情報](https://www.spigotmc.org/resources/economyshopgui.69927/update?resource_update_id=656259)で、Geyser/Floodgate向けBedrock専用Formsとタッチ端末限定オプションの追加、日本語ファイルの`lang-jp.yml`→`lang-ja.yml`へのrenameを確認しました。[7.3.2公式更新情報](https://www.spigotmc.org/resources/economyshopgui.69927/update?update=657560)にはBedrock texture対応とJsonShopFormsのnavigation修正が含まれます。今回は標準Formsだけを使用し、JsonShopFormsのPlugin・packは追加しません。

JARの標準`config.yml`は`config-version: 2.0.1.9`で、`LanguageFiles/lang-ja.yml`を同梱しています。既存設定とのキー比較では削除キーはなく、新規キーは`bedrock-forms`、`per-player-languages: false`、`enchanted-variants: false`でした。今回追加するForms設定は上流既定を使い、商品を1回の選択で操作するため`use-double-click-for-touch-devices`だけ既定の`true`から`false`へ変更します。目的外の新規optional featureは追加せず、既定の無効状態を維持します。経済Provider・価格・sections/shops・既存のクリックとnavigation設定は維持し、7.3.2の起動・取引・画面遷移は未検証です。

### FIREARMS Bridge 0.3.0確認（2026-10-07）

[公開Release v0.3.0](https://github.com/FEATO-org/feato-gun-valhalla-bridge/releases/tag/v0.3.0)はdraft=false、prerelease=falseです。JAR/ZIPを取得し、公開`SHA256SUMS`とGitHub asset digestのSHA-256一致、ZIP整合性、JARの`plugin.yml`（version 0.3.0 / ValhallaMMO依存）を確認しました。JARの`bridge.properties`とZIPのmarkerはrelease ID **4** / protocol **1**で一致し、pack formatはmin/maxとも`[107, 1]`です。

| 配布物 | 検証済みSHA-256 |
| --- | --- |
| feato-gun-valhalla-bridge-plugin-0.3.0.jar | `66e51bedfdd4b586eb55be408f3531a31adc6d2edc0af4b4225a55a5ff7bf26f` |
| feato-gun-valhalla-bridge-datapack-0.3.0.zip | `2061d58bbe32398d716dce1e9fb7a1732a8ff2491b5c6be4229f7740a4d9add4` |

両manifestのURLを同時更新します。Paper 26.2 build 126 / Java 25 / ValhallaMMO 1.10.3 / Gun Core 1.0.15 / Modern Guns 1.9.3は同じ固定対象です。追跡configは0.3.0 JAR同梱版とbyte単位で一致し、debug.enabled / shot-context / damage-integrationはfalseのままです。既存の旧版JAR/ZIP削除globと管理者reload権限を維持します。

公開版はPhase 1 PoCで、Shot Context Adapter、銃撃EXP、Damage連携、Ability効果は未実装です。今回の取得・静的確認は実サーバー起動や保存・再接続・reloadの実機成功を証明しません。0.3.0の本番適用・実機確認は未実施です。適用・バックアップ・復旧手順は[minecraft/README.md](../minecraft/README.md#銃器スキルfirearms-bridge-030--phase-1-poc)を参照してください。

### FIREARMS Bridge 0.2.0確認（2026-10-04）

[公開Release v0.2.0](https://github.com/FEATO-org/feato-gun-valhalla-bridge/releases/tag/v0.2.0)はdraft=false、prerelease=falseです。JAR/ZIPをGETし、公開`SHA256SUMS`とGitHub asset digestとの一致、ZIP整合性、JARの`plugin.yml`（FEATOGunValhallaBridge / 0.2.0 / ValhallaMMO依存）、`bridge.properties`とZIP内markerのrelease ID `3` / protocol `1`の一致を確認しました。ZIPの`pack.mcmeta`はmin/max formatとも`[107, 1]`です。

| 配布物 | GET検証済みSHA-256 |
| --- | --- |
| feato-gun-valhalla-bridge-plugin-0.2.0.jar | `6dc28fd421620d62bd3f8c1b9137f4aa1841fdd05398ec49a77fdffa1af28307` |
| feato-gun-valhalla-bridge-datapack-0.2.0.zip | `3e6699a3f35e3ac2f06fc68ca954626e5114e840bed25266e198fb19f00ab8db` |

Paper build 126 / Minecraft 26.2 / Java 25 / ValhallaMMO 1.10.3 / Gun Core 1.0.15 / Modern Guns 1.9.3は従来どおりです。Composeのbuild固定とBridge旧版だけを対象とするJAR/ZIP整理も維持します。追跡configは0.2.0公開JARの初期設定と完全一致し、debugは無効です。

0.2.0は`/firearms reload`を追加したPhase 1 PoCで、銃撃EXP・Damage連携・Ability効果は未実装です。`plugin.yml`のreload専用権限`feato.gunvalhalla.reload`は既定OP、既存debug権限とは独立し、debug無効時もconsoleから実行できます。管理者グループ向け権限スクリプトへreloadだけを追加し、debugの付与設定は変更しません。

0.1.0ではユーザー実機報告でhandshake・FIREARMS登録・銃器表示・Lv0 Profileの再ログイン維持を確認しました。0.2.0の実機起動と新reload経路、特定XP値・Level Up・完全再起動後の保存・DB値・Perk三択は未確認です。respec/recalculationは未確認のまま後回しとし、後続開発を止める理由にはしません。更新・config反映・実機確認・復旧手順は[minecraft/README.md](../minecraft/README.md#銃器スキルfirearms-bridge-030--phase-1-poc)を参照してください。

### FEATO Horsemanship 0.3.0（2026-10-05）

[公開Release](https://github.com/FEATO-org/feato_horsemanship/releases/tag/v0.3.0)のJAR・Skill YAML・SHA256SUMSを認証なしでGETし、公開asset digestとSHA-256を照合しました。JAR内のplugin.ymlは0.3.0 / api-version 26.2 / ValhallaMMO必須、最大class majorは69（Java 25）です。同梱SkillとRelease YAMLは一致し、効果設定は追跡configと一致します。最新GUI、43 PerkのID・条件・報酬・座標・EXP曲線を維持し、未使用statsだけを除去しています。

| Asset | 検証済みSHA-256 |
| --- | --- |
| feato-horsemanship-0.3.0.jar | `302d0395f8fc3cfa027efa5dc074d42e4332f3bcb76af32d721d359441cda395` |
| horsemanship.yml | `6606ed03dccb8102ed8f6363d43513bee9b537550eddbaab183b3f2f0cbcbd0c` |

正本は `minecraft/java/plugins/FEATOHorsemanship/horsemanship.yml`、読み込み先は `/data/plugins/FEATOHorsemanship/horsemanship.yml` です。v0.3.0の専用Java Skill/Profileと同時に配布し、旧ValhallaMMO Custom Skillは管理元と永続Volumeから退避します。Perk取得データの削除やresetは行いません。移行・バックアップ・受入試験・切り戻しは[導入手順](../minecraft/java/plugins/ValhallaMMO/HORSEMANSHIP_SETUP.md)を参照してください。

2026-10-05、公開v0.3.0 JARを隔離localhostのPaper 26.2 build 126 / Oracle GraalVM Java 25.0.4 / ValhallaMMO 1.10.3で起動し、専用Skill/Profile登録、43 Perk・6排他条件、標準reset/refund報酬の登録、SQLiteへの合成UUIDのProfile/PowerProfileの保存・読込み、既存の合成Profile値（Lv・EXP・累積EXP・NG+）の保持、正常停止を確認しました。公開JARの全classは前段で17テストとclean buildを通した修正ソースのclassと一致します。GUI検証8テストとgit diff --checkも成功しました。BetterHorses/DualHorse/Magicを含む同時起動、実プレイヤーの標準EXP/Profileコマンド、騎乗・戦闘、logout/login、reset/refund実行・NG+取得、本番はv0.3.0では未確認です。

#### 旧0.2.0の確認履歴（現行配置には使用しない）

[指定Release](https://github.com/FEATO-org/feato_horsemanship/releases/tag/v0.2.0)のJARとCustom SkillをGETし、GitHub Release asset digest、同梱`SHA256SUMS`とSHA-256を照合しました。認証なしのJAR取得はHTTP 200です。JAR内の`plugin.yml`でdata folder名`FEATOHorsemanship`、ValhallaMMO必須、BetterHorses / DualHorse任意を確認し、クラスの最大major versionは69（Java 25）です。Release添付のSkillとJAR内のSkillは同一です。

| Asset | 検証済みSHA-256 |
| --- | --- |
| feato-horsemanship-0.2.0.jar | `613002f811eb7c2ad613cf015fe40c050f879edd2a1561a4c198451c18a52a19` |
| horsemanship.yml | `a384b5494df865c317686f78d306afb9c81beb87b1d2bb8052409157f0a34677` |

Release asset名と取得URLは小文字のままですが、旧0.2.0ではGit管理・配布時の正本を `minecraft/java/plugins/ValhallaMMO/skills/custom/HORSEMANSHIP.yml` としていました。内容・SHA-256は変更せず、ValhallaMMO 1.10.3の大文字ファイル名での読み込みに合わせていました。 2026-10-04、隔離したLinux / Java 25 / Paper 26.2 build 126でValhallaMMO 1.10.3とFEATOHorsemanship 0.2.0のenable完了を確認しました。Bridge・本番・育成や保存などの全体動作は未確認です。

Paper 26.2 build 126 / Oracle GraalVM 25.0.4、ValhallaMMO 1.10.3、BetterHorses 6.4、DualHorse 1.5.4、Magic 11.2.4で、Custom Skill登録、5 Pluginの有効化、Magicから馬術Lv・EXPの認識、馬術設定reload、正常停止を隔離したローカル環境で確認しました。43 Perkの報酬・前提・排他条件・座標も静的検証しています。v0.1.0で再現した`horsemanship_first_saddle_set`未登録エラーは解消しました。一般プレイヤーのPerk取得・NG+・騎乗・育成連携、Java/Bedrock操作、本番動作は未確認です。

既存BetterHorsesのSpiget URLは動的で、2026-10-03のGET結果を使用したローカル起動版は6.4でした。配布元の馬術対象表記は6.3です。取得方式は維持し、実際の本番起動版はログで確認してください。起動前patchは`settings.mounted-damage-boost.enabled`だけを無効化します。配置・停止バックアップ・実機確認・戻し方は[馬術の導入手順](../minecraft/java/plugins/ValhallaMMO/HORSEMANSHIP_SETUP.md)を参照してください。

### GET検証済みSHA-512

| Distribution | SHA-512 |
| --- | --- |
| LuckPerms-Bukkit-5.5.71.jar | `188a91f0a543d23bfda32385fca6db63d61e49c8a422bd452a260bd9cbc6a7d7fe45071199e9fca8f3ce43c2b41ee84fd315bd15464577028ff3951a7d4fab27` |
| LuckPerms-Velocity-5.5.71.jar | `a619da8804727bed7b2b2ee5383974329a3c09181a67745484fdffd0f4b6c5b13c44aa88e0d2b30d13f3068d9b0f3e26863abba9855f80a7eb5f9455ca6c40d4` |
| lucktags-1.4.jar | `1052d2ea814da732d5e39447384df0427fd14c2e1f206441b3d71a5a65b10733bf30db983cc92e21079503687c9097310d43b237e388db7d8d1129fc56989855` |
| feato-gun-valhalla-bridge-plugin-0.3.0.jar | `168aabb27d747299233da1ebfc9637c677f30c3c39184403e185ad858a0964b006146d43a4eaaabb0843a745452547b7e01bb2d0bac7ece67e83383f9cdc92d3` |
| feato-gun-valhalla-bridge-datapack-0.3.0.zip | `be83d4edc94e914bfd8a73ffbf7aaf83fdf941e3ae511858f7e5ed42e86f70f62d58a4f0f6e1d631d249d140ea3753a9f4aeefe25ba2af93707def36424daea7` |
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
| minegames-1.0.5.jar | `54c3a6d5a5060cf3cb2016cbc3f76d7d40d2d96fd1e1e5bc1741c12b155086be10d34fdab58b75e5c3cbe0a338de75c3a6b42e6d3142341c8247b87d14d8b771` |
| EconomyShopGUI-7.3.2.jar | `128cf92056360ed4c3afaecd0ccd2a95366b3e191dc5d784753642cfe6de2344027cec42ac8e92d8c5b4608b82396c9cfedd305e2e2536b2410c2a57d5653565` |
| FEATO-Ancient-Coin-1.0.0.jar | `d4e7608d9d1f2614a6e420f3ee7e02a84b96e8c638cc9f5c6fa17f554aaaa99ef6af3d54a180a7002f0b87959ff249420c255a6bd48bfe8f81017d44e106e238` |
| FEATO-Coin-Exchange-1.1.0.jar | Release公開後にGitHub Release asset digestを記録 |
| FancyNpcs-2.12.0.jar | `f7a52c7e44d004e4235c12bf8d6936b25188ae7259b375d8b310b56538e724452805173e3781f9326c8fa794802f329c18416cbafccf5b5fab5016a628027399` |
| FancyHolograms-2.12.0.jar | `93ea248525fa2bf8efcd13456e35833c069a0bea2bdddc1cc6a61b68f00681b91f928443dbe82a974041253a9393eca8203743382063cda56c6fb39259ed4a21` |
| squaremap-paper-mc26.2-1.3.15.jar | `a6f00e0ea57268ed30b4aa2246b8ea3424f1210daab01bd47b217ec334199e792605f9419b7cfed7ed07cac20ad125593ddaf181c0ee72a129255563c75ab11e` |
| DualHorse-1.5.4.jar | `fd70684e9b3263bfc4edb9bde54a5fc1cc08c9f2ca4577434e2517dd7a3e5958029ebb0fd4090faa0545ae957531608cafe5452cb30d87f67344b28ac30e75d2` |
| BetterHorses-6.3.jar | `d54e921e073eec52dbe81542f0d06713bf1c217a645c4644caf410fcc08ebfa27723866d7de3803a2be7c3d4143c61943849dd9e959f312f8d465426d863e704` |
| Enchants+ v1.6 1.21 - 1.21.11.zip | `93e507c428287d7e8562a2ddd5a6488e47fcd76282426d683621c947f4fa8dda6a0ed605d458a1fed659ac5aa0909f01c8adb32994664788abe35fce0411083b` |
| dead-chest-4.31.0.jar | `8f39b4a11c5c4a168fe55f4a9e77e11c3aff9aa778a3a32565990e1de07b5d0fc7c28d14da1720fae08300f8874df89fd5f970c9bb796a7c19e2ceb1e3484028` |

## 26.2追加構成の起動検証（2026-09-21）

Hurricane追加前に、Paper 26.2 build 126 / Java 25で全19 Pluginを同時に有効化し、正常停止を確認しました。FancyNpcs 2.12.0、squaremap 1.3.15、DualHorse 1.5.4、Better Horses 6.3を含みます。squaremapは8123番で起動し、ValhallaMMOはja-jp、Backpack Plusはjpn、EconomyShopGUIはlang-jp.ymlを読み込みました。ExecutableItemsはemergency_returnを含む追跡アイテム1件を読み込み、EconomyShopGUIはfeato_shop 1セクション/1ショップとEssentialsX Economy接続を確認しました。Hurricaneは公式READMEの対応表記が26.1までのため、Paper 26.2での起動ログと両collision workaroundの実機動作は未検証です。

Better HorsesはProtocolLibなしでも起動しますが一部機能を無効化します。DualHorseの配布metadataは26.1.2までのため、26.2では起動確認に加えて実プレイヤーで二人乗り、再接続、馬データ保存、Better Horsesとの併用を確認してください。NPCクリック、帰還札の100G徴収・1回消費・teleport、Java/Bedrock接続はクライアント試験が必要です。
