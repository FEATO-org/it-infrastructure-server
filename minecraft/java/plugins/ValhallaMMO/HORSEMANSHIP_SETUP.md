# FEATO Horsemanship の導入

## 採用版と配布先

[FEATO Horsemanship v0.2.0](https://github.com/FEATO-org/feato_horsemanship/releases/tag/v0.2.0)を使用します。配布元の対象はPaper 26.2 build 126 / Java 25、ValhallaMMO 1.10.3、任意連携はBetterHorses 6.3とDualHorse 1.5.4です。既存Spiget URLは動的で、ローカル検証で実際に使用したBetterHorsesは6.4でした。本番でも起動ログで版を確認してください。

| 配布元 | コンテナ内の読み込み先 |
| --- | --- |
| `minecraft/java/plugins.txt`の固定Release JAR URL | `/data/plugins/feato-horsemanship-0.2.0.jar` |
| `minecraft/java/plugins/ValhallaMMO/skills/custom/HORSEMANSHIP.yml`（Release添付を基にGUIを調整） | `/data/plugins/ValhallaMMO/skills/custom/HORSEMANSHIP.yml` |
| `minecraft/java/plugins/FEATOHorsemanship/config.yml`（JAR同梱初期設定） | `/data/plugins/FEATOHorsemanship/config.yml` |
| `minecraft/java/prepare-paper-plugins.sh`と`patches/betterhorses-horsemanship.json` | `/extras/prepare-paper-plugins.sh`と`/extras/betterhorses-horsemanship.json` |

追跡するPlugin設定はComposeの`/plugins` mountから起動前に`/data/plugins`へ同期されます。ValhallaMMOが起動時にSkillを`HORSEMANSHIP`として登録するため、JARとSkillを同時に配布してPaperを再起動します。通常の配布ではGit管理の設定と`plugins.txt`を配置すればよく、Git管理外アセット用の`copy_plugins_to_remote.sh`による馬術JARの手動コピーは不要です。

`REMOVE_OLD_MODS_INCLUDE`には`feato-horsemanship-*.jar`を追加して、起動前に旧版JARを除去します。更新時は実在するRelease tagとasset名へURLを更新し、Skillと効果設定も同じ版の差分を確認してください。`/horsemanship reload`は効果設定の再読込だけで、Skill定義の変更にはPaper再起動が必要です。本番でGit管理設定を調整した場合は、次のデプロイ前に取り込みます。

## 専用 Skill/Profile 修正版への移行（公開待ち）

v0.2.0には、YAML Custom Skillの共通Profile型が標準EXP経路で解決されず、馬術EXP付与時に例外が発生する問題があります。enable成功はEXP・永続化の正常性を保証しません。配布元Pluginで専用Java Skill/Profileへの修正を準備しています。修正版の公開Release URLが確定するまで、このリポジトリのJAR manifestと旧Skill配置はv0.2.0のままです。旧JARへ新配置だけを適用しないでください。

修正版を採用する際は、以下を同じ作業ブランチで反映します。

1. `minecraft/java/plugins.txt`を実在する修正版Release JARの固定URLへ更新し、`deploys/versions.md`へ取得URL・対応版・確認結果を記録します。
2. 現在のGUI調整済み `minecraft/java/plugins/ValhallaMMO/skills/custom/HORSEMANSHIP.yml` を `minecraft/java/plugins/FEATOHorsemanship/horsemanship.yml` へ移し、未使用の `stats` セクションだけを除去します。Perk ID・表示・座標・条件・報酬・EXP曲線を維持します。新しい読み込み先は `/data/plugins/FEATOHorsemanship/horsemanship.yml` です。
3. `minecraft-data`ノードのPaperを正常停止し、ValhallaMMO DBと設定・旧JARを整合した組としてバックアップします。旧 `ValhallaMMO/skills/custom/horsemanship.yml` と `HORSEMANSHIP.yml`、別名でHORSEMANSHIPを定義する旧YAMLをVolume外へ退避します。Git側の削除だけではVolumeから消えません。管理元の `/plugins` にも旧ファイルを残さないでください。
4. 修正版JARと新配置の設定を配布し、起動前同期と完全再起動で適用します。MinecraftやValhallaMMOの `/reload`、Pluginのdisable/enableは使用しません。`/horsemanship reload`は引き続き効果設定だけが対象です。
5. `HORSEMANSHIP registered with dedicated HorsemanshipSkill/HorsemanshipProfile`を確認します。旧Skillとの重複や登録失敗ではPluginがdisableし、移動・戦闘Listenerは登録されません。
6. 管理者で `/skills`、`/valhalla profile HORSEMANSHIP`、`/valhalla exp HORSEMANSHIP 10`を実行し、EXP増分を確認します。鞍上の第一歩の未取得状態で100ブロック約10 EXP、取得後約10.5 EXP、馬上戦闘は2秒間隔0.5 EXPを確認します。対象馬・操縦者・後席・ログインし直し・完全再起動後の保存、標準reset/refund・NG+・排他条件も確認します。テストには本番プレイヤーデータを使用しません。

修正版はValhallaMMOのDB初期化後にUnlockCondition → 専用Profile → 専用Skillの順で公開API登録します。標準のLv・EXP・累積EXP・NG+、共通スキルポイント、PowerProfileの通常/永続取得PerkとPerk IDを維持し、データを削除・resetせず、独自DB/PDCへ移しません。旧EXPの独自移行は行いません。切り戻しは停止中に移行前の整合したDB・設定・JARを復元します。

## スキルと権限

馬術はLv 0-100、移動・持久・操作・戦闘・育成の5系統です。初期設定とPerkのLv・コスト・他スキルLv・排他条件は配布元の値を維持します。v0.2.0は通常PerkをValhallaMMOの永続profile内の取得リストで判定し、NG+効果は永続取得したMaster / Legendから判定します。共通スキルポイントは他スキルと共有します。

- 対象mountは馬、スケルトンホース、ゾンビホース、ロバ、ラバ。ラクダとラマは初期設定で対象外です。
- 移動EXPは操縦者に100ブロックごと10、後席には付与しません。馬上戦闘EXPは攻撃者本人に2秒間隔で0.5を付与します。
- Perk取得前の操縦速度は-5%、鞍上の第一歩の取得後は-2%、手綱の心得の取得後はペナルティなしです。
- Lv20の「追う」は操縦中にメインハンドのリードを右クリックして使用します。初期値は応答1秒、速度+6%、5秒、再使用35秒、終了後の疲労率15%です。
- BetterHorsesの遺伝・Trait・base attributeは馬術で直接書き換えません。`馬を見る目`取得者は`/horsemanship inspect`、`生産者の眼`取得者は`/horsemanship parent`と`/horsemanship predict`を使えます。
- 育成コマンドは取得Perkで制限され、追加の一般権限は不要です。reload用`feato.horsemanship.admin`は既定OPで、`setup_minecraft_permissions.sh`では管理グループだけに付与します。

標準のActionBarとチャットを使用し、専用リソースパックの追加は不要です。

## スキルツリーGUIの配置

Git管理のSkillはv0.2.0の表示を調整したものです。Perk ID・Lv・cost・報酬・前提・排他・NG+と効果設定は維持し、JARやReleaseのSkillをそのまま上書きするとGUI変更が失われます。今後の版更新では表示差分を保持して照合してください。

ValhallaMMO 1.10.3 JAR内のArchery / Mining / Heavy Armor / Farmingを参考に、Lv10ごとにxを2進め、左から右へ進行します。主幹はy=6、機動0、持久3、技術9、馬上戦闘14、馬管理18です。線用の空間を確保し、馬上戦闘のLv70・90は上段13／下段15へ配置します。馬管理のLv40・60・80にノードは追加しません。

```text
機動 y=0     駿足 ─ 抜け出し ─ 全速駆け ─ 即応 ─ 電光の発進 ─ 風に乗る ─ 疾風一体
持久 y=3     長駆 ─ 絶えぬ追い ─ 遠乗りの心得 ─ 巡航の極意 ─ 息を吹き返す ─ 不屈の遠乗り ─ 果てなき道
基礎 y=6     鞍上の第一歩 ─ 手綱の心得 ─ 追う ─ 巧者の手綱 ─ 熟練騎手 ─ 信頼の手綱 ─ 人馬一体
技術 y=9     確かな手綱 ─ 飛越 ─ 足取り確か ─ 冷静な手綱 ─ 精密操作 ─ 確かな着地 ─ 手綱の達人
戦闘 y=14    騎兵 ─┬─ 突撃号令
                  ├─ 騎射の心得
                  └─ 古参騎兵 ─┬─ 重装騎兵 ─┬─ 鉄騎先鋒
                               │            └─┐
                               │               初撃（Lv80、中央）
                               │            ┌─┘
                               └─ 軽装騎兵 ─┴─ 疾駆戦騎
馬管理 y=18  馬を見る目 ─ 生産者の眼 ─ 血統研究 ─ 名伯楽
```

図は前提の概念図です。Combatの騎射・古参騎兵は騎兵から、鉄騎先鋒／疾駆戦騎は重装／軽装から線を引きます。初撃からLv90への取得前提は追加しません。接続線は対象Perkの標準3状態色（灰・橙・緑）で描き、各slotを1つの線だけに割り当てます。標準設定と公式Magic+ValhallaMMO packの既存モデルで向きを確認し、独自CMDやT字モデルは追加していません。

Lv30の5入口はx=6に揃え、「追う」からの分岐を説明と標準の前提表示で示します。複数レーンを横断する5本の長い線は省き、専門内の前提だけを接続します。飛越・突撃号令は「追う」に追加効果、抜け出し・絶えぬ追いは「追う」を変化させる、と説明冒頭で区別します。駿足・長駆は両立可能、排他はLv40の説明と既存lockで示します。Lv100は基礎の右端x=20、信頼の手綱だけを接続します。NG+は標準Archery同様hiddenの共通座標(0,20)に置き、通常線から外します。

`starting_coordinates: "0,3"`はメニュー内部の中心値ではなく、初期表示の左上に対応します（内部でx+4、y+2）。初期9×5枠のx=0..8、y=3..7に基礎Lv0・10・20と持久Lv30が入り、上下スクロールで残る専門入口、右スクロールで後半へ進みます。6レーン全部を5行に詰めません。ナビゲーションボタンが基礎序盤のノードを隠さない座標です。

説明は現在の`FEATOHorsemanship/config.yml`とv0.2.0実装に基づき、`/n`区切りで最大4行に整理しています。必要Lv・cost・他スキルLv・取得前提はValhalla標準loreへ任せます。設定の数値を変更した場合は説明も同期してください。失速の補助回復には既存の最低水平速度・移動ごとの上限が適用されます。

GUI用の8件の検証テスト（重複・誤った角の向き・効果変更の拒否を含む）と変更前YAML比較が成功しました。Pluginソースの一時コピーへ追跡Skill・効果設定を組み込み、既存14テストと`test`、続けて`clean build`を実行して成功しています。配布JARは更新していません。

ローカル静的検証はPyYAMLのあるPythonで`python script/validate_horsemanship_tree.py --baseline <変更前のhorsemanship.yml>`を実行します。検証テストは`python -m unittest discover -s script -p test_horsemanship_tree.py`です。GUI配置の実クライアント表示は未確認です。適用は既存の起動前同期とPaper再起動を使い、Java/Bedrockで初期表示・スクロール・各lock状態・loreを確認してください。GUIだけ戻す場合は停止中に変更前SkillをGit配布元とVolume側へ戻して再起動し、JAR・効果設定・profileは維持します。

## BetterHorsesの馬上ダメージ補正

馬術側の攻撃補正と重複しないよう、`prepare-paper-plugins.sh`は既存のFloodgate鍵コピーを実行した後、`mc-image-helper patch`で永続Volumeの`/data/plugins/BetterHorses/config.yml`にある`settings.mounted-damage-boost.enabled`だけを`false`にします。ほかの繁殖・育成・Trait設定は保持します。

初回で設定ファイルがない場合は、このキーを含む最小設定を作成します。BetterHorses 6.4が不足している既定値を起動時に補完することをローカル確認しています。空ファイルなど不正な状態では準備処理が失敗してPaper起動を止めます。このキーは毎起動時に無効化します。

## 適用順

1. `minecraft-data`ノードでPaperを停止し、Paper Volume（ValhallaMMO profile・共通スキルポイント・取得Perkを含む）と既存BetterHorses設定をバックアップします。
2. 既存Volumeの `ValhallaMMO/skills/custom/` に小文字名の旧Skill設定がある場合は、Paper停止中にバックアップしてVolume外へ退避します。同期で旧名が削除されるとは限りません。正本は `HORSEMANSHIP.yml` の1ファイルだけにします。Git管理のSkill・効果設定・`plugins.txt`・追加の起動スクリプトとpatch・Composeを同じ版で配置します。起動スクリプトの実行権限を保持してください。
3. 必要な環境変数がある環境でCompose / Swarm設定を検証し、Paper taskを更新します。bind mountファイルの更新だけでSwarmが再起動したと判断せず、taskの再作成と起動前同期を確認します。
4. `/data/plugins/ValhallaMMO/skills/custom/HORSEMANSHIP.yml` の配置と旧名が残っていないことを確認します。ValhallaMMOの`Registered custom skill HORSEMANSHIP.yml`、`FEATO Horsemanship enabled`、BetterHorses連携・排他条件登録の警告がないこと、実際の各Plugin版を確認します。Volume側の馬上ダメージ加算が`false`であることも確認します。
5. 権限設定スクリプトを実行する場合は、`minecraft-data`ノードで実際の一般・管理グループ名を指定します。このスクリプトは既存の商店・経済・役職権限も適用します。
6. 次のプレイヤー操作を確認してから利用を開始します。

## 確認済みと未確認

2026-10-04、隔離したlocalhost限定のPaper 26.2 build 126 / Oracle GraalVM 25.0.4、ValhallaMMO 1.10.3、FEATO Horsemanship 0.2.0、BetterHorses 6.4、DualHorse 1.5.4、Magic 11.2.4で確認しました。

- Release asset digestとSHA256SUMSの一致、同梱Skillとの一致、Java 25 / api-version 26.2。
- 43 PerkのYAML、取得報酬、NG+報酬、前提Perk、排他条件、重複しない座標。
- 馬術の登録と5 Pluginの有効化、Magicから馬術Lv・EXPの認識、馬術設定reload、正常停止。
- BetterHorses最小設定への不足既定値の補完。起動前patchの初回作成、既存設定保持、繰り返し適用、空設定での起動拒否。

このローカル検証はMinecraft全Plugin構成やVault Economyを含めた検証ではありません。Magic側には既存exampleの重複キー・式警告がありましたが、馬術の報酬未登録エラー・連携初期化・排他条件登録の警告はありませんでした。

過去のmacOS上の起動確認は、Linuxでのファイル名の大小文字を区別した読み込みを保証しません。ValhallaMMO 1.10.3が大文字のSkill typeを設定ファイル名として使うため、Release添付の小文字名を配布時には `HORSEMANSHIP.yml` とします。ConfigurableProfile・EXP付与・Profile Registry・progression再計算の既知の懸念は今回未対応で、enable成功だけでは育成・保存・EXP処理全体の正常性を判断しません。

2026-10-04、隔離したLinux / Java 25 / Paper 26.2 build 126で、大文字名の追跡設定を使いValhallaMMO 1.10.3とFEATOHorsemanship 0.2.0のenable完了を確認しました。埋め込みリソース欠落・ValhallaMMOのenable失敗・起動中のdisableは発生していません。この検証にはFEATOGunValhallaBridgeと本番の全Plugin構成を含めていません。

本番とJava/Bedrockの実プレイヤー操作は未確認です。以下を実機で確認してください。

- スキルツリーと日本語表示、Lv・EXP・共通スキルポイント、通常Perk取得・返却・reset、NG+、排他Perk、他スキルLv条件。
- 対象mountの操縦者への移動EXP、DualHorse後席への移動EXP抑止、攻撃者本人への戦闘EXP。
- Perk取得前後の速度、「追う」、疲労・クールダウン、降車・再接続時の一時効果解除、馬上攻撃補正の重複がないこと。
- 育成コマンドの取得条件、BetterHorses Training・回復補助、一般プレイヤーのreload拒否。
- 既存のMagic、BetterHorses、DualHorseと本番の全Pluginを含めた併用。

## 戻し方

Paperを停止し、導入前の配布設定・旧JAR除去対象・管理権限設定へ戻します。`PRE_START_SCRIPT`を`/extras/copy-floodgate-key.sh`へ戻し、馬術用の準備スクリプトとpatchのmountを外します。Volume内の`feato-horsemanship-*.jar`と`ValhallaMMO/skills/custom/HORSEMANSHIP.yml`をVolume外へ退避し、BetterHorses設定をバックアップから戻してから再起動します。Gitからの削除だけではVolume内のファイルは消えません。付与済みの`feato.horsemanship.admin`も必要に応じて管理グループから外します。

導入後に消費した共通スキルポイント・profileも戻す場合は、導入前の整合したバックアップから復旧します。馬術v0.1.0へのダウングレードは行わないでください。2026-10-03の同じPaper / ValhallaMMO構成では`horsemanship_first_saddle_set`の未登録エラーでValhallaMMOと馬術が無効化されました。v0.2.0では通常Perk報酬と取得状態の参照先を揃え、この起動エラーは解消しています。
