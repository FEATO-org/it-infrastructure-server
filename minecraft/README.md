# Minecraft運用（Paper 26.2）

## 構成

```text
Java TCP 25565 / Bedrock UDP 19132
  -> nginx -> Velocity 4.2.0
                ├ Geyser-Velocity
                │  └ EmoteOffhand (Geyser Extension)
                ├ Floodgate
                └ LuckPerms
                     │ modern forwarding
                     ▼
                   Paper 26.2 build 126
                     ├ LuckPerms / LuckTags
                     ├ EssentialsX Core / Spawn
                     ├ VaultUnlocked / EssentialsUnlocked
                     ├ Floodgate (backend API / Bedrock detection)
                     ├ EconomyShopGUI Free
                     ├ FancyNpcs
                     ├ squaremap :8123
                     ├ ValhallaMMO / Magic 11.2.4 / FEATO Horsemanship 0.2.0
                     ├ FEATO Gun-Valhalla Bridge 0.2.0 (Phase 1 PoC)
                     ├ SCore / ExecutableItems
                     ├ WorldEdit / CraftBook
                     ├ ImageFrame
                     ├ BreweryX 3.7.1
                     ├ ProtocolLib 5.5.0-SNAPSHOT / PlaceholderAPI 2.12.3
                     ├ Better Horses / DualHorse
                     ├ Backpack Plus
                     ├ DeadChest 4.31.0
                     ├ Hurricane (bamboo / pointed dripstone collision only)
                     ├ FEATO Ancient Coin 1.0.0
                     └ FEATO Coin Exchange 1.1.0
Data Packs: Enchants Plus / Gun Core 1.0.15 / Modern Guns 1.9.3 / Bridge 0.2.0
Web: nginx dynmap.feato.jp -> squaremap :8123
```

対象バージョンは26.2です。`.env`の`MINECRAFT_VERSION`が既定値を上書きするため、デプロイ前に26.2であることを確認してください。

GeyserとFloodgateはVelocityへ配置し、Bedrock判定をPaper側Pluginでも利用できるようFloodgate-SpigotもPaperへ配置します。Velocity側は`send-floodgate-data: true`で暗号化したBedrock player dataを転送します。両Floodgateは同一のDocker Swarm secret `floodgate_key`を使用します。Paperコンテナは起動時に`/run/secrets/floodgate_key`を`/data/plugins/floodgate/key.pem`へコピーし、Floodgateは`key-file-name: key.pem`で参照します。Velocityのmodern forwarding、共有forwarding secret、Paperのoffline modeは維持します。Paper、MariaDB、squaremapはホストへ直接公開しません。

EmoteOffhandはPaper/Velocity PluginではなくGeyser Extensionです。管理側の
`resources/minecraft/geyser/extensions/EmoteOffhand.jar`を更新時のみ
`script/copy_plugins_to_remote.sh`でVPSへ配布します。現行の
`deploys/app/compose.yml`にはExtensionのmountがないため、コンテナ内の
`/plugins/Geyser-Velocity/extensions/EmoteOffhand.jar`への配置と読み込みは
未確認です。通常deploy時には取得しません。
`gameplay.emotes-enabled: true`は維持し、旧`emote-offhand-workaround`は追加しません。
HurricaneはPaper Pluginとして`plugins.txt`から公式APIで取得します。追跡する
`java/plugins/Hurricane/hurricane.conf`では、Bedrockの移動補正に必要なbambooと
pointed dripstoneだけを有効にしています。両回避策は対象ブロックのサーバー側衝突を
なくすため、改造クライアントによる通過リスクと設置時の不安定さを理解したうえで運用してください。

## 採用Plugin

Paper側の取得URLは[plugins.txt](java/plugins.txt)、詳細な版・配布元・ハッシュは[versions.md](../deploys/versions.md)で管理します。

- 権限・表示: LuckPerms、LuckTags
- 経済・基本機能: EssentialsX Core / Spawn、VaultUnlocked、EssentialsUnlocked
- カジノ: MineGames 1.0.5（初期利用はSlotsのみ）
- 商店・NPC: EconomyShopGUI Free、FancyNpcs
- マップ: squaremap
- RPG・アイテム: ValhallaMMO、Magic 11.2.4、SCore、ExecutableItems
- 銃器スキル検証: FEATO Gun-Valhalla Bridge 0.2.0（Phase 1 PoC）
- 建築・表示: WorldEdit、CraftBook、ImageFrame
- 馬・収納: Better Horses、DualHorse、FEATO Horsemanship 0.2.0、Backpack Plus
- 醸造・料理: BreweryX 3.7.1（標準レシピ・日本語表示）
- 死亡時保護: DeadChest 4.31.0
- 独自機能: FEATO Ancient Coin 1.0.0、FEATO Coin Exchange 1.1.0

DeadChest 4.31.0は公式metadataでPaper 26.2に対応し、Java 25で起動を確認しています。
死亡・回収のプレイヤー操作と本番は未確認です。旧JARは既存の`REMOVE_OLD_MODS_INCLUDE`で
`/data/plugins/dead-chest-*.jar`だけを除去し、4.31.0を再取得します。
起動前にDeadChestの自動更新を無効化し、`/data/plugins/update/dead-chest-*.jar`も除去します。
起動時patchで`/data/plugins/DeadChest/config.yml`の`chest.duration-seconds`を`0`（無期限）へ固定し、
死亡チェストは時間経過では期限切れにしません。他の死亡保護設定（`chest.max-per-player`を含む）は
既存値を保持し、JARの版は4.31.0のままインフラ側で管理します。本変更の本番動作は未確認です。

ProtocolLibは公式Development Buildのasset IDとSHA-256を固定して起動前に取得します。
一覧と固定取得元は`plugins.txt`、詳細は[versions.md](../deploys/versions.md)を参照してください。
PlaceholderAPIは2.12.3本体だけを導入し、外部Expansionは追加しません。
GhastMasterは運用版を特定できないため、今回の本体管理化は未実施です。
既存の手動JARの正式版・公式配布元を確認するまで、そのJARを維持してください。
`setup_minecraft_permissions.sh`には一般グループの`ghastmaster.share`だけを追加しています。

Magicの`vengeance.variables: bubble`追加とMineGamesの外部YAMLの重複削除を反映しました。
ただしMagic 11.2.4の式評価警告とMineGames 1.0.5のJAR内既定YAMLの重複警告は
ローカル起動で残っています。本体版、式、メッセージ文言は変更していません。

旧Vault、XConomy、XConomy_Reload、SetSpawn、Genius Shop、Dynmapは採用しません。既存VolumeからJARが自動削除されるとは限らないため、停止中に退避してください。Dynmapのタイルはバックアップ後に残して構いませんが、squaremapは別形式で再描画します。

## 日本語化

- BreweryX: `language: ja`、追跡する`BreweryX/languages/ja.yml`と標準`recipes.yml`の日本語訳
- EssentialsX: `locale: ja`
- EconomyShopGUI: `lang-ja.yml`（7.3.2同梱）、通貨ロケール`ja-JP`
- ValhallaMMO: `language: ja-jp`。Gistを原本として追跡
- Backpack Plus: 公式同梱`jpn`ロケール
- Better Horses: 追跡する`language.yml`を日本語化
- AncientCoin: 表示文言はPlugin設定で日本語
- FancyNpcs、squaremap、SCore、ExecutableItems、DualHorseは採用版に公式日本語ロケールがありません

ValhallaMMOの訳は、JAR内英語原本とキー・配列・名前付きプレースホルダーが一致する場合だけ更新します。

```bash
./script/sync_valhallammo_ja.sh /path/to/ValhallaMMO_1.10.3.jar
```

この処理は[日本語Gist](https://gist.github.com/LenTakayama/e8f65dbce8e58baec96c8554a4eba4e5)を一時領域へ取得し、[検証スクリプト](../script/validate_valhallammo_translation.py)を通過してから置換します。

## 醸造・料理（BreweryX）

BreweryX 3.7.1を公式固定URLから取得します。標準SQLite保存とゲーム挙動を維持し、
操作案内・品質表示・標準飲料と料理の表示を日本語化し、紅茶・ミルク系・料理・
デザートなど17品と芋焼酎の追加レシピを設定しています。標準23品の設定は維持しています。
Paper 26.2 build 126で起動と日本語ヘルプを確認しましたが、本体はバージョンを
`Unknown`と警告します。既存全Pluginとの併用と実製造・飲用は未検証です。
配置先、翻訳仕様、再起動とコーヒーの手動確認は
[BreweryX運用手順](java/plugins/BreweryX/README.md)を参照してください。

## 魔術（ValhallaMMO + Magic）

Magic 11.2.4の公式`valhalla` exampleを使用し、ValhallaMMOへ`魔術` Skill（Lv 0-100）を追加します。成長の主体はValhallaMMOの魔術Lv、EXP、Skill Point、Skill Treeです。MagicはSpell、Mana、Cooldown、Casting、魔導具UI、演出だけを担当し、独立した第二のMMOレベルやSpell Pointを使いません。

- 魔術のEXP曲線は`(%level% + 75 * 2^(%level%/8.5)) + 300`です。successful castの`earns_type: valhalla_xp_magic`と`earns_multiplier: 10`でValhalla魔術EXPへ変換し、Spell別の`earns`と共通`earns_cooldown: 2 minutes`を固定します。Missileの初心者向けXP回復短縮はRank I/IIとも使用しません。daily limitは設けません。
- Spell Shopは公式`OpenValhallaSkillTreeAction`でValhallaのSkill Treeを開きます。戦闘、防護、秘術の3分岐とMana系統を設け、Rank IIを含む全取得コストは39です。Skill PointはValhallaMMOの既存Power profileで全Skill共通管理されるため、魔術専用の約20ポイント上限は独自integrationなしでは強制できません。運用上は他Skillとの配分を含め約20を目安にします。
- Manaは100、回復4/秒から開始します。Path upgradeとMana perkを同じ公式rewardにまとめ、Lv10で115、Lv30で135、Lv60で165、Lv100で185へ増加し、回復は最終6/秒です。Magic 11.2.4のMana値は整数のため、指定目安5.8/秒は6/秒へ丸めています。
- Pathは`beginner`、`student`、`apprentice`、`master`を内部進行に使用し、Lv100補正だけ`feato_archmage`を追加します。プレイヤーには魔術LvとSkill Treeを主表示します。
- Cooldownはすべてミリ秒です。Magic MissileとFireballはブロックを破壊せず、高位戦闘魔法を含め通常武器の継続火力を置き換えない設定です。
- `enable_spell_upgrades: true`でRank variantを読み込み、`enable_automatic_spell_upgrades: false`で使用回数によるSpell・Pathの自動進行を止めます。Rank IIは元Spell取得を条件に各1ポイントで解放します（Missile Lv20、Leap Lv25、Heal Lv30、Fireball Lv35、Blink Lv40、Shield Lv45、Push Lv50、Gills Lv55、Lightning Lv65）。公式rewardは元Spellの使用Rankを更新します。Rank I/IIを独立したSpellとして選択する方式ではありません。Recall・Light・天候・WoundのRank perkやRank III以降は追加しません。
- 魔術Lvによる直接Damage倍率は追加しません（0%）。成長はSpell解放、Mana、Mana回復、移動・探索・防御の選択を主体にします。
- 天象術は晴天祈願、雨乞い、嵐の招来です。すべてMagicの`WeatherAction`でワールド天候だけを変更し、コマンド、追加落雷攻撃、Mob spawnは使いません。
- WandはSpell選択・発動UIとしてのみ使用します。rarity、ランダム性能、恒常的な攻撃強化、Magic Armorは採用しません。
- Fill、Box、Blob、Construct、採掘・生産代替、Portal、常時Flight、Mob召喚などの禁止SpellはSkill Treeへ登録しません。

Magic側のresource pack自動配布は無効です。公式[Magic+ValhallaMMO pack](https://rp.elmakers.com/Magic-valhalla-RP-26.2.zip)を既存の[resourcepack統合手順](java/resourcepack/README.md)の入力にし、完成した単一packだけを配布してください。Java/BedrockともCustom Modelに依存せず、日本語のSpell名と説明で識別できます。

`ValhallaMMO/skills/magic_progression.yml`は分岐、必要Lv、コストを固定するためGitで追跡します。Magic update時はmagic_progression.ymlの再生成要否をrelease noteで確認し、必要なら再生成後にdiffを確認する。

初期WandはMagicの`feato_wand_shop`で150Gで販売します。これは公式Survivalの`buyshop`を継承したMagic Shop actionであり、`wand|default`をMagic自身が生成します。Vault連携の通貨を使用するため、購入額はEssentialsX Economyから徴収されます。WandはSpell選択・発動UIのみで、`beginner` Pathの進行設定とは別です。

Wand販売NPCは、販売位置に立って次を実行します。

```text
/npc create wand_vendor
/npc displayname wand_vendor <gold>魔導具店</gold>
/npc interaction_cooldown wand_vendor 1s
/npc action wand_vendor RIGHT_CLICK add console_command castp {player} feato_wand_shop
```

`console_command`はConsoleとして`castp <player> <spell>`を実行するため、一般Playerへ`magic.commands.cast`や`magic.commands.castp`は付与しません。

実機では、MagicとValhallaMMOのenable順、魔術profile作成、Spell XP加算、Skill Point総数、Path upgrade、Mana表示・回復、各Spellの成功判定とCooldown、Spell Shop GUI、日本語表示、Java/Bedrockの魔導具操作、統合resource packの表示を確認してください。

### XP・Rank II調整の適用確認

Fishing/Smithingの標準progressionは、[versions.md](../deploys/versions.md)のSHA-512と一致するValhallaMMO 1.10.3 JAR内の`skills/`を原本として追加しました。FishingはチャンクXP減衰の対象外、Smithingの耐久スタック上限は同一チャンク・素材ごとに300です。素材倍率は以下のとおりで、SmithingのEXP曲線と耐久スタック倍率・最大値は標準値を維持します。

| 素材 | Lv0–19 | Lv20–39 | Lv40–59 | Lv60–79 | Lv80+ |
| --- | ---: | ---: | ---: | ---: | ---: |
| Wood / Leather | 100% | 75% | 50% | 25% | 10% |
| Stone / Copper / Chain | 100% | 100% | 75% | 50% | 25% |
| Iron / Gold | 80% | 100% | 100% | 100% | 100% |
| Diamond | 50% | 75% | 100% | 125% | 125% |
| Netherite | 25% | 50% | 75% | 100% | 125% |

共通チャンク減衰は300イベント後にスキルXPを80%、EXP orbを50%にします。通常活動への過度な減衰を緩和しつつ、Grinder対策を残します。

適用時はPaperを停止してValhallaMMO/Magicの設定とプレイヤーprofileをバックアップし、追跡設定を通常デプロイで`/plugins`から永続Volumeの`/data/plugins`へ同期して再起動します。VPSへのファイルコピーだけでは適用確認になりません。既存プレイヤーのSmithing倍率が新しいstarting/special perk値に再計算されることも確認し、差が残る場合は公開を止めて公式のprofile再計算手順を確認してください。

今回の設定は隔離したPaper 26.2 build 126 / Java 25でMagic 11.2.4とValhallaMMO 1.10.3の起動・正常停止、全9種のRank IIの`spells`一覧への登録、`valhalla_xp_magic`通貨登録を確認しました。Gills IIはMagic標準のRank継承を使用し、明示的な`inherit: gills`は循環参照になるため指定しません。既存の上流YAML重複警告とVengeanceの式評価警告は残ります。プレイヤー操作と本番profileへの適用は未確認です。

公開前にJava/Bedrockで次を確認します。

- Magic/Valhallaの起動、全9種のRank II（カスタム`gills|2`を含む）の読み込みとperk reward解決、ツリーのノード・線・日本語表示。
- 未取得時はRank I、取得後は同じSpellでRank IIの性能・Mana・Cooldownとなり、使用だけでRank/Pathが進まないこと。既存profileに以前の上位Rankが残っていないこと。
- successful castのXPがValhalla `MAGIC` profileに加算されること。Missile Rank I/IIのXP回復が2分であり、Missileだけ異常に高速なXP源にならないこと。
- Fireball IIの地形破壊・着火なし、Recallが同一ワールドのhomeのみ、Gills IIが60秒持続し水中移動の付加効果も保持、magicbow/magicswordが無効であること。
- Fishingの同一地点での通常XP、Smithingの300スタック制限と各レベル帯の素材倍率（特にLv20以降のIron/Gold 100%）。

問題があればPaperを停止し、旧追跡設定と変更前profileのバックアップを戻して再起動します。Rank II取得後に設定だけを戻すと取得済みperkとSpell Rankが食い違うため、profileも同じ時点に戻します。

## 銃器スキル（FIREARMS Bridge 0.2.0 / Phase 1 PoC）

[公開Release v0.2.0](https://github.com/FEATO-org/feato-gun-valhalla-bridge/releases/tag/v0.2.0)のPlugin JARとDatapack ZIPを、`java/plugins.txt`と`java/datapacks.txt`の固定URLから取得します。両方のrelease IDは`3`、protocolは`1`です。更新時は必ず両manifestの版を同時に変更してください。

対象はPaper **26.2 build 126** / Java 25 / ValhallaMMO **1.10.3** / Gun Core **1.0.15** / Modern Guns **1.9.3**です。Composeで`PAPER_BUILD: "126"`を固定し、`.env`の`MINECRAFT_VERSION`も26.2であることを適用前に確認します。Gun CoreとModern Gunsは既存の固定版を維持します。build・対象版・Datapack markerの不一致やheartbeat停止ではBridgeが登録を停止するため、起動ログの確認が必要です。起動中の登録待ちではプレイヤーのログインが一時拒否されます。

0.2.0は専用FIREARMS profile、銃器スキルの検証用ツリー、管理者debug、Datapackの互換性確認、Bridge設定の再読み込みを実装したPoCです。銃撃によるEXP獲得、通常銃撃・武器殴打のDamage連携、Ability効果、最終スキルツリーは未実装です。`tactical-reload`などの設定は将来用で、Phase 1では効果を発揮しません。ValhallaMMOの既存設定は変更せず、必須の`mining`、`weapons_light`、`armor_light`、`armor_heavy`、`archery`は有効なままです。

| 管理対象 | 起動時の配置先 |
| --- | --- |
| Plugin JAR | `/data/plugins/feato-gun-valhalla-bridge-plugin-0.2.0.jar` |
| `java/plugins/FEATOGunValhallaBridge/config.yml` | `/data/plugins/FEATOGunValhallaBridge/config.yml`（`/plugins`から同期） |
| Datapack ZIP | `/data/${LEVEL:-world}/datapacks/feato-gun-valhalla-bridge-datapack-0.2.0.zip` |

初期値は0.2.0の公開JAR同梱の設定と同じで、`debug.enabled: false`を維持します。0.2.0では`/firearms reload`を追加し、Bridgeの`config.yml`だけを安全に再読み込みできます。debug無効時も実行でき、成功時は現在のdebug状態を表示します。YAML・必須キー・型・有限値・範囲の検証失敗時は、有効な旧設定とファイルを保持して理由とWARNを返します。

`feato.gunvalhalla.reload`はPluginの既定OPで、`setup_minecraft_permissions.sh`の管理者グループへの許可対象に追加します。consoleからも利用できます。一般・役職グループには追加しません。debug用の`feato.gunvalhalla.debug`は独立した権限で、検証対象の管理者だけに付与します。reload権限だけでは検証用EXPを付与できず、debugを有効にしても銃撃EXPは自動付与されません。

debug切替は追跡するconfigと実際の`/data/plugins/FEATOGunValhallaBridge/config.yml`を同じ値へ変更してから、`/firearms reload`で反映・表示を確認します。`/plugins`の管理元だけを変更しても、起動時同期前のruntimeファイルは変わりません。runtime側だけを編集した場合も、次回起動時に管理元で上書きされるため差分を管理元へ戻してください。検証終了後は`debug.enabled: false`へ戻してreloadします。

reloadでSkill/Profile、ValhallaMMO Registry、Perk tree、Datapack handshake・markerは変更しません。停止したBridgeの再登録・復旧、Plugin JAR/Datapack更新、Skill/Profile構造の変更には完全再起動が必要です。Minecraft `/reload`、ValhallaMMO reload、Plugin disable/enableは実行しません。

起動時の旧版削除は、Plugin側では既存FEATO JAR対象にBridge JARのglobを追加し、Datapack側では`feato-gun-valhalla-bridge-datapack-*.zip`だけを対象とします。別の名前の旧版や展開済みBridgeディレクトリがある場合は、停止中に手動で退避してください。Datapackの選択的削除はitzgの[setupスクリプト](https://github.com/itzg/docker-minecraft-server/blob/master/scripts/start-setupDatapack)と[取得helperのprune仕様](https://github.com/itzg/mc-image-helper/blob/main/README.md)に従います。

### 適用前の確認と戻し方

0.1.0ではユーザーから完全起動・Datapack handshake・FIREARMS登録・銃器表示・Lv0 Profileの再ログイン維持を確認したと報告を受けています。今回の0.2.0更新と新しいreload経路の実機確認は未実施です。特定XP値の保存一致、Level Up、完全再起動後の永続化、DB上の値、Perk三択排他は未確認のままです。respec/recalculationは未確認のまま後回しとし、その検証待ちで後続開発を止めません。残る検証は本番DBを使わない隔離環境で、[上流のPhase 1手順](https://github.com/FEATO-org/feato-gun-valhalla-bridge/blob/v0.2.0/docs/poc.md#reproducible-live-test-procedure-dedicated-test-server)で保存・login・再起動を確認し、respecは後日検証します。共通Skill Pointと既存Skillへの影響も記録してください。`SKILLS_REFUND_EXP`は他SkillのPerkもresetするため、本番プレイヤーへの検証には使いません。

0.2.0へ更新する際は、サーバーを正常停止してWorldとValhallaMMOのSQLite DB（実際の保存先を確認）をバックアップし、manifest・設定・Composeを配布して完全起動します。`/reload`は使いません。実際のPaper build、ValhallaMMOとBridgeのenable、marker一致・登録完了ログ、`profiles_firearms`の作成、`/skills`の表示、同一UUIDの再接続・完全再起動後の保存値を確認します。markerは`fgv_bridge` objectiveの`#release = 3`、`#protocol = 1`です。新しいreloadは、console・対象管理者からdebugのON/OFFと表示、不正設定拒否・旧設定保持、一般プレイヤーの拒否、Profile・handshakeの継続を確認します。通常設定のdebugは無効へ戻します。

問題が出たら正常停止し、BridgeのJAR/ZIPの両manifest行を外して再起動します。上記globに一致するBridge配布物は起動時に削除されます。削除後に両方が読み込まれていないことをログと配置先で確認してください。旧版へ戻す場合も両方の版を揃えます。Plugin削除だけでは保存済みprofileは戻らないため、データ異常時は停止したままバックアップとの照合・復旧を行います。

## 馬術（ValhallaMMO + FEATO Horsemanship）

[FEATO Horsemanship v0.3.0](https://github.com/FEATO-org/feato_horsemanship/releases/tag/v0.3.0)で、ValhallaMMOに「馬術」（Lv 0-100）と移動・持久・操作・戦闘・育成のスキルツリーを追加します。専用Java Skill/ProfileをDB初期化後に登録し、v0.2.0のEXP付与時のProfile解決エラーに対応します。対象は馬、スケルトンホース、ゾンビホース、ロバ、ラバです。移動EXPは操縦者だけに100ブロックごと10、鞍上の第一歩取得後は+5%、馬上戦闘EXPは攻撃者本人に2秒間隔で0.5を付与する初期設定です。Lv20の「追う」は操縦中にメインハンドへリードを持って右クリックすると発動し、速度+6%、5秒、再使用35秒です。Perk取得前の操縦速度は-5%、鞍上の第一歩の取得後は-2%、手綱の心得の取得後はペナルティなしです。

JARは`java/plugins.txt`の固定URLから取得し、最新GUIを維持したSkillを`java/plugins/FEATOHorsemanship/horsemanship.yml`、効果設定を`java/plugins/FEATOHorsemanship/config.yml`として追跡します。起動前に`/plugins`から`/data/plugins`へ同期します。旧 `ValhallaMMO/skills/custom/horsemanship.yml`・`HORSEMANSHIP.yml` は停止中に管理元とVolumeから退避してください。Gitの削除だけではVolumeから消えず、残存すると二重登録で馬術Pluginが停止します。JARと新Skill配置を同時に適用し、完全再起動してください。

BetterHorsesの馬上ダメージ加算だけを起動前patchで無効化し、ほかの既存設定は保持します。一般プレイヤーの育成コマンドは取得Perkで制限し、reload権限は管理グループだけへ付与します。

公開アセットのハッシュ・同梱Skill・効果設定と既存GUIの一致を確認しました。v0.3.0の隔離起動確認と実機未確認事項は[馬術の導入手順](java/plugins/ValhallaMMO/HORSEMANSHIP_SETUP.md)を参照してください。本番適用とJava/Bedrockのプレイヤー操作は未確認です。

## CraftBook Chairs（休憩）

CraftBook 3.10.13のChairsを有効化します。階段に看板を付け、ブロックを持たずに
右クリックすると階段の向きに合わせて着席できます。着席中は20 tickごとに
health 0.5（0.25ハート）回復し、通常の20 TPSでは約4秒で1ハートです。
回復は最大HPを超えません。看板必須、`max-distance: 3`、`max-click-radius: 5`です。

3.10.13の[Chair実装](https://github.com/EngineHub/CraftBook/blob/3.10.13/src/main/java/com/sk89q/craftbook/mechanics/Chair.java)と
[設定ロード処理](https://github.com/EngineHub/CraftBook/blob/3.10.13/src/main/java/com/sk89q/craftbook/bukkit/CraftBookPlugin.java)を確認しています。
一般グループには`craftbook.mech.chair.use`だけを追加します。既存の公式ProtocolLib
5.5.0-SNAPSHOT固定assetを使用し、CraftBook・WorldEditの版は維持します。

`mechanisms.yml`全体の同期による既存設定のリセットを避けるため、初回用の空の設定を
`java/config-seeds/craftbook-mechanisms.yml`で管理し、`/plugins`の通常同期から外しています。
起動前スクリプトは`/data/plugins/CraftBook/mechanisms.yml`が存在しない場合だけseedを
コピーし、`java/patches/craftbook-chairs.json`でChairsの7キーだけを更新します。
既存の`blocks`と他mechanicの値は保持します。`blocks`が未設定なら3.10.13の
`BlockCategories.STAIRS`による既定一覧をCraftBook自身が補完します。
空ファイル・不正な構造は起動前処理の失敗として扱います。

適用時はPaperを正常停止して既存CraftBook設定をバックアップし、seed・patchのmountと
起動後の読み込み先を確認してください。戻す場合はChairsを無効化し、Chairs patchと
利用権限を外して、停止中にバックアップの`mechanisms.yml`を戻します。

Requires runtime verification:

- 看板付き階段で着席でき、看板なし・ブロックを持った状態では着席しないこと。
- 着席方向、health 0.5 / 20 tickの回復、最大HPの上限、Sneak等による離席。
- Java版とGeyser経由のBedrock版での着席・離席。
- 既存全Pluginとの併用時にProtocolLibによる回帰がないこと。

## CraftBook Cauldronの無効化

BreweryXとの大釜利用の競合が疑われ、経験抽出が実運用で正常に利用できなかったため、CraftBookのCauldronを無効化し、経験抽出レシピと専用設定を撤去しました。経験値の瓶はFEATO商店で購入できます。

適用前にPaperを正常停止して既存CraftBook設定をバックアップし、再起動後に`/data/plugins/CraftBook/config.yml`でCauldronが無効であることを確認してください。配布元で削除したファイルは永続Volumeに残る場合があります。`mechanisms.yml`にはChairsや本番独自の設定があり得るため、ファイル全体を削除せず、Cauldron専用設定・レシピだけを確認して撤去してください。戻す場合はPaperを正常停止し、配布元と永続Volumeの設定を適用前のバックアップへ戻して再起動します。

実機未確認です。適用後は次を確認してください。

- CraftBook Cauldronが動作せず、BreweryXの大釜利用に影響がないこと。
- FEATO商店の販売ページに経験値の瓶が表示され、200Gで16個購入でき、所持金が200G減少すること。
- 経験値の瓶をショップへ売却できないこと。
- Java版GUIとBedrock版Formsの両方で正常に購入できること。

## 経済と通常商店

経済ProviderはEssentialsX、Vault API層はVaultUnlocked、橋渡しはEssentialsUnlockedです。初期残高200G、通貨記号は金額の後ろ、負残高は禁止です。

`/shop`の`feato_shop`は単一ショップを維持し、EconomyShopGUIの標準ページナビゲーションで「販売」と「買取」を分離します。Java/Bedrockともクリック種別の使い分けを必須にしません。

EconomyShopGUI Free 7.3.2では、Java Editionは従来のInventory GUI、Bedrock Editionは標準のリスト形式Form UIを使用します。`bedrock-forms.enable: true`、`only-enable-for-touch-devices: false`で、iOS/Android以外も含めた全Bedrockプレイヤーを対象にします。タッチ端末も1回の選択で操作できるよう`use-double-click-for-touch-devices: false`とし、`use-grid-forms: false`でJsonShopFormsは利用しません。

既存のVelocity上のGeyserと、同一鍵・`send-floodgate-data: true`で接続したPaper側FloodgateでBedrockを判定します。GeyserがPaper上にないため、FormのアイコンIDはPluginが取得・キャッシュします（上流既定の48時間、palette版の指定なし、強制更新なし）。追跡する`java/plugins/EconomyShopGUI/config.yml`はComposeの`/plugins` mountから起動時に永続Volumeの`/data/plugins/EconomyShopGUI/config.yml`へ同期されます。ファイルの配布後は、起動ログで7.3.2・`lang-ja.yml`の読み込みと適用先の設定を確認してください。

| 商品 | 取引 | 数量 | 価格 |
| --- | --- | ---: | ---: |
| Gunpowder | 購入 | 32 | 50G |
| Oxidized Copper | 購入 | 32 | 100G |
| Player Head | 購入 | 1 | 100G |
| Mending Enchanted Book | 購入 | 1 | 2,000G |
| Villager Spawn Egg | 購入 | 1 | 2,000G |
| Experience Bottle | 購入 | 16 | 200G |
| Blaze Powder（買取不可） | 購入 | 1 | 3,000G |

買取品はすべて1個から売却できます。以下の価格は64個あたりです（設定上は64で割った1個価格）。

| 分類 | 商品 | 64個あたり |
| --- | --- | ---: |
| 農業 | Wheat | 10G |
| 農業 | Carrot, Potato, Melon Slice, Sugar Cane, Cactus, Sweet Berries, Glow Berries | 5G |
| 農業 | Poisonous Potato | 3G |
| 農業 | Beetroot, Nether Wart | 12G |
| 農業 | Pumpkin, Cocoa Beans | 8G |
| 採集 | Apple | 15G |
| 採集 | Red Mushroom, Brown Mushroom | 5G |
| 畜産 | Beef, Porkchop, Mutton | 15G |
| 畜産 | Chicken | 8G |
| 畜産 | Leather | 10G |
| 畜産 | Feather, Egg | 3G |
| 畜産 | White Wool | 5G |
| 漁業 | Cod, Salmon | 20G |
| 漁業 | Pufferfish, Tropical Fish | 25G |
| その他 | Rotten Flesh | 3G |

Honeycomb、Honey Bottle、Rabbit、Rabbit Hideは買取対象外です。Minecraft上の最大スタック数にかかわらず64個換算の価格基準を使用します。

## MineGames Slots

MineGames 1.0.5のSlotsを既存Vault Economyで利用します。3リール×1行、4種類のシンボルを等確率で抽選し、当たり1/2/3個の倍率は0.5/3/17倍です。理論RTPは89.84375%。プレイヤーのBET変更ボタンと新規参加時のJoin Giftは無効です。Dice/Crapsは1.0.5ではコマンドが登録されず、設定でも無効としています。ほかのゲームのstationは作成しません。

| 台 | BET | 当たり | 1/2/3個の払戻 | 最大払戻 |
| --- | ---: | --- | --- | ---: |
| Beginner | 10G | GOLD_BLOCK | 5 / 30 / 170G | 170G |
| Standard | 50G | DIAMOND_BLOCK | 25 / 150 / 850G | 850G |

両台の理論RTPは同じです。グローバル`max-payout: 10000.0`は設定事故用の上限で、通常の最大払戻850Gには適用されません。stationの座標はサーバー上で決め、管理者または村長が各場所で次を実行します。`set`と`setwinning`は対象stationの近くで実行します。一般プレイヤーへ`slots.admin`を付与しません。

Beginnerの場所で:

```text
/slotsadmin create 3 1
/slotsadmin set cost-per-spin 10
/slotsadmin setwinning GOLD_BLOCK
```

Standardの別の場所で:

```text
/slotsadmin create 3 1
/slotsadmin set cost-per-spin 50
/slotsadmin setwinning DIAMOND_BLOCK
```

村長は `slots.admin` により、Slot stationの新規設置、削除・再生成、station設定、外観、1プレイ料金、hologram位置を操作できます。採用中のMineGames 1.0.5にはSlots管理権限の細分化がなく、同じ権限でグローバル設定変更、`/slotsadmin reload`、`/slotsadmin housebalance`、`/slotsadmin housewithdraw` も実行できます。特に `housewithdraw` は村予算・カジノ資金に直接影響するため、誤操作に注意してください。

デプロイ後はPaper起動ログでMineGamesのenableとVault Economy provider取得成功を確認します。各台のBETとwinning blockを確認し、レバー操作でVault残高がBET分減り、当選時に配当が残高へ入ることを少額で試します。新規参加時のJoin Gift、`/dice`、`/craps`、BET変更ボタンが利用できないことも確認します。`/slotsadmin housebalance`でBET・払戻統計を確認してください。

## 緊急帰還札

ExecutableItemsの`emergency_return`を右クリックすると、EssentialsX Spawnで本拠点へ移動し、使用回数を1減らします。販売はEssentialsX kit `return_ticket`で行い、`kit-return_ticket: 100`により100Gを徴収します。一般プレイヤーへ`essentials.spawn`は与えません。

本拠点で管理者が一度`/setspawn`を実行してください。帰還札NPCは、その位置に立って次を実行します。

```text
/npc create return_ticket_vendor
/npc displayname return_ticket_vendor <gold>緊急帰還札</gold>
/npc interaction_cooldown return_ticket_vendor 1s
/npc action return_ticket_vendor RIGHT_CLICK add need_permission essentials.kits.return_ticket
/npc action return_ticket_vendor RIGHT_CLICK add player_command kit return_ticket
```

FancyNpcsの`player_command_as_op`は使用しません。価格徴収、EIアイテム発行、右クリック時の消費はJava版とBedrock版の実プレイヤーで公開前に確認してください。

## 役職旗

ExecutableItemsの役職旗は通常のBannerとして設置でき、特殊能力だけをActivator内のLuckPerms permissionで制限します。いずれもリソースパックを使用せず、1本ずつ扱います。

| 旗 | permission | 効果範囲 | 効果 | Cooldown |
| --- | --- | --- | --- | --- |
| 村長旗 (`mayor_flag`) | `feato.mayor` | 発動者を含む半径24ブロック | 30分: Speed I、Glowing、Haste I、Hero of the Village I、Weakness I。20分: Jump Boost I、Conduit Power I | 発動者ごとに10分 |
| 警備隊長旗 (`guard_captain_flag`) | `feato.guard_captain` | 発動者を含む半径16ブロック | 8分: Strength I、Resistance I、Absorption II、Glowing I、Mining Fatigue I。5分: Fire Resistance I | 発動者ごとに5分 |

`setup_minecraft_permissions.sh`は通常のEIアイテム操作permissionを一般グループへ付与し、追加ロール`mayor`と`guard_captain`を作成します。`mayor`には`feato.mayor`、`ei.item.mayor_flag`に加え、村の公共設備を運営するための例外としてMineGames Slotsの`slots.admin`を付与します。村長は引き続きサーバー管理者ではなく、OP権限やサーバー全般の管理権限は持ちません。`slots.admin`は設置だけでなくグローバル設定や資金引き出しまで含む広い権限です。`guard_captain`には従来の専用permissionのみを付与します。

## 役場職員 / 行政代執行文書

役場職員はLuckPermsの補助グループ `town_clerk`（`feato.town_clerk`）を持ち、行政代執行文書（`administrative_enforcement_order`）をEssentialsX kitで1枚10Gで購入できます。購入用kit権限は役場職員だけに付与し、文書は警備隊などへ自由に譲渡できます。使用は一般プレイヤーも可能です。

右クリックで1枚消費し、使用者本人に採掘速度上昇IV・火炎耐性I・コンジットパワーIを90秒、攻撃力上昇II・耐性IIを60秒、発光I・空腹IIを120秒付与します。使用クールダウンはありません。村長の許可は運用上のルールで、システムの発動条件にはしません。

販売NPCの登録、役職の付与・解除、公開前の確認は [行政代執行文書セットアップ](java/plugins/ExecutableItems/ADMINISTRATIVE_ENFORCEMENT_ORDER_SETUP.md) を参照してください。NPCは管理者によるWorld上での登録が必要です。

## 古銭換金

古銭生成と換金は別Pluginとして運用します。

- **FEATO Ancient Coin**: 古銭生成、Lootへの追加、古銭Item定義、`custom_data`付与
- **FEATO Coin Exchange**: 正規古銭識別、所持古銭の一括消費、Vault Economyへの一括換金、失敗時rollback、Player通知

正規古銭は、`minecraft:gold_nugget`かつ`minecraft:custom_data={feato_coin:{id:"ancient_coin",schema:1}}`だけです。交換レートは1枚あたり50Gです。通常のGold Nugget、表示名だけを変えたもの、Loreだけを似せたものは換金対象にしません。

```text
FancyNpcs
    │ console_command 1個
    ▼
FEATO Coin Exchange
    ├─ ConsoleSender検証
    ├─ Player解決
    ├─ 正規古銭判定
    ├─ Inventory/Offhandの正規古銭を一括消費
    ├─ Vaultへ合計額を1回入金
    ├─ 失敗時rollback
    └─ Playerへ結果通知
```

`FEATO Coin Exchange` はConsoleSenderからの`/feato-coin-exchange <player>`のみを受け付ける前提です。一般PlayerおよびOP Playerへコマンド実行権限は付与せず、FancyNpcsからも`player_command`、`player_command_as_op`、`scoreboard`、`clear`、`eco give`、`wait`、複数の`console_command`を用いません。

`plugins.txt`はAncient Coin 1.0.0とCoin Exchange 1.1.0のGitHub Release JARを取得します。GitHubのasset名にはバージョンが含まれるため、両URLは新しい安定Releaseごとに実在するtagとasset名へ更新してください。起動時は古いFEATO版JARを削除してから一覧のJARを再取得するため、版違いが残って二重に有効化されることはありません。Coin Exchange 1.1.0のRelease asset公開後にデプロイしてください。初期設定は`java/plugins/FEATOCoinExchange/config.yml`で管理し、交換額は`exchange-value: 50.0`です。

### FancyNpcs設定

```text
/npc create ancient_coin_trader
/npc displayname ancient_coin_trader <gold>古銭商</gold>
/npc interaction_cooldown ancient_coin_trader 1s
/npc action ancient_coin_trader RIGHT_CLICK add console_command feato-coin-exchange {player}
```

交換処理として登録するactionは最後の`console_command`だけです。既存の案内用`message` actionがある場合は削除してから登録します。FancyNpcsの`console_command`はConsoleとして実行され、`{player}`はクリックしたPlayer名に置換されます。

## LuckPerms

既存グループ名を`default`と仮定しません。Paperタスクが動くminecraft-dataノードで、一般・管理グループ名を明示して実行します。

```bash
./script/setup_minecraft_permissions.sh <player-group> <admin-group>
```

スクリプトは一般グループへ残高確認、送金、EIアイテム使用、FEATO商店だけを許可し、一般`/spawn`、`essentials.kits.return_ticket`、EconomyShopGUIの一括売却コマンドを拒否します。`featocoinexchange.execute`などFEATO Coin Exchangeの実行権限は一般・管理のいずれにも付与しません。管理グループへ経済、spawn、kit、商店編集、NPC作成と`console_command`を含む必要なaction種別だけを個別付与します。ワイルドカード権限、prefix、suffix、継承は変更しません。

LuckPermsはVelocity/Paper共通MariaDBを使います。SQL messagingによる反映のため、両側で`/lp info`、Velocityで`/lpv info`を確認します。

## squaremap

squaremap 1.3.15をPaper 26.2用JARで導入し、内部Webサーバーを8123番で起動します。既存の`dynmap.feato.jp`とnginx経路を再利用するためDNS変更は不要です。このホスト名は互換性維持のため残した名称で、表示内容はsquaremapです。

初回公開前に管理者が対象ワールドを指定してfull renderを実行し、CPU、メモリ、ディスク使用量を監視してください。プレイヤー位置、洞窟や非公開領域の表示方針も公開前に確認します。

## Floodgate backend key

Paper側Floodgate導入前に、現在Velocity側Floodgateが使用している`key.pem`を安全な管理端末へ取り出し、同じ内容からSwarm secret `floodgate_key`を作成してください。鍵そのものはGitへ保存しません。新しい鍵を生成する場合はVelocity/Paperを同じ鍵へ同時に切り替えます。公式Floodgateの要件どおり、proxy側`send-floodgate-data`を有効にし、backend側と同一鍵であることを確認してからBedrock接続を試験します。

PaperはMinecraft起動前にSecretを`/data/plugins/floodgate/key.pem`へ毎回上書きコピーします。Secretがない、空、またはコピーできない場合は起動を中止します。

## 描画距離・シミュレーション距離

初期目標は描画16チャンク・シミュレーション10チャンクです。実測前のため、最適値や動作確認済みの値ではありません。
`deploys/app/compose.yml`の`VIEW_DISTANCE`と`SIMULATION_DISTANCE`は、
[itzgの起動処理](https://docker-minecraft-server.readthedocs.io/en/latest/configuration/server-properties/)で
永続Volume内の`/data/server.properties`の`view-distance`と`simulation-distance`へ反映されます。
現行Composeはこの更新を無効化する`OVERRIDE_SERVER_PROPERTIES=false`や`SKIP_SERVER_PROPERTIES=true`を指定していません。
`java/config/spigot.yml`は`/config/spigot.yml`から`/data/spigot.yml`へ同期され、
両距離の[`default`](https://docs.papermc.io/paper/reference/spigot-configuration/#world-settings_default_view-distance)を維持して`server.properties`を参照します。追跡中のワールド別設定・Plugin設定には、両距離の上書き制限はありません。

1. 変更前のTPS、MSPT、メモリ使用量と人数・活動内容を記録します。
2. [通常のデプロイ手順](../deploys/README.md#4-環境変数とデプロイ)で変更を適用し、Paperを再起動します。
3. 起動後、Paperタスクが動く`minecraft-data`ノードで次を実行し、`view-distance=16`と`simulation-distance=10`を確認します。秘密値を含むファイル全体は表示しません。

   ```bash
   docker exec <minecraft-server-container> sh -c 'grep -E "^(view-distance|simulation-distance)=" /data/server.properties'
   ```

4. Java／Bedrockの両方で地形の見通しと移動時のチャンク読み込みを確認します。クライアント側の描画距離も確認してください。Paperの[`auto-config-send-distance: true`](https://docs.papermc.io/paper/reference/global-configuration/#chunk-loading-advanced_auto-config-send-distance)は維持しているため、クライアントの指定距離が小さいと送信範囲も小さくなります。
5. 変更前後で同程度の人数・活動に揃え、TPS、MSPT、メモリ使用量を比較します。TPSが継続して20を下回る、またはMSPTが継続して50msを超える場合は原因を確認し、必要ならComposeの両環境変数を`14`／`8`へ戻して再デプロイします。再起動後、同じ2項目と負荷を再確認します。

本番Volume内のワールド別設定や追加Pluginによる上書き、Java／Bedrockの実機動作、負荷の比較は適用時の確認事項です。

## デプロイ前後

1. appを停止し、Minecraft/Proxy VolumeとMariaDBを整合した状態でバックアップします。
2. Volume内の旧JARを確認し、旧Vault、XConomy、SetSpawn、Genius Shop、Dynmapと重複版をVolume外へ退避します。
3. 旧Data PackとAncient Coin Data Packを確認し、二重抽選を避けて退避します。
4. Compose/Swarm設定を検証してデプロイします。
5. `setup_minecraft_permissions.sh`を実グループ名で実行し、本拠点で`/setspawn`、NPC作成を行います。起動ログでFEATO Coin ExchangeのenableとVault Economy provider取得成功を確認します。
6. Java/Bedrock両方で商店、残高、帰還札、馬、Backpack、AncientCoin drop、squaremap表示を確認します。Coin Exchangeは、次の換金試験も行います。

   - 正規古銭1枚でNPCを右クリックし、1枚減少、残高が50G増加、成功メッセージを確認する。
   - 古銭なし、通常Gold Nugget、名前だけ「古銭」のGold Nugget、Loreだけ似せたGold Nuggetでは、残高・アイテムが変化せず交換不可メッセージとなることを確認する。
   - 正規古銭を複数slotとoffhandに持って1回クリックし、すべての正規古銭が消費され、枚数×50Gだけ残高が増えることを確認する。
   - 一般PlayerとOP Playerの双方が`/feato-coin-exchange <自分>`を直接実行すると拒否され、残高・古銭が変化しないことを確認する。

Hurricane追加前のローカル検証では、Paper 26.2 build 126 / Java 25で19 Pluginをすべて有効化し、正常停止まで確認しました。確認できた内容は、設定読込、依存解決、コマンド登録、squaremap 8123起動、ValhallaMMO `ja-jp`、Backpack Plus `jpn`、当時追跡していたEI 1アイテム、EconomyShopGUI 1セクション/1ショップ、VaultとEssentialsX Economy連携です。Hurricaneは公式READMEの対応表記が26.1までのため、26.2での起動ログとbamboo / pointed dripstoneの実機動作をデプロイ前に確認してください。

EconomyShopGUI 7.3.2の起動と以下の実クライアント操作は未確認です（Requires runtime verification）。過去の7.2.1の起動確認とは分けて、公開前に確認してください。

- Bedrock: `/shop`が標準Form UIで開くこと、商品を1回選択して購入数量指定へ進めること、購入・売却対象の選択と取引が成立すること、購入→売却・売却→購入の両方向と戻る操作が正常なことを確認する。残高・Inventoryの増減と、サーバーログに例外がないことも確認する。
- Java: 従来のInventory GUIで商品選択・購入・売却・数量指定・navigationが7.2.1から退行していないことを確認する。

クライアント操作が必要なJava/Bedrockログイン、NPCクリック、100G徴収、帰還札の消費とteleport、商品売買、馬の二人乗り、各Data Pack、古銭dropは本番公開前の実機確認事項です。Better HorsesはProtocolLibなしでも起動しますが、一部機能が無効になるという通知があります。現在は固定したProtocolLibを導入し、隔離起動でBetterHorsesの接続を確認しています。プレイヤー操作は未確認です。
