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
| Minecraft server image | java25（Javaメジャーのみ指定） | https://docker-minecraft-server.readthedocs.io/en/latest/versions/java/ |
| Minecraft proxy image | java25（Javaメジャーのみ指定） | https://github.com/itzg/docker-mc-proxy/blob/main/README.md |
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
