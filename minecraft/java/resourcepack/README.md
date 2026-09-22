# FEATO リソースパック統合

このツールは、Magic 11.2.4公式のMagic+ValhallaMMO pack、Gun Core Resources V1.0.15、Modern Guns Resources V1.9.3、Backpack Plus 3.2.0用resource packを統合し、第三者アセットを改変しない単一のサーバー用リソースパックを作成します。以下から取得したZIPを `sources/` に置き、次を実行します。

- Magic+ValhallaMMO: [Magic-valhalla-RP-26.2.zip](https://rp.elmakers.com/Magic-valhalla-RP-26.2.zip)
- Gun Core Resources V1.0.15: [ZIPを取得](https://cdn.modrinth.com/data/Ti7LgRXJ/versions/X7knYm9t/Gun%20Core%20-%20Resources%20V1.0.15.zip)
- Modern Guns Resources V1.9.3: [ZIPを取得](https://cdn.modrinth.com/data/ufgOyMFr/versions/bcKCNJp2/Modern%20Guns%20-%20Resources%20V1.9.3.zip)
- Backpack Plus 3.2.0: [公式ページ掲載の1.21.4用resource pack](https://www.dropbox.com/scl/fi/b0orwjwm7q342fkidewjq/BackpackPlus_Resourcepack_1_21_4.zip?rlkey=ynawukzi4gjb2evsp1ghq4mvb&dl=1)

```bash
python minecraft/java/resourcepack/merge.py \
  --output minecraft/java/resourcepack/dist/feato-resource-pack.zip \
  minecraft/java/resourcepack/sources/Magic-valhalla-RP-26.2.zip \
  "minecraft/java/resourcepack/sources/Gun Core - Resources V1.0.15.zip" \
  "minecraft/java/resourcepack/sources/Modern Guns - Resources V1.9.3.zip" \
  minecraft/java/resourcepack/sources/BackpackPlus_Resourcepack_1_21_4.zip
```

生成後は `resources/minecraft/resourcepacks/java/feato-resource-pack.zip` へコピーし、`script/copy_plugins_to_remote.sh` でdeployment nodeへ配布します。

出力ZIPと隣接する`.sha1`ファイルはGit管理対象外です。ZIPを実在する公開URLで配布した後、`.sha1`ファイルの40文字の値をMinecraftの`resource-pack-sha1`へ設定してください。`pack.mcmeta`は統合用設定へ置き換え、`overrides/pack.png`がある場合のみ出力パックのアイコンとして採用します。入力パック固有の`pack.png`とルートの`version.txt`は出力しません。

複数の入力に同じパスで異なる内容のファイルがある場合、原則として統合はエラーで終了します。`assets/*/lang/*.json`と`assets/*/sounds.json`はエントリをキー単位で統合します。`assets/minecraft/items/*.json`は、同一fallbackを持つ`custom_model_data`の`range_dispatch`に限り、thresholdを衝突検知して昇順に統合します。同じキー／thresholdの値が異なる場合や、不正なJSON・重複キーがある場合はエラーで停止し、後勝ち上書きは行いません。言語ファイルでは文字列以外の値も拒否します。Modern Gunsのアセットは編集しないでください。

2026-09-22時点の入力では、Magic+ValhallaMMOとGun Coreの`assets/minecraft/lang/en_us.json`はキーの重複がなく、Gun CoreとModern Gunsの`assets/gbg/sounds.json`は共通キーの値が一致しています。Magic+ValhallaMMOとBackpack Plusの`assets/minecraft/items/brown_dye.json`は、互いに重複しないCustomModelDataを保持して統合できます。MagicとBackpack Plus側の自動配布は無効化しており、このFEATO統合packだけをサーバー設定から配布します。

Gun Coreは[公式Modrinthプロジェクト](https://modrinth.com/datapack/gun-core)からのみ取得してください。Gun CoreはGGCL v1.1で配布されており、配布用バンドルには当該プロジェクトへの明確な帰属表示が必要です。Modern Gunsも[公式Modrinthプロジェクト](https://modrinth.com/datapack/modern-guns)からのみ取得してください。ライセンスはCC BY-NC-ND 4.0です。
