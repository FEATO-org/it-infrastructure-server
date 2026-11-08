# イワシコ寄生虫 Modpack

提供 ZIP の SHA-256 は `8358ed7acf2d8385fc8b9209e114d587e2920fd97ba8fa44b6796f3f82b678a6`。`manifest.json` は Minecraft 1.20.1 / Forge 47.4.28 と 44 組の CurseForge project ID / file ID を固定する。`modlist.html` は ZIP の一覧を改行正規化したもの。共有 URL は取得元に使わない。

[Auto CurseForge](https://docker-minecraft-server.readthedocs.io/en/latest/types-and-platforms/mod-platforms/auto-curseforge/) で manifest を使う。Java 17 イメージの組み込み API key を使用し、配布制限されたファイルがあれば起動ログに示される手順に従い同じ ID のファイルを手動取得する。キーを変更する必要があるときは Swarm secret と `CF_API_KEY_FILE` を使用し、Git に記載しない。

以下はサーバーから除外する: Inventory Profiles Next (495267)、libIPN (679177)、Embeddium (908741)、Just Enough Resources (240630)、Sound Physics Remastered (535489)。[Inventory Profiles Next](https://www.curseforge.com/minecraft/mc-mods/inventory-profiles-next) と [libIPN](https://www.curseforge.com/minecraft/mc-mods/libipn) はクライアント用、[Embeddium](https://www.curseforge.com/minecraft/mc-mods/embeddium) はクライアント描画用、[JER](https://www.curseforge.com/minecraft/mc-mods/just-enough-resources-jer) はクライアント向け JEI 拡張、[Sound Physics](https://github.com/henkelmax/sound-physics-remastered/issues/172) の音響処理はクライアント向け。イメージ同梱の除外規則も適用されるため、[AppleSkin](https://github.com/squeek502/AppleSkin) は空腹・隠し満腹度の同期を使えるよう明示的に含める。JourneyMap はサーバー機能があるため残す。JEI なども提供 pack と依存関係を維持する。

ZIP の overrides は古い別 Mod の設定、クライアント設定、個人の画面・履歴情報、外部サービス設定を含む。現在の pack に関係する共通設定だけを `../config/config/` に選別した。`prepare-forge.sh` が存在しない設定だけを `/data/config` にコピーするため、Volume の設定は再起動や更新で自動上書きされない。更新時は新しい ZIP の manifest と設定の差分・Mod 依存関係を確認し、Volume をバックアップしてから必要な変更を明示的に反映する。ワールド単位の `serverconfig` は `/data/world/serverconfig` の実物を優先し、ZIP の古い Ars Nouveau 設定を現在の pack に適用しない。

[Ambassador](https://github.com/adde0109/Ambassador) は Forge 1.13–1.20.1 の通信を中継し、[Proxy Compatible Forge](https://github.com/adde0109/Proxy-Compatible-Forge) は Modern Forwarding を実装する。Forge は既存の Swarm secret を読み、一時ファイルから設定する。`/data/config/proxy-compatible-forge.toml` は一時ファイルへのシンボリックリンクであり、秘密値そのものは Volume に保存しない。既存の通常ファイルがある場合は起動を拒否するので、秘密情報として保護・退避後に作業する。

隔離環境では元の Manifest と指定5件の除外で Forge 47.4.28 が起動し、Proxy Compatible Forge の初期化を確認した。AppleSkin の明示追加後も再起動に成功し、同じワールドの `level.dat` を確認した。複数 Mod が起動時エラーを記録したため [運用手順](../../README.md#forge-1201-切替) の受入確認を行う。実際の Mod 通信・Velocity 4.2.0 との接続は未検証。

## 隔離試験で取得したサーバー用ファイル

- `appleskin-forge-mc1.20.1-2.5.1.jar`
- `appliedenergistics2-forge-15.4.12.jar`
- `architectury-9.2.14-forge.jar`
- `carryon-forge-1.20.1-2.1.2.7.jar`
- `cloth-config-11.1.136-forge.jar`
- `cosmeticarmorreworked-1.20.1-v1a.jar`
- `create-1.20.1-6.0.8.jar`
- `createaddition-1.20.1-1.3.3.jar`
- `creatingspace-1.20.1-1.7.21.jar`
- `curios-forge-5.14.1+1.20.1.jar`
- `elevatorid-1.20.1-1.9.1-forge.jar`
- `FarmersDelight-1.20.1-1.3.4.jar`
- `ftb-library-forge-2001.2.13.jar`
- `ftb-ultimine-forge-2001.1.8.jar`
- `geckolib-forge-1.20.1-4.8.4.jar`
- `gravestone-forge-1.20.1-1.0.35.jar`
- `GrimoireOfGaia4-1.20.1-4.0.0-alpha.12.jar`
- `guideme-20.1.15.jar`
- `jei-1.20.1-forge-15.56.0.205.jar`
- `journeymap-forge-1.20.1-6.0.7.jar`
- `kotlinforforge-4.12.0-all.jar`
- `ldlib-forge-1.20.1-1.0.52.a.jar`
- `nolandostructurez-0.0.1-1.20.1.jar`
- `ognmarts-0.1.6-beta.jar`
- `openblocks_reborn-1.0.2-1.20.1.jar`
- `Patchouli-1.20.1-85-FORGE.jar`
- `photon-forge-1.20.1-1.1.17.jar`
- `proxy-compatible-forge-1.3.1.jar`
- `shincolle-kai-1.20.1-1.0.0.jar`
- `sliceanddice-forge-3.6.0.jar`
- `tacz-forge-1.20.1-1.2.0.jar`
- `tacz_c-1.0.2-forge-1.20.1.jar`
- `torchesbecomesunlight-0.5.0-hotfix2.jar`
- `touhoulittlemaid-1.5.3-forge+mc1.20.1.jar`
- `travelersbackpack-forge-1.20.1-9.1.58.jar`
- `youkaishomecoming-2.7.2.jar`

既存 Volume の除外・包含条件を変更する場合はバックアップ後、一時的に `CF_FORCE_SYNCHRONIZE=true` を設定して再同期し、不要な再適用を避けるため検証後に外す。

## 追加予定の Create アドオン（隔離検証待ち）

| Mod | 固定版 | CurseForge project / file |
| --- | --- | --- |
| [Steam 'n' Rails](https://www.curseforge.com/minecraft/mc-mods/create-steam-n-rails/files/8745475) | 1.7.3 Forge 1.20.1 | 688231 / 8745475 |
| [Diesel Generators](https://www.curseforge.com/minecraft/mc-mods/create-diesel-generators/files/7932785) | 1.3.12 Forge 1.20.1 | 869316 / 7932785 |
| [Create Big Cannons](https://www.curseforge.com/minecraft/mc-mods/create-big-cannons/files/7478036) | 5.10.2 Forge 1.20.1 | 646668 / 7478036 |
| [Ritchie's Projectile Library](https://www.curseforge.com/minecraft/mc-mods/ritchies-projectile-library/files/7292523) | 2.1.1 Forge 1.20.1 | 1279407 / 7292523 |

Create Crafts & Additions 1.3.3 は既存のため変更しない。Steam 'n' Rails と Diesel Generators の配布 JAR の Forge メタデータでは Create 6.0.8 が依存範囲に含まれる。Big Cannons 5.10.2 の配布ページは Create 6.0.8 を明記している。4 件の組み合わせの専用サーバー起動、ゲーム内動作とクライアント接続は未確認。Big Cannons の JAR 自動取得は調査環境で HTTP 403 となったため Auto CurseForge での取得も要確認。

クライアントも同じ manifest の追加 4 件を導入する。反映前に Forge Volume を停止してバックアップし、隔離環境で起動と接続を検証する。戻す場合は追加前の manifest を復元し、追加された 4 件の JAR のみを確認して退避する。ワールド Volume は削除しない。新規 Mod のブロック・アイテムを保存後に Mod を外すとデータが欠損し得るため、必要に応じて導入前のバックアップを復元する。
