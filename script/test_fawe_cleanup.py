#!/usr/bin/env python3
"""Exercise the actual pre-start cleanup loop in an isolated persistent-volume fixture."""
from pathlib import Path
import subprocess
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]


class FaweCleanupTest(unittest.TestCase):
    def test_obsolete_only_and_idempotent(self):
        script = (REPO / 'minecraft/java/prepare-paper-plugins.sh').read_text()
        start = script.index('for obsolete_jar in ')
        loop = script[start:script.index('\ndone', start) + len('\ndone')]
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp) / 'data'
            removed = ['plugins/worldedit-bukkit-7.4.5.jar',
                       'plugins/worldedit-bukkit-7.3.0.jar',
                       'plugins/update/worldedit-bukkit-7.4.5.jar',
                       'plugins/.paper-remapped/worldedit-bukkit-7.4.5.jar',
                       'plugins/update/dead-chest-4.30.0.jar']
            retained = ['plugins/FastAsyncWorldEdit-Paper-2.16.0.jar',
                        'plugins/update/FastAsyncWorldEdit-Paper-2.16.0.jar',
                        'plugins/craftbook-3.10.13.jar', 'plugins/ValhallaMMO_1.10.3.jar',
                        'plugins/update/another-plugin.jar',
                        'plugins/WorldEdit/config.yml', 'plugins/WorldEdit/schematics/example.schem',
                        'plugins/dead-chest-4.31.0.jar']
            for name in removed + retained:
                p = data / name
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text('fixture: ' + name)
            directory = data / 'plugins/worldedit-bukkit-directory.jar'
            directory.mkdir()
            command = loop.replace('/data/', str(data) + '/')
            for _ in range(2):
                subprocess.run(['sh', '-eu', '-c', command], check=True)
                for name in removed:
                    self.assertFalse((data / name).exists(), name)
                for name in retained:
                    self.assertEqual((data / name).read_text(), 'fixture: ' + name)
                self.assertTrue(directory.is_dir())


if __name__ == '__main__':
    unittest.main()
