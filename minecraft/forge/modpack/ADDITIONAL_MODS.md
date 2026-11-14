# Forge 追加 Mod の調査と受入条件

2026-11-14 時点。`develop` の基準は Bad Mobs を含む manifest 58 件（クライアント専用の除外対象を含む）。Forge 47.4.28、Create 6.0.8、AE2 15.4.12、GuideME 20.1.15、TaCZ 1.2.0、SBW は 0.8.9 に変更する。以下の11件を manifest に追加し、環境と依存関係は隔離試験で受け入れるまで未確定とする。CurseForge の各固定ページと、Curse Maven から取得した同一 project/file ID の JAR の `META-INF/mods.toml` を照合した。JAR の取得成功は Auto CurseForge による取得成功を意味しない。全候補の固定ファイルページは Forge 1.20.1 対応表記。Forge 範囲は JAR の loaderVersion または forge 依存を記す。BOTH は依存の適用側であり、接続要件の実測ではない。

| 候補（固定配布元） | project / file | JAR メタデータと判断 |
| --- | --- | --- |
| [Create: Connected 1.2.3](https://www.curseforge.com/minecraft/mc-mods/create-connected/files/8290615) | 947914 / 8290615 | 追加。Forge 47+、Create 6.0.8+ BOTH。1.2.0 の登録パッケージ変更に依存する他アドオンとの競合は未検証。 |
| [Create: Easy Stone Generators 1.0.0 Beta](https://www.curseforge.com/minecraft/mc-mods/create-stone-generators/files/6224618) | 1206505 / 6224618 | 追加。loader 47+、Minecraft 1.20.1 BOTH。JAR に Create の依存範囲記載なし。別の `create-stone-generator` ではない。Create 6 でのレシピ・起動は未検証。 |
| [ExtendedAE 1.4.22](https://www.curseforge.com/minecraft/mc-mods/ex-pattern-provider/files/9304849) | 892005 / 9304849 | 追加。Forge 47+、AE2 15.4.1+、GuideME [20.1.7,20.2.0)、Glodium 1.0+、すべて BOTH。現行固定版は宣言範囲内。 |
| [Create: Teleporters 3.0.1b](https://www.curseforge.com/minecraft/mc-mods/create-teleporters/files/9172985) | 829272 / 9172985 | 追加。Forge [47.4.10,48)、Create [6.0.8,6.0.9) BOTH。配布元は Custom Portal の TPS と遠距離リンクの修正を記載、実測は未実施。 |
| [Create: Mining Laser 0.0.6](https://www.curseforge.com/minecraft/mc-mods/create-mining-laser/files/7192728) | 1378602 / 7192728 | 追加。Forge 47+、Create [6.0.6,6.1.0) BOTH。生産量とチャンク処理は未測定。 |
| [Zoe Isn't Cyberpunk 2.2.5](https://www.curseforge.com/minecraft/mc-mods/zoe-isnt-cyberpunk/files/7253085) | 896842 / 7253085 | 追加。loader 47+、Minecraft 1.20.1 BOTH、JEI 任意。TaCZ・Weapons and Tactics・SBW とのバランスや競合は未検証。 |
| [Create: New Age 1.2.0](https://www.curseforge.com/minecraft/mc-mods/create-new-age/files/8215201) | 905861 / 8215201 | 追加。Forge 47+、Create [6.0.8,6.1.0)、ESL 1.1.3 BOTH。JAR は ESL 1.1.3 を jar-in-jar で同梱、読み込みは未確認。Crafts & Additions と電力機能が重なるが相互運用は未検証。配布元は過熱した原子炉が爆発すると明記、建築への影響を試験する。 |
| [Iron Furnaces 4.1.8](https://www.curseforge.com/minecraft/mc-mods/iron-furnaces/files/7888952) | 237664 / 7888952 | 追加。Forge 46+、Minecraft [1.20,1.21)、JEI 13+ 任意 BOTH。 |
| [Glodium 1.5](https://www.curseforge.com/minecraft/mc-mods/glodium/files/5226922) | 957920 / 5226922 | 追加。Forge 47+、Minecraft [1.20.1,1.21) BOTH。ExtendedAE のライブラリ。 |
| [AEInfinityBooster 1.0.0+51](https://www.curseforge.com/minecraft/mc-mods/aeinfinitybooster/files/6482257) | 559313 / 6482257 | 追加。Forge 47+、AE2 15.0.9-beta+ BOTH。配布元の現行説明には `chunkLoadingEnabled=true` があるが、対象 JAR のクラス・メタデータで設定登録や同キーを確認できず、生成設定も未検証。false の seed は推測して作らない。対象版のチャンク維持の有無と生成設定を実機確認する。 |
| [Invasion Mod (Fork) 2.0.0](https://www.curseforge.com/minecraft/mc-mods/invasion-mod-unofficial/files/8844167) | 1628663 / 8844167 | 削除。Forge 47.1.106+、Minecraft 1.20.1 BOTH。既存ワールドに Nexus や Mob 等がある場合の影響は未検証。 |
| [Frontline Combat Pack 1.2.1](https://www.curseforge.com/minecraft/mc-mods/frontline-combat-pack/files/8650627) | 1465874 / 8650627 | 追加。Forge 47+、SBW `[0.8.9]` BOTH を必須とし、SBW 0.8.9 JAR の申告版と一致する。隔離新規ワールドは起動・再起動したが弾薬処理の Mixin が失敗。接続・ゲーム内動作・SBW 単体との負荷比較は未検証。 |

既存 Weapons and Tactics 1411291 / 9473803 は維持し、SBW は 1218165 / 8104849 に変更する。どちらも重複登録しない。記載以外の任意依存・競合、生成設定と既定値、クライアント接続、ワールド保存形式は未確認。追加 Mod はブロック・アイテム等を保存し得るため、除去後の保存はデータ喪失につながる。JAR の依存宣言が満たされても実行時互換性の証明にはならない。

## 隔離試験と運用

本番 Volume をマウントしない。x86_64 の隔離環境で停止時の整合した Volume コピーまたは新規ワールドを使い、[性能管理](../PERFORMANCE.md) の測定条件を記録する。基準58件、次に Connected・Iron Furnaces・New Age・ExtendedAE・Glodium、次に Easy Stone・Teleporters・Mining Laser・Zoe の順に試す。次に AEInfinityBooster を追加する。SBW 0.8.9 単体と Frontline 追加後を同条件で比較し、Invasion を含まない構成を検証する。

各段階で起動時間、登録 Mod、依存・Mixin・ClassNotFound エラー、ヒープ・RSS・CPU・GC、spark の TPS・平均と P95 MSPT、チャンク・エンティティ数を同一条件で記録する。Java クライアント接続、レシピ、保存・再起動も確認する。暫定目標は TPS 20、P95 45ms 以下、基準からの悪化15%以内であり負荷条件を併記する。複数 Mining Laser・ExtendedAE の高速バス／パターンプロバイダー／Assembler Matrix、Teleporters の遠距離・別ディメンション・列車、New Age 原子炉の建築破壊、Zoe と既存戦闘 Mod を試す。Invasion の削除後に Nexus・Mob 等の保存データを確認する。SBW と Frontline、追加 Mod の共存を確認する。

今回、対象構成の隔離起動・再起動では Frontline の Mixin 失敗を確認した。[試験結果](README.md#2026-11-14-隔離起動結果) を参照。基準および各段階の性能、クライアント接続・ゲーム内動作は未測定。ARM64 上のエミュレーションは本番性能の代用にしない。新設定 seed は追加していない。`prepare-forge.sh` は存在しない `/data/config` のファイルだけを seed するため、将来設定を追加する場合は新規 Volume と既存 Volume を区別し、既存設定を停止・バックアップ後に個別比較して反映する。ワールド単位の serverconfig も実物を確認する。

適用時は [既存の更新・復旧手順](README.md#58件版への更新と復旧) に従い停止し、world、playerdata、mods、tacz、config、管理状態を含む Volume 全体をバックアップして復元可能性を確認する。クライアントにも対応 pack を配布する。`CF_FORCE_SYNCHRONIZE` は常設しない。残存 JAR を除去する必要があれば実体と ID を確認し対象だけを退避する。ロールバックは停止して旧 revision と整合した停止時 Volume バックアップを一緒に復元し、新 Mod のデータを欠いたワールドを保存しない。本番操作は今回実施していない。
