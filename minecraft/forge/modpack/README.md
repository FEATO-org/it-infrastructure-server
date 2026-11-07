# Forge Modpack 調査用資料（未導入）

このディレクトリは提供された CurseForge カスタムプロファイル「イワシコ寄生虫」の導入準備用です。サーバー構成には接続されておらず、この資料だけではデプロイできません。

- `manifest.json` と `modlist.html` は提供 ZIP から抽出したもの（`modlist.html` は改行と BOM を正規化）。ZIP の SHA-256 は `8358ed7acf2d8385fc8b9209e114d587e2920fd97ba8fa44b6796f3f82b678a6`。
- Manifest は Minecraft 1.20.1、Forge 47.4.28、40 件の CurseForge project ID / file ID を指定する。ファイルの取得可否、依存関係、サーバーでの動作は未検証。
- ZIP の `overrides` は `config/` 以下 165 ファイルを含む。クライアント設定とサーバー向け設定の選別、ワールド固有の serverconfig の適用先、既存設定の更新時の扱いを確認してから取り込む。現時点では未収録。
- [Auto CurseForge](https://docker-minecraft-server.readthedocs.io/en/latest/types-and-platforms/mod-platforms/auto-curseforge/) は非公開 manifest と固定された file ID を扱えるが、サーバー専用除外、手動ダウンロードが必要なファイル、依存関係を確認する必要がある。Java 17 以降の現行イメージには API key が含まれるが、別途 key を指定することもできる。
- [Velocity の互換性資料](https://docs.papermc.io/velocity/server-compatibility/)は Forge 1.13–1.20.1 に Ambassador を案内し、Modern Forwarding には Proxy Compatible Forge を指定している。Velocity 4.2.0 とこの Modpack の組み合わせは未検証。既存の forwarding secret を安全に渡す起動処理と、実接続での UUID 検証が必要。
- Geyser / Floodgate のアセットを保全しつつ Bedrock 接続を明示的に拒否する方法、Paper の切戻し、Volume 分離、監視先の切替も未実装。

Paper のレプリカ数、Velocity の接続先、公開ポートは変更していない。Forge 導入と利用者向け変更記録は上記を解決した後に追加する。
