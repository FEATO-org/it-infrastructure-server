# Geyser custom mappings

Place Geyser custom mapping `.json` files directly in this directory. They are copied to the deployment node by `script/copy_plugins_to_remote.sh` and mounted read-only at `/plugins/Geyser-Velocity/custom_mappings`.

Backpack Plus 3.2.0の[公式Bedrock配布](https://www.dropbox.com/scl/fo/0ndsqtxuuh81dztlmmf0q/AH-umlGt2pp0asmKN7lJ_ao?rlkey=yufp61f6zkkso0h0xvscwrply&dl=0)に含まれる`geyser_mappings.json`は旧`format_version: 1`です。Geyser 2.9.3以降ではv1がdeprecatedのため、同じCustomModelData、Bedrock identifier、iconを現行v2 `legacy`定義へ変換した`backpackplus_geyser_mappings.json`を配置します。配布物はGit管理対象外です。

The current [ValhallaMMO Geyser Resource Pack Wiki](https://github.com/Athlaeos/ValhallaMMO/wiki/Geyser-Resource-Pack-%F0%9F%8E%A8) names its mapping `ValhallaMMOmappings.json`, but labels the distribution as unofficial and unmaintained and gives no compatible ValhallaMMO or Minecraft version. Its mapping uses deprecated Geyser custom-item format v1. Verify compatibility with ValhallaMMO 1.10.3 and Minecraft 26.2 before placing the unmodified file here.
