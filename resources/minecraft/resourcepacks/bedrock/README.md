# Bedrock resource packs

Place Bedrock `.mcpack` or `.zip` files directly in this directory. They are copied to the deployment node by `script/copy_plugins_to_remote.sh` and mounted read-only at `/plugins/Geyser-Velocity/packs`.

Backpack Plus 3.2.0は[公式Bedrock配布](https://www.dropbox.com/scl/fo/0ndsqtxuuh81dztlmmf0q/AH-umlGt2pp0asmKN7lJ_ao?rlkey=yufp61f6zkkso0h0xvscwrply&dl=0)の`backpackplus_geyser_resources.mcpack`をこのディレクトリへ配置します。対応するmappingは`../../geyser/custom_mappings/backpackplus_geyser_mappings.json`です。配布物はGit管理対象外です。

The current [ValhallaMMO Geyser Resource Pack Wiki](https://github.com/Athlaeos/ValhallaMMO/wiki/Geyser-Resource-Pack-%F0%9F%8E%A8) links `ValhallaMMO_Geyser.zip`, containing `ValhallaMMObedrock.mcpack`, `ValhallaMMOmappings.json`, and an obsolete `GeyserOptionalPack`. The Wiki labels this contribution as unofficial and unmaintained and does not state compatibility with ValhallaMMO 1.10.3 or Minecraft 26.2. Do not deploy the bundled `GeyserOptionalPack`.

When compatibility has been verified, place only `ValhallaMMObedrock.mcpack` here and place `ValhallaMMOmappings.json` in `../../geyser/custom_mappings/`. Third-party assets are intentionally ignored by Git.
