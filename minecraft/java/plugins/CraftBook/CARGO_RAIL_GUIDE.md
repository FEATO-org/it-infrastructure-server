# CraftBook 貨物線路ガイド

FEATO Minecraft サーバーで、離れた農場・生産拠点と倉庫をチェスト付きトロッコで結ぶための運用ガイドです。

対象は CraftBook 3.10.13 系です。貨物線路では主に以下の Mechanic を使用します。

- `MinecartDeposit`: チェストとチェスト付きトロッコ間の積み下ろし
- `MinecartStation`: トロッコの停止・指定方向への発車
- `MinecartElevator`: トロッコの階層間垂直搬送
- `MinecartReverser`: トロッコの反転、または進行方向の矯正
- `MinecartBooster`: 長距離線での加速（既に有効）
- `MinecartSpeedModifiers`: トロッコ速度調整（既に有効）
- `Pipes`: 倉庫内でのアイテム搬送・分配（既に有効）

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
 [CartLift Up]
      │
      │ 垂直搬送
      ▼
 [CartLift]   ← 倉庫2階
      │
 [Collect]
      │
 受入チェスト
      │
    Pipes
      │
 分類先チェスト群
```

倉庫が2階にあるため、長距離輸送はトロッコ、階層間輸送は `MinecartElevator`、荷下ろし後の倉庫内物流は `Pipes` と役割を分離します。

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
- レッドストーン入力 ON: 看板方向を基準に指定方向へ発車

### 手動駅

ボタンやレバーで Station にレッドストーン入力を与えます。

### 自動折返し駅

Deposit / Collect を Station の手前に設置し、Station を常時ONにしておくことで、積み下ろし後にそのまま発車させられます。

## 5. MinecartElevator: 2階倉庫への垂直搬送

倉庫が2階にあるため、トロッコ自体を `MinecartElevator` で垂直搬送します。

標準のリフトブロックは `minecraft:nether_bricks` です。リフトブロックの上にレールを置き、その下に看板を設置します。

### 1階: 上り側

看板の2行目:

```text
[CartLift Up]
```

上方にある `[CartLift Down]` または `[CartLift]` を探してトロッコを転送します。

### 2階: 到着側

看板の2行目:

```text
[CartLift]
```

`[CartLift]` は到着専用で、そこから自動的に別階へ再転送しません。

```text
2F    レール ─── [CartLift] ─── [Collect] ─── [Station]
                    ▲
                    │
                    │ 垂直搬送
                    │
1F    レール ─── [CartLift Up]
```

上りと下りを自動化する場合は、同じ列を往復させるよりも **上り用と下り用のCartLiftを別列にする**ことを推奨します。これにより到着直後の再転送や進行方向の混乱を避けられます。

下り用は2階に `[CartLift Down]`、1階に到着専用 `[CartLift]` を設置します。

## 6. Reverser

`MinecartReverser` の標準ブロックは `minecraft:white_wool` です。

レールの下を白色の羊毛にすると、通過したトロッコの進行方向を反転できます。

```text
      レール
========□========
      白色羊毛
```

### Directed Reverser

看板の2行目:

```text
[Reverse]
```

単純な2拠点貨物線では必須ではありません。分岐や合流を作る段階で利用してください。

## 7. 長距離線路の加速

`MinecartBooster` は既に有効です。

標準設定では線路下に次のブロックを置くことで速度を変更できます。

| ブロック | 動作 |
| --- | --- |
| 金鉱石 | 通過時に速度を25%増加 |
| 金ブロック | 最大速度まで加速 |
| ソウルサンド | 速度を50%へ低下 |
| 砂利 | 速度を80%へ低下 |

通常は Vanilla のパワードレールを主体にし、長い直線や速度不足が問題になる場所で Booster を補助的に使用してください。

## 8. 推奨する農場駅

```text
倉庫から →

===========[Deposit]====[Station]=== 終端
                │             │
          農産物チェスト      └ 倉庫方向へ発車

                  ← 発車後は倉庫へ戻る
```

流れ:

1. 空のチェスト付きトロッコが到着
2. `[Deposit]` で農産物を積載
3. Station に進入
4. 倉庫方向へ発車

## 9. 推奨する2階倉庫駅

```text
農場
 │
 │ 長距離線
 ▼
1F [CartLift Up]
       │
       │
       ▼
2F [CartLift]
       │
    [Collect]
       │
   受入チェスト
       │
     Pipes
   ┌───┼───┬───┐
   ▼   ▼   ▼   ▼
  穀物 野菜 種  その他
       │
   [Station]
       │
2F [CartLift Down]  ← 下り用の別列
       │
       ▼
1F [CartLift]
       │
       └──── 農場へ返送
```

この構成では、鉄道部分と倉庫内物流を分離できます。

## 10. Pipes による倉庫内自動分配

`Pipes` は既に有効です。

基本構成:

1. アイテム源となる受入チェスト
2. 受入チェストへ向けた粘着ピストン
3. ガラス等のパイプ用ブロック
4. 分配先チェストへ向けた通常ピストン
5. 分配先チェスト

粘着ピストンが OFF → ON になったとき、受入チェストからパイプへアイテムを吸い出します。

標準設定では1回の動作につき1スタックを搬送します。

### フィルタ

CraftBook 3.x ではピストンに `[Pipe]` 看板を付け、3行目に許可対象、4行目に除外対象を指定するフィルタ機能があります。

```text

[Pipe]
<許可対象>
<除外対象>
```

ただし、3.x公式ドキュメントは旧式の数値アイテムIDで例示されています。FEATOサーバーは現行Minecraft上で動作しているため、**実際のアイテム指定構文はサーバー上で検証してから本番の仕分けルールへ固定してください**。

そのため現時点の正式方針は次の通りです。

- Pipesによる倉庫内自動分配機能は採用する
- 分配設備は `受入チェスト → Pipes → 分類先チェスト` とする
- 個別アイテムのフィルタ構文は実機確認後に確定する
- フィルタできない場合でも、Pipes自体は倉庫内搬送に利用できる

`MinecartSorter` はトロッコそのものを線路分岐させるMechanicであり、倉庫内のアイテム分類には使用しません。

## 11. LuckPerms

通常プレイヤーが貨物線設備を作成できるよう、以下の権限を付与します。

```text
craftbook.vehicles.deposit
craftbook.vehicles.cartlift
craftbook.vehicles.reverser
craftbook.vehicles.station
craftbook.circuits.pipes
```

FEATOの `script/setup_minecraft_permissions.sh` に追加済みです。

セットアップスクリプト:

```bash
./script/setup_minecraft_permissions.sh <player-group> <admin-group>
```

個別に付与する場合:

```text
/lp group <player-group> permission set craftbook.vehicles.deposit true
/lp group <player-group> permission set craftbook.vehicles.cartlift true
/lp group <player-group> permission set craftbook.vehicles.reverser true
/lp group <player-group> permission set craftbook.vehicles.station true
/lp group <player-group> permission set craftbook.circuits.pipes true
```

## 12. チャンク読み込みに関する注意

Minecraft のトロッコは、線路があるチャンクが読み込まれていない状態では継続して走行・処理できません。

CraftBook には `ChunkAnchor` がありますが、線路全体を常時読み込みするとサーバー負荷が増えるため、FEATOでは今回有効化していません。

運用開始時は次の方針とします。

- 通常のプレイヤー活動範囲内の物流線として利用する
- 長距離線路へ大量の ChunkAnchor を設置しない
- 完全無人物流が必要になった場合は、チャンク負荷を測定した上で別途設計する

## 13. 有効化している関連Mechanic

```yaml
enabled-mechanics:
  - MinecartBooster
  - MinecartDeposit
  - MinecartElevator
  - MinecartReverser
  - MinecartSpeedModifiers
  - MinecartStation
  - Pipes
```

## 14. 将来拡張

貨物線が増えた場合は、次の Mechanic を追加候補とします。

- `MinecartSorter`: 貨物内容やトロッコ種別による線路分岐
- `MinecartDispenser`: トロッコの回収・再配置、車庫運用
- `MinecartMoreRails`: 複雑な交差・物流網への拡張

これらは現在の農場↔倉庫の1対1輸送には不要なため、有効化していません。

## 15. 公式資料

- CraftBook 3.x Minecart Mechanics: https://craftbook.enginehub.org/en/3.x/mechanics/minecart/
- Collectors and Depositors: https://craftbook.enginehub.org/en/3.x/mechanics/minecart/block/collector_depositor/
- Station: https://craftbook.enginehub.org/en/3.x/mechanics/minecart/block/station/
- Minecart Elevator: https://craftbook.enginehub.org/en/3.x/mechanics/minecart/block/elevator/
- Reverser: https://craftbook.enginehub.org/en/3.x/mechanics/minecart/block/reverser/
- Boosters and Brakes: https://craftbook.enginehub.org/en/3.x/mechanics/minecart/block/booster_brake/
- Pipes: https://craftbook.enginehub.org/en/3.x/mechanics/pipes/
