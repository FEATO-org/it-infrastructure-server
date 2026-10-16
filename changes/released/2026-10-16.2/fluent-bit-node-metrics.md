---
category: fix
scope: node-monitoring
change: ホストのCPUやメモリなどのメトリクス収集設定を修正しました。
reason: Fluent Bitがホストのprocfsとsysfsを誤ったパスから読み込んでいたためです。
---
