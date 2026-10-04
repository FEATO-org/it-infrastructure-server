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
- 保存は標準の`storage.type: SQLITE`、`database: brewery-data`。
  実データは`/data/plugins/BreweryX/brewery-data.db`に保存されます。Gitには含めません。

材料、数量、時間、蒸留、熟成、樽材、難易度、アルコール量、効果、コマンド、
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
