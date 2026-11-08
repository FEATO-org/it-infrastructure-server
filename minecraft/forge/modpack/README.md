# イワシコ寄生虫 Modpack

提供された58件版から Superb Warfare、Gucci & Vuitton Attachments、LesRaisins Tactical Equipements を除いた `manifest.json` は Minecraft 1.20.1 / Forge 47.4.28 と 55 組の CurseForge project ID / file ID を固定する。`modlist.html` も同じ除外を反映した一覧。共有 URL は取得元に使わない。

[Auto CurseForge](https://docker-minecraft-server.readthedocs.io/en/latest/types-and-platforms/mod-platforms/auto-curseforge/) で manifest を使う。Java 17 イメージの組み込み API key を使用し、配布制限されたファイルがあれば起動ログに示される手順に従い同じ ID のファイルを手動取得する。キーを変更する必要があるときは Swarm secret と `CF_API_KEY_FILE` を使用し、Git に記載しない。

以下はサーバーから除外する: Inventory Profiles Next (495267)、libIPN (679177)、Embeddium (908741)、Just Enough Resources (240630)、Sound Physics Remastered (535489)、[Tactical HUD](https://www.curseforge.com/minecraft/mc-mods/tacz-tactical-hud) (1768274)、[More Overlays Updated](https://www.curseforge.com/minecraft/mc-mods/more-overlays-updated) (391382)、[Entity Culling](https://www.curseforge.com/minecraft/mc-mods/entityculling) (448233)、[Oculus](https://www.curseforge.com/minecraft/mc-mods/oculus) (581495)。後者4件は配布元がクライアント用と記載している。[Inventory Profiles Next](https://www.curseforge.com/minecraft/mc-mods/inventory-profiles-next) と [libIPN](https://www.curseforge.com/minecraft/mc-mods/libipn) はクライアント用、[Embeddium](https://www.curseforge.com/minecraft/mc-mods/embeddium) はクライアント描画用、[JER](https://www.curseforge.com/minecraft/mc-mods/just-enough-resources-jer) はクライアント向け JEI 拡張、[Sound Physics](https://github.com/henkelmax/sound-physics-remastered/issues/172) の音響処理はクライアント向け。イメージ同梱の除外規則も適用されるため、[AppleSkin](https://github.com/squeek502/AppleSkin) は空腹・隠し満腹度の同期を使えるよう明示的に含める。JourneyMap はサーバー機能があるため残す。JEI なども提供 pack と依存関係を維持する。

ZIP の overrides は古い別 Mod の設定、クライアント設定、個人の画面・履歴情報、外部サービス設定を含む。現在の pack に関係する共通設定だけを `../config/config/` に選別した。`prepare-forge.sh` が存在しない設定だけを `/data/config` にコピーするため、Volume の設定は再起動や更新で自動上書きされない。更新時は新しい ZIP の manifest と設定の差分・Mod 依存関係を確認し、Volume をバックアップしてから必要な変更を明示的に反映する。ワールド単位の `serverconfig` は `/data/world/serverconfig` の実物を優先し、ZIP の古い Ars Nouveau 設定を現在の pack に適用しない。

[Ambassador](https://github.com/adde0109/Ambassador) は Forge 1.13–1.20.1 の通信を中継し、[Proxy Compatible Forge](https://github.com/adde0109/Proxy-Compatible-Forge) は Modern Forwarding を実装する。Forge は既存の Swarm secret を読み、一時ファイルから設定する。`/data/config/proxy-compatible-forge.toml` は一時ファイルへのシンボリックリンクであり、秘密値そのものは Volume に保存しない。既存の通常ファイルがある場合は起動を拒否するので、秘密情報として保護・退避後に作業する。

隔離環境では元の Manifest と指定5件の除外で Forge 47.4.28 が起動し、Proxy Compatible Forge の初期化を確認した。AppleSkin の明示追加後も再起動に成功し、同じワールドの `level.dat` を確認した。複数 Mod が起動時エラーを記録したため [運用手順](../../README.md#forge-1201-切替) の受入確認を行う。実際の Mod 通信・Velocity 4.2.0 との接続は未検証。

## 隔離試験で取得したサーバー用ファイル

- `appleskin-forge-mc1.20.1-2.5.1.jar`
- `appliedenergistics2-forge-15.4.12.jar`
- `architectury-9.2.14-forge.jar`
- `carryon-forge-1.20.1-2.1.2.7.jar`
- `cloth-config-11.1.136-forge.jar`
- `cosmeticarmorreworked-1.20.1-v1a.jar`
- `create-1.20.1-6.0.8.jar`
- `createaddition-1.20.1-1.3.3.jar`
- `creatingspace-1.20.1-1.7.21.jar`
- `curios-forge-5.14.1+1.20.1.jar`
- `elevatorid-1.20.1-1.9.1-forge.jar`
- `FarmersDelight-1.20.1-1.3.4.jar`
- `ftb-library-forge-2001.2.13.jar`
- `ftb-ultimine-forge-2001.1.8.jar`
- `geckolib-forge-1.20.1-4.8.4.jar`
- `gravestone-forge-1.20.1-1.0.35.jar`
- `GrimoireOfGaia4-1.20.1-4.0.0-alpha.12.jar`
- `guideme-20.1.15.jar`
- `jei-1.20.1-forge-15.56.0.205.jar`
- `journeymap-forge-1.20.1-6.0.7.jar`
- `kotlinforforge-4.12.0-all.jar`
- `ldlib-forge-1.20.1-1.0.52.a.jar`
- `nolandostructurez-0.0.1-1.20.1.jar`
- `ognmarts-0.1.6-beta.jar`
- `openblocks_reborn-1.0.2-1.20.1.jar`
- `Patchouli-1.20.1-85-FORGE.jar`
- `photon-forge-1.20.1-1.1.17.jar`
- `proxy-compatible-forge-1.3.1.jar`
- `shincolle-kai-1.20.1-1.0.0.jar`
- `sliceanddice-forge-3.6.0.jar`
- `tacz-forge-1.20.1-1.2.0.jar`
- `tacz_c-1.0.2-forge-1.20.1.jar`
- `torchesbecomesunlight-0.5.0-hotfix2.jar`
- `touhoulittlemaid-1.5.3-forge+mc1.20.1.jar`
- `travelersbackpack-forge-1.20.1-9.1.58.jar`
- `youkaishomecoming-2.7.2.jar`

既存 Volume の除外・包含条件を変更する場合はバックアップ後、一時的に `CF_FORCE_SYNCHRONIZE=true` を設定して再同期し、不要な再適用を避けるため検証後に外す。

## 旧44件版で追加した Create アドオン（参考・隔離検証待ち）

| Mod | 固定版 | CurseForge project / file |
| --- | --- | --- |
| [Steam 'n' Rails](https://www.curseforge.com/minecraft/mc-mods/create-steam-n-rails/files/8745475) | 1.7.3 Forge 1.20.1 | 688231 / 8745475 |
| [Diesel Generators](https://www.curseforge.com/minecraft/mc-mods/create-diesel-generators/files/7932785) | 1.3.12 Forge 1.20.1 | 869316 / 7932785 |
| [Create Big Cannons](https://www.curseforge.com/minecraft/mc-mods/create-big-cannons/files/7478036) | 5.10.2 Forge 1.20.1 | 646668 / 7478036 |
| [Ritchie's Projectile Library](https://www.curseforge.com/minecraft/mc-mods/ritchies-projectile-library/files/7292523) | 2.1.1 Forge 1.20.1 | 1279407 / 7292523 |

Create Crafts & Additions 1.3.3 は既存のため変更しない。Steam 'n' Rails と Diesel Generators の配布 JAR の Forge メタデータでは Create 6.0.8 が依存範囲に含まれる。Big Cannons 5.10.2 の配布ページは Create 6.0.8 を明記している。4 件の組み合わせの専用サーバー起動、ゲーム内動作とクライアント接続は未確認。Big Cannons の CurseForge 配布 JAR は固定 URL から取得でき、Forge メタデータの Create 6.0.8 と Ritchie’s Projectile Library 2.1.1 の依存範囲を確認した。Auto CurseForge での取得・起動は未確認。

以下の58件版への更新・復旧手順を優先する。

## TaCZディレクトリの退避

TaCZ本体、Weapons and Tacticsなどの関連Modと Arcana は維持する。`content.lock` から Charge into Battle、EOS Lab、Alex Kim の Gunpack ZIP を外したため、再起動時に自動再取得しない。Classics Reborn は以前に同期対象から外している。

本番のForgeを停止してVolume全体をバックアップする。`/data/tacz/` には Gunpack のほか利用者が置いたZIP・展開済みフォルダ・設定・その他のファイルが含まれる可能性がある。対象全体を確認し、以下のコマンドでディレクトリを `/data/.feato-content/retired/tacz-directory/tacz/` へまとめて移動する。既知のGunpackの管理記録も同じ退避先の `records/` へ移す。ModのJARと `/data/config/`、ワールドは操作しない。

新しいリポジトリと `content.lock` をデータノードへ配置し、停止・バックアップ後に実行する。Volumeとパスは実物を確認する。ディレクトリ自体が存在しなければ何もしない。シンボリックリンク、管理記録の不一致、退避先の競合は移動前に拒否する。

```bash
FORGE_VOLUME='実際のForge Volume名'
REPO_DIR='更新済みリポジトリの絶対パス'
FORGE_IMAGE='itzg/minecraft-server:java17@sha256:632741e7e7fce0fa2730c428ffdd8f6fb346355d2568548d56b5a313020e1287'
docker run --rm --user 0:0 --entrypoint bash \
  -v "$FORGE_VOLUME:/data" \
  -v "$REPO_DIR/minecraft/forge/retire-tacz-directory.sh:/retire-tacz-directory.sh:ro" \
  "$FORGE_IMAGE" /retire-tacz-directory.sh /data
```

適用後、TaCZは起動時に新しい `/data/tacz/` や既定コンテンツを生成する可能性がある。ディレクトリを永続的に存在させない設定ではない。追加Gunpackが再取得されないことを確認する。プレイヤーのクライアントに追加Gunpackがある場合は同様に退避し、接続・ゲーム内動作を検証する。削除したGunpack由来の銃器・アイテムは利用できなくなる可能性があり、削除後にワールドを保存すると復元できない場合がある。戻す際は停止して整合した更新前Volumeのバックアップと旧lockを復元する。

## 58件版への更新と復旧

旧44件との差分は Weapons and Tactics (Mod)、Superb Warfare、Storage Drawers、FerriteCore、Tactical HUD、More Overlays Updated、ModernFix、Gucci & Vuitton Attachments、Delightful、Torchmaster、Entity Culling、LesRaisins Tactical Equipements、Oculus、spark、Create: Copper & Zinc の15件追加、GraveStone の削除、Create Big Cannons の file 7478036 から [8169547](https://www.curseforge.com/minecraft/mc-mods/create-big-cannons/files/8169547) への更新。Weapons and Tactics は [JAR版 1411291 / 9473803](https://www.curseforge.com/minecraft/mc-mods/tacz-weapons-and-tactics-mod) を採用し、旧 ZIP 版は使わない。クライアント専用9件は manifest に残す。

適用前にサーバーを停止し Forge Volume 全体（world、playerdata、config、mods、tacz、管理状態）を整合した状態でバックアップし、復元を試す。GraveStone の削除により残存する墓やその所持品などが読み込めなくなる・失われるおそれがある。事前に墓とアイテムを回収し、旧Mod・旧設定を含む停止時バックアップを保存する。欠落データを保存したワールドに後からModを戻しても復元できる保証はない。

公式の [Auto CurseForge 再同期](https://docker-minecraft-server.readthedocs.io/en/latest/types-and-platforms/mod-platforms/auto-curseforge/) は `CF_FORCE_SYNCHRONIZE=true` で除外条件を再評価する。停止・バックアップ後、隔離コピーでまず一時設定して試す。再同期が旧 JAR の削除を保証するとは確認できていないため、旧 GraveStone、旧 Create Big Cannons、除外9件を `/data/mods/` で project/file ID・実体から特定し、残存していれば対象だけを `/data/mods/` の外へ退避する。識別不能なら停止して調査し、ディレクトリ全体を削除しない。Arcana と他の手動管理 JAR を維持する。検証後は一時設定を外す。

起動前の同期は `/data/tacz/feato-weapons-and-tactics.zip` と管理記録の双方が旧 SHA-256 `e9983776641a5ffa95fef55198d91ff595faff1630934cb4bfa7d6a8c4666c10` に一致する場合のみ `/data/.feato-content/retired/` に退避し、管理記録を除く。未管理、改変、退避先の競合は起動を拒否し、手動調査する。対象がなければ続行する。TaCZディレクトリの退避については上記の手順を参照する。

プレイヤーは新しい提供 Modpack を適用し、旧 Weapons and Tactics ZIP を `tacz/` から手動で退避して JAR版だけにする。追加Gunpackは退避し、Arcanaは `mods/` に維持する。設定とセーブは別途保全する。

[Weapons and Tactics 配布元](https://www.curseforge.com/minecraft/mc-mods/tacz-weapons-and-tactics-mod/files/all) は 0.4.1 を Forge 1.20.1 / TaCZ 1.2.0 向けとし、Big Cannons 5.11.4 は Create 6.0.7 以降を指定する。Create 6.0.8・TaCZ 1.2.0 はその表記範囲内だが、全Modの依存・レシピ・銃器ID・ネットワーク、Arcana と他Gunpackの競合、および実接続は未検証。隔離コピーで Forge とクライアントの起動・接続、レシピ・銃器・墓を確認する。旧版の隔離起動結果は新版の確認ではない。

ロールバックは停止後に旧リビジョンの manifest・設定・lock を戻し、更新前の Volume バックアップを復元する。旧ZIPを復元する場合は退避先のハッシュと管理記録を確認して元に戻す。新Modを保存したワールドを旧Mod構成のまま保存しない。

## 提供 overrides のサーバー設定

提供 overrides から Diesel Generators、Delightful、Farmer’s Delight、FerriteCore、ModernFix、Steam ’n’ Rails、ShinColle-kai（採掘テーブルを含む）、Storage Drawers、Torchmaster の共通設定を `../config/config/` に初回用として取り込んだ。これらの値は新規 Volume または対応ファイルが存在しない場合にのみ `prepare-forge.sh` により `/data/config/` にコピーされ、既存 Volume 上の同名設定は上書きされない。適用する必要がある場合は停止・バックアップ後、実際の設定と提供値を比較し、運用者が対象設定を個別に反映する。ゲーム内の効果は未検証。

既存の共通設定は保持する。提供版の Touhou Little Maid 設定には妖精関連の値の変更とクライアント固有のマイク設定があるが、既存設定の上書きは行わない。クライアント専用設定、個人情報を含み得るファイル、overrides 内の未管理JAR・Gunpack・モデル・音声・ワールドは一括コピーしない。これらの要否と再配布条件は別途確認する。

## Superb Warfare の削除

提供された58件版から [Superb Warfare 0.8.9.2](https://www.curseforge.com/minecraft/mc-mods/superb-warfare/files/9019882)（project 1218165 / file 9019882）を外した。Superb Warfare 削除直後は manifest と modlist は57件だった。クライアントでも対象JARをインスタンスの `mods/` の外へ退避し、サーバーと同じ構成にする。TaCZとArcanaは維持する。Gunpackは上記の退避方針に従う。

適用前に Forge を停止し、Volume全体（world、playerdata、mods、configを含む）をバックアップする。Superb Warfare の銃・乗り物・ブロック・インベントリなど、このModに由来する保存済みデータが失われる可能性がある。対象の回収・保存の要否を確認し、隔離コピーで Mod を除いた起動とワールドを検証する。除外後のワールドを保存してからJARを戻しても、消えたデータの復元は保証されない。復旧が必要なら停止して更新前の Volume バックアップと旧 manifest・JAR・設定を揃えて復元する。

本番Volumeには `superbwarfare-0.8.9.2-mc1.20.1-65d985a64-all.jar` が存在した。manifestから外すだけで既存JARが消える保証はない。データノードで対象Volumeを確認し、停止・バックアップ後に次のコマンドで対象だけを `/data/mods/` の外に退避する。旧JARと異なる内容、シンボリックリンク、退避先競合の場合は停止して調査する。`FORGE_VOLUME` は実際のVolume名に置き換える。

```bash
FORGE_VOLUME='実際のForge Volume名'
FORGE_IMAGE='itzg/minecraft-server:java17@sha256:632741e7e7fce0fa2730c428ffdd8f6fb346355d2568548d56b5a313020e1287'
docker run --rm --user 0:0 --entrypoint bash -v "$FORGE_VOLUME:/data" "$FORGE_IMAGE" -euc '
  src=/data/mods/superbwarfare-0.8.9.2-mc1.20.1-65d985a64-all.jar
  dst=/data/.feato-content/retired/superbwarfare-0.8.9.2-mc1.20.1-65d985a64-all.jar
  hash=559930003f638080de648a8621821d785158768c3f69a762094ef4c8d3c4cc12
  if [[ ! -e "$src" && ! -L "$src" ]]; then echo "対象JARは存在しません"; exit 0; fi
  [[ ! -L "$src" && -f "$src" ]] || { echo "通常ファイルではありません" >&2; exit 1; }
  [[ "$(sha256sum "$src" | cut -d " " -f 1)" == "$hash" ]] || { echo "SHA-256不一致" >&2; exit 1; }
  mkdir -p "$(dirname "$dst")"
  [[ ! -e "$dst" && ! -L "$dst" ]] || { echo "退避先が存在します" >&2; exit 1; }
  mv -- "$src" "$dst"
  echo "対象JARを退避しました: $dst"
'
```

運用者が更新済み構成を適用し起動後、`/data/mods/` に対象が再生成されていないことと、クライアント接続を確認する。旧 config や `world/serverconfig` は自動削除せず保持する。未使用設定の整理はバックアップのうえ別途判断する。

## Classics Reborn の退避

Classics Reborn ZIP は同期対象から削除した。既存Volume上の ZIP は自動削除されないため、更新した lock を配布する前に Forge を停止して Volume 全体をバックアップし、対象の `tacz/feato-classics-reborn.zip` と管理記録を確認して `/data/tacz/` の外へ退避する。対象Gunpackの銃器やアイテムの保存データが失われるおそれがあり、削除後にワールドを保存すると戻せない場合がある。必要な場合は停止時の旧Volumeと旧lockを揃えて復元する。

以下はデータノードで実行する例。Volume名を確認して指定する。既知のSHA-256と管理記録が両方一致する通常ファイルだけを退避し、不一致や退避先の競合があれば停止する。ZIPが存在しない場合は何も変更しない。別名ZIPや展開済みGunpackは自動で対象にならないため個別に確認する。

```bash
FORGE_VOLUME='実際のForge Volume名'
FORGE_IMAGE='itzg/minecraft-server:java17@sha256:632741e7e7fce0fa2730c428ffdd8f6fb346355d2568548d56b5a313020e1287'
docker run --rm --user 0:0 --entrypoint bash -v "$FORGE_VOLUME:/data" "$FORGE_IMAGE" -euc '
  src=/data/tacz/feato-classics-reborn.zip
  state=/data/.feato-content/tacz_feato-classics-reborn.zip.sha256
  dst=/data/.feato-content/retired/feato-classics-reborn.zip
  hash=6aa04aa13b87969b4a4f9edceb6ca69dc226f439d9fdbe82ec02b4620d4c1981
  if [[ ! -e "$src" && ! -L "$src" ]]; then echo "対象ZIPは存在しません。管理記録は変更していません。"; exit 0; fi
  [[ ! -L "$src" && -f "$src" && ! -L "$state" && -f "$state" ]] || { echo "ZIPまたは管理記録を確認してください" >&2; exit 1; }
  [[ "$(cat "$state")" == "$hash" && "$(sha256sum "$src" | cut -d " " -f 1)" == "$hash" ]] || { echo "SHA-256または管理記録が不一致です" >&2; exit 1; }
  mkdir -p "$(dirname "$dst")"
  [[ ! -e "$dst" && ! -L "$dst" && ! -e "$dst.sha256" && ! -L "$dst.sha256" ]] || { echo "退避先が存在します" >&2; exit 1; }
  mv -- "$src" "$dst"
  mv -- "$state" "$dst.sha256"
  echo "対象ZIPと管理記録を退避しました"
'
```

クライアント側でも同じ Gunpack の ZIP や展開版を `tacz/` から退避する。現在は追加Gunpackをすべて退避し、Arcana、TaCZ本体、ほかの設定は維持する。適用後に対象が再取得されず、クライアント接続を確認する。

## Gucci & Vuitton と LesRaisins Tactical の削除

[Gucci & Vuitton Attachments](https://www.curseforge.com/minecraft/mc-mods/tacz-gucci-vuitton-attachments/files/6062098)（project 1103436 / file 6062098）と [LesRaisins Tactical Equipements](https://www.curseforge.com/minecraft/mc-mods/tacz-lesraisins-tactical-equipements/files/8652673)（project 1273094 / file 8652673）を manifest と一覧から外す。LesRaisins のGit管理の初回設定を外し、既存Volumeの設定は保持する。TaCZ本体、Weapons and Tactics、Arcanaと他のModは維持する。クライアントの `mods/` からも両ModのJARを外し、`tacz/` に両GunpackのZIPまたは展開版が残っていないか確認する。

停止中のForge Volumeをバックアップし、対象Mod由来のアタッチメント・装備・アイテムの回収と復旧要否を確認する。Modを外してワールドを保存すると関連データが失われる可能性がある。復旧時は停止したうえで旧Mod構成と削除前Volumeの整合したバックアップを復元する。

既存VolumeのJARはmanifestから外すだけでは残る可能性がある。データノードで実際のVolume名を確認し、サービス停止・バックアップ後に次を実行する。確認済みの固定版とSHA-256が一致するJARだけを読込対象外へ退避する。対象をすべて事前確認し、一つでも不一致なら移動を始めない。対象なしは正常終了し、別版・変更・シンボリックリンク・退避先競合時は停止する。

```bash
FORGE_VOLUME='実際のForge Volume名'
FORGE_IMAGE='itzg/minecraft-server:java17@sha256:632741e7e7fce0fa2730c428ffdd8f6fb346355d2568548d56b5a313020e1287'
docker run --rm --user 0:0 --entrypoint bash -v "$FORGE_VOLUME:/data" "$FORGE_IMAGE" -euc '
  entries=(
    "guccivuitton-1.20.1-0.2.2.jar|9247e55f20acf8ec89af56d4ad45fcc8fe08bee9f7189421ef31835f3516bd57"
    "lrtactical-1.20.1-0.4.3.jar|930372cab33e1f563f597c74f9155b5ed25e6f2b0ff7e12dfc86255e1020ef2d"
  )
  dest=/data/.feato-content/retired
  for dir in /data/mods /data/.feato-content "$dest"; do
    [[ ! -L "$dir" && ( ! -e "$dir" || -d "$dir" ) ]] || { echo "安全でないディレクトリ: $dir" >&2; exit 1; }
  done
  for entry in "${entries[@]}"; do
    IFS="|" read -r name hash <<< "$entry"
    src="/data/mods/$name"; dst="$dest/$name"
    if [[ ! -e "$src" && ! -L "$src" ]]; then echo "対象なし: $name"; continue; fi
    [[ ! -L "$src" && -f "$src" ]] || { echo "通常ファイルではありません: $src" >&2; exit 1; }
    [[ "$(sha256sum "$src" | cut -d " " -f 1)" == "$hash" ]] || { echo "SHA-256不一致: $src" >&2; exit 1; }
    [[ ! -e "$dst" && ! -L "$dst" ]] || { echo "退避先が存在します: $dst" >&2; exit 1; }
  done
  mkdir -p "$dest"
  for entry in "${entries[@]}"; do
    IFS="|" read -r name hash <<< "$entry"
    src="/data/mods/$name"
    [[ ! -f "$src" ]] || { mv -- "$src" "$dest/$name"; echo "退避: $name"; }
  done
'
```

更新したmanifestを配布し起動後、対象JARが再取得されないこととクライアント接続を確認する。別名・別バージョンのJARは自動的に対象にならないため、存在する場合は個別に特定する。
