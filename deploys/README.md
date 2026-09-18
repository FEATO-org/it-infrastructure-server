# Docker Swarm production deployment

この構成は次の3スタックをデプロイします。

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
openssl rand -hex 32 | docker secret create forwarding_secret -
openssl rand -base64 32 | docker secret create rcon_password -
docker secret create cloudflare_tunnel_token /secure/path/cloudflare-tunnel-token
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

## 4. 環境変数とデプロイ

既存の`.env`をmanagerだけに配置し、最低でもスクリプトが検査する
変数を設定します。repositoryの絶対パスは全ての`minecraft-data`ノードで同じに
してください。外部アセットを別の場所へ置く場合は`MINECRAFT_ASSET_ROOT`を設定
します。

```bash
# 単一ノードでは配置先ノード上で先にGraalVMイメージを作成
./script/build_minecraft_graalvm.sh
sudo -E TLS_STATE_FILE=/var/lib/swarm-certbot/swarm-secrets.env \
  ./script/deploy_swarm.sh
```

スクリプトは4つの暗号化overlay networkを必要時に作成し、`app`、`system`、
`infra`の順で更新します。

## 5. DNSとファイアウォール

- `api.feato.jp`と`minecraft.feato.jp`（Web map）はCloudflare Proxyを有効化
- Minecraft Java/Bedrock用の`play.feato.jp`はDNS Only
- `play.feato.jp`はedgeノードIPへ向け、必要ならJava用SRVも設定

Cloudflare通常ProxyはMinecraft TCP/UDPを中継しません（Spectrumを契約する場合を
除く）ので、ゲーム用hostnameをWeb用hostnameと分けます。

nginxのpublishはSwarm routing meshではなく`mode: host`です。そのため
`edge=true`でnginxタスクが動くノードだけが次をlistenします。

- `80/tcp`、`443/tcp`
- `25565/tcp`
- `19132/udp`

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
