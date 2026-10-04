FROM itzg/minecraft-server:java25-graalvm
LABEL org.opencontainers.image.source="https://github.com/FEATO-org/it-infrastructure-server"
COPY minecraft/java/plugins.txt minecraft/java/datapacks.txt minecraft/java/copy-floodgate-key.sh /extras/
COPY minecraft/java/datapacks/ /extras/datapacks/
COPY minecraft/java/plugins/ /plugins/
COPY minecraft/java/config/bukkit.yml minecraft/java/config/spigot.yml /config/
COPY minecraft/java/config/paper-global.yml minecraft/java/config/paper-world-defaults.yml /config/config/
