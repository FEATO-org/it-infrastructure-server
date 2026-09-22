# FEATO リソースパック統合

このツールは、ValhallaMMO、Gun Core Resources V1.0.15、Modern Guns Resources V1.9.3 を統合し、第三者アセットを改変しない単一のサーバー用リソースパックを作成します。以下から取得したZIPを `sources/` に置き、次を実行します。

- ValhallaMMO: サーバーコンソールで `/val resourcepack download` を実行する。詳細は[公式Resource Pack手順](https://github.com/Athlaeos/ValhallaMMO/wiki/Default-Resource-Pack-%F0%9F%8E%A8)を参照する。
- Gun Core Resources V1.0.15: [ZIPを取得](https://cdn.modrinth.com/data/Ti7LgRXJ/versions/X7knYm9t/Gun%20Core%20-%20Resources%20V1.0.15.zip)
- Modern Guns Resources V1.9.3: [ZIPを取得](https://cdn.modrinth.com/data/ufgOyMFr/versions/bcKCNJp2/Modern%20Guns%20-%20Resources%20V1.9.3.zip)

```bash
python minecraft/java/resourcepack/merge.py \
  --output minecraft/java/resourcepack/dist/feato-resource-pack.zip \
  minecraft/java/resourcepack/sources/ValhallaMMO.zip \
  "minecraft/java/resourcepack/sources/Gun Core - Resources V1.0.15.zip" \
  "minecraft/java/resourcepack/sources/Modern Guns - Resources V1.9.3.zip"
```

出力ZIPと隣接する`.sha1`ファイルはGit管理対象外です。ZIPを実在する公開URLで配布した後、`.sha1`ファイルの40文字の値をMinecraftの`resource-pack-sha1`へ設定してください。`overrides/pack.png`がある場合のみ出力パックのアイコンとして採用し、入力パック内の`pack.png`は使用しません。

複数の入力に同じパスで異なる内容のファイルがある場合、統合はエラーで終了します。互換性のある上流パックを選択して解消し、Modern Gunsのアセットは編集しないでください。

Gun Coreは[公式Modrinthプロジェクト](https://modrinth.com/datapack/gun-core)からのみ取得してください。Gun CoreはGGCL v1.1で配布されており、配布用バンドルには当該プロジェクトへの明確な帰属表示が必要です。Modern Gunsも[公式Modrinthプロジェクト](https://modrinth.com/datapack/modern-guns)からのみ取得してください。ライセンスはCC BY-NC-ND 4.0です。
