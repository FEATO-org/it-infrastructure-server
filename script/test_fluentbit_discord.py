#!/usr/bin/env python3
"""Exercise the actual Fluent Bit Lua callback without making HTTP requests.

Requires lupa (e.g. PYTHONPATH=/path/to/lupa python3 script/test_fluentbit_discord.py).
Fixtures are representative samples, not logs captured from FEATO production.
"""
import json
from pathlib import Path
import unittest

from lupa import LuaRuntime

ROOT = Path(__file__).resolve().parents[1]


class DiscordLogTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lua = LuaRuntime(unpack_returned_tuples=True)
        cls.lua.execute((ROOT / 'fluentbit/discord.lua').read_text())
        cls.callback = cls.lua.globals().process_minecraft_log

    def check_event(self, line, route, expected):
        code, _, result = self.callback('minecraft.forge', 0, self.lua.table_from({'log': line}))
        self.assertEqual(code, 2)
        self.assertEqual(result['route'], route)
        self.assertEqual(result['headers']['Content-Type'], 'application/json')
        body = json.loads(result['body'])
        self.assertEqual(body['allowed_mentions'], {'parse': []})
        self.assertIn(expected, body.get('content', '') + ''.join(e['title'] + e['description'] for e in body.get('embeds', [])))

    def test_events(self):
        fixtures = [
            ('[12:34:56] [Server thread/INFO]: Steve joined the game', 'notify', 'Steve** がサーバーに参加'),
            ('[12:34:56] [Server thread/INFO] [minecraft/MinecraftServer]: Steve joined the game', 'notify', 'Steve** がサーバーに参加'),
            ('[12:34:56] [Server thread/INFO] [minecraft/MinecraftServer]: Steve left the game', 'notify', 'Steve** がサーバーから退出'),
            ('[12:34:56] [Server thread/INFO] [minecraft/MinecraftServer]: <Steve> hello', 'notify', '**Steve**: hello'),
            ('[12:34:56] [Server thread/INFO] [minecraft/MinecraftServer]: Steve was slain by Zombie', 'notify', 'Steve was slain by Zombie'),
            ('[12:34:56] [Server thread/INFO] [minecraft/DedicatedServer]: Starting minecraft server version 1.20.1', 'notify', '1.20.1'),
            ('[12:34:56] [Server thread/INFO] [minecraft/DedicatedServer]: Done (3.123s)! For help, type "help"', 'notify', '3.123 秒'),
            ('[12:34:56] [Server thread/INFO] [minecraft/MinecraftServer]: Stopping server', 'notify', 'サーバー停止中'),
            ('[12:34:56] [Server thread/ERROR] [example/Mod]: Something failed', 'error', 'Something failed'),
        ]
        for line, route, expected in fixtures:
            with self.subTest(line=line):
                self.check_event(line, route, expected)

    def test_dropped(self):
        for line in [
            '[12:34:56] [Server thread/WARN] [example/Mod]: Something failed',
            '[12:34:56] [Server thread/INFO] [example/Mod]: Initializing mod',
            '\tat example.Mod.run(Mod.java:12)',
            'Caused by: java.lang.Exception: Something failed',
        ]:
            with self.subTest(line=line):
                code, _, _ = self.callback('minecraft.forge', 0, self.lua.table_from({'log': line}))
                self.assertEqual(code, -1)


if __name__ == '__main__':
    unittest.main()
