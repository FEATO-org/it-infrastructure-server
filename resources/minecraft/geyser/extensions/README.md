# Geyser extensions

EmoteOffhand is a Geyser Extension, not a Velocity Plugin. Place the managed
`EmoteOffhand.jar` directly in this directory; it is intentionally excluded
from Git by the repository-wide `*.jar` rule.

The artifact is copied to the VPS only when
`script/copy_plugins_to_remote.sh` is run, then mounted read-only into the
container. A normal deploy neither downloads nor copies this JAR.

| Location | Path |
| --- | --- |
| Management host | `resources/minecraft/geyser/extensions/EmoteOffhand.jar` |
| VPS (default) | `/opt/it-infrastructure-server/resources/minecraft/geyser/extensions/EmoteOffhand.jar` |
| Container | `/plugins/Geyser-Velocity/extensions/EmoteOffhand.jar` |

## Source and updates

- Modrinth Project ID: `pVsz9nZm`
- Version ID: `YiejycoE`
- Artifact: `EmoteOffhand.jar`
- Download URL: <https://cdn.modrinth.com/data/pVsz9nZm/versions/YiejycoE/EmoteOffhand.jar?mr_download_reason=standalone&mr_game_version=1.21.11&mr_loader=geyser>

To update, obtain the intended JAR manually, replace
`EmoteOffhand.jar` in this directory, then rerun
`script/copy_plugins_to_remote.sh`. Do not add an automatic download step to
the deployment workflow.
