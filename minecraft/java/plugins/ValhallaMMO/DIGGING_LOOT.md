# Ancient Coin Digging Loot 運用

## 管理対象と正本

初回作成時の正本は実サーバーでValhallaMMOが保存した設定です。以後は、この
リポジトリの設定を正本とします。

| 用途 | パス |
| --- | --- |
| Git管理するファイル | `minecraft/java/plugins/ValhallaMMO/loot_tables/digging.json` |
| Paperコンテナ内でValhallaMMOが読み書きするファイル | `/data/plugins/ValhallaMMO/loot_tables/digging.json` |

`deploys/app/compose.yml` は `minecraft/java/plugins` をコンテナの `/plugins` に
read-onlyでmountし、minecraft-server imageがその内容を `/data/plugins` へ同期する。
したがって、生成済みファイルをGitへ取り込んだ後の配布元は上記リポジトリパスである。

このリポジトリには正規生成済みの `digging.json` がまだないため、
`loot_tables/.gitkeep` だけを配置している。空の `digging.json` を作成したり、既存の
JSONを複製したりしないこと。

## 初回設定（実サーバー）

対象バージョンは `minecraft/java/plugins.txt` で指定している ValhallaMMO 1.10.3。
同梱の `plugin.yml` とコマンド登録を確認した管理GUIコマンドは次のとおり。

```text
/val loot
```

管理者は実サーバーで以下を順に行う。

1. `/ancientcoin give` を実行し、正規の Ancient Coin を取得する。
2. `/val loot` で ValhallaMMO Loot Table Editor を開く。
3. Loot Table `digging`、Pool `treasure` を選択する。
4. 手順1で取得した**実物の Ancient Coin**を新しい Drop Entry として登録する。
5. 次の初期値を設定する。

   | 項目 | 値 |
   | --- | --- |
   | base quantity min / max | `1` / `1` |
   | fortune quantity min / max | `0` / `0` |
   | chance | `0.0003` |
   | GUI上の確率 | `0.03%` |
   | 概算 | 約 `1 / 3333` |
   | chanceQuality / Luck bonus | `0` |
   | guaranteed | `false` |

6. `/val saveall` を実行する。ValhallaMMOが正規の Bukkit ItemStack serialization を含む
   `/data/plugins/ValhallaMMO/loot_tables/digging.json` を保存したことを確認する。
7. 自然生成されたDigging対象ブロックで動作確認する。テスト時だけ確率を上げた場合は、
   本番値へ戻して `/val saveall` を再実行してから取り込む。

Luck補正は初期導入では使わない。Mob Drop側の Ancient Coin 設定は変更しない。

## ItemStack登録の必須事項

Ancient Coin は `/ancientcoin give` で得た実物だけを登録する。次の行為は禁止する。

- `digging.json` の `drop` Base64 を手作業で生成、推測、加工する
- 既存 Gold Nugget のBase64を流用する
- JSON上でItemStackを直接組み立てる
- `custom_data` を失った Gold Nugget、または見た目だけ似た別ItemStackを登録する

正規ItemStackには `minecraft:custom_data` を含むため、GUIを通じてValhallaMMO自身に
serializationさせる以外の方法は使わない。

## 不正利用対策

Ancient Coin専用の `BlockBreakListener`、独自ブロック履歴、追加Pluginは作成しない。
砂や土を設置して破壊するだけで古銭を無限生成する用途への対策は、ValhallaMMO既存の
placed-block判定を利用する。加えて、Digging対象ブロック判定、world blacklist、
WorldGuardによるDigging無効リージョンなど、既存のValhallaMMO報酬可否判定に従う。

公開前には、自然生成ブロックでの抽選と、プレイヤー設置ブロック、blacklist world、
Digging無効WorldGuardリージョンでの非抽選を実機確認すること。

## 初回のGit取り込み

`/val saveall` 後、minecraft-data node上で実行中のPaperコンテナからファイルを取得する。
`app_minecraft-server` が1タスクだけ動いていることを確認してから行う。

```bash
container_id=$(docker ps -q --filter label=com.docker.swarm.service.name=app_minecraft-server)
docker cp "$container_id:/data/plugins/ValhallaMMO/loot_tables/digging.json" \
  minecraft/java/plugins/ValhallaMMO/loot_tables/digging.json
git diff --check
git diff -- minecraft/java/plugins/ValhallaMMO/loot_tables/digging.json
```

差分では、Ancient Coin Entryだけが意図どおり追加され、既存Digging Lootが消失・意図せず
変更されていないことを確認する。正規ItemStackのBase64文字列は検査・編集対象ではない。
確認後に `digging.json` をコミットする。

## 以後の変更とデプロイ

以後は `minecraft/java/plugins/ValhallaMMO/loot_tables/digging.json` をGitの正本として
サーバーへ配布する。GUIで本番サーバーのLoot Tableを変更した場合は、次のデプロイより前に
必ず前節の手順で実サーバーの生成物をGitへ逆輸入し、差分を確認してコミットする。

配布先の `minecraft/java/plugins` はread-only mountであり、ValhallaMMOが書き換えるのは
`/data/plugins` 側である。Git上の変更を反映するには、deployment nodeの作業ツリーを更新後、
`app_minecraft-server` を再作成してimageの `/plugins` → `/data/plugins` 同期を実行させる。
Swarmでは通常、次のように強制更新する。

```bash
docker service update --force app_minecraft-server
```

更新後は、コンテナ内の `/data/plugins/ValhallaMMO/loot_tables/digging.json` がGitでレビュー・
コミットした版であることを確認してから公開する。起動、reload、save操作がruntime側の
Loot Tableを変更し得るため、runtimeの変更をGitへ取り込まずに次回デプロイしないこと。
