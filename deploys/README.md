# Docker Swarm production deployment

この構成は次の3スタックを使用します。app/system は Portainer Git Stack、infra は bootstrap で管理します。

- `app`: Discord Bot、Velocity、Paper
- `system`: MariaDB、Fluent Bit、mc-monitor、cAdvisor、nginx
- `infra`: Portainer Server/Agent、Cloudflare Tunnel

外部へpublishするサービスは`system_nginx`だけです。PortainerはCloudflare
Tunnel経由、MariaDB・監視エンドポイント・Minecraftバックエンドは暗号化
overlay network内だけで通信します。

UbuntuにはDocker Engine 25以降とCompose pluginを導入してください。cAdvisorの
現行版は古いDocker Engineをサポートしません。MinecraftバックエンドはVelocity
modern forwardingを利用するためPaper 26.2（Java 25）を既定にしています。

採用バージョンと確認先は[versions.md](versions.md)を参照してください。
Minecraftの移行・専用DB作成・対応版待機・実機確認は
[Minecraft運用](../minecraft/README.md)に記載しています。
初回はsystemを先に更新してLuckPerms DBを準備してからappを更新してください。

## 1. Swarmノード

Swarmのmanagerは障害許容が必要なら奇数台（通常3台）にします。複数VPS間の
Swarm制御・データ通信はWireGuardなどのprivate interfaceへ固定してください。

```bash
docker swarm init \
  --advertise-addr <WG_MANAGER_IP> \
  --data-path-addr <WG_MANAGER_IP>
```

join時も`--advertise-addr <WG_NODE_IP> --data-path-addr <WG_NODE_IP>`を指定します。
ノード間ではprivate interfaceに限り、manager向け`2377/tcp`、全ノード間の
`7946/tcp`、`7946/udp`、`4789/udp`を許可します。

配置先を明示します。`<NODE>`は`docker node ls`に表示される名前です。

```bash
docker node update --label-add edge=true <EDGE_NODE_1>
docker node update --label-add edge=true <EDGE_NODE_2>
docker node update --label-add cloudflare-tunnel=true <EDGE_NODE_1>
docker node update --label-add cloudflare-tunnel=true <EDGE_NODE_2>
docker node update --label-add portainer-data=true <MANAGER_NODE>
docker node update --label-add database-data=true <DATABASE_NODE>
docker node update --label-add minecraft-data=true <MINECRAFT_NODE>
```

nginxとcloudflaredは該当ラベルの全ノードで動作します。Portainer、MariaDB、
Minecraftはローカルvolumeを使うためラベルで1ノードへ固定しています。これらを
自動フェイルオーバーさせるには、別途レプリケーション対応ストレージ、DB
レプリケーション、バックアップと復旧手順が必要です。

## 2. Swarm secrets

manager上で一度だけ作成します。値をコマンドライン引数へ直接書かないでください。

```bash
openssl rand -base64 48 | docker secret create mariadb_root_password -
openssl rand -base64 48 | docker secret create mariadb_app_password -
openssl rand -base64 48 | docker secret create luckperms_db_password -
openssl rand -hex 32 | docker secret create forwarding_secret -
# Existing Floodgate private key; do not generate a replacement key here.
docker secret create floodgate_key /secure/path/floodgate-key.pem
openssl rand -base64 32 | docker secret create rcon_password -
openssl rand -base64 32 | docker secret create minecraft_proxy_rcon_password -
docker secret create cloudflare_tunnel_token /secure/path/cloudflare-tunnel-token
```

`floodgate_key`には、現在Velocity側Floodgateが使用している`key.pem`を指定します。Velocity/Paperで同一鍵を使用するため、新しいランダム値を生成しないでください。鍵ファイルはrepositoryへ保存しません。

`minecraft_proxy_rcon_password`はVelocity Proxy専用であり、Paperの
`rcon_password`と共有しません。Proxy RCONはコンテナ内のTCP 25575だけで有効化し、
ホスト、Swarm ingress、nginxへは公開しません。Proxy起動後はホストから次のように
管理コマンドを実行できます。

```bash
docker exec <minecraft-proxy-container> rcon-cli "geyser dump"
```

`cloudflare_tunnel_token`はremote-managed Tunnelのtokenです。Cloudflare
DashboardでPortainer用Public Hostnameを作り、originを
`https://portainer-host:9443`にします。Portainerの自己署名証明書を使う場合は
origin側だけ`noTLSVerify`を有効にし、Public HostnameにはCloudflare Accessの
認証ポリシーを必ず設定します。Portainerの`9443`と`8000`はホストにpublish
されません。

## 3. TLS証明書

証明書はCloudflare DNS-01でmanager上のCertbotコンテナが取得します。Certbotへ
Docker socketを渡さず、ホスト側スクリプトだけがversion付きSwarm secretを作成し、
nginxを1タスクずつ更新します。

Cloudflare API tokenは対象zoneに限定し、権限は`Zone:DNS:Edit`と読み取りに必要な
最小権限だけにします。Tunnel tokenとは別のtokenです。

```bash
sudo install -d -m 0700 /etc/swarm /var/lib/swarm-certbot
sudo install -m 0600 /secure/path/cloudflare-dns-token \
  /etc/swarm/cloudflare-dns-token
sudoedit /etc/swarm/certbot.env
```

`/etc/swarm/certbot.env`の例:

```dotenv
CERTBOT_EMAIL=admin@example.com
CERTBOT_CERT_NAME=feato.jp
CERTBOT_DOMAINS=feato.jp,*.feato.jp
CLOUDFLARE_API_TOKEN_FILE=/etc/swarm/cloudflare-dns-token
CERTBOT_STATE_DIR=/var/lib/swarm-certbot
TLS_STATE_FILE=/var/lib/swarm-certbot/swarm-secrets.env
TLS_SECRET_PREFIX=feato_tls
NGINX_SERVICE=system_nginx
```

systemd unitの`ExecStart`にあるrepository pathが実際の配置先と異なる場合は先に
修正してください。

```bash
sudo cp deploys/system/systemd/swarm-certbot-renew.* /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start swarm-certbot-renew.service
sudo systemctl enable --now swarm-certbot-renew.timer
```

初回実行で`/var/lib/swarm-certbot/swarm-secrets.env`に現在のTLS secret名が保存
されます。timerは毎日確認しますが、証明書内容が変わらなければnginx更新も新規
secret作成もしません。旧secretはロールバック用に自動削除しません。

## 4. bootstrap と Portainer Git Stack

通常更新に manager や各 node の checkout は不要です。静的構成は次のイメージに
同梱し、world、DB、Proxy data、Fluent Bit state は従来の named volume に保存します。

| 用途 | GHCR image | build file | 同梱先 |
| --- | --- | --- | --- |
| Paper | `ghcr.io/feato-org/feato-minecraft-server` | `minecraft/Dockerfile` | `/extras`, `/plugins`, `/config` |
| Velocity | `ghcr.io/feato-org/feato-minecraft-proxy` | `minecraft-proxy/Dockerfile` | `/rcon-init`, `/patches`, `/config`, `/plugins` |
| nginx | `ghcr.io/feato-org/feato-nginx` | `nginx/Dockerfile` | `/etc/nginx` |
| Fluent Bit | `ghcr.io/feato-org/feato-fluent-bit` | `fluentbit/Dockerfile` | `/fluent-bit/etc` |
| MariaDB | `ghcr.io/feato-org/feato-mariadb` | `deploys/system/mariadb/Dockerfile` | `/docker-entrypoint-initdb.d/20-luckperms.sh` |

Paper は従来どおり `/plugins` → `/data/plugins`、`/config` → `/data` を同期します。
Proxy は `/plugins` → `/server/plugins`、`/config` → `/server` を既存 itzg 起動処理で
同期します。image に永続 Volume の中身を COPY しません。設定の更新日時による
同期スキップ等も base image の従来仕様を維持します。Git 追跡設定を実機で変更したら、
次の image build 前に取り込み、deploy 後に実際の読込先の反映を確認してください。

### 初期構築

1. 上記の Swarm 初期化、node labels、既存鍵を含む external secrets、TLS を準備します。
2. manager 上で `sudo -E ./script/bootstrap_swarm.sh` を実行します。
   `.env` と `/var/lib/swarm-certbot/swarm-secrets.env` は manager の bootstrap 用にのみ
   読み込みます。必要な変数は `TLS_FULLCHAIN_SECRET` と `TLS_PRIVATE_KEY_SECRET`
   （秘密値ではなく Secret 名）です。スクリプトは manager と Secret の存在を検査し、
   4つの既存 external overlay network を必要時に作成して infra だけを検証・更新します。
3. GitHub Actions の `Swarm images` を main で手動実行し、5 image の公開完了を確認します。
   初回公開前は GitHub に Portainer webhook secrets を登録しません。
4. Portainer の Swarm environment に `system` と `app` を Git Repository 方式で作成します。
   stack 名は **必ず `system` / `app`** にします。infra は作成しません。
5. system の MariaDB 起動・LuckPerms DB 準備を確認してから app を起動します。
   新規構築では先に minecraft-data node に `app_minecraft_server_data` を
   `docker volume create app_minecraft_server_data` で作成します。
   system の Fluent Bit はこの volume を external として参照します。
   既存構成の移行では Volume を作り直しません。

既存 DB Volume では initdb は再実行されません。LuckPerms DB が未作成の場合だけ、
MariaDB task が動く node で `docker exec <mariadb-container> bash
/docker-entrypoint-initdb.d/20-luckperms.sh` を明示的に実行します。既存 user の
password はこのスクリプトで更新されません。権限設定やプレイヤー設定は
[Minecraft 運用](../minecraft/README.md)の確認事項に従います。

`deploy_swarm.sh` と `swarm_infra_deploy.sh` は bootstrap の互換 wrapper です。
app/system の通常更新は実行しません。bootstrap/Certbot を動かす manager の
スクリプト配置だけは引き続き必要です。

### Portainer UI の設定

| 項目 | app | system |
| --- | --- | --- |
| Stack name | `app` | `system` |
| Repository URL | `https://github.com/FEATO-org/it-infrastructure-server` | 同左 |
| Repository reference | `refs/heads/main` | 同左 |
| Compose path | `deploys/app/compose.yml` | `deploys/system/compose.yml` |
| GitOps updates | Webhook | Webhook |
| Re-pull image | 有効 | 有効 |
| Force redeployment | 有効 | 有効 |
| Relative path volumes | 不要 | 不要 |

`main` は mutable tag なので、GitOps/Webhook の **Re-pull image** を必ず有効にし、
同じ Git commit への再 build にも対応するため **Force redeployment** も有効にします。
独立した Git polling は image build 完了前に deploy する競合を作るので使用しません。
[Portainer GitOps](https://docs.portainer.io/user/docker/stacks/add)を参照してください。
[relative paths](https://docs.portainer.io/advanced/relative-paths)は Git checkout を
bind mount 元にする機能です。この構成では node の filesystem 配布を不要にするため
image 同梱を使用し、NFS や relative path volumes を必須にしません。

private repository は read-only Git 認証を Portainer 内に保存します。
GHCR package が private の場合は Portainer Registries に `ghcr.io` と `read:packages`
の資格情報を登録し、対象 environment で pull できることを確認します。
Cloudflare Access を経由する webhook は、既存 Access policy に専用 service token の
Service Auth を追加し、GitHub Secrets の `CF_ACCESS_CLIENT_ID` と
`CF_ACCESS_CLIENT_SECRET` に保存します。両方設定されると workflow が認証 header を
付けます。片方だけの設定は失敗にします。webhook URL は stack ごとの GitHub Secrets
にのみ保存し、既存 Access の保護を維持します。

Portainer Environment variables に以下を設定します。`.env` は Git に追加しません。

| Stack | 必須変数 | 任意変数（既定値） |
| --- | --- | --- |
| app | `DISCORD_TOKEN`, `GUILD_IDS`, `APP_MODE`, `NOTIFY_CHANNEL_ID` | `MINECRAFT_VERSION` (26.2), `BETTER_HORSES_SPIGET_RESOURCE` (124223), `MINECRAFT_SERVER_IMAGE`, `MINECRAFT_PROXY_IMAGE` (上記 image の main) |
| system | `NOTIFY_WEBHOOK_URL`, `ERROR_WEBHOOK_URL`, `LOKI_USER_ID`, `PROM_USER_ID`, `GRAFANA_API_KEY`, `APP_MODE`, `TLS_FULLCHAIN_SECRET`, `TLS_PRIVATE_KEY_SECRET` | `MARIADB_DATABASE`/`MARIADB_USER` (app), `PROMETHEUS_REMOTE_WRITE_HOST`, `METRICS_SCRAPE_INTERVAL` (2m), `NGINX_IMAGE`, `FLUENT_BIT_IMAGE`, `MARIADB_IMAGE` |

Discord webhook 変数は従来どおり `discord.com` に送る URI（`/api/webhooks/...`）です。
TLS の変数には上記 TLS state ファイルにある最新の **Swarm Secret 名**を指定します。
external secrets は bootstrap が検査する既存名のままです。
app: `forwarding_secret`, `floodgate_key`, `rcon_password`,
`minecraft_proxy_rcon_password`, `luckperms_db_password`。
system: `mariadb_root_password`, `mariadb_app_password`, `luckperms_db_password` と TLS 2件。
infra: `cloudflare_tunnel_token`。Secret の値を UI の image 設定や Git に転記しません。

### TLS rotation と Portainer の desired state

Certbot は引き続き manager で更新し、同じ命名方式で Secret を生成して nginx service
の Secret を差し替えます。Portainer system の古い Secret 名が次の GitOps deploy で
復元されないよう、移行時に `/etc/swarm/certbot.env` に次を追加します。

```dotenv
PORTAINER_URL=https://<trusted-portainer-origin>
PORTAINER_SYSTEM_STACK_ID=<system-stack-id>
PORTAINER_API_TOKEN_FILE=/etc/swarm/portainer-api-token
```

manager に Python 3 を用意し、system stack を管理できる API token を root-only
（0600）のファイルに保存します。Cloudflare Access 等で API を保護している場合は
manager から到達できる信頼済み HTTPS endpoint を用意します。Access service token が
必要な場合は `PORTAINER_ACCESS_TOKEN_FILE=/etc/swarm/portainer-access-token.json` を
追加し、`client_id` と `client_secret` の2キーを含む JSON を root-only 0600 で保存します。
TLS 検証は無効にしません。
`sync_portainer_tls.py` は Git 設定更新 API で TLS 2変数だけを置換し、既存の environment、
branch、Git 認証、GitOps、prune 設定を保存します。response や token はログに出しません。
nginx 更新の前に同期し、API エラーなら更新を止めます。次の timer 実行でも同期を再試行
するため、証明書が同じでも復旧できます。GitOps の deploy が進行中なら完了後に再試行します。

この API 連携は Portainer 本番での確認が必要です。移行作業中は system webhook を
無効のままにし、timer を一度実行して Portainer UI の TLS 2変数と nginx の Secret 名が
一致することを確認してから有効にしてください。手動 TLS rollback でも両方を揃えます。
Portainer 管理前は上記3変数を未設定にでき、従来の Certbot 単独運用を維持します。

### 日常更新と GitHub Actions

`Git push → Swarm images → GHCR → Portainer webhook → app/system update` が更新経路です。
workflow の path filter は変更された image だけを build し、PR は build/設定検証だけを
行います。main への push と main の手動実行だけが GHCR へ `main` と
`sha-<full commit SHA>` tag を公開します。全対象 image の build・設定検証・push 成功後に
対応 stack の webhook を呼びます。Compose のみの変更も対応 stack を更新します。
手動実行では全 image を build します。公開 image は `linux/amd64` と `linux/arm64` を含みます。

GitHub Settings → Secrets and variables → Actions に `PORTAINER_APP_WEBHOOK_URL` と
`PORTAINER_SYSTEM_WEBHOOK_URL` を別々に登録します。未設定なら image 公開を成功のまま
完了し、deploy はスキップします。webhook エラーは deploy job を失敗にします。
webhook 応答は task 更新完了を保証しないので、Portainer と下記 service 状態を確認します。
未変更 image の SHA tag は新しい commit には作られません。rollback 用に各 service の
最後に成功した image digest または SHA tag を記録してください。

### 既存構成の移行

1. GitOps/webhook を未設定のまま、現在の service spec、stack 設定、配置 node、image digest、
   TLS Secret 名を安全な場所へ記録します。app を停止して Minecraft/Proxy Volume と
   MariaDB を整合した状態でバックアップし、Portainer data もバックアップします。
2. 使用中の Git 管理外 Bedrock pack/custom mapping/ローカル Data Pack を回収して
   リポジトリの該当 asset directory へ取り込みます。ファイル名・hash・実際の読み込み先を
   照合します。Secret、鍵、world、DB、player data は取り込みません。
   Java resource pack は既存公開 URL と SHA-1 の配布方法を維持します。
   今回回収済みの6件と実行中 Proxy との照合結果は [ASSETS.md](../resources/minecraft/ASSETS.md) に記録しています。
3. main の image 公開完了を確認します。stack の保存先を変える前に、同じ Volume 名を
   同じラベル node で再利用することを確認します。`docker stack rm` はローカル named
   volume を削除しませんが、サービス停止を伴うため保守時間内に行います。
4. CLI 作成の external stack を Git Stack として新規登録できない場合は、保守時間内に
   `docker stack rm app`、`docker stack rm system` を行い、旧サービスと stack 内部 network の
   削除完了を待って、**同じ名前**で Portainer Git Stack を作成します。infra、external
   networks、secrets、volumes は削除しません。別名 stack の作成は新規空 Volume につながります。
5. system（MariaDB/監視/nginx）→ app の順で起動し、起動ログ、DB、Volume、Secret と
   Git 追跡設定の反映を確認します。旧 Swarm Config は rollback 用に残します。
6. TLS API 同期を設定・試験し、Java/Bedrock TCP/UDP/NetherNet、squaremap、監視を確認します。
   backend の task 再生成後、DNS 更新待ちを含め nginx 再起動なしで新規接続が回復することを
   保守時間内に確認します。既存の TCP session が再接続になること自体は変わりません。
7. webhook を登録して日常運用を開始します。各 node の古い checkout/asset を削除する前に、
   Java pack 公開元、manager の Certbot/systemd スクリプト、rollback 用 checkout の用途を確認します。

### rollback

まず webhook/GitOps を止めます。Portainer で image 変数を保存済み SHA tag または digest へ
戻して Pull and redeploy します。設定は image 内にあるため、該当 image を戻せば設定も戻ります。
TLS は引き続き最新 Secret 名を使い、Volume・network・placement は変えません。
Git の Compose 変更も戻す場合は rollback 用 branch/ref を選び、戻した Compose を確認します。

CLI 管理へ戻す場合は、保守時間内に Portainer app/system を削除し（Volume の削除は選択しない）、
旧 checkout と全 node の元の bind mount 資産を復元して、保存した旧 Compose を manager から
system → app の順に deploy します。必要な旧 Swarm Config と現在の TLS Secret を使います。
データを巻き戻す必要がある場合だけ、app/DB を停止して整合したバックアップを復元します。
infra と Cloudflare Tunnel は変更しません。

### メトリクス診断

Fluent Bit のログ tail、Discord、Loki と cAdvisor/mc-monitor/node_exporter_metrics から
Grafana Cloud `prometheus_remote_write` への経路は変更しません。取得間隔は
`METRICS_SCRAPE_INTERVAL` の既定 **2m** です。既存ラベルは `app_mode`、
`monitor=cadvisor` / `minecraft` / `node`、node の `instance=${HOSTNAME}` です。
追加のラベルは導入しません。

```bash
docker service ps system_fluent-bit --no-trunc
docker service ps system_cadvisor --no-trunc
docker service ps system_minecraft-monitor --no-trunc
docker service logs --since 30m system_fluent-bit
```

ログには既存のアプリケーション由来情報が含まれ得るため、共有前に確認してください。
Grafana Explore の Prometheus data source で、直近10分以上の範囲を選んで確認します。

```promql
count by (app_mode, monitor) ({monitor=~"cadvisor|minecraft|node"})
count({monitor="cadvisor"})
count({monitor="minecraft"})
count({monitor="node"})
topk(20, count by (__name__) ({__name__=~".+"}))
```

TODO: Fluent Bit と cAdvisor はともに global service です。`Host cadvisor` の service
VIP scrape は各 node の local cAdvisor を必ず収集できる保証がありません。node-local
scrape 方式の見直しは別作業です。Grafana Alloy への移行は今回は実装しません。

## 5. DNSとファイアウォール

- `api.feato.jp`と`dynmap.feato.jp`（squaremap。互換性のため既存ホスト名を維持）はCloudflare Proxyを有効化
- Minecraft Java/Bedrock用の`minecraft.feato.jp`はDNS Only
- `minecraft.feato.jp`はedgeノードIPへ向け、必要ならJava用SRVも設定

Cloudflare通常ProxyはMinecraft TCP/UDPを中継しません（Spectrumを契約する場合を
除く）ので、ゲーム用hostnameをWeb用hostnameと分けます。

nginxのpublishはSwarm routing meshではなく`mode: host`です。そのため
`edge=true`でnginxタスクが動くノードだけが次をlistenします。

- `80/tcp`、`443/tcp`
- `25565/tcp`
- `19132/tcp`
- `19132/udp`、`19133/udp`（NetherNet WebRTC）

UFWだけではDockerのpublish規則を十分に制御できないため、この構成でも
`ufw-docker`または同等の`DOCKER-USER`ルールが必要です。80/443は可能なら
Cloudflareの公開IP rangeだけを許可し、Minecraftポートは利用方針に沿って制限
してください。`ports:`を持たない他サービスのために追加の許可規則を作る必要は
ありません。Xserver側のパケットフィルターも同じallowlistに揃えます。

## 6. 確認

```bash
docker stack services app
docker stack services system
docker stack services infra
docker service ps system_nginx
docker service logs --since 10m system_nginx
docker service logs --since 10m infra_cloudflared
systemctl list-timers swarm-certbot-renew.timer
```

2台以上のedgeノードで、片方を`docker node update --availability drain <NODE>`に
してもHTTPSが応答することを本番公開前に確認してください。
