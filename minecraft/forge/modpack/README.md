# イワシコ寄生虫 Modpack

提供された58件版から LesRaisins Tactical Equipements を除き Bad Mobs を追加した `manifest.json` は Minecraft 1.20.1 / Forge 47.4.28 と追加 Mod と Curios For Ammo Box を含む CurseForge project ID / file ID を固定する。Frontline 2.0.0 は CurseForge manifest 外で固定する。追加分の依存・保留理由・未検証事項は [調査と受入条件](ADDITIONAL_MODS.md) を参照。`modlist.html` は従来の一覧で、Ammo Box 追加分は含まない。Zoe Isn't Cyberpunk は manifest と一覧から削除済み。共有 URL は取得元に使わない。

## 2026-11-25 Botany Pots 系と Energy Meter の追加

Minecraft 1.20.1 / Forge 47.4.28 / Java 17 を維持し、クライアントとサーバーの共通 manifest に次の4件を固定する。

| Mod | バージョン | CurseForge project:file |
| --- | --- | --- |
| Botany Pots Ore Planting | 15.40.0+1.18.2-1.20.4 | [872868:7755193](https://www.curseforge.com/minecraft/mc-mods/botany-pots-ore-planting/files/7755193) |
| Bookshelf | 20.2.15 | [228525:7612389](https://www.curseforge.com/minecraft/mc-mods/bookshelf/files/7612389) |
| Botany Pots | 13.0.43 | [353928:7612402](https://www.curseforge.com/minecraft/mc-mods/botany-pots/files/7612402) |
| Energy Meter | 1.0.1 | [532169:7676339](https://www.curseforge.com/minecraft/mc-mods/energymeter/files/7676339) |

各ファイルは CurseForge の Forge / Minecraft 1.20.1 対応表記と Release 区分を確認した。Botany Pots Ore Planting 15.40.0 は 1.18.2–1.20.4 対応で、Botany Pots と Bookshelf を必須とする。取得した JAR の `META-INF/mods.toml` では、それぞれ Botany Pots `[8.0.0,17.0.0)`、Bookshelf `[13.0.0,24.0.0)`、loader 40 以上を要求する。Botany Pots は Forge 47 以上と Bookshelf 20 以上、Bookshelf は Forge 47 以上、Energy Meter は Forge 47.1.3 以上を要求し、固定版は宣言範囲内。Energy Meter の ComputerCraft は任意依存で、追加の必須 Mod はない。依存の side は BOTH だが、接続互換性の実測ではない。

Energy Meter 1.0.1 は 1.20.1 向け Release で、配布元は重大な不具合修正を除き更新を終了すると記載する。4 JAR は公式 CurseForge CDN と、ARM64 の隔離環境の Auto CurseForge から取得でき、両取得物の SHA-256 は一致した。値は順に `d2c8e64860c84babf5c18fb6ffdb8f2de700f11987976ee3d1d6309c6d289f1c`、`7980d4a0beed1dcd2c283cf65f3c93f6b0085833f3ac490014979c95f1dfaf67`、`55c0a1457d4ca107d5b1b005310df32672dad59b2ce0c4ca150c525848eed474`、`699da7c48989f07632ca569ff6bbe93220f4d4c8972a6133c74d7e53e96e9817`。これらは取得物の算出値で、独立した配布元ハッシュとの照合ではない。実行時互換性は別途確認する。既存 Mod や設定、Compose、content.lock は変更しない。modlist.html は従来一覧で今回の追加分を含まない。

固定 Java 17 イメージの ARM64 隔離環境で、共通 manifest と Compose の除外・包含条件を使った新規ワールドは Forge 47.4.28 の `Done` に到達した。本番の `content.lock` 配布物、設定、Velocity、既存ワールドは含まない。必須依存不足や Mixin の ERROR は確認されなかったが、クラス不在の Mixin 警告、Photon の専用サーバーでのクライアントクラス読込エラー、他 Mod のタグ・戦利品・レシピのエラーが出たため、構成全体の正常性は保証できない。クライアント接続、ゲーム内動作、保存後の再起動と本番は未検証。

適用前に停止時の Forge Volume とクライアントのセーブ・設定をバックアップし、隔離コピーで指定 JAR の取得と依存関係、起動・接続・鉢の栽培と鉱石生成・エネルギー計測・保存再起動を確認する。クライアントは更新後の共通 manifest を使う Modpack に更新するか、上記固定ページから同じ4版を取得して既存の mods に追加し、同一 Mod の重複を避ける。鉱石の自動生産による資源バランスと多数の鉢の負荷は未評価。問題があれば本番適用を中止し、旧 revision と変更前の整合した Volume バックアップを復元し、クライアントも旧構成へ戻す。既存ワールドに追加 Mod のブロックやアイテムを保存した後は単純な JAR 削除で安全に戻せるとは限らない。

## SuperbWarfare Addon 削除と地形破壊設定

共通 manifest から [SuperbWarfare Addon 1.0.1](https://www.curseforge.com/minecraft/mc-mods/superbwarfare-addon/files/8793995)（project 1580826 / file 8793995）を除外した。SBW 本体 0.8.9.2（1218165 / 9019882）と Frontline 2.0.0 は維持する。`modlist.html` は従来一覧で Addon は含まれていなかった。クライアントにも更新後の共通 manifest を使った Modpack を配布する。

Addon の [配布元](https://www.curseforge.com/minecraft/mc-mods/superbwarfare-addon) によれば排莢・薬莢アイテム、排莢ルール、コンテンツや車両レシピ・鉱石生成の制御、任意の MTS 連携などが失われる。既存設定やデータパックの Addon 用ルールは機能しなくなる。所持品・コンテナ・ワールド内の Addon アイテム等は欠落し、削除状態で保存すると復元できない可能性がある。実際の対象データ、レシピ、既存ワールドの互換性は未確認。

`config/defaultconfigs/superbwarfare-server.toml` は爆発の `explosion_destroy` と `extra_explosion_effect`、投射物の `allow_projectile_destroy_blocks`、車両衝突の `collision_destroy_soft_blocks`、`collision_destroy_normal_blocks`、`collision_destroy_hard_blocks`、`collision_destroy_blocks_beastly` を `false` にする。その他の設定値は指定しない。[0.8.9.2 Forge 1.20.1 の配布ソース](https://modrinth.com/mod/superb-warfare/version/81Iyv9ao) の設定定義と爆発、追加破壊、弾丸、車両衝突の処理を確認した。爆発のエンティティダメージは別処理である。SBW 固有の設置・解体や道具によるブロック操作は対象外。ゲーム内での効果は未確認で、既に破壊された地形は戻らない。

Compose は `minecraft/forge/config` を `/forge-config` に mount し、`prepare-forge.sh` が存在しないファイルだけ `/data/defaultconfigs` へ配置する。Forge は新規ワールド作成時に defaultconfigs をワールドの `serverconfig` に取り込む。Compose は `LEVEL` を指定していないため標準では `/data/world/serverconfig/superbwarfare-server.toml` だが、実環境の `/data/server.properties` の `level-name` と実際のワールドパスを必ず確認する。既存の `/data/defaultconfigs` の同名ファイルも上書きしない。既存ワールドの `serverconfig` は更新されない。部分設定からの不足項目補完と実際の読み込みは未検証。

適用担当者向け手順（本番操作は未実施）:

1. メンテナンス中に Forge を正常停止し、world・playerdata・mods・config・defaultconfigs 等を含む Volume 全体とクライアントのセーブ・設定を整合した状態でバックアップし、隔離環境で復元を確認する。Addon のアイテムや独自データの喪失を許容できなければ適用しない。
2. 停止中に `/data/mods/` と各クライアントの mods を調査する。対象は `superbaddon-1.0.1.jar`（Mod ID `superbaddon`、file 8793995、既取得物の SHA-256 `86fee0a858bcc85d27330ca80eb96aa24587b098b174b02ec1a1a0119b6f682a`）。名称だけで判断せず JAR の `META-INF/mods.toml` とハッシュ・入手元を照合し、残存する対象だけを mods 外へ退避する。Auto CurseForge による自動削除は保証されない。識別できなければ中止し、`superbwarfare` 本体や他の Mod は退避しない。
3. 将来の新規ワールドにも適用する場合、既存 `/data/defaultconfigs/superbwarfare-server.toml` があれば内容を保全して以下と同じ7キーのみ編集する。存在しない場合は seed が配置される。既存ワールドでは実際の `level-name` に対応する `serverconfig/superbwarfare-server.toml` をバックアップし、既存の各セクション内の7キーだけを上記 seed の値に変更する。キーがなければ該当セクションに追加し、セクションがなければ作る。同名キー・セクションを重複させず、他の値や未知のキーを維持する。設定ファイル自体が存在しない場合は seed を配置し、Forge による補完と値を隔離環境で確認する。
4. バックアップの隔離コピーで新規・既存ワールドの起動、生成された serverconfig の7値、ログ、Addon データの欠落、保存・再起動、クライアント接続を確認する。爆発・投射物・車両衝突とエンティティへのダメージも試し、異常があれば適用を中止する。
5. ロールバックは停止後に変更後データを別途保全し、旧 revision と変更前の整合した Volume バックアップを一緒に復元し、クライアントも旧構成に戻す。設定だけ戻す場合はバックアップした各キーの元値を復元する。Addon 欠落状態で保存したデータや既に破壊された地形は設定変更だけでは戻らない。

## 2026-11-19 SBW・TaCZ 更新と CCRP 追加

以下は当時の履歴であり、Addon は上記のとおり削除済み。

Minecraft 1.20.1 / Forge 47.4.28 と Java 17 を維持し、共通 manifest は [SBW 0.8.9.2](https://www.curseforge.com/minecraft/mc-mods/superb-warfare/files/9019882) (1218165 / 9019882)、[SuperbWarfare Addon 1.0.1](https://www.curseforge.com/minecraft/mc-mods/superbwarfare-addon/files/8793995) (1580826 / 8793995)、[TaCZ 1.2.0-hotfix](https://www.curseforge.com/minecraft/mc-mods/timeless-and-classics-zero/files/9623132) (1028108 / 9623132) を固定する。Addon は従来の manifest にないため新規追加。Addon JAR は SBW 0.8.9.1 以上と GeckoLib 4.4.6 以上を要求し、配布ページは 0.8.9.1 への対応を記載する。0.8.9.2 との実動作は未確認。 SBW JAR は必須の SimpleBedrockModel 2.5.1 を jar-in-jar で同梱する。SBW、Addon、TaCZ の取得 JAR の SHA-256 はそれぞれ `559930003f638080de648a8621821d785158768c3f69a762094ef4c8d3c4cc12`、`86fee0a858bcc85d27330ca80eb96aa24587b098b174b02ec1a1a0119b6f682a`、`6b26506e73cfbc8ad56c39d4da09b9463dfa7e23b8b13389b80354e526548f5d`。SBW は公式 Modrinth の SHA-512 と一致、Addon・TaCZ は取得物の算出値であり配布元の独立したハッシュ照合は未実施。

[Frontline 2.0.0](https://modrinth.com/mod/frontline-combat-pack/version/2.0.0) は Modrinth `TnzHcrvV / skviTkFg` の `fcp-2.0.0.jar` を `content.lock` 経由で `/data/mods/feato-frontline-combat-pack.jar` に配置する。CurseForge の旧版は manifest から外した。取得 JAR の SHA-256 は `8bcfd35d393c28812dc5fbb426b4b0691ce280644174b458dbf7ae3687c0c105`、配布元 SHA-512 と一致。JAR は Forge 47+、Minecraft 1.20.1、SBW 0.8.9.1+、GeckoLib 4.7.2+ を要求し、固定 GeckoLib 4.8.4 は範囲内。一方 Modrinth API の必須 SBW 指定は 1.21.1 NeoForge 版 `izD7dnxq` を指す。配布メタデータと JAR の不一致は未解決であり、導入前に作者の確認と隔離起動が必要。旧 1.2.1 の Mixin 失敗が解消したとは確認していない。

[CCRP 1.1.7_hotfix4](https://www.curseforge.com/minecraft/customization/tacz-classics-reborn/files/9629324) (1079169 / 9629324) は一覧上 1.20.1 Forge 版。配布表示名は `[1.20.1Forge][TACZ1.2.0+Arcana1.4.2]CCRP_1.1.7_hotfix4.zip`、実ファイル名は `1.20.1Forge-TACZ1.2.0-Arcana1.4.2-CCRP_1.1.7_hotfix4.zip`。1.21.1 NeoForge 版 9629304 とは異なる。ZIP 検査と SHA-256 を確認し、`content.lock` が展開せず `/data/tacz/feato-ccrp.zip` に配置する。ZIP の `gunpack.meta.json` の namespace は `ccrp`、内部 `gunpack_info.json` の version は `1.1.8` で配布表示と異なる。依存チェック宣言はなく、名前の Arcana 1.4.2 表記だけでは必須か判断できない。既存 Arcana 1.4.2 hotfix は維持する。以前の Classics 1.1.4 は起動障害のため撤去済みで、今回復活しない。CCRP と RABasya、既存 TaCZ アドオンの実行時競合は未確認。

**適用条件:** 停止した Forge Volume 全体とクライアントの設定・セーブをバックアップし復元を確認する。Auto CurseForge が旧 JAR を削除する保証はない。`/data/mods/` とクライアントで旧 SBW、旧 TaCZ、旧 Frontline 1.2.1、および同じ Mod ID の JAR を実体・ID で特定し、残存する旧版だけを mods 外へ退避する。識別できなければ適用を中止する。旧 CCRP や統合版・展開版も特定して `tacz/` 外へ退避し、他の Gunpack は維持する。設定は自動上書きされないため既存設定と新バージョンを比較する。隔離コピーで依存・Mixin・Gunpack ログ、クライアント接続、銃器・車両、既存ワールドの保存と再起動を確認してから適用する。クライアントにも同じ Mod バージョンと CCRP ZIP を配布する。

切り戻しは停止後、更新後データを別途保全し、旧 revision と更新前の整合した Volume バックアップを一緒に復元し、クライアントも旧構成へ戻す。今回の起動・ゲーム内動作・既存ワールド互換性は未確認。本番操作は行っていない。

## ShinColle-kai 1.1.0 への更新

[公式 Release](https://github.com/halkirisame/ShinColle-kai/releases/tag/v1.20.1-1.1.0) と [CurseForge](https://www.curseforge.com/minecraft/mc-mods/shincolle-kai/files/9591104) は Minecraft 1.20.1 / Forge 向け 1.1.0（1683061 / 9591104）に前提 Mod はなく、GeckoLib は同梱とする。1.0.0（file 9470212）から艦の能力・艦隊画面・宝箱を変更し、保存艦や装備の消失などを修正する。追加設定は既定値で従来の挙動を保つとされ、追跡中の `shincolle_kai-*` 設定は変更しない。既存設定への不足項目の補完や保存データ互換性は未検証。

適用前に Forge を停止し、world・playerdata・保存艦の卵・mods・config を含む Volume 全体を整合した状態でバックアップし、復元を確認する。停止時バックアップの隔離コピーで取得、起動、保存艦と装備、保存・再起動、クライアント接続を確認し、互換性に問題があれば適用を中止する。サーバーと全クライアントを同じ 1.1.0 に揃える。

Auto CurseForge の更新後も旧 JAR が残る可能性がある。`/data/mods/` とクライアントの mods で旧版と新版の実体を識別し、同時にロードしない。旧版が残れば停止・バックアップ後に対象だけを mods 外へ安全に退避し、識別できなければ中止する。既存設定を削除・再生成・上書きしない。切り戻す場合は停止し、更新後データを別途保全してから旧 manifest と更新前の整合した Volume バックアップを一緒に復元し、クライアントも旧版に戻す。今回の取得・起動・接続・ゲーム内動作・既存ワールド互換性は未確認。本番操作は未実施。

## Zoe Isn't Cyberpunk の削除

Project ID 896842 / File ID 7253085 をサーバー・クライアント共通 manifest から除外した。削除後の起動や既存ワールド互換性は未検証。既存ワールドやプレイヤーの所持品に同 Mod のデータがある場合、削除後に保存すると失われる可能性がある。

適用前に Forge を停止し、world・playerdata・mods・config を含む Volume 全体をバックアップして復元可能性を確認する。停止時バックアップの隔離コピーで削除後の起動・保存・再起動と対象データを確認する。既存 Volume に JAR が残る可能性があるため、`/data/mods/` で実体と project/file ID を確認し、残っていれば対象だけを mods 外へ退避する。識別できない場合は中止する。クライアントにも更新後の Modpack を配布し、旧 JAR が残らないことを確認する。

ロールバックする場合は停止し、以前の構成と整合した削除前の Volume バックアップを一緒に復元する。本番操作は未実施。

## SBW の版変更と Frontline の追加・Invasion の削除

[SBW 0.8.9 final](https://www.curseforge.com/minecraft/mc-mods/superb-warfare/files/8104849)（1218165 / 8104849）と [Frontline Combat Pack 1.2.1](https://www.curseforge.com/minecraft/mc-mods/frontline-combat-pack/files/8650627)（1465874 / 8650627）を固定し、Invasion Mod（1628663 / 8844167）を外す。SBW JAR の申告版は `0.8.9` で Frontline の必須範囲 `[0.8.9]` に一致する。SBW は Forge 47+、Kotlin for Forge 4.11.0+、Curios 5.4.0+、GeckoLib 4.4.6+ を要求し、既存版は宣言範囲内。起動・ゲーム内動作・クライアント接続・性能は未検証。[調査と試験](ADDITIONAL_MODS.md) を参照する。

SBW 0.8.9.2 からのダウングレードや Invasion の削除でアイテム、乗り物、ブロック、Mob、Nexus 等のデータを失う可能性がある。SBW 0.8.9.2 の JAR には 0.8.9 にないアイテムモデルやレシピがある。欠落した状態で保存すると後から Mod を戻しても復元できる保証はない。事前に利用中のデータを調査し、損失を許容できない場合は適用を中止する。

本番適用前に Forge を停止し、world・playerdata・mods・config・tacz・管理状態を含む Volume 全体を整合した状態でバックアップして復元を試す。隔離コピーで SBW 0.8.9 単体と Frontline 追加後の起動、依存、既存データ、レシピ、接続、保存・再起動、TPS・MSPT・メモリを確認する。Invasion が存在した場合は削除後の保存データも確認する。0.8.9.2 の SBW 設定 seed と既存 Volume の設定は上書きせず、0.8.9 との互換性を個別確認する。`prepare-forge.sh` は既存設定を上書きしない。

`/data/mods/` では旧 SBW 0.8.9.2 と Invasion の JAR を project/file ID・実体から特定する。Auto CurseForge が旧 JAR を削除する保証は未確認のため、残存時は対象だけを mods 外へ退避し、SBW が重複しないことを確認する。識別不能なら中止する。クライアントも同じ構成へ変更する。ロールバックは停止後、旧リビジョンと変更前の整合した Volume バックアップを一緒に復元する。`CF_FORCE_SYNCHRONIZE` は常設しない。本番操作は未実施。

### 2026-11-14 隔離起動結果

空 Volume・テスト用 secret・外部公開ポートなし、固定イメージの amd64 digest を ARM64 ホスト上でエミュレーションし、ヒープ 4G・メモリ上限 6G で試験した。Auto CurseForge は SBW 0.8.9 と Frontline 1.2.1 を取得し、新規ワールドで `Done` に到達、正常停止後の同じワールドでも再起動した。初回は `prepare-forge.sh` の実行権限不足で停止したため、実行可能にしたコピーで再試行し、Git のファイルモードを修正した。

**受入未完了:** 初回と再起動時に Frontline の `AmmoSupplierItemMixin` が SBW の `use` を見つけられず `InvalidInjectionException` を記録した。サーバーは起動したが、弾薬処理への影響は未特定であり、本番適用前に原因と動作を確認する。SBW の client class 読込警告、Photon の client class 読込エラー、Create Connected の任意連携先 class 不在警告、Torches Become Sunlight の構造物生成中の far chunk エラー等も出た。クライアント接続、実ワールドのダウングレード、レシピ・車両・弾薬の操作、負荷比較は未確認。エミュレーションと縮小ヒープでの試験は本番性能を示さない。試験用サーバーは停止した。

## Bad Mobs と Cecaelia

[Bad Mobs 19.0.4](https://www.curseforge.com/minecraft/mc-mods/bad-mobs/files/5086469)（Project 233258 / File 5086469）を既存の Auto CurseForge manifest に追加し、`grimoireofgaia:cecaelia` の自然・スポナー・スポーンエッグ・変換によるスポーンを禁止する。JAR の Forge メタデータ上の必須依存は Forge 47 以降のみ。作者はクライアントとサーバー両方への導入を要求し、サーバー単独は非サポートとしているため、提供クライアント Modpack にも同じ版を追加する。制御自体はサーバー側の設定で行われる。既存 Mod や Proxy との実接続は未検証。

Git の `../config/config/badmobs-common.toml` は新規 Volume または同名ファイルがない既存 Volume で起動前に `/data/config/badmobs-common.toml` へコピーされる。既存ファイルは上書きしない。既存ファイルがある場合は Forge を停止し Volume 全体をバックアップしたうえで実ファイルを確認し、`[grimoireofgaia.cecaelia]` の `allowNormalSpawning`、`allowSpawners`、`allowSpawnEggs`、`allowConversions` の4項目をすべて `false` に変更する。セクションがなければ Git の該当セクションを追加し、同名セクションやキーを重複させない。他Mobの設定を維持し、起動後の設定ファイルとログを確認する。既存ファイルは自動更新されないため、この手作業が適用条件となる。Forge が不足する設定を補完する際の値の保持、取得、起動、4経路の動作は未検証であり、先に隔離コピーで確認する。

Bad Mobs のエンティティ参加イベントは該当個体を破棄するため、すでにワールド内にいる Cecaelia もチャンク再読込等で削除される可能性がある。コマンド等の他のスポーン理由も通常スポーン設定で拒否され得る。適用前にワールドを含む停止時 Volume のバックアップと復元を確認する。ロールバックは停止後、以前の manifest と設定に戻し、Bad Mobs の JAR が残る場合は対象だけを mods 外へ退避する。失われた個体は Mod の削除だけでは戻らないため、必要に応じ更新前の整合した Volume バックアップを復元する。

[Auto CurseForge](https://docker-minecraft-server.readthedocs.io/en/latest/types-and-platforms/mod-platforms/auto-curseforge/) で manifest を使う。Java 17 イメージの組み込み API key を使用し、配布制限されたファイルがあれば起動ログに示される手順に従い同じ ID のファイルを手動取得する。キーを変更する必要があるときは Swarm secret と `CF_API_KEY_FILE` を使用し、Git に記載しない。

サーバー専用 Chunky 1.3.146 と最適化 Mod 3件は共通 manifest と別に固定配布する。FerriteCore の既存 Volume への反映、MeowIce、spark、Chunky と最適化 Mod の管理と復旧は [Forge パフォーマンス管理](../PERFORMANCE.md) を参照。適用・実動作は未確認。

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

## RABasya・Ammo Box

[RABasya Firepower Pack 1.1.2](https://www.curseforge.com/minecraft/customization/tacz-rabasya-firepower-pack/files/9454179) (1126780 / 9454179) は `content.lock` で固定し、起動前に `/data/tacz/` へ同期する。配布 ZIP の SHA-256 を確認し、Forge 47.4.28、TaCZ 1.2.0、Arcana 1.4.2 hotfix、Gucci & Vuitton、Curios For Ammo Box を含む隔離環境で、Classics 退避相当の構成が `Done` に到達した。本番構成、クライアント接続とゲーム内動作は未確認。

[Curios For Ammo Box 1.2.2](https://www.curseforge.com/minecraft/mc-mods/curios-for-ammo-box/files/9527336) (1339813 / 9527336) は共通 manifest に追加し、クライアントとサーバーで揃える。JAR は Forge 47+、Minecraft [1.20.1,1.21)、TaCZ 1.2.0+ を必須と宣言。配布元は Curios API も必須とするが JAR メタデータにはその版範囲がない。既存 Curios 5.14.1 と TaCZ 1.2.0 は維持する。1.2.2 の配布元は TACZ-addon 1.2.0 とのクラッシュと HUD 二重計数の修正を記載するが、他の Ammo Box 関連 Mod との競合や動作は未確認。

適用・切り戻しは [Classics Reborn の退避](#classics-reborn-の退避) を参照する。クライアントとサーバーには同版の RABasya と共通 Modpack を用意する。

## TaCZディレクトリの退避

TaCZ本体、Weapons and Tacticsなどの関連Modと Arcana は維持する。`content.lock` から Charge into Battle、EOS Lab、Alex Kim の Gunpack ZIP を外したため、再起動時に自動再取得しない。Classics Reborn だけを退避する場合は [専用手順](#classics-reborn-の退避) を参照する。

本番のForgeを停止してVolume全体をバックアップする。`/data/tacz/` には Gunpack のほか利用者が置いたZIP・展開済みフォルダ・設定・その他のファイルが含まれる可能性がある。対象全体を確認し、以下のコマンドでディレクトリを `/data/.feato-content/retired/tacz-directory/tacz/` へまとめて移動する。既知のGunpackの管理記録も同じ退避先の `records/` へ移す。ModのJARと `/data/config/`、ワールドは操作しない。

TaCZディレクトリを退避する場合は、新しいリポジトリと `content.lock` をデータノードへ配置し、停止・バックアップ後に実行する。Volumeとパスは実物を確認する。ディレクトリ自体が存在しなければ何もしない。シンボリックリンク、管理記録の不一致、退避先の競合は移動前に拒否する。

```bash
FORGE_VOLUME='実際のForge Volume名'
REPO_DIR='更新済みリポジトリの絶対パス'
FORGE_IMAGE='itzg/minecraft-server:java17@sha256:632741e7e7fce0fa2730c428ffdd8f6fb346355d2568548d56b5a313020e1287'
docker run --rm --user 0:0 --entrypoint bash \
  -v "$FORGE_VOLUME:/data" \
  -v "$REPO_DIR/minecraft/forge/retire-tacz-directory.sh:/retire-tacz-directory.sh:ro" \
  "$FORGE_IMAGE" /retire-tacz-directory.sh /data
```

適用後、TaCZは起動時に新しい `/data/tacz/` や既定コンテンツを生成する可能性がある。ディレクトリを永続的に存在させない設定ではない。現行の lock では RABasya が再取得される。プレイヤーのクライアントに追加Gunpackがある場合は同様に退避し、接続・ゲーム内動作を検証する。削除したGunpack由来の銃器・アイテムは利用できなくなる可能性があり、削除後にワールドを保存すると復元できない場合がある。戻す際は停止して整合した更新前Volumeのバックアップと旧lockを復元する。

## 58件版への更新と復旧

旧44件との差分は Weapons and Tactics (Mod)、Superb Warfare、Storage Drawers、FerriteCore、Tactical HUD、More Overlays Updated、ModernFix、Gucci & Vuitton Attachments、Delightful、Torchmaster、Entity Culling、LesRaisins Tactical Equipements、Oculus、spark、Create: Copper & Zinc の15件追加、GraveStone の削除、Create Big Cannons の file 7478036 から [8169547](https://www.curseforge.com/minecraft/mc-mods/create-big-cannons/files/8169547) への更新。Weapons and Tactics は [JAR版 1411291 / 9473803](https://www.curseforge.com/minecraft/mc-mods/tacz-weapons-and-tactics-mod) を採用し、旧 ZIP 版は使わない。クライアント専用9件は manifest に残す。

適用前にサーバーを停止し Forge Volume 全体（world、playerdata、config、mods、tacz、管理状態）を整合した状態でバックアップし、復元を試す。GraveStone の削除により残存する墓やその所持品などが読み込めなくなる・失われるおそれがある。事前に墓とアイテムを回収し、旧Mod・旧設定を含む停止時バックアップを保存する。欠落データを保存したワールドに後からModを戻しても復元できる保証はない。

公式の [Auto CurseForge 再同期](https://docker-minecraft-server.readthedocs.io/en/latest/types-and-platforms/mod-platforms/auto-curseforge/) は `CF_FORCE_SYNCHRONIZE=true` で除外条件を再評価する。停止・バックアップ後、隔離コピーでまず一時設定して試す。再同期が旧 JAR の削除を保証するとは確認できていないため、旧 GraveStone、旧 Create Big Cannons、除外9件を `/data/mods/` で project/file ID・実体から特定し、残存していれば対象だけを `/data/mods/` の外へ退避する。識別不能なら停止して調査し、ディレクトリ全体を削除しない。Arcana と他の手動管理 JAR を維持する。検証後は一時設定を外す。

起動前の同期は `/data/tacz/feato-weapons-and-tactics.zip` と管理記録の双方が旧 SHA-256 `e9983776641a5ffa95fef55198d91ff595faff1630934cb4bfa7d6a8c4666c10` に一致する場合のみ `/data/.feato-content/retired/` に退避し、管理記録を除く。未管理、改変、退避先の競合は起動を拒否し、手動調査する。対象がなければ続行する。TaCZディレクトリの退避については上記の手順を参照する。

プレイヤーは新しい提供 Modpack を適用し、旧 Weapons and Tactics ZIP を `tacz/` から手動で退避して JAR版だけにする。追加Gunpackは退避し、Arcanaは `mods/` に維持する。設定とセーブは別途保全する。

[Weapons and Tactics 配布元](https://www.curseforge.com/minecraft/mc-mods/tacz-weapons-and-tactics-mod/files/all) は 0.4.1 を Forge 1.20.1 / TaCZ 1.2.0 向けとし、Big Cannons 5.11.4 は Create 6.0.7 以降を指定する。Create 6.0.8・TaCZ 1.2.0 はその表記範囲内だが、全Modの依存・レシピ・銃器ID・ネットワーク、Arcana と他Gunpackの競合、および実接続は未検証。隔離コピーで Forge とクライアントの起動・接続、レシピ・銃器・墓を確認する。旧版の隔離起動結果は新版の確認ではない。

ロールバックは停止後に旧リビジョンの manifest・設定・lock を戻し、更新前の Volume バックアップを復元する。旧ZIPを復元する場合は退避先のハッシュと管理記録を確認して元に戻す。新Modを保存したワールドを旧Mod構成のまま保存しない。

## 提供 overrides のサーバー設定

提供 overrides から Diesel Generators、Delightful、Farmer’s Delight、FerriteCore、ModernFix、Superb Warfare、Steam ’n’ Rails、ShinColle-kai（採掘テーブルを含む）、Storage Drawers、Torchmaster の共通設定を `../config/config/` に初回用として取り込んだ。これらの値は新規 Volume または対応ファイルが存在しない場合にのみ `prepare-forge.sh` により `/data/config/` にコピーされ、既存 Volume 上の同名設定は上書きされない。適用する必要がある場合は停止・バックアップ後、実際の設定と提供値を比較し、運用者が対象設定を個別に反映する。ゲーム内の効果は未検証。

既存の共通設定は保持する。提供版の Touhou Little Maid 設定には妖精関連の値の変更とクライアント固有のマイク設定があるが、既存設定の上書きは行わない。クライアント専用設定、個人情報を含み得るファイル、overrides 内の未管理JAR・Gunpack・モデル・音声・ワールドは一括コピーしない。これらの要否と再配布条件は別途確認する。

## Classics Reborn の退避

[Classics Reborn 1.1.4](https://www.curseforge.com/minecraft/customization/tacz-classics-reborn/files/9629350)（1079169 / 9629350）は、同梱されていない CCRP 弾薬を参照する。Arcana 1.4.2 hotfix の銃器インデックス読み込みで起動停止を再現したため、Classics を `content.lock` から外す。Arcana、TaCZ、RABasya、Gucci & Vuitton、Weapons and Tactics、Curios For Ammo Box は維持する。

1. Forge を停止し、Volume 全体と対応クライアントをバックアップして復元可能性を確認する。Classics 由来の銃器などがある場合は、停止時バックアップの隔離コピーで所持品と保存・再起動への影響を確認する。欠落した状態で保存すると、ZIP を戻してもデータを復元できない場合がある。
2. `/data/tacz/` の別名 ZIP、展開フォルダ、旧 Classics/CCRP 統合版、管理記録を確認する。別名や展開版があれば、対象を特定して `/data/tacz/` の外へ退避する。クライアント側も Classics と重複する旧版を `tacz/` の外へ退避する。
3. 同じリビジョンの `content.lock` と `sync-content.sh` をデータノードへ配布する。起動前同期は `tacz/feato-classics-reborn.zip` と管理記録が共に 1.1.4 の SHA-256 `2d0c082c234c7c30b40055225b518481d13fad9401c4c442f65fb5b04664f8df` に一致する場合に、ZIP を `/data/.feato-content/retired-classics/feato-classics-reborn-1.1.4.zip` に移し、現用の管理記録を除く。ZIP がなければ同期を続行する。不一致、対象 ZIP・管理記録・退避先のシンボリックリンク、退避先ファイルの競合時は起動を停止して調査する。
4. 起動ログで Classics の読み込みがなく、RABasya と標準 Gunpack が読み込まれ、`Done` に到達することを確認する。クライアント接続、銃器と所持品、保存後の再起動を確認する。

Classics 専用の退避ディレクトリは、起動時に Forge の UID/GID 1000:1000 で作成する。旧手順で root が作成した共用の `/data/.feato-content/retired/` と、そこに既に退避した ZIP はその場所で保管する。権限エラーが続く場合は、停止・バックアップ後に `stat -c '%u:%g %a %n'` で `/data/tacz`、`/data/.feato-content`、存在する場合は `/data/.feato-content/retired-classics` を確認する。必要な修正は UID 1000 の書き込み・通過を妨げているディレクトリに限定する。

切り戻しは Forge を停止して更新後データを別途保全し、旧リビジョンの lock・同期スクリプトと整合した停止時 Volume バックアップを揃えて復元する。クライアントの構成も合わせる。障害版を含む構成へ戻す場合は、先に隔離コピーで起動可否を確認する。

## Gucci & VuittonとSuperb Warfareの復活

以下は従来の 0.8.9.2 復活時の記録。現行版の適用手順は上記を優先する。

[Gucci & Vuitton Attachments](https://www.curseforge.com/minecraft/mc-mods/tacz-gucci-vuitton-attachments/files/6062098)（project 1103436 / file 6062098）と [Superb Warfare](https://www.curseforge.com/minecraft/mc-mods/superb-warfare/files/9019882)（project 1218165 / file 9019882）をmanifestへ戻す。TaCZとArcanaは維持し、LesRaisins Tactical Equipementsは削除したまま。Superb Warfareの共通設定seedは新規Volumeや設定未作成時だけコピーする。既存Volumeの設定は上書きしない。

反映前にForgeを停止し、world・playerdata・config・modsを含むVolume全体をバックアップする。削除中にワールドが保存された場合、対象Modのアイテムや設置物はModの復活だけでは復元できない可能性がある。復旧が必要な場合は、復活前に保存したワールドとの関係を確認し、整合した削除前バックアップと旧Mod構成を用いて隔離環境で確認する。

更新manifest適用時、[Auto CurseForge](https://docker-minecraft-server.readthedocs.io/en/latest/types-and-platforms/mod-platforms/auto-curseforge/) が指定IDのJARを同期する。対象ファイルが退避済みの場合も再取得されるか起動ログと `/data/mods/` を確認する。取得に失敗した場合は公式配布元から同一ファイルを取得し、Forge停止後にSHA-256を照合して復元する。旧退避先から戻す場合も同じハッシュを確認し、同じModの別名JARが重複しないようにする。

- `guccivuitton-1.20.1-0.2.2.jar`: `9247e55f20acf8ec89af56d4ad45fcc8fe08bee9f7189421ef31835f3516bd57`
- `superbwarfare-0.8.9.2-mc1.20.1-65d985a64-all.jar`: `559930003f638080de648a8621821d785158768c3f69a762094ef4c8d3c4cc12`

クライアントも同じ2版とArcanaを導入し、同じModを重複させない。起動と接続、両Modのアイテム・銃・アタッチメント、既存ワールドを確認する。復活版の実サーバー起動・接続、ゲーム内の互換性は未検証。

LesRaisins Tacticalは引き続き同期対象外。過去の `retire-removed-tacz-addons.sh` はGucciとArcanaの設定まで退避してしまうためGitから削除した。データノードに古いコピーが残っていても実行しない。`/data/tacz/` を退避する場合は [TaCZディレクトリの退避](#taczディレクトリの退避) を使う。

隔離した新規ワールドのx86_64環境（エミュレーション、固定Java 17イメージ、Forge 47.4.28）では、`CF_FORCE_SYNCHRONIZE=true` により2 JARの再取得とSHA-256一致を確認し、Arcana・Proxy Compatible Forgeを含むサーバーが `Done` まで起動した。Gucci JARは `/data/tacz/gucci_vuitton_attachment` を自動展開するため、以前 `tacz/` を退避していても再生成される。旧ZIPや同名の別Gunpackは重複させない。Modのゲーム内動作、クライアント接続、Forwarding SecretとVelocity経由の接続、実ワールド、本番の動作は未検証。隔離ARM64環境ではArcanaネイティブライブラリのGLIBC不足により起動しなかった。Photonのクライアントクラス読込等の既存エラーも別途残る。
