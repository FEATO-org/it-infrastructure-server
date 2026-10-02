#!/usr/bin/env bash
set -Eeuo pipefail
image="${1:?Usage: validate_image.sh IMAGE KIND}"
kind="${2:?Usage: validate_image.sh IMAGE KIND}"
case "$kind" in
  nginx)
    cert_dir="$(mktemp -d)"
    trap 'rm -rf -- "$cert_dir"' EXIT
    openssl req -x509 -nodes -newkey rsa:2048 -days 1 \
      -keyout "$cert_dir/tls_privkey.pem" -out "$cert_dir/tls_fullchain.pem" \
      -subj /CN=validation.invalid >/dev/null 2>&1
    docker run --rm --network none --entrypoint nginx \
      --volume "$cert_dir:/run/secrets:ro" "$image" -t
    ;;
  fluent-bit)
    docker run --rm --network none --entrypoint /fluent-bit/bin/fluent-bit \
      -e NOTIFY_WEBHOOK_URL=/validation -e ERROR_WEBHOOK_URL=/validation \
      -e LOKI_USER_ID=validation -e PROM_USER_ID=validation \
      -e GRAFANA_API_KEY=validation -e APP_MODE=validation \
      -e METRICS_SCRAPE_INTERVAL=2m -e PROMETHEUS_REMOTE_WRITE_HOST=validation.invalid \
      "$image" --dry-run -c /fluent-bit/etc/fluent-bit.conf
    ;;
  minecraft-server)
    docker run --rm --network none --entrypoint sh "$image" -ec \
      'test -s /extras/plugins.txt; test -s /extras/datapacks.txt; test -d /extras/datapacks; test -d /plugins; test -s /config/config/paper-global.yml; sh -n /extras/copy-floodgate-key.sh'
    ;;
  minecraft-proxy)
    docker run --rm --network none --entrypoint bash "$image" -ec \
      'bash -n /rcon-init/proxy-rcon-entrypoint.sh; test -s /patches/geyser-nethernet.json; test -s /config/velocity.toml; test -s /plugins/Geyser-Velocity/config.yml; test -d /plugins/Geyser-Velocity/packs; test -d /plugins/Geyser-Velocity/custom_mappings; test -s /plugins/Geyser-Velocity/packs/pack.zip; test -s /plugins/Geyser-Velocity/packs/backpackplus_geyser_resources.mcpack; test -s /plugins/Geyser-Velocity/custom_mappings/geyser_item_mappings.json'
    ;;
  mariadb)
    docker run --rm --network none --entrypoint bash "$image" \
      -n /docker-entrypoint-initdb.d/20-luckperms.sh
    ;;
  *) echo "Unknown image kind: $kind" >&2; exit 1 ;;
esac
