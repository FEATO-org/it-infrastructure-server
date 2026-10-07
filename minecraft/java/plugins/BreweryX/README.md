# BreweryX 3.7.1

公式[3.7.1 Release](https://github.com/BreweryTeam/BreweryX/releases/tag/3.7.1)から案内される
[Modrinth固定版](https://modrinth.com/plugin/breweryx/version/XmLbPZhp)を採用します。
JARは`minecraft/java/plugins.txt`で取得し、既存運用どおりGitには含めません。
公式配布metadataにはPaper / Minecraft 26.2が含まれますが、本体のバージョン判定は
26.2を`Unknown`として警告します。Paperの版は変更していません。

## 設定と保存先

Composeの`PLUGINS_FILE: /extras/plugins.txt`でJARを取得します。
追跡するこのディレクトリは`/plugins/BreweryX`へmountされ、itzgの起動時同期で
永続Volume内の`/data/plugins/BreweryX`へ配置されます。
`script/copy_plugins_to_remote.sh`によるJAR配布は不要です。

- `config.yml`: 公式JARの初回生成設定を基準に、`language: ja`だけ変更。
- `languages/ja.yml`: JAR内`languages/en.yml`の全151キーを日本語化。
- `recipes.yml`: 同じJARが生成した標準24件（23件の有効なレシピと無効な`ex`）の表示文言だけ日本語化。
- `custom-items.yml`: 3.7.1の生成既定定義を全件保全し、材料だけで照合する`feato_tea_leaves`を追加。
- 保存は標準の`storage.type: SQLITE`、`database: brewery-data`。
  実データは`/data/plugins/BreweryX/brewery-data.db`に保存されます。Gitには含めません。

標準23品の材料、数量、時間、蒸留、熟成、樽材、難易度、アルコール量、効果、コマンド、
飲酒演出などは上流標準値のままです。権限設定スクリプトへの追加は不要です。
JARの`plugin.yml`では`brewery.user`が`default: true`で通常の醸造操作を許可し、
`brewery.admin`は`default: op`です。一般プレイヤーに管理権限を追加しないでください。

## 翻訳の読み込み根拠

[3.7.1ソース](https://github.com/BreweryTeam/BreweryX/tree/3.7.1)と公式配布JARを確認しました。
`configuration/configurer/Translation.getTranslation`は言語コードを小文字化し`.yml`を付け、
`TranslationManager`と`ConfigHead.getFilePath`は`languages/<code>.yml`を参照します。
独自コード`ja`は同梱リストへの登録不要ですが、ファイルが存在しないとエラーになります。

`ConfigTranslations`の英語フォールバックは設定コメント用の`config-langs`です。
`ja`のコメントリソースは同梱されていないため、起動時の
`Could not find config translation, using default`は想定内です。
`TranslationManager.updateTranslationFiles`の不足キー補完は同梱言語が対象で、
独自`ja.yml`の欠落キーが自動で英語になるとは仮定しません。更新時には英語原本との全キー比較が必要です。

樽の看板は`listeners/BlockListener`が英語`Barrel`または`Etc_Barrel`の値を照合します。
今回の翻訳では`樽`と`Barrel`の両方が使用できます。
`CMD_Ingredient`はシミュレーションの案内用で、材料IDの判定には使用しません。
コマンド名、引数構文、レシピID、素材IDは英語のままです。
`Brew_MinutePluralPostfix`は日本語に複数形語尾がないため空文字です。

標準`recipes.yml`はJAR内のYAMLではなく`RecipesSector`から起動時に生成されます。
今回の原本は隔離Paper 26.2 build 126 / Java 25で公式JARから生成したものです。
品質別名称の`/`、loreの`+`、`++`、`+++`と色コードを保持しています。

## 検証（2026-10-04）

- 固定URLから取得したJARのSHA-512がModrinth metadataと一致。
- 追加YAMLをパースし、翻訳151キー、値の型・リスト長、`&vN`、色・装飾コード、改行、コマンド構文を英語原本と比較。
- 全24レシピについて、表示以外の値・識別子・有効状態が生成原本と一致。
  表示の品質区切り・条件記号・色コードも一致。設定値は`language`以外すべて原本と一致。
- `127.0.0.1:25586`の隔離サーバーで英語初回起動、日本語設定での再起動、
  `Using language: ja.yml`、SQLite、enable、Consoleの`brew help`の日本語出力を確認。
  起動後に書き戻された設定・翻訳・レシピの値も追跡ファイルと一致。
- 正常停止を確認。既存全Pluginとの同時起動、クライアント表示、実際の醸造・飲用、
  樽・蒸留・飲酒演出、Java/Bedrock操作、本番は未検証です。

## 反映・手動確認

設定と`plugins.txt`を通常の配布経路で配置後、Paperを再起動してください。
JAR追加と`/plugins`からの同期が必要なので、`/brew reload`だけで初回導入は完了しません。
この変更では本番への配布・デプロイ・操作は行っていません。

検証用サーバーで公開前に以下を確認してください。

1. 同じPaper 26.2 / Java 25で既存Pluginも含めて起動し、3.7.1のenable、
   `ja.yml`、SQLite、レシピ読み込みエラーの有無を確認する。`Unknown`警告も確認する。
2. 一般プレイヤーで`/brew help`、`/brew info`、大釜の時計による時間表示、
   樽のGUIと看板`樽`・`Barrel`、管理操作の拒否が適切か確認する。
3. 火の上の水入り大釜にココア豆12個と牛乳入りバケツ2個を投入し、
   時計で実時間2分の煮込みを確認してガラス瓶で取り出す。
   標準コーヒーは蒸留・熟成不要。日本語名・lore・品質を確認して飲み、
   再生・移動速度効果と酔い度減少（`alcohol: -6`）を確認する。
4. アイスコーヒー・ホットチョコレートと酒類も、名称・品質表示・飲用文言、
   樽熟成・蒸留・標準飲酒演出を確認する。Java/Bedrockの両方で操作する。
5. 正常停止後に再起動し、SQLiteの保存状態が維持されることを確認する。

初回反映前にPaper永続Volumeをバックアップしてください。戻す場合はPaper停止中に
BreweryX JARを退避し、取得一覧から外します。保存データを削除せず保管してください。

## 追加飲料・料理18品

追加17品はアルコール0、蒸留・樽熟成不要です。芋焼酎だけ蒸留2回（各60秒）、
樽熟成不要、アルコール設定値18です。実際のアルコール値には品質が影響します。
ゼリー、パンナコッタ、コンポート、スープも、ガラス瓶で取り出すBreweryX飲料です。
栄養補給ゼリーは再生・移動速度効果を持ち、満腹度回復やコマンド実行はありません。
ミルク系完成品にバニラのミルクバケツの全効果解除を期待しないでください。

茶葉はオークの葉（OAK_LEAVES）またはダークオークの葉（DARK_OAK_LEAVES）です。
**1回の仕込みではどちらか1種類に統一**します。単独なら同じ数量・レシピ・品質です。
3.7.1の材料照合では混合した2種類の数量を合算できず、混合を同等品質として扱いません。
名前やloreの指定は不要です。ミルクはMILK_BUCKET、蜂蜜はHONEY_BOTTLE、
山菜はFERN、ゼラチン相当はSLIME_BALL、冷却相当はSNOWBALLを使います。

表の加熱時間はゲーム内時間ではなく**実時間の分**、数量は大釜への投入個数です。
効果はすべてレベルⅠで、表の持続時間は品質10の値です。
品質0/10の補間端点は、正の効果の下端が上端の半分（切り捨て、再生は最低3秒）、
芋焼酎の弱体化だけ60→30秒です。成功品の品質1で正確に下端になるとは限りません。

| ID | 名称 | 材料（個数） | 加熱（分） | difficulty | 蒸留 | 品質10の効果（Ⅰ） |
| --- | --- | --- | ---: | ---: | --- | --- |
| `feato_black_tea` | 紅茶 | 茶葉×6 | 2 | 2 | 不要 | HASTE 30秒 |
| `feato_milk_tea` | ミルクティー | 茶葉×6、MILK_BUCKET×1、SUGAR×2 | 2 | 2 | 不要 | HASTE 30秒、REGENERATION 5秒 |
| `feato_royal_milk_tea` | ロイヤルミルクティー | 茶葉×10、MILK_BUCKET×3、SUGAR×3 | 4 | 4 | 不要 | HASTE 60秒、REGENERATION 8秒 |
| `feato_apple_tea` | アップルティー | 茶葉×6、APPLE×2 | 3 | 3 | 不要 | HASTE 30秒、SPEED 30秒 |
| `feato_berry_tea` | ベリーティー | 茶葉×6、SWEET_BERRIES×4 | 3 | 3 | 不要 | HASTE 30秒、REGENERATION 8秒 |
| `feato_honey_tea` | ハニーティー | 茶葉×6、HONEY_BOTTLE×1 | 3 | 3 | 不要 | HASTE 45秒、REGENERATION 5秒 |
| `feato_iced_tea` | アイスティー | 茶葉×6、SNOWBALL×4、SUGAR×1 | 1 | 3 | 不要 | SPEED 30秒、HASTE 20秒 |
| `feato_caffe_latte` | カフェラテ | COCOA_BEANS×8、MILK_BUCKET×3 | 2 | 2 | 不要 | SPEED 60秒、REGENERATION 5秒 |
| `feato_caffe_mocha` | カフェモカ | COCOA_BEANS×8、MILK_BUCKET×2、COOKIE×3 | 3 | 3 | 不要 | SPEED 45秒、HASTE 45秒 |
| `feato_honey_latte` | ハニーラテ | COCOA_BEANS×8、MILK_BUCKET×2、HONEY_BOTTLE×1 | 3 | 3 | 不要 | SPEED 45秒、REGENERATION 8秒 |
| `feato_hot_milk` | ホットミルク | MILK_BUCKET×2 | 1 | 2 | 不要 | REGENERATION 5秒 |
| `feato_honey_milk` | ハニーミルク | MILK_BUCKET×2、HONEY_BOTTLE×1 | 2 | 2 | 不要 | REGENERATION 10秒 |
| `feato_sansai_soup` | 山菜スープ | FERN×4、POTATO×3 | 4 | 3 | 不要 | REGENERATION 12秒 |
| `feato_berry_compote` | ベリーコンポート | SWEET_BERRIES×12、SUGAR×4 | 3 | 3 | 不要 | REGENERATION 10秒 |
| `feato_panna_cotta` | パンナコッタ | MILK_BUCKET×4、SUGAR×2、SLIME_BALL×1、SNOWBALL×2 | 3 | 4 | 不要 | REGENERATION 12秒 |
| `feato_coffee_jelly` | コーヒーゼリー | COCOA_BEANS×8、SUGAR×3、SLIME_BALL×1、SNOWBALL×2 | 3 | 3 | 不要 | SPEED 45秒、HASTE 30秒 |
| `feato_nutrition_jelly` | 栄養補給ゼリー | APPLE×2、HONEY_BOTTLE×1、SUGAR×2、SLIME_BALL×1、SNOWBALL×2 | 3 | 4 | 不要 | REGENERATION 10秒、SPEED 20秒 |
| `feato_imo_shochu` | 芋焼酎 | POTATO×12、WHEAT×3 | 12 | 4 | 2回・各60秒 | RESISTANCE 15秒、WEAKNESS 30秒 |

### 初級から応用への作り方

1. 火で加熱できる水入り大釜とガラス瓶、時計を用意します。材料は1個ずつ投入し、
   投入後の残りスタック・空容器を確認します。時計で加熱時間を確認できます。
2. 初級の紅茶は同じ種類の茶葉6個を投入して実時間2分加熱します。
   ホットミルクは牛乳入りバケツ2個で1分です。時間になったらガラス瓶で取り出します。
3. 次に茶葉にリンゴ・ベリー・蜂蜜を加える茶系や、カフェラテなどを表の配合で作ります。
   前の仕込みの材料を残さず、別の大釜または空にした大釜で始めてください。
4. 応用の入口はロイヤルミルクティー（茶葉10・ミルク3・砂糖3、4分）と
   パンナコッタ（ミルク4・砂糖2・スライムボール1・雪玉2、3分）です。
   材料が増えるので数量を確認し、瓶で取り出します。樽や蒸留は不要です。
5. 芋焼酎はジャガイモ12・小麦3を12分加熱して瓶に取り出し、醸造台で
   グロウストーンダストを使って2回蒸留します。1回60秒、樽熟成は不要です。

数量・時間のずれや余分な材料にはBreweryXの許容誤差があります。
常に不成立になるとは限らず、品質低下や別レシピへの一致が起こり得ます。
品質別名称は「薄い／通常名／上質な」、loreと飲用メッセージは日本語です。
リソースパック・独自モデルは使用しません。

### 配布前の保全と共存試験

今回の追加は設定だけで、プラグイン版・権限・ValhallaMMO・CraftBook設定は変更しません。
`/plugins`から`/data/plugins`への同期前に、停止中の検証用Volumeをバックアップし、
実行側の`custom-items.yml`に独自定義があれば取得して差分を確認してください。
独自定義を上書きせず、IDの衝突を確認して既定定義・茶葉定義とマージします。
Git管理対象の更新は配布元へ取り込み、DB・プレイヤーデータをコピーで上書きしません。
本番の実行設定・稼働版・独自定義の有無は今回確認していません。

共存は未検証です。ValhallaMMOの大釜クリックはMONITORでキャンセル済み操作も
処理され得ます。追跡blacklistはBUCKET、WATER_BUCKET、LAVA_BUCKET、SNOW_BUCKET、
GLASS_BOTTLEのみで、今回の材料やCLOCKは除外されていません。
1.10.3同梱alchemy設定の`quick_empty_potions: true`ではBreweryX飲料の除外がなく、
実行側の値は未確認です。醸造台クリックのNORMAL処理・キャンセルとの順序も要試験です。
CraftBookの追跡`Cauldron.require-sign: true`だけでは排他処理を保証できません。
広いblacklist追加、既存機能無効化、互換プラグイン・JAR改変・版変更は行いません。
問題が出たら現象・最小対策・影響範囲を記録して承認を得てから変更してください。

本番や実データを使わず、Paper 26.2 build 126 / Java 25 / BreweryX 3.7.1 /
ValhallaMMO 1.10.3 / CraftBook 3.10.13と必要な依存プラグインを揃えた新規隔離環境で、
次の項目を記録します。26.1で試験するまでは26.1対応を保証しません。

| 試験 | 手順・期待値 |
| --- | --- |
| 起動・読み込み | 41品の有効レシピ、ja.yml、SQLite、3 Pluginのenableを確認。無効レシピ・読込エラーなし。既知のUnknown版警告・日本語設定コメントfallbackは区別して記録 |
| 18品の製造 | 表の正確な材料・時間で1品ずつ製造。茶系7品はオークのみ／ダークオークのみ各1回、目的品の品質10を確認 |
| 蒸留 | 芋焼酎を実際に2回（各60秒）蒸留し、熟成せず完成。通常クリック・シフトクリック・ドラッグ・可能ならホッパーでも試す |
| 表示・飲用 | 日本語名・色・lore・飲用メッセージ、低／中／高品質名、効果Ⅰと品質10持続時間、アルコール値を確認 |
| 消費・返却 | 材料1個ずつの消費、残りスタック保全、ミルクの空バケツ・蜂蜜の空瓶返却、CLOCKが消費されないことを確認 |
| 完成品の再投入 | 完成品を手に大釜を右クリックし、意図しない空瓶化・消失がないことを確認 |
| 大釜共存 | ValhallaMMO併用で二重消費・残りスタック消失・別ストレージ投入がないことを確認。CraftBook看板あり／なしで各機能の役割を記録 |
| 境界配合 | 必要材料を1種類欠く、数量±1、加熱±1分、余分な材料1個、茶葉3+3（ロイヤル5+5）を試す。目的品・品質・消費を記録し、数量ずれの一律不成立は期待しない。混合を品質10と期待しない |
| 回帰 | 標準コーヒー・アイスコーヒー・ホットチョコレート・ウォッカ・ジン、ValhallaMMOの通常大釜／醸造台、CraftBook看板大釜の代表機能を確認 |
| 保存・再起動 | 正常停止・再起動後の設定と新規テストデータの保存を確認。Java/Bedrockで表示と操作を確認 |

追加を戻す場合は停止中に配布元の追加18品と茶葉定義を戻します。
独自定義とDBは保全し、既存の追加品の扱いは検証環境で確認してから本番判断します。
設定追加の完了と、本番反映の可否は別です。共存・操作試験完了前は反映可と判断しません。

### 今回の追加設定の検証（2026-10-05）

- 基準developコミット`6956c10c1af0a92bedc9b305c1ef27c9cd859cf6`と、作業開始時HEAD
  `e28d533fb8830d4ad1adc86e26d53382808232d9`の対象構成に差分なし。
- YAMLの重複キーを拒否してパースし、追加18品の材料・時間・難易度・蒸留・熟成・
  アルコール・効果の全指定値を照合。Paper 26.2 build 126のMaterial enum、
  色指定、日本語名称・lore・飲用文言、固定効果Ⅰの構文を確認。
- 既存23品と無効な例1件は全フィールド不変。config・ja.yml・plugins.txtも不変。
  3.7.1生成既定のcustomItems全5件と、blue-flowers・標準ジンの参照を保全。
- 正確な配合は25ケース（茶系7品×2種、その他11品）を確認。
  3.7.1の材料・加熱の品質評価に基づき、目的品が品質10で、並び順に依存せず
  他候補の品質上限は10未満。熟成・樽材の減点を省いた上限を使う静的計算であり、
  実サーバーのAPIを実行した試験ではありません。
- 材料欠落・数量±1・加熱±1分・余分な材料・混合茶葉の164ケースで、目的品の
  品質上限と競合候補を算出。数量・時間ずれや余分な材料で成立し得る許容誤差を
  維持し、混合茶葉が同等の品質10にならないことを確認。
- 新規の隔離ディレクトリでPaper 26.2 build 126 / Java 25 / BreweryX 3.7.1を
  起動試行しましたが、サンドボックスによる`127.0.0.1:25587`のbind拒否で
  プラグイン設定読み込み前に停止しました。設定読み込み・実製造・飲用・返却・
  蒸留・保存・ValhallaMMO/CraftBook共存は未実施です。前日の起動確認は追加18品の
  動作確認を意味しません。上の再現手順で共存試験を完了するまで本番反映可否は未判定です。
- 本番の確認・配布・デプロイは行っていません。

静的検証の再実行にはPyYAMLとJDKの`javap`が必要です。3.7.1が新規隔離環境で生成した
`custom-items.yml`の原本と、対象Paper API JARを指定します。実行側の独自定義を
「原本」として使わないでください。

```sh
python3 script/validate_breweryx_recipes.py \
  --paper-api /path/to/paper-api-26.2.build.126-stable.jar \
  --default-custom-items /path/to/generated-3.7.1/custom-items.yml
```
