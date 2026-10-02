FROM itzg/mc-proxy:java25
LABEL org.opencontainers.image.source="https://github.com/FEATO-org/it-infrastructure-server"
COPY minecraft-proxy/proxy-rcon-entrypoint.sh /rcon-init/proxy-rcon-entrypoint.sh
COPY minecraft-proxy/patches/ /patches/
COPY minecraft-proxy/config/ /config/
COPY minecraft-proxy/plugins/ /plugins/
COPY resources/minecraft/resourcepacks/bedrock/ /plugins/Geyser-Velocity/packs/
COPY resources/minecraft/geyser/custom_mappings/ /plugins/Geyser-Velocity/custom_mappings/
