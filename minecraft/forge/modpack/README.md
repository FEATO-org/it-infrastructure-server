# イワシコ寄生虫 Modpack

新たに提供された `manifest.json` は Minecraft 1.20.1 / Forge 47.4.28 と 58 組の CurseForge project ID / file ID を固定する。`modlist.html` は ZIP の一覧を改行正規化したもの。共有 URL は取得元に使わない。

[Auto CurseForge](https://docker-minecraft-server.readthedocs.io/en/latest/types-and-platforms/mod-platforms/auto-curseforge/) で manifest を使う。Java 17 イメージの組み込み API key を使用し、配布制限されたファイルがあれば起動ログに示される手順に従い同じ ID のファイルを手動取得する。キーを変更する必要があるときは Swarm secret と `CF_API_KEY_FILE` を使用し、Git に記載しない。

以下はサーバーから除外する: Inventory Profiles Next (495267)、libIPN (679177)、Embeddium (908741)、Just Enough Resources (240630)、Sound Physics Remastered (535489)、[Tactical HUD](https://www.curseforge.com/minecraft/mc-mods/tacz-tactical-hud) (1768274)、[More Overlays Updated](https://www.curseforge.com/minecraft/mc-mods/more-overlays-updated) (391382)、[Entity Culling](https://www.curseforge.com/minecraft/mc-mods/entityculling) (448233)、[Oculus](https://www.curseforge.com/minecraft/mc-mods/oculus) (581495)。後者4件は配布元がクライアント用と記載している。[Inventory Profiles Next](https://www.curseforge.com/minecraft/mc-mods/inventory-profiles-next) と [libIPN](https://www.curseforge.com/minecraft/mc-mods/libipn) はクライアント用、[Embeddium](https://www.curseforge.com/minecraft/mc-mods/embeddium) はクライアント描画用、[JER](https://www.curseforge.com/minecraft/mc-mods/just-enough-resources-jer) はクライアント向け JEI 拡張、[Sound Physics](https://github.com/henkelmax/sound-physics-remastered/issues/172) の音響処理はクライアント向け。イメージ同梱の除外規則も適用されるため、[AppleSkin](https://github.com/squeek502/AppleSkin) は空腹・隠し満腹度の同期を使えるよう明示的に含める。JourneyMap はサーバー機能があるため残す。JEI なども提供 pack と依存関係を維持する。

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

## 旧44件版で追加した Create アドオン（参考・隔離検証待ち）

| Mod | 固定版 | CurseForge project / file |
| --- | --- | --- |
| [Steam 'n' Rails](https://www.curseforge.com/minecraft/mc-mods/create-steam-n-rails/files/8745475) | 1.7.3 Forge 1.20.1 | 688231 / 8745475 |
| [Diesel Generators](https://www.curseforge.com/minecraft/mc-mods/create-diesel-generators/files/7932785) | 1.3.12 Forge 1.20.1 | 869316 / 7932785 |
| [Create Big Cannons](https://www.curseforge.com/minecraft/mc-mods/create-big-cannons/files/7478036) | 5.10.2 Forge 1.20.1 | 646668 / 7478036 |
| [Ritchie's Projectile Library](https://www.curseforge.com/minecraft/mc-mods/ritchies-projectile-library/files/7292523) | 2.1.1 Forge 1.20.1 | 1279407 / 7292523 |

Create Crafts & Additions 1.3.3 は既存のため変更しない。Steam 'n' Rails と Diesel Generators の配布 JAR の Forge メタデータでは Create 6.0.8 が依存範囲に含まれる。Big Cannons 5.10.2 の配布ページは Create 6.0.8 を明記している。4 件の組み合わせの専用サーバー起動、ゲーム内動作とクライアント接続は未確認。Big Cannons の CurseForge 配布 JAR は固定 URL から取得でき、Forge メタデータの Create 6.0.8 と Ritchie’s Projectile Library 2.1.1 の依存範囲を確認した。Auto CurseForge での取得・起動は未確認。

以下の58件版への更新・復旧手順を優先する。

## TaCZ Gunpack と Arcana

TaCZ 1.2.0 の GunPackLoader はゲームディレクトリの `tacz/` 内の ZIP を読み込む。以下は配布 ZIP ルートに `gunpack.meta.json` があり、ZIP の整合性と SHA-256 を確認した。導入後の動作・各 Gunpack 同士の互換性は未検証。

| Gunpack | バージョン | CurseForge project / file | 対応情報 |
| --- | --- | --- | --- |
| [Charge into Battle: Reboot](https://www.curseforge.com/minecraft/customization/tacz-charge-into-battle-reboot-pack/files/7280896) | 0.3 | 1075478 / 7280896 | 1.1.7+ 表記、1.2.0 での動作は未確認 |
| [EOS Lab](https://www.curseforge.com/minecraft/customization/tacz-eoslab-gunpack/files/7182834) | 1.1.1 hotfix1 | 1201057 / 7182834 | 1.1.5+ 表記、1.2.0 での動作は未確認 |
| [Alex Kim’s Gunpack](https://www.curseforge.com/minecraft/customization/alex-kims-gunpack-tacz-gun-pack/files/9494048) | V14.12.25 | 1220585 / 9494048 | 配布ファイル名に TaCZ 1.2.0 の記載 |
| [Classics Reborn](https://www.curseforge.com/minecraft/customization/tacz-classics-reborn/files/9474740) | 1.1.7 hotfix3 | 1079169 / 9474740 | TaCZ 1.2.0 と Arcana 1.4.2 向け表記 |

Classics 用の [Arcana 1.4.2 hotfix 作者公式 Release](https://github.com/Hamster-Baron/TACZ-Arcana/releases/tag/1.4.2-loader-hybrid-hotfix) は CurseForge 審査待ちのため固定 GitHub Release を使用する。作者によれば本 JAR は保護 Gunpack の読み込み機能を含み、公開ソースからのビルドとは異なる。JAR の内部メタデータでは TaCZ 1.2.0 以上、Forge 47 以上、Kotlin for Forge 4.12 以上を要求し、既存構成には Kotlin for Forge 4.12.0 が含まれる。Arcana は TaCZ 内部を変更するため、既存アドオンとの競合も含め隔離試験する。

`../content.lock` に各固定 URL と SHA-256、`../sync-content.sh` に同期処理を置く。Forge 起動前に `/data/tacz/feato-*.zip` と `/data/mods/feato-arcana.jar` を検証し、欠けたファイル・管理済みで更新が必要なファイルだけ取得する。未管理ファイルや管理後に変更されたファイルの上書きを拒否し、その他のファイルは削除しない。ZIP のダウンロードと配置は実施するが、作者が再配布を制限しているものもあるため、ZIP を再配布用 Modpack に同梱せず利用者が各配布元から取得する。配布条件を各作者の配布ページでも確認する。

導入前に停止中の Forge Volume をバックアップし、既存 `/data/tacz/` に同じ Gunpack の ZIP または展開版がないか、`/data/mods/` に Arcana の別 JAR がないか確認して重複を避ける。対象 ZIP 間には `data/tacz/recipe_filters/default.json` やアタッチメントタグなど共通パスが26件あり、レシピ・タグの合成結果および衝突の有無は未確認。ゲーム内で検証する。GitHub Release の直接 URL が失敗した場合は同じ公式 asset の GitHub API URL にフォールバックする。両方にアクセスできない場合は同じ公式 Release の JAR を別途取得し、SHA-256 が `content.lock` と一致することを確認して停止中の `/data/mods/feato-arcana.jar` に手動配置する。ファイル未取得、ハッシュ不一致、所有権不明の競合時は起動前処理が失敗する。

クライアントの CurseForge Modpack は新しい58件の manifest に更新し、各配布ページから上記 4 ZIP と Arcana を取得する。`content.lock` の SHA-256 を確認後、ZIP はインスタンスの `tacz/`、Arcana は `mods/` に配置する。Bash と curl が利用可能な場合は `bash minecraft/forge/sync-content.sh <インスタンスのゲームディレクトリ> minecraft/forge/content.lock` でも同じ固定ファイルを用意できる。Windows 等では各配布元から手動取得し、既存の同名 Gunpack を重複させない。TaCZ の `ClientGunPackDownloadUrls` はソース上非推奨であり、完全な Gunpack 自動配布として使用しない。クライアント固有設定やセーブデータをサーバーへコピーしない。

更新時は対象の配布元・ID・実ファイル・ライセンス・SHA-256 を照合し `content.lock` と本表を更新する。管理対象だけを外す場合、停止後に `content.lock` で対象を特定し `/data/tacz/feato-*.zip` または `/data/mods/feato-arcana.jar` と対応する `/data/.feato-content/` の記録を手動退避する。現在の lock を維持したまま起動すると再取得するため、併せて対象を lock から除くか旧リビジョンへ戻す。TaCZ 設定や他の Gunpack、Volume は削除しない。新規 Mod 由来のデータを保存後のロールバックには導入前バックアップが必要。

## 58件版への更新と復旧

旧44件との差分は Weapons and Tactics (Mod)、Superb Warfare、Storage Drawers、FerriteCore、Tactical HUD、More Overlays Updated、ModernFix、Gucci & Vuitton Attachments、Delightful、Torchmaster、Entity Culling、LesRaisins Tactical Equipements、Oculus、spark、Create: Copper & Zinc の15件追加、GraveStone の削除、Create Big Cannons の file 7478036 から [8169547](https://www.curseforge.com/minecraft/mc-mods/create-big-cannons/files/8169547) への更新。Weapons and Tactics は [JAR版 1411291 / 9473803](https://www.curseforge.com/minecraft/mc-mods/tacz-weapons-and-tactics-mod) を採用し、旧 ZIP 版は使わない。クライアント専用9件は manifest に残す。

適用前にサーバーを停止し Forge Volume 全体（world、playerdata、config、mods、tacz、管理状態）を整合した状態でバックアップし、復元を試す。GraveStone の削除により残存する墓やその所持品などが読み込めなくなる・失われるおそれがある。事前に墓とアイテムを回収し、旧Mod・旧設定を含む停止時バックアップを保存する。欠落データを保存したワールドに後からModを戻しても復元できる保証はない。

公式の [Auto CurseForge 再同期](https://docker-minecraft-server.readthedocs.io/en/latest/types-and-platforms/mod-platforms/auto-curseforge/) は `CF_FORCE_SYNCHRONIZE=true` で除外条件を再評価する。停止・バックアップ後、隔離コピーでまず一時設定して試す。再同期が旧 JAR の削除を保証するとは確認できていないため、旧 GraveStone、旧 Create Big Cannons、除外9件を `/data/mods/` で project/file ID・実体から特定し、残存していれば対象だけを `/data/mods/` の外へ退避する。識別不能なら停止して調査し、ディレクトリ全体を削除しない。Arcana と他の手動管理 JAR を維持する。検証後は一時設定を外す。

起動前の同期は `/data/tacz/feato-weapons-and-tactics.zip` と管理記録の双方が旧 SHA-256 `e9983776641a5ffa95fef55198d91ff595faff1630934cb4bfa7d6a8c4666c10` に一致する場合のみ `/data/.feato-content/retired/` に退避し、管理記録を除く。未管理、改変、退避先の競合は起動を拒否し、手動調査する。対象がなければ続行する。他の Gunpack と Arcana は従来通り。

プレイヤーは新しい提供 Modpack を適用し、旧 Weapons and Tactics ZIP を `tacz/` から手動で退避して JAR版だけにする。残る4 ZIP と Arcana はそれぞれ `tacz/` と `mods/` に維持し、同じ内容の別ファイルが重複しないことを確認する。設定とセーブは別途保全する。

[Weapons and Tactics 配布元](https://www.curseforge.com/minecraft/mc-mods/tacz-weapons-and-tactics-mod/files/all) は 0.4.1 を Forge 1.20.1 / TaCZ 1.2.0 向けとし、Big Cannons 5.11.4 は Create 6.0.7 以降を指定する。Create 6.0.8・TaCZ 1.2.0 はその表記範囲内だが、全Modの依存・レシピ・銃器ID・ネットワーク、Arcana と他Gunpackの競合、および実接続は未検証。隔離コピーで Forge とクライアントの起動・接続、レシピ・銃器・墓を確認する。旧版の隔離起動結果は新版の確認ではない。

ロールバックは停止後に旧リビジョンの manifest・設定・lock を戻し、更新前の Volume バックアップを復元する。旧ZIPを復元する場合は退避先のハッシュと管理記録を確認して元に戻す。新Modを保存したワールドを旧Mod構成のまま保存しない。

## 提供 overrides のサーバー設定

提供 overrides から Diesel Generators、Delightful、Farmer’s Delight、FerriteCore、LesRaisins Tactical Equipements、ModernFix、Steam ’n’ Rails、ShinColle-kai（採掘テーブルを含む）、Storage Drawers、Superb Warfare、Torchmaster の共通設定を `../config/config/` に初回用として取り込んだ。これらの値は新規 Volume または対応ファイルが存在しない場合にのみ `prepare-forge.sh` により `/data/config/` にコピーされ、既存 Volume 上の同名設定は上書きされない。適用する必要がある場合は停止・バックアップ後、実際の設定と提供値を比較し、運用者が対象設定を個別に反映する。ゲーム内の効果は未検証。

既存の共通設定は保持する。提供版の Touhou Little Maid 設定には妖精関連の値の変更とクライアント固有のマイク設定があるが、既存設定の上書きは行わない。クライアント専用設定、個人情報を含み得るファイル、overrides 内の未管理JAR・Gunpack・モデル・音声・ワールドは一括コピーしない。これらの要否と再配布条件は別途確認する。
