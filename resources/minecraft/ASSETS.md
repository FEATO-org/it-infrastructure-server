# Image に同梱する Minecraft アセット

2026-10-03 に、稼働中 Swarm service の bind mount 配布元から読み取り回収しました。
既存 Bedrock pack 2件と custom mapping 4件の内容は変更していません。
稼働中 Proxy の `/server/plugins/Geyser-Velocity/` にある6件とも SHA-256 が一致しました。
source は deployment node の `resources/minecraft/` 以下で、同名ファイルを Git で追跡し、
Velocity image の `/plugins/Geyser-Velocity/packs` / `custom_mappings` へ同梱します。
起動時は既存 itzg 処理が `/server/plugins/Geyser-Velocity/` へコピーします。

| ファイル | 回収時 SHA-256 |
| --- | --- |
| `resources/minecraft/resourcepacks/bedrock/backpackplus_geyser_resources.mcpack` | `d8d81c7eedaef54452db09b203f571bc158ad18e9e8bc05600abbbf19eda9906` |
| `resources/minecraft/resourcepacks/bedrock/pack.zip` | `225b1af7610a2c0610a38e7d3abcccf663c67501fbb180e9264a03edd74269e1` |
| `resources/minecraft/geyser/custom_mappings/geyser_waypoint_style_mappings.json` | `805f3d6ccaffe4ecc7ef675577697c8322cbe405141d6be42dc254803e2329e7` |
| `resources/minecraft/geyser/custom_mappings/geyser_block_mappings.json` | `169a987d970ebcd674923a44aac3de80931cd31b69f5561408c86f4a6e81d85f` |
| `resources/minecraft/geyser/custom_mappings/geyser_item_mappings.json` | `76616189b17f853f50ab6b493f49a5e99a40989f364f9814812917870f44298a` |
| `resources/minecraft/geyser/custom_mappings/geyser_skull_mappings.json` | `12065cbe8daa26d70cdf37a3f795046ac9ab33770dabc5fe24017ff44575433d` |

本番側の curated `minecraft/java/datapacks/` に ZIP はありませんでした。
Data Pack の URL 一覧と `/extras/datapacks` の取り扱いは維持します。
Java resource pack の公開配信と Geyser Extension の既存未接続の配布経路は別管理です。
Git 管理対象を本番だけで更新せず、次の image build 前に変更を取り込んでください。
