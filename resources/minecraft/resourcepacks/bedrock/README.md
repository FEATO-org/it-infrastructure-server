# Bedrock resource packs

Place Bedrock `.mcpack` or `.zip` files directly in this directory. They must be tracked in Git before the Velocity image build and are embedded at `/plugins/Geyser-Velocity/packs`.

Backpack Plus 3.2.0は[公式Bedrock配布](https://www.dropbox.com/scl/fo/0ndsqtxuuh81dztlmmf0q/AH-umlGt2pp0asmKN7lJ_ao?rlkey=yufp61f6zkkso0h0xvscwrply&dl=0)の`backpackplus_geyser_resources.mcpack`をこのディレクトリへ配置します。本番で使用中の対応するmappingは`../../geyser/custom_mappings/geyser_item_mappings.json`に統合されています。使用中の配布物をGitへ取り込み、Velocity imageから配布します。

The current [ValhallaMMO Geyser Resource Pack Wiki](https://github.com/Athlaeos/ValhallaMMO/wiki/Geyser-Resource-Pack-%F0%9F%8E%A8) links `ValhallaMMO_Geyser.zip`, containing `ValhallaMMObedrock.mcpack`, `ValhallaMMOmappings.json`, and an obsolete `GeyserOptionalPack`. The Wiki labels this contribution as unofficial and unmaintained and does not state compatibility with ValhallaMMO 1.10.3 or Minecraft 26.2. Do not deploy the bundled `GeyserOptionalPack`.

When compatibility has been verified, place only `ValhallaMMObedrock.mcpack` here and place `ValhallaMMOmappings.json` in `../../geyser/custom_mappings/`. Track any newly adopted assets in Git before building the image.

現在同梱する `pack.zip` は本番で配信中の `feato_bedrock_resources_pack` をそのまま回収したものです。
ファイル一覧と SHA-256 は [ASSETS.md](../../ASSETS.md) を参照してください。
