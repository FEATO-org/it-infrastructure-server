# Geyser custom mappings

Place Geyser custom mapping `.json` files directly in this directory. They must be tracked in Git before the Velocity image build and are embedded at `/plugins/Geyser-Velocity/custom_mappings`.

Backpack Plus 3.2.0の[公式Bedrock配布](https://www.dropbox.com/scl/fo/0ndsqtxuuh81dztlmmf0q/AH-umlGt2pp0asmKN7lJ_ao?rlkey=yufp61f6zkkso0h0xvscwrply&dl=0)に含まれる`geyser_mappings.json`は旧`format_version: 1`です。Geyser 2.9.3以降ではv1がdeprecatedのため、本番ではBackpack Plusを含むCustomModelData、Bedrock identifier、iconをv2 `legacy`定義へ変換した`geyser_item_mappings.json`へ統合しています。使用中の配布物をGitへ取り込み、Velocity imageから配布します。

The current [ValhallaMMO Geyser Resource Pack Wiki](https://github.com/Athlaeos/ValhallaMMO/wiki/Geyser-Resource-Pack-%F0%9F%8E%A8) names its mapping `ValhallaMMOmappings.json`, but labels the distribution as unofficial and unmaintained and gives no compatible ValhallaMMO or Minecraft version. Its mapping uses deprecated Geyser custom-item format v1. Verify compatibility with ValhallaMMO 1.10.3 and Minecraft 26.2 before placing the unmodified file here.

本番で読み込んでいる4件を内容変更なしで追跡しています。item mapping は format v2、
block/skull/waypoint の3件は既存の空の format v1 定義を維持します。
ファイル一覧と SHA-256 は [ASSETS.md](../../ASSETS.md) を参照してください。
