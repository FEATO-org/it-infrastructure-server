# it-infrastructure-server

Docker Swarm 上の本番インフラと Minecraft サーバーを管理します。

```mermaid
flowchart TB
    Git[Git push] --> Actions[GitHub Actions]
    Actions --> GHCR[GHCR custom images]
    Actions --> Portainer
    Bootstrap[Swarm bootstrap] --> Infra[infra: Portainer / Agent / Cloudflare Tunnel]
    Infra --> Portainer
    Portainer --> App[app: Discord Bot / Velocity / Paper]
    Portainer --> System[system: nginx / MariaDB / Fluent Bit / cAdvisor / mc-monitor]
    Player[Java / Bedrock / Web] --> Nginx[nginx]
    Nginx --> Velocity[Velocity / Geyser / Floodgate]
    Velocity --> Paper[Paper / squaremap]
    FluentBit[Fluent Bit] --> Grafana[Grafana Cloud: Loki / Prometheus]
    Certbot[manager: Certbot timer] --> TLS[Swarm TLS secrets / Portainer environment]
```

日常更新は Git push → GitHub Actions → GHCR → Portainer → app/system です。
初期構築と infra の更新は bootstrap から行います。

- [本番構築・Portainer 設定・移行・rollback](deploys/README.md)
- [Minecraft 構成と実機確認](minecraft/README.md)
- [採用バージョン](deploys/versions.md)
- [ユーザー向け変更記録](changes/README.md)
