---
category: fix
scope: minecraft-connection
change: Minecraft サーバー再起動後に、ゲーム接続と地図表示の接続先を自動更新するようにしました。
reason: 接続先が変わると、nginx を手動再起動するまで接続できない場合があったためです。
---
