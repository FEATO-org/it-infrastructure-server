# 村長ロール / 村長旗セットアップ

## 目的

村長は管理者ではなく、村の公共事業・イベント・村予算の運用を担う社会的役職として扱う。

選出は原則立候補制、候補者がいない場合は管理側で指名する。任期は定めず、本人の申し出等で退任する。

村長には LuckPerms の補助グループ `mayor` を付与し、専用 permission `feato.mayor` だけを持たせる。管理者権限は与えない。

## 村長旗の仕様

- ExecutableItems ID: `mayor_flag`
- ベースアイテム: `minecraft:blue_banner`
- Banner pattern:
  - `minecraft:cross` / `white`
  - `minecraft:circle` / `pink`
- 最大スタック数: 1
- 通常Bannerとして設置可能
- NPCから村長のみ無制限に取得可能
- 旗を所持していても、`feato.mayor` を持たないプレイヤーは号令を発動できない
- 号令は空中右クリック時のみ発動させ、ブロック右クリック時の通常設置を妨げない
- 効果対象: 発動者本人を含む半径24ブロック以内のプレイヤー
- Cooldown: 20分（1200秒）

### バフ / デバフ

30分:

- Speed I
- Glowing
- Haste I
- Hero of the Village I
- Weakness I

20分:

- Jump Boost I
- Slow Falling
- Conduit Power I

Weakness I は、村長旗を遠征・戦闘用の恒常強化へ転用しにくくするための意図的なデバフ。

## 演出

号令発動時にはバフ範囲内へ標準Minecraftサウンドとパーティクルを出す。

推奨サウンド:

1. `minecraft:item.goat_horn.sound.0`
2. `minecraft:block.bell.use`
3. `minecraft:entity.player.levelup`（小さめ、高めのpitch）

推奨パーティクル:

- `minecraft:end_rod`（白系）
- `minecraft:cherry_leaves`（ピンク系）
- `minecraft:happy_villager`（少量）

リソースパック独自モデル・独自サウンドには依存しない。

## LuckPerms

初回のみグループを作成する。

```text
/lp creategroup mayor
/lp group mayor permission set feato.mayor true
```

表示用prefixは既存のLuckTags表示方式を実機確認したうえで設定する。村長をprimary groupへ変更せず、既存プレイヤーグループへ追加parentとして付与する。

就任:

```text
/lp user <player> parent add mayor
```

退任:

```text
/lp user <player> parent remove mayor
```

## ExecutableItemsアイテム作成

Banner patternの内部保存形式を手書きで推測しないこと。Paper 26.2上で正しいVanilla Bannerを生成し、そのアイテムをメインハンドに持った状態からExecutableItemsへ取り込む。

まず管理者が次を実行する。

```text
/give @s minecraft:blue_banner[minecraft:banner_patterns=[{pattern:"minecraft:cross",color:"white"},{pattern:"minecraft:circle",color:"pink"}],minecraft:max_stack_size=1] 1
```

生成した旗をメインハンドに持ち、ExecutableItemsで `mayor_flag` として作成する。

```text
/ei create mayor_flag
```

生成された `plugins/ExecutableItems/items/mayor_flag.yml` を確認し、Banner patternと最大スタック数が保持されていることを確認してから、以下のActivator設定を追加する。

### Activator要件

- `PLAYER_RIGHT_CLICK`
- targetは空中右クリックに限定
- アイテムを消費しない
- 設置をキャンセルしない
- `feato.mayor` を必須条件にする
- cooldown 1200秒
- cooldown中は発動をキャンセルする
- 同じ `mayor_flag` を複数所持した場合にPlayer cooldownが共有されることを実機確認する

### 実行コマンド例

ExecutableItemsの採用版が保存した実際のYAML構造を維持して追加すること。コマンド実行元の権限問題を避けるため、プレイヤーにVanilla `/effect` や `/playsound` 権限を新規付与しないこと。

号令中心を `%player%` とする例:

```text
execute at %player% run effect give @a[distance=..24] minecraft:speed 1800 0 true
execute at %player% run effect give @a[distance=..24] minecraft:glowing 1800 0 true
execute at %player% run effect give @a[distance=..24] minecraft:haste 1800 0 true
execute at %player% run effect give @a[distance=..24] minecraft:hero_of_the_village 1800 0 true
execute at %player% run effect give @a[distance=..24] minecraft:weakness 1800 0 true
execute at %player% run effect give @a[distance=..24] minecraft:jump_boost 1200 0 true
execute at %player% run effect give @a[distance=..24] minecraft:slow_falling 1200 0 true
execute at %player% run effect give @a[distance=..24] minecraft:conduit_power 1200 0 true
execute at %player% run playsound minecraft:item.goat_horn.sound.0 master @a[distance=..24] ~ ~ ~ 1 1
execute at %player% run playsound minecraft:block.bell.use master @a[distance=..24] ~ ~ ~ 0.7 1
execute at %player% run playsound minecraft:entity.player.levelup master @a[distance=..24] ~ ~ ~ 0.35 1.35
execute at %player% run particle minecraft:end_rod ~ ~1 ~ 1.5 1 1.5 0.03 24 force @a[distance=..24]
execute at %player% run particle minecraft:cherry_leaves ~ ~1 ~ 1.8 1 1.8 0.02 24 force @a[distance=..24]
execute at %player% run particle minecraft:happy_villager ~ ~1 ~ 1.2 0.8 1.2 0.02 12 force @a[distance=..24]
```

## FancyNpcs配布

NPC側とActivator側の両方で権限制御する。

NPC側は `feato.mayor` を持つプレイヤーだけ `mayor_flag` を1本受け取れるようにする。取得回数そのものは制限しない。

例:

```text
/npc create mayor_flag_supplier
/npc displayname mayor_flag_supplier <blue>村役場職員</blue>
/npc interaction_cooldown mayor_flag_supplier 1s
/npc action mayor_flag_supplier RIGHT_CLICK add need_permission feato.mayor
/npc action mayor_flag_supplier RIGHT_CLICK add console_command ei give {player} mayor_flag 1
```

FancyNpcs / ExecutableItemsの採用版で実際のgive構文を `/ei help` でも確認してから本番登録すること。

## 実機確認

Java版とBedrock版の両方で確認する。

1. 村長がNPCから旗を取得できる。
2. 非村長はNPCから取得できない。
3. 旗は1スタック1本になる。
4. 村長・非村長とも、所持している旗を通常Bannerとして設置できる。
5. 村長は空中右クリックで号令を発動できる。
6. 非村長が同じ旗を持っていても号令を発動できない。
7. 発動者を含む半径24ブロック内だけに8効果が付与される。
8. 24ブロック外には付与されない。
9. 音とパーティクルが範囲内で正常に再生される。
10. 20分Cooldownが動作する。
11. 複数の `mayor_flag` を持ち替えてもCooldownを回避できないことを確認する。採用版の挙動で共有されない場合は、複数旗による回避を仕様として許容する。
12. 退任して `mayor` parentを外した直後、既存の旗を持っていても号令を使用できない。
