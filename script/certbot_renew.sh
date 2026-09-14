#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

CERTBOT_IMAGE="${CERTBOT_IMAGE:-certbot/dns-cloudflare:v5.8.0}"
CERTBOT_STATE_DIR="${CERTBOT_STATE_DIR:-/var/lib/swarm-certbot}"
CLOUDFLARE_API_TOKEN_FILE="${CLOUDFLARE_API_TOKEN_FILE:-/etc/swarm/cloudflare-dns-token}"
TLS_STATE_FILE="${TLS_STATE_FILE:-${CERTBOT_STATE_DIR}/swarm-secrets.env}"
NGINX_SERVICE="${NGINX_SERVICE:-system_nginx}"
TLS_SECRET_PREFIX="${TLS_SECRET_PREFIX:-feato_tls}"
CERTBOT_CERT_NAME="${CERTBOT_CERT_NAME:-feato.jp}"
CERTBOT_EMAIL="${CERTBOT_EMAIL:-${DEFAULT_EMAIL:-}}"
CERTBOT_DOMAINS="${CERTBOT_DOMAINS:-feato.jp,*.feato.jp}"

if [[ "$(docker info --format '{{.Swarm.ControlAvailable}}')" != "true" ]]; then
  echo "Run this script on a Swarm manager." >&2
  exit 1
fi

if [[ -z "${CERTBOT_EMAIL}" ]]; then
  echo "CERTBOT_EMAIL (or DEFAULT_EMAIL) is required." >&2
  exit 1
fi

if [[ ! -r "${CLOUDFLARE_API_TOKEN_FILE}" ]]; then
  echo "Cloudflare API token file is not readable: ${CLOUDFLARE_API_TOKEN_FILE}" >&2
  exit 1
fi

install -d -m 0700 "${CERTBOT_STATE_DIR}"
credentials_file="$(mktemp "${CERTBOT_STATE_DIR}/cloudflare.ini.XXXXXX")"
trap 'rm -f "${credentials_file}"' EXIT

token="$(tr -d '\r\n' < "${CLOUDFLARE_API_TOKEN_FILE}")"
if [[ -z "${token}" ]]; then
  echo "Cloudflare API token file is empty." >&2
  exit 1
fi
printf 'dns_cloudflare_api_token = %s\n' "${token}" > "${credentials_file}"
unset token

IFS=',' read -r -a domain_list <<< "${CERTBOT_DOMAINS}"
domain_args=()
for domain_name in "${domain_list[@]}"; do
  domain_name="${domain_name#"${domain_name%%[![:space:]]*}"}"
  domain_name="${domain_name%"${domain_name##*[![:space:]]}"}"
  [[ -n "${domain_name}" ]] && domain_args+=(-d "${domain_name}")
done

if (( ${#domain_args[@]} == 0 )); then
  echo "CERTBOT_DOMAINS must contain at least one domain." >&2
  exit 1
fi

docker run --rm \
  --volume "${CERTBOT_STATE_DIR}:/etc/letsencrypt" \
  --volume "${credentials_file}:/run/secrets/cloudflare.ini:ro" \
  "${CERTBOT_IMAGE}" \
  certonly \
  --non-interactive \
  --agree-tos \
  --keep-until-expiring \
  --email "${CERTBOT_EMAIL}" \
  --cert-name "${CERTBOT_CERT_NAME}" \
  --dns-cloudflare \
  --dns-cloudflare-credentials /run/secrets/cloudflare.ini \
  --dns-cloudflare-propagation-seconds 30 \
  "${domain_args[@]}"

fullchain_file="${CERTBOT_STATE_DIR}/live/${CERTBOT_CERT_NAME}/fullchain.pem"
private_key_file="${CERTBOT_STATE_DIR}/live/${CERTBOT_CERT_NAME}/privkey.pem"

if [[ ! -s "${fullchain_file}" || ! -s "${private_key_file}" ]]; then
  echo "Certbot completed but certificate files were not found." >&2
  exit 1
fi

if command -v openssl >/dev/null 2>&1; then
  openssl x509 -in "${fullchain_file}" -noout -checkend 604800
fi

certificate_hash="$(sha256sum "${fullchain_file}" | awk '{print substr($1,1,16)}')"
secret_version="${certificate_hash}"
new_fullchain_secret="${TLS_SECRET_PREFIX}_fullchain_${secret_version}"
new_private_key_secret="${TLS_SECRET_PREFIX}_privkey_${secret_version}"

if ! docker secret inspect "${new_fullchain_secret}" >/dev/null 2>&1; then
  docker secret create "${new_fullchain_secret}" "${fullchain_file}" >/dev/null
fi
if ! docker secret inspect "${new_private_key_secret}" >/dev/null 2>&1; then
  docker secret create "${new_private_key_secret}" "${private_key_file}" >/dev/null
fi

state_file_tmp="$(mktemp "${CERTBOT_STATE_DIR}/swarm-secrets.env.XXXXXX")"
printf 'TLS_FULLCHAIN_SECRET=%q\n' "${new_fullchain_secret}" > "${state_file_tmp}"
printf 'TLS_PRIVATE_KEY_SECRET=%q\n' "${new_private_key_secret}" >> "${state_file_tmp}"
chmod 0600 "${state_file_tmp}"
mv -f "${state_file_tmp}" "${TLS_STATE_FILE}"

if ! docker service inspect "${NGINX_SERVICE}" >/dev/null 2>&1; then
  echo "Created TLS secrets. Deploy the system stack using ${TLS_STATE_FILE}."
  exit 0
fi

old_fullchain_secret="$(
  docker service inspect \
    --format '{{range .Spec.TaskTemplate.ContainerSpec.Secrets}}{{if eq .File.Name "tls_fullchain.pem"}}{{.SecretName}}{{end}}{{end}}' \
    "${NGINX_SERVICE}"
)"
old_private_key_secret="$(
  docker service inspect \
    --format '{{range .Spec.TaskTemplate.ContainerSpec.Secrets}}{{if eq .File.Name "tls_privkey.pem"}}{{.SecretName}}{{end}}{{end}}' \
    "${NGINX_SERVICE}"
)"

if [[ "${old_fullchain_secret}" == "${new_fullchain_secret}" &&
      "${old_private_key_secret}" == "${new_private_key_secret}" ]]; then
  echo "Certificate is unchanged; nginx already uses the current secrets."
  exit 0
fi

update_args=(
  --update-parallelism 1
  --update-delay 10s
  --update-order stop-first
)

[[ -n "${old_fullchain_secret}" ]] && update_args+=(--secret-rm "${old_fullchain_secret}")
[[ -n "${old_private_key_secret}" ]] && update_args+=(--secret-rm "${old_private_key_secret}")
update_args+=(
  --secret-add "source=${new_fullchain_secret},target=tls_fullchain.pem"
  --secret-add "source=${new_private_key_secret},target=tls_privkey.pem"
)

docker service update "${update_args[@]}" "${NGINX_SERVICE}"
echo "nginx now uses TLS secrets for certificate version ${secret_version}."
echo "Previous secrets were retained so the prior certificate remains recoverable."
