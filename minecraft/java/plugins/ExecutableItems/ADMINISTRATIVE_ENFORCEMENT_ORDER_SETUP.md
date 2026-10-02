# 役場職員 / 行政代執行文書セットアップ

## 役割と利用条件

役場職員は行政代執行文書を購入・配布する社会的役職。警備隊などへ文書を渡し、行政代執行の人員として作業を依頼できる。

- LuckPerms補助グループ: `town_clerk`
- 役職permission: `feato.town_clerk`
- ExecutableItems ID / EssentialsX kit: `administrative_enforcement_order`
- ベースアイテム: `minecraft:paper`
- 購入価格: 1枚10G。購入回数・kitの待ち時間は制限しない
- 購入できるのは役場職員。譲渡・使用は役職に関係なく可能
- 右クリックで使用者本人のみに発動し、1枚消費。使用クールダウンなし
- 村長の許可は運用上のルール。許可確認、村長・役場職員の使用条件、所有者制限は実装しない

## 効果

すべて使用時に同時に付与する。コマンドのamplifierは表示レベルから1を引いた値。

| 効果 | 表示レベル | 持続時間 | amplifier |
| --- | --- | --- | --- |
| 採掘速度上昇 | IV | 90秒 | 3 |
| 攻撃力上昇 | II | 60秒 | 1 |
| 耐性 | II | 60秒 | 1 |
| 火炎耐性 | I | 90秒 | 0 |
| コンジットパワー | I | 90秒 | 0 |
| 発光 | I | 120秒 | 0 |
| 空腹 | II | 120秒 | 1 |

コンジットパワーは水中作業への対応。発光は担当者の可視化、空腹は作業による消耗を表す。旗の既存効果は解除・変更しない。特に警備隊長旗の採掘速度低下Iとの併用時は、採掘速度を実機確認する。

## 設定の反映と権限

Git管理の設定は通常のデプロイ手順で配置し、Paper起動時の `/plugins` から `/data/plugins` への同期を経て反映する。管理側のファイルを置くだけでは稼働中設定は更新されない。

`script/setup_minecraft_permissions.sh <player-group> <admin-group>` は、一般グループへ `ei.item.administrative_enforcement_order` を付与し、`town_clerk` に `feato.town_clerk` と `essentials.kits.administrative_enforcement_order` を付与する。購入用kit権限は一般グループへ付与しない。プレイヤーへ `ei give`、`effect`、`eco` の管理コマンド権限は付与しない。

就任・退任は既存primary groupを変更せず、追加parentで扱う。

```text
/lp user <player> parent add town_clerk
/lp user <player> parent remove town_clerk
```

## 10Gでの販売

既存の帰還札と同じEssentialsX kit方式で販売する。`kits.yml` のkitからConsoleでEIアイテムを1枚発行し、`config.yml` の `command-costs.kit-administrative_enforcement_order: 10` で徴収する。役場職員による `/essentials:kit administrative_enforcement_order` の直接購入も同じ価格・権限で扱う。

NPCを設置する位置で、管理者が以下を登録する。

```text
/npc create administrative_enforcement_order_vendor
/npc displayname administrative_enforcement_order_vendor <gold>行政代執行文書販売</gold>
/npc interaction_cooldown administrative_enforcement_order_vendor 1s
/npc action administrative_enforcement_order_vendor RIGHT_CLICK add need_permission feato.town_clerk
/npc action administrative_enforcement_order_vendor RIGHT_CLICK add need_permission essentials.kits.administrative_enforcement_order
/npc action administrative_enforcement_order_vendor RIGHT_CLICK add player_command essentials:kit administrative_enforcement_order
```

価格徴収と発行はkitに集約する。`player_command_as_op` や、別々の `eco take` / `ei give` actionは使用しない。NPCはWorld上での登録が必要で、このリポジトリ変更だけでは作成されない。

## 公開前の実機確認

Java / Bedrockの両方で確認する。本変更では本番適用・実機確認は行っていない。

1. 役場職員はNPCと直接kitの両方で、10Gを支払い正規文書を1枚取得できる。
2. 非役場職員はNPC・直接kitから購入できず、残高も変わらない。
3. 残高不足では文書を取得できず、10G以上の残高では1回につき10Gだけ減る。購入失敗時に二重徴収・無料発行が起きない。
4. インベントリ満杯時の発行・徴収を確認する。EIの発行失敗時にkitの徴収だけが残る場合は、販売を公開せず既存の配布経路を見直す。
5. 譲渡先の一般プレイヤーが、役職・所有者・村長許可の条件なしで使用できる。
6. メインハンド・オフハンドからの右クリックで、スタックから1枚だけ消費し、使用者だけに7効果が正しいレベル・時間で付与される。通常の紙や隣のプレイヤーには作用しない。
7. 退任後は購入できず、手元の文書や配布済み文書は引き続き使用できる。
8. 旗・既存装備・ValhallaMMOと併用し、採掘速度・実ダメージ・耐性を確認する。銃器への攻撃力上昇の適用も実機確認し、標準Strengthだけで銃器強化まで保証しない。
