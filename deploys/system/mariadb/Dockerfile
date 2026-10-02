FROM mariadb:13.0.2
LABEL org.opencontainers.image.source="https://github.com/FEATO-org/it-infrastructure-server"
COPY --chmod=755 deploys/system/mariadb/init-luckperms.sh /docker-entrypoint-initdb.d/20-luckperms.sh
