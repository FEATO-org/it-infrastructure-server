# バージョン確認（2026-09-18）

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
| Minecraft server image | itzg java25 + Oracle GraalVM 25（ローカルビルド） | https://docker-minecraft-server.readthedocs.io/en/latest/versions/java/ |
| Minecraft proxy image | itzg/mc-proxy:java25（公式HotSpotイメージ） | https://github.com/itzg/docker-mc-proxy/blob/main/README.md |
| Paper / Minecraft | 26.2、Java 25 | https://papermc.io/downloads/paper/ |
| ImageFrame | 2026.1.4 | https://modrinth.com/plugin/imageframe/versions |
| WorldEdit | 7.4.5（Bukkit） | https://modrinth.com/plugin/worldedit/versions |
| CraftBook | 3.10.13 | https://modrinth.com/plugin/craftbook/versions |
| DeadChest | 4.30.0 | https://modrinth.com/plugin/dead-chest/versions |
| HorseEnhancer | 2.1.3（変更なし） | https://github.com/Nevakanezah/HorseEnhancer/releases/tag/v2.1.3 |

GitHubは`releases/latest`の`prerelease=false`を確認しています。
Docker HubでMariaDB・nginx・Portainer・itzgの採用タグの存在も確認しました。
Java 25の要件: https://docs.papermc.io/paper/getting-started/

独自Bot `support-feato-system` は公開Releaseがないため既存の`main`を維持しています。
Velocity、Geyser、Floodgate、SPIGET_RESOURCESはイメージ内のダウンローダーが取得します。
これらの動的取得とローカルplugins内のJARは固定版の保証対象外です。
DeadChestの最新releaseの対応表には26.2がなく、HorseEnhancerとSpigetプラグインも
Paper 26.2での起動・動作確認が必要です。安定版という分類と互換性は別に確認します。

`.env`の`MINECRAFT_VERSION`は26.2の既定値より優先されます。
本番のサービス名は`minecraft-server`です。
既存の`minecraft_server_data` volume名は維持しています。
本番のMariaDB上限は1G、Minecraft上限は7G、最大ヒープは6Gです。

既存DBを11.4から更新する場合はバックアップと公式アップグレード手順が必要です。
既存ワールドも26.2への更新前にバックアップしてください。コンテナのロールバックだけでは
更新済みのDB・ワールドのデータ形式は元に戻りません。

Minecraftのjava25タグは更新されるため、再取得時にイメージの内容が変わります。

## GraalVM設定

公式mc-proxyにGraalVMタグはなく、minecraft-serverのjava25-graalvmは
images.json上deprecatedです。そのため`minecraft/Dockerfile.graalvm`で
本体のitzg java25イメージにOracle GraalVM 25の最新更新版を導入します。
プロキシは公式のitzg/mc-proxy:java25とG1GC最適化を使います。
Oracle版を使うのはMeowIceのGraalVMフラグがenterpriseコンパイラ設定を要求するためです。
https://www.graalvm.org/jdk25/getting-started/
https://raw.githubusercontent.com/itzg/docker-minecraft-server/master/images.json

単一ノードではデプロイ前に`./script/build_minecraft_graalvm.sh`を実行します。
複数ノードでは`.env`の`MINECRAFT_SERVER_IMAGE`に各ノードからpullできる
レジストリのイメージ名を指定してビルドし、本体のイメージをpushしてください。
ビルドスクリプトは自動push・デプロイしません。

本体はAikarを無効にし、`USE_MEOWICE_FLAGS`と`USE_MEOWICE_GRAALVM_FLAGS`を有効化。
プロキシはこれらの変数をサポートしないため、`JVM_XX_OPTS`でG1GC、並列参照処理、
ヒープの事前確保、明示的GCの抑制、GC停止時間の目標200msを指定します。
小さい1Gヒープには本体用の16Mリージョン設定を流用せず、JVMの自動調整を使います。
両方ともメモリ上限とヒープの上限は従来値を維持します。
https://docker-minecraft-server.readthedocs.io/en/latest/configuration/jvm-options/#enable-meowices-flags
https://github.com/itzg/docker-mc-proxy/blob/main/README.md

更新時はビルドを再実行してください。性能向上は未計測のため、デプロイ後に
TPS/MSPT、GC停止時間、コンテナメモリとOOMの有無を比較してください。

本体のMeowIce設定に含まれるUseFastUnorderedTimeStampsとUseNUMAは、
VPSのハードウェア特性に依存するためJVM_OPTSで無効化します。
ローカル検証では本体のビルド、GraalVM 25.0.4、Graal Enterpriseコンパイラ、
本体のイメージ内スクリプトが生成するMeowIce/GraalVMフラグでのJVM起動を確認しました。
ローカルDockerではcgroupのメモリ制限を適用できないため、上限内の実負荷検証はVPSで行います。

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
