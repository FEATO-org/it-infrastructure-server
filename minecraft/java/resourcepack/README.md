# FEATO resource-pack merge

This tool produces a single server resource pack from the ValhallaMMO pack, Gun Core Resources V1.0.15, and Modern Guns Resources V1.9.3 without altering third-party asset files. Download the official ZIP releases, place them in `sources/`, then run:

```bash
python minecraft/java/resourcepack/merge.py \
  --output minecraft/java/resourcepack/dist/feato-resource-pack.zip \
  minecraft/java/resourcepack/sources/ValhallaMMO.zip \
  "minecraft/java/resourcepack/sources/Gun Core - Resources V1.0.15.zip" \
  "minecraft/java/resourcepack/sources/Modern Guns - Resources V1.9.3.zip"
```

The output ZIP and adjacent `.sha1` file are ignored by Git. Use the exact 40-character SHA-1 file content for Minecraft's `resource-pack-sha1` setting after hosting the ZIP at a real public URL. `overrides/pack.png`, when present, becomes the output icon; input `pack.png` files are never used.

The merge fails if two inputs provide different bytes at the same path. Resolve such conflicts by choosing compatible upstream packs; do not edit Modern Guns assets.

Download Gun Core only from its [official Modrinth project](https://modrinth.com/datapack/gun-core). Gun Core is licensed under GGCL v1.1; any distributed bundle must visibly attribute that project. Download Modern Guns only from its [official Modrinth project](https://modrinth.com/datapack/modern-guns); it is licensed under CC BY-NC-ND 4.0.
