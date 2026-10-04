# FEATO Horsemanship の導入

## 採用版と配布先

[FEATO Horsemanship v0.2.0](https://github.com/FEATO-org/feato_horsemanship/releases/tag/v0.2.0)を使用します。配布元の対象はPaper 26.2 build 126 / Java 25、ValhallaMMO 1.10.3、任意連携はBetterHorses 6.3とDualHorse 1.5.4です。既存Spiget URLは動的で、ローカル検証で実際に使用したBetterHorsesは6.4でした。本番でも起動ログで版を確認してください。

| 配布元 | コンテナ内の読み込み先 |
| --- | --- |
| `minecraft/java/plugins.txt`の固定Release JAR URL | `/data/plugins/feato-horsemanship-0.2.0.jar` |
| `minecraft/java/plugins/ValhallaMMO/skills/custom/horsemanship.yml`（Release添付） | `/data/plugins/ValhallaMMO/skills/custom/horsemanship.yml` |
| `minecraft/java/plugins/FEATOHorsemanship/config.yml`（JAR同梱初期設定） | `/data/plugins/FEATOHorsemanship/config.yml` |
| `minecraft/java/prepare-paper-plugins.sh`と`patches/betterhorses-horsemanship.json` | `/extras/prepare-paper-plugins.sh`と`/extras/betterhorses-horsemanship.json` |

追跡するPlugin設定はComposeの`/plugins` mountから起動前に`/data/plugins`へ同期されます。ValhallaMMOが起動時にSkillを`HORSEMANSHIP`として登録するため、JARとSkillを同時に配布してPaperを再起動します。通常の配布ではGit管理の設定と`plugins.txt`を配置すればよく、Git管理外アセット用の`copy_plugins_to_remote.sh`による馬術JARの手動コピーは不要です。

`REMOVE_OLD_MODS_INCLUDE`には`feato-horsemanship-*.jar`を追加して、起動前に旧版JARを除去します。更新時は実在するRelease tagとasset名へURLを更新し、Skillと効果設定も同じ版の差分を確認してください。`/horsemanship reload`は効果設定の再読込だけで、Skill定義の変更にはPaper再起動が必要です。本番でGit管理設定を調整した場合は、次のデプロイ前に取り込みます。

## スキルと権限

馬術はLv 0-100、移動・持久・操作・戦闘・育成の5系統です。初期設定とPerkのLv・コスト・他スキルLv・排他条件は配布元の値を維持します。v0.2.0は通常PerkをValhallaMMOの永続profile内の取得リストで判定し、NG+効果は永続取得したMaster / Legendから判定します。共通スキルポイントは他スキルと共有します。

- 対象mountは馬、スケルトンホース、ゾンビホース、ロバ、ラバ。ラクダとラマは初期設定で対象外です。
- 移動EXPは操縦者に100ブロックごと10、後席には付与しません。馬上戦闘EXPは攻撃者本人に2秒間隔で0.5を付与します。
- Perk取得前の操縦速度は-5%、鞍上の第一歩の取得後は-2%、手綱の心得の取得後はペナルティなしです。
- Lv20の「追う」は操縦中にメインハンドのリードを右クリックして使用します。初期値は応答1秒、速度+6%、5秒、再使用35秒、終了後の疲労率15%です。
- BetterHorsesの遺伝・Trait・base attributeは馬術で直接書き換えません。`馬を見る目`取得者は`/horsemanship inspect`、`生産者の眼`取得者は`/horsemanship parent`と`/horsemanship predict`を使えます。
- 育成コマンドは取得Perkで制限され、追加の一般権限は不要です。reload用`feato.horsemanship.admin`は既定OPで、`setup_minecraft_permissions.sh`では管理グループだけに付与します。

標準のActionBarとチャットを使用し、専用リソースパックの追加は不要です。

## BetterHorsesの馬上ダメージ補正

馬術側の攻撃補正と重複しないよう、`prepare-paper-plugins.sh`は既存のFloodgate鍵コピーを実行した後、`mc-image-helper patch`で永続Volumeの`/data/plugins/BetterHorses/config.yml`にある`settings.mounted-damage-boost.enabled`だけを`false`にします。ほかの繁殖・育成・Trait設定は保持します。

初回で設定ファイルがない場合は、このキーを含む最小設定を作成します。BetterHorses 6.4が不足している既定値を起動時に補完することをローカル確認しています。空ファイルなど不正な状態では準備処理が失敗してPaper起動を止めます。このキーは毎起動時に無効化します。

## 適用順

1. `minecraft-data`ノードでPaperを停止し、Paper Volume（ValhallaMMO profile・共通スキルポイント・取得Perkを含む）と既存BetterHorses設定をバックアップします。
2. Git管理のSkill・効果設定・`plugins.txt`・追加の起動スクリプトとpatch・Composeを同じ版で配置します。起動スクリプトの実行権限を保持してください。
3. 必要な環境変数がある環境でCompose / Swarm設定を検証し、Paper taskを更新します。bind mountファイルの更新だけでSwarmが再起動したと判断せず、taskの再作成と起動前同期を確認します。
4. ValhallaMMOの`Registered custom skill horsemanship.yml`、`FEATO Horsemanship enabled`、BetterHorses連携・排他条件登録の警告がないこと、実際の各Plugin版を確認します。Volume側の馬上ダメージ加算が`false`であることも確認します。
5. 権限設定スクリプトを実行する場合は、`minecraft-data`ノードで実際の一般・管理グループ名を指定します。このスクリプトは既存の商店・経済・役職権限も適用します。
6. 次のプレイヤー操作を確認してから利用を開始します。

## 確認済みと未確認

2026-10-04、隔離したlocalhost限定のPaper 26.2 build 126 / Oracle GraalVM 25.0.4、ValhallaMMO 1.10.3、FEATO Horsemanship 0.2.0、BetterHorses 6.4、DualHorse 1.5.4、Magic 11.2.4で確認しました。

- Release asset digestとSHA256SUMSの一致、同梱Skillとの一致、Java 25 / api-version 26.2。
- 43 PerkのYAML、取得報酬、NG+報酬、前提Perk、排他条件、重複しない座標。
- 馬術の登録と5 Pluginの有効化、Magicから馬術Lv・EXPの認識、馬術設定reload、正常停止。
- BetterHorses最小設定への不足既定値の補完。起動前patchの初回作成、既存設定保持、繰り返し適用、空設定での起動拒否。

このローカル検証はMinecraft全Plugin構成やVault Economyを含めた検証ではありません。Magic側には既存exampleの重複キー・式警告がありましたが、馬術の報酬未登録エラー・連携初期化・排他条件登録の警告はありませんでした。

本番とJava/Bedrockの実プレイヤー操作は未確認です。以下を実機で確認してください。

- スキルツリーと日本語表示、Lv・EXP・共通スキルポイント、通常Perk取得・返却・reset、NG+、排他Perk、他スキルLv条件。
- 対象mountの操縦者への移動EXP、DualHorse後席への移動EXP抑止、攻撃者本人への戦闘EXP。
- Perk取得前後の速度、「追う」、疲労・クールダウン、降車・再接続時の一時効果解除、馬上攻撃補正の重複がないこと。
- 育成コマンドの取得条件、BetterHorses Training・回復補助、一般プレイヤーのreload拒否。
- 既存のMagic、BetterHorses、DualHorseと本番の全Pluginを含めた併用。

## 戻し方

Paperを停止し、導入前の配布設定・旧JAR除去対象・管理権限設定へ戻します。`PRE_START_SCRIPT`を`/extras/copy-floodgate-key.sh`へ戻し、馬術用の準備スクリプトとpatchのmountを外します。Volume内の`feato-horsemanship-*.jar`と`ValhallaMMO/skills/custom/horsemanship.yml`をVolume外へ退避し、BetterHorses設定をバックアップから戻してから再起動します。Gitからの削除だけではVolume内のファイルは消えません。付与済みの`feato.horsemanship.admin`も必要に応じて管理グループから外します。

導入後に消費した共通スキルポイント・profileも戻す場合は、導入前の整合したバックアップから復旧します。馬術v0.1.0へのダウングレードは行わないでください。2026-10-03の同じPaper / ValhallaMMO構成では`horsemanship_first_saddle_set`の未登録エラーでValhallaMMOと馬術が無効化されました。v0.2.0では通常Perk報酬と取得状態の参照先を揃え、この起動エラーは解消しています。
