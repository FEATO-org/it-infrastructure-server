# CraftBook 貨物線路ガイド

FEATO Minecraft サーバーで、離れた農場・生産拠点と倉庫をチェスト付きトロッコで結ぶための運用ガイドです。

対象は CraftBook 3.10.13 系です。貨物線路では主に以下の Mechanic を使用します。

- `MinecartDeposit`: チェストとチェスト付きトロッコ間の積み下ろし
- `MinecartStation`: トロッコの停止・指定方向への発車
- `MinecartReverser`: トロッコの反転、または進行方向の矯正
- `MinecartBooster`: 長距離線での加速（既に有効）
- `MinecartSpeedModifiers`: トロッコ速度調整（既に有効）

## 1. 推奨する基本構成

農場と倉庫を単線で結び、1台のチェスト付きトロッコを往復させます。

```text
[農場]
 農産物チェスト
      │
 [Deposit]
      │
 [Station]  ← 農場から倉庫方向へ発車
      │
====== 長距離線路 ======
      │
 [Collect]
      │
 [Station]  ← 倉庫から農場方向へ発車
      │
 倉庫チェスト
[倉庫]
```

Station は進行方向を指定して発車できるため、単純な2拠点往復では Reverser を必須としません。

Reverser は以下の用途で使用します。

- レッドストーンなしで単純に反転させたい
- 分岐や合流部で一方向へ揃えたい
- 将来、複数拠点を結ぶ貨物網へ拡張したい

## 2. 農場側: トロッコへの積み込み

### 必要なもの

- チェスト付きトロッコ
- レール
- 鉄鉱石ブロック 1個
- チェスト 1〜2個
- 看板 1個

### 配置

`MinecartDeposit` の標準ブロックは `minecraft:iron_ore` です。

```text
横から見た例

      レール
========□========
      鉄鉱石
        │
      看板
```

鉄鉱石に隣接する位置へ積み込み元チェストを置きます。最大2個のチェストを隣接できます。

看板の2行目を次のようにします。

```text
[Deposit]
```

このサーバーでの用途では、`[Deposit]` は **隣接チェスト → チェスト付きトロッコ** の方向へアイテムを移します。

3行目を空欄にすると対象アイテムを限定せず搬送します。

CraftBook 3.x のドキュメントには3行目で数値IDを指定する旧式のアイテムフィルタがありますが、FEATOサーバーは現行Minecraft環境のため、数値IDフィルタは実機確認なしでは使用しないでください。通常の貨物線では3行目を空欄にする運用を推奨します。

## 3. 倉庫側: トロッコから荷下ろし

基本構造は農場側と同じです。

看板の2行目を次のようにします。

```text
[Collect]
```

`[Collect]` は **チェスト付きトロッコ → 隣接チェスト** の方向へアイテムを移します。

名称が直感と逆に感じやすいため注意してください。

- `[Deposit]`: チェストからトロッコへ積む
- `[Collect]`: トロッコからチェストへ降ろす

## 4. Station の作り方

`MinecartStation` の標準ブロックは `minecraft:obsidian` です。

```text
      レール
========□========
      黒曜石
        │
      看板
```

看板の2行目を次のようにします。

```text
[Station]
```

看板はレールの2〜3ブロック下に設置できます。

Station は以下のように動作します。

- レッドストーン入力なし / OFF: トロッコを停止
- レッドストーン入力 ON: 看板が向いている方向へ発車

看板は、**トロッコを発車させたい方向を向くように設置**します。

### 手動駅

ボタンやレバーで Station にレッドストーン入力を与えます。

荷物を確認してから発車させたい場合はこちらを使用します。

### 自動折返し駅

Deposit / Collect を Station の手前に設置し、Station を常時ONにしておくと、貨物トロッコは次の順で処理されます。

1. Deposit / Collect 上を通過
2. アイテムを積み下ろし
3. Station へ進入
4. Station の看板方向へ発車
5. 来た線路を逆方向へ戻る

このため、単線の農場↔倉庫シャトルでは Reverser を追加しなくても自動往復を構成できます。

## 5. Reverser

`MinecartReverser` の標準ブロックは `minecraft:white_wool` です。

レールの下を白色の羊毛にすると、通過したトロッコの進行方向を反転できます。

```text
      レール
========□========
      白色羊毛
```

### Directed Reverser

特定方向だけを許可したい場合は看板を追加します。

看板の2行目:

```text
[Reverse]
```

看板を許可したい進行方向へ向けます。正しい方向で進入したトロッコはそのまま通過し、逆方向から来たトロッコだけ反転します。

単純な2拠点貨物線では必須ではありません。分岐や合流を作る段階で利用してください。

## 6. 長距離線路の加速

`MinecartBooster` は既に有効です。

標準設定では線路下に次のブロックを置くことで速度を変更できます。

| ブロック | 動作 |
| --- | --- |
| 金鉱石 | 通過時に速度を25%増加 |
| 金ブロック | 最大速度まで加速 |
| ソウルサンド | 速度を50%へ低下 |
| 砂利 | 速度を80%へ低下 |

通常は Vanilla のパワードレールを主体にし、長い直線や速度不足が問題になる場所で Booster を補助的に使用してください。

Booster は看板を必要としないため、今回追加した LuckPerms 権限は不要です。

## 7. 推奨する農場駅の配置

倉庫から農場へ来る方向を `→` とした場合の例です。

```text
倉庫から →

===========[Deposit]====[Station]=== 終端
                │             │
          農産物チェスト      └ 看板は倉庫方向を向ける

                  ← 発車後は倉庫へ戻る
```

流れ:

1. 空のチェスト付きトロッコが倉庫から到着
2. `[Deposit]` で農産物を積載
3. Station に進入
4. Station が倉庫方向へ発車

## 8. 推奨する倉庫駅の配置

農場から倉庫へ来る方向を `→` とした場合の例です。

```text
農場から →

===========[Collect]====[Station]=== 終端
                │             │
            倉庫チェスト      └ 看板は農場方向を向ける

                  ← 発車後は農場へ戻る
```

流れ:

1. 荷物を積んだチェスト付きトロッコが農場から到着
2. `[Collect]` で倉庫チェストへ荷下ろし
3. Station に進入
4. Station が農場方向へ発車

これを繰り返すことで、1台の貨物トロッコが農場と倉庫の間を往復します。

## 9. LuckPerms

通常プレイヤーが貨物線設備を作成できるよう、以下の権限を付与します。

```text
craftbook.vehicles.deposit
craftbook.vehicles.reverser
craftbook.vehicles.station
```

FEATOの `script/setup_minecraft_permissions.sh` に追加済みです。

セットアップスクリプトは従来通り以下で実行します。

```bash
./script/setup_minecraft_permissions.sh <player-group> <admin-group>
```

個別に付与する場合は次のコマンドでも設定できます。

```text
/lp group <player-group> permission set craftbook.vehicles.deposit true
/lp group <player-group> permission set craftbook.vehicles.reverser true
/lp group <player-group> permission set craftbook.vehicles.station true
```

## 10. チャンク読み込みに関する注意

Minecraft のトロッコは、線路があるチャンクが読み込まれていない状態では継続して走行・処理できません。

そのため、農場と倉庫が非常に離れている場合、完全無人の24時間物流には向きません。

CraftBook には `ChunkAnchor` がありますが、線路全体を常時読み込みするとサーバー負荷が増えるため、FEATOでは今回有効化していません。

運用開始時は次の方針とします。

- 通常のプレイヤー活動範囲内の物流線として利用する
- 長距離線路へ大量の ChunkAnchor を設置しない
- 完全無人物流が必要になった場合は、チャンク負荷を測定した上で別途設計する

## 11. 今回有効化した CraftBook Mechanic

`minecraft/java/plugins/CraftBook/config.yml` に以下を追加しています。

```yaml
enabled-mechanics:
  - MinecartDeposit
  - MinecartReverser
  - MinecartStation
```

既存の以下はそのまま利用できます。

```yaml
  - MinecartBooster
  - MinecartSpeedModifiers
```

## 12. 将来拡張

貨物線が増えた場合は、次の Mechanic を追加候補とします。

- `MinecartSorter`: 貨物内容やトロッコ種別による自動分岐
- `MinecartDispenser`: トロッコの回収・再配置、車庫運用
- `MinecartMoreRails`: 複雑な交差・物流網への拡張

これらは現在の農場↔倉庫の1対1輸送には不要なため、有効化していません。

## 13. 公式資料

- CraftBook 3.x Minecart Mechanics: https://craftbook.enginehub.org/en/3.x/mechanics/minecart/
- Collectors and Depositors: https://craftbook.enginehub.org/en/3.x/mechanics/minecart/block/collector_depositor/
- Station: https://craftbook.enginehub.org/en/3.x/mechanics/minecart/block/station/
- Reverser: https://craftbook.enginehub.org/en/3.x/mechanics/minecart/block/reverser/
- Boosters and Brakes: https://craftbook.enginehub.org/en/3.x/mechanics/minecart/block/booster_brake/
