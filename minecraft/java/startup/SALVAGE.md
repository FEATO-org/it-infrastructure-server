# ValhallaMMO 装備分解の品質制限

釣りLv50の分解パークを取得したプレイヤーが、鍛冶品質情報を持たない通常装備も
分解できるようにします。自作・他プレイヤー製作・釣り・Mobドロップの入手経路で
制限を追加しません。既存の品質付き装備も対象です。品質を付与する処理ではありません。

## 確認した構成と仕様

2026-10-14、`plugins.txt` の [公式1.10.3 JAR](https://cdn.modrinth.com/data/rxrgsoud/versions/GkeSDJSq/ValhallaMMO_1.10.3.jar)
を取得し、ZIP整合性、`plugin.yml` の版、レシピ、`javap -c -p` の実装を確認しました。
SHA-256は `a3e94b75cf3d050769bba63dcf1a10df1db0b286c28cc2e11a2ff85acba403fc` です。
[公式ソース](https://github.com/Athlaeos/ValhallaMMO) は補助資料として参照し、以下は
masterの仕様を推測したものではなく、取得した1.10.3 JARで確認した内容です。

- `CraftingTableListener.verifyIngredients` はtinkerレシピで
  `requireValhallaTools` がtrue、`EquipmentClass` に該当し、
  `SmithingItemPropertyManager.hasSmithingQuality` がfalseなら結果を返しません。
  判定はPDCの `valhallammo:quality_smithing`（INTEGER）の有無です。品質の値、製作者や所有者の一致ではありません。
- 同じメソッドのレシピ解放判定は独立しています。`unlockedForEveryone`、
  Profileの解放済みレシピ、`valhalla.allrecipes`、`valhalla.recipe.<name>` を検査します。
  今回はそれらも、追跡中の `skills/fishing_progression.yml` のLv50 / `recipes_unlock` も変更しません。
  一般プレイヤーへ解放を迂回する権限を追加しません。
- `onLoad` / `save` は欠損ファイルだけをJARから生成します。Paper起動前には、
  初回のレシピJSONはまだありません。26.2ではbase、1.21.9+、26.1+を生成します。
  1.21.11+は26.1未満向けなので新規seedしません。既存ファイルは検査します。
- `CustomRecipeRegistry.loadFiles` はbaseと対応版のファイルを読み込みます。
  版別gridファイルを100tick後に `gridRecipes.values()` で再保存することもJARで確認しました。
  また `saveAll` はbaseファイルを保存します。そのためbaseだけの一度きりの編集では不十分です。
  既存の空配列 `[]` に既定レシピを補充することはしません。
- Gitの `plugins/ValhallaMMO/` にはgridレシピはありません。
  `/plugins` はGit管理の設定、`/data/plugins/ValhallaMMO/recipes/` が永続Volume内の実際の読み込み先です。
  追跡設定との同期を先に行い、その後の `PRE_START_SCRIPT` で補正し、最後にPaperを起動します。
  順序は [itzgの起動スクリプト](https://github.com/itzg/docker-minecraft-server/tree/de5350c08e4eb9332b22341c33fd3e180fb85670/scripts)
  の `start-setupMounts` と `start-finalExec` で確認しました。
  イメージタグは可変なので、実際の配布イメージでの起動ログ確認は受入時に必要です。

| JAR内のファイル | 公式分解レシピ数 | 既定のtrue数 | 初回seed（26.2） |
| --- | ---: | ---: | --- |
| `grid_recipes.json` | 67 | 67 | する |
| `grid_recipes_1_21_9+.json` | 15 | 15 | する |
| `grid_recipes_26_1+.json` | 4 | 4 | する |
| `grid_recipes_1_21_11+.json` | 4 | 4 | しない（既存は検査） |

公式名は合計86種類です。最後の2ファイルの4種類は同名のrealspearです。
防具（革・チェーン・金・鉄・ダイヤ・銅）、公式の木・石・金・鉄・ダイヤ・銅の
工具・武器・追加武器が対象です。公式に存在しない名前は作りません。
既存FEATOの釣りパークは94件の `salvage_*` を解放し、公式86種類をすべて含みます。
差の8件は取得JARの公式レシピに存在しません。解放一覧はそのまま保持します。

## 実装と保護範囲

`prepare-paper-plugins.sh` の末尾から `startup/valhalla-salvage.sh` を実行します。
Java 25と既存mc-image-helperのJackson（`/usr/share/mc-image-helper/lib/*`）を使う
一回限りの処理で、常駐Pluginや新規ランタイムを追加しません。
汎用 `mc-image-helper patch` だけではJARとの識別照合、全対象の事前検証、
無変更時の書き込み回避をまとめて保証できないため、小さな専用処理に分離しました。

1. ダウンロード済みのValhallaMMO JARが1個で、上記SHA-256と一致することを検証します。
   staged updaterのValhallaMMO JAR、未レビューのJAR、Minecraft VERSIONが26.2以外なら起動を止めます。
2. 固定JARから4ファイルを解析し公式名の一覧を得ます。既存JSONを優先し、
   未生成の有効版ファイルだけ同梱の**完全な公式ファイル**をseedします。
   空ファイル・空レシピの生成、既存ファイルの初期化、全レシピ再生成は行いません。
3. 名前だけでなく、公式のshaped/shapeless key、tinker設定・配置、材料のslotとoptionが一致する
   レシピだけtrueをfalseへ変更します。公式レシピの版別ファイルからbaseへの移動にも対応します。
   レシピキーまたは材料のoptionを変更した独自レシピはskippedになります。
   同じ公式ID・配置・optionを維持したカスタマイズは公式レシピの編集として扱います。
   `exactIngredient` のBukkit ItemStack再シリアライズは照合から除き、値自体を保持します。
   公式IDを流用して材料アイテムだけ置換した独自レシピはこの境界では区別できないため、適用前に確認してください。
4. 材料、結果、Modifier、未知フィールド、解放設定を保持します。
   boolean以外の品質flag、不正JSON、重複キー・レシピ名、余分なJSON文書、symlinkを拒否します。
   全対象ファイルを解析・検証してから書き込み、同じディレクトリの一時ファイルをatomic moveします。
   原子的なmoveに非対応なら通常の上書きへfallbackしません。
   原子性はファイル単位です。複数ファイルのI/O失敗では、成功済みファイルが補正済みの場合があります。
5. falseだけのファイルは書き込みません。ファイルごとに `inspected`、`changed`、
   `unchanged`、`skipped` と理由をログへ出します。解析エラーに入力JSONを表示しません。
   skippedがある場合は成功扱いでも運用レビューが必要です。

品質情報のないアイテムに対する別の材料条件やModifierは引き続き有効です。
低い鍛冶スキルや耐久値では結果が0になって分解できない場合があります。
品質flagをfalseにしただけで全アイテムの分解成功を保証するものではありません。

## バランスと特殊装備

1.10.3の `AmountScale` は分解者の一般・素材別の鍛冶品質statとfraction stat、
`skillEfficiency` を使います。元の装備の品質値を還元率として使う処理ではありません。
JARの `skills/smithing.yml` は
`quantity_scaling: '0.7/300 * %rating% + 0.1,MULTIPLIER,0,0.8'` です。
既定で還元率は0〜80%に制限されます。耐久減少分を `AmountSet` の基準量に掛けて
切り捨てた後、還元率を掛けて再び切り捨てます。
公式分解は `skillEfficiency=1`、`minimumFraction=0`、`damagePenalty=true` を維持します。
Gitでsmithing.ymlは配布していないため、永続Volume側でカスタマイズされている場合の
還元率上限は未確認です。既存レシピのAmountSetやminimumFraction等が編集済みの場合も
この既定の計算とは異なります。80%を本番の確認済み値として扱わないでください。

| 装備例 | 通常製作の主素材量 | 分解基準量 | 最大還元（無傷、既定80%） |
| --- | --- | ---: | --- |
| 鉄のツルハシ | 鉄3個＋棒 | 27 | 鉄ナゲット21個 |
| ダイヤのヘルメット | ダイヤ5個 | 45 | ダイヤの破片36個（9破片換算で4個） |
| 革のヘルメット | 革5個 | 5 | 革4個 |
| 木／石のツルハシ | 主素材3個＋棒 | 3 | 主素材2個 |

公式の通常装備の往復だけでは、既定上限により製作主素材より少ない還元になります。
釣り・Mobドロップは製作支出のない素材供給となり、装備の回収farmは素材供給を増やします。
この変更で意図した範囲ですが、実サーバーの供給量・経済への影響は未測定です。

**特殊アイテムに対するリスクはあります。** JARの `MaterialChoice.matches` は基本素材だけ、
`MaterialWithIDChoice.matches` は素材とValhalla CustomIDを検査し、両方IDなしも許可します。
CustomModelData、名前、エンチャント、他PluginのPDCだけで特殊装備を除外する条件ではありません。
例えば隔離サーバーで品質なし・CustomModelData付き鉄防具を安価に発行し、Lv50パーク取得者で
公式分解へ入れると、材料条件上は受理される可能性があります。反復購入／発行価格と
還元素材の売値が逆転すると経済上の増殖になります。この再現は実機では未実施です。
FEATOで実際に無限・安価に発行できる該当特殊装備は今回の静的調査で特定できていません。

適用前にMagic / ExecutableItems / Bridge等の実際の装備を列挙し、入手コスト、基本素材、
Valhalla CustomID、CMD、PDC、分解・換金結果を比較してください。危険な品が見つかったら
公開を止め、対象アイテムの除外validationや材料choiceの厳密化を別変更として検討します。
今回は還元式・材料構成・Modifierを変更していません。

## ローカル検証

公式JARと配布済みmc-image-helperのlibディレクトリを用意して実行します。
テスト用一時ディレクトリだけを使用します。

```sh
VALHALLA_JAR=/path/to/ValhallaMMO_1.10.3.jar \
MC_HELPER_LIB=/path/to/mc-image-helper/lib \
python3 script/test_valhalla_salvage.py
sh -n minecraft/java/startup/valhalla-salvage.sh
sh -n minecraft/java/prepare-paper-plugins.sh
```

静的検証・一時ファイルの補正テストは、Paperの起動・プレイヤー操作の実機確認ではありません。

## 適用・受入確認（運用者が実行）

本作業では本番デプロイ、Volume変更、権限変更、Profile変更を実行していません。

1. `develop` 集約後、[Swarm運用](../../../deploys/README.md)に従うリリースで適用します。
   `minecraft-data` ラベルの対象ノードと実際の `app_minecraft_server_data` Volume名を確認します。
   管理側の `DEPLOY_ROOT` に新しいstartupディレクトリまで配置してください。
2. Paperを正常停止し、停止状態でVolumeのValhallaMMOディレクトリを安全な場所にバックアップします。
   とくに `recipes/grid_recipes*.json`、`skills/smithing.yml`、`recipes/disabled_recipes.yml` を確認します。
   バックアップはリポジトリへ追加せず、既存のDB・Profileのバックアップ方針も維持します。
   各JSONの欠損・空配列・独自設定を控え、同じ公式IDを流用した特殊レシピを確認します。
3. [既存のdeployスクリプト](../../../script/deploy_swarm.sh)に従ってComposeのmount変更を適用し、
   stop-firstで完全再起動します。bind mount内だけの更新ではSwarm taskの再起動が
   起きない場合があるため、承認された運用時にPaperサービスの完全再起動まで行います。
   reloadやパークの再取得、resetは行いません。
4. 起動ログで3有効版ファイルの `source` と件数、品質flag、skipped、ERRORの有無を確認します。
   初回seedのchangedは67＋15＋4＝86です。既存Volumeは統合やカスタマイズで件数が異なります。
   未生成の旧版1.21.11+は `inactive-version-missing` と出ます。
   actual `/data/plugins/ValhallaMMO/recipes/` とGit側を照合し、レシピが `/plugins` に
   誤配置されて全面同期されていないことを確認します。Gitの正本は補正処理で、JSON全体ではありません。
5. 一般権限で、Lv50パーク取得者と未取得者の2名を使って以下を試験します。
   どちらにも `valhalla.allrecipes` / `valhalla.recipe.*` やOPを付与しません。
   製作UIに装備を単独で置き、結果表示・1回分解・消費数・結果数・連続／shift操作を記録します。

| 試験対象 | 確認内容 |
| --- | --- |
| 自作の通常装備 | 品質情報がないことを確認し、公式材料条件に適合して分解できる |
| 他プレイヤー製作装備 | 製作者に依存せず、同条件で分解できる |
| 釣り装備 | 入手元、品質の有無、基本素材、還元量を記録する |
| Mobドロップ装備 | 同上。入手farmの収支も記録する |
| 耐久減少装備 | 同種の無傷装備より還元が減る。結果0の場合の拒否も確認する |
| エンチャント装備 | 材料条件に従い分解し、エンチャント／素材が二重に残らない |
| Valhalla品質付き装備 | 変更前と還元量・消費数が一致する |
| 他Pluginの特殊装備 | CustomID/CMD/PDC、発行・製作費、分解可否、換金収支を確認する |
| Lv50未取得／パークなし | 解放を迂回する権限なしでは結果を取得できない |

6. 鍛冶スキルの異なる取得者で還元率を比較し、釣りスキルと鍛冶の役割を確認します。
   さらに正常停止→完全再起動を行い、品質flagと独自レシピ・Profileの維持、ログの再補正数を確認します。
   Pluginが版別JSONを再保存するためファイルのbytes全体が同じとは限りません。
   Java / Bedrockの両方で操作確認してください。これらの実機試験は未実施です。

## 更新とロールバック

- Plugin更新時はhash mismatchで起動を止めます。新JARの版・レシピ・判定・読み込み順を再調査し、
  hash、対象ファイル、対応Minecraft版、テストを一緒に更新します。未知の版へ自動適用しません。
  mc-image-helperのJackson配置またはJava source launcherが変わった場合も、隔離起動で確認します。
- PluginのGUI保存やupdaterが設定を戻しても、次回起動時の検証・補正が必要です。
  稼働中のGUI保存でtrueに戻した場合は即時補正されません。
  外部同期・明示的reset・設定全再生成は通常運用に含めません。
- 戻すときはPaperを正常停止し、起動前のsalvage呼び出しとstartup mountを含む変更を取り消してから、
  対象JSONだけを適用前バックアップから復元します。Profile／World／DBは巻き戻しません。
  初回seed前に存在しなかったファイルを扱う場合は、停止中に現行ファイルを退避し、
  **後から追加した独自レシピがないことを確認**してから、Pluginの初期生成へ戻します。
- 適用後に独自レシピを編集した場合、バックアップ全体の復元はせず、最新JSONを退避して
  diffを確認し、補正した公式IDのflagだけを以前の値へ戻します。元からfalseの設定はfalseを維持します。
  この場合、バックアップで対象ごとの適用前値を確認してください。
  完全再起動後に独自設定・解放条件・還元量を再確認します。
