"""Run the real DeadChest pre-start block with mc-image-helper in disposable Docker data.

Requires PyYAML and a locally available minecraft-server image; set TEST_MINECRAFT_IMAGE
when testing a local image. This does not start Paper or validate player interactions.
"""
import copy
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
JAVA = ROOT / 'minecraft/java'
IMAGE = os.environ.get('TEST_MINECRAFT_IMAGE', 'itzg/minecraft-server:java25-graalvm')


class DeadChestStartupTest(unittest.TestCase):
    def test_settings_and_repeated_start(self):
        defaults = yaml.safe_load((JAVA / 'config-seeds/deadchest-config.yml').read_text())
        modern = copy.deepcopy(defaults)
        modern['chest'].update({'max-per-player': 27, 'owner-only-open': False})
        modern['updates']['custom-field'] = 'retain'
        modern['auto-update'] = False
        modern['custom'] = {'retain': True}
        legacy = {
            'maxDeadChestPerPlayer': 31, 'OnlyOwnerCanOpenDeadChest': False,
            'IndestructibleChest': False, 'AutoCleanupOnStart': False,
            'StoreXP': True, 'StoreXPPercentage': 75, 'DropMode': 2,
            'DropBlock': 3, 'ExcludedWorld': ['fixture_world'], 'auto-update': False,
        }
        fixtures = {
            'fresh': None, 'modern': modern, 'legacy': legacy,
            'minimal': {'chest': {'max-per-player': 19}},
        }
        with tempfile.TemporaryDirectory(prefix='deadchest-startup-') as temp:
            base = Path(temp)
            extras = base / 'extras'
            extras.mkdir()
            for source in ['patches/deadchest-updates.json', 'config-seeds/deadchest-config.yml']:
                shutil.copy2(JAVA / source, extras / Path(source).name)
            # Execute the actual production block; unrelated Floodgate/ProtocolLib setup is excluded.
            script = (JAVA / 'prepare-paper-plugins.sh').read_text()
            block = script[script.index('# Prevent loss of unclaimed items'):]
            (extras / 'test.sh').write_text('#!/bin/sh\nset -eu\n' + block)
            for name, config in fixtures.items():
                folder = base / name / 'plugins/DeadChest'
                folder.mkdir(parents=True)
                if config is not None:
                    (folder / 'config.yml').write_text(yaml.safe_dump(config))
                (folder / 'data-sentinel').write_bytes(b'keep chest and player data\n')
            subprocess.run([
                'docker', 'run', '--rm', '--network', 'none', '--entrypoint', 'sh',
                '-v', f'{base}:/checks', '-v', f'{extras}:/extras:ro', IMAGE, '-ec',
                'for name in fresh modern legacy minimal; do '
                'ln -s /checks/$name/plugins /data/plugins; '
                'sh /extras/test.sh; cp /data/plugins/DeadChest/config.yml /checks/$name-first.yml; '
                'sh /extras/test.sh; cmp /checks/$name-first.yml /data/plugins/DeadChest/config.yml; '
                'rm /data/plugins; done',
            ], check=True, timeout=180)
            for name, config in fixtures.items():
                with self.subTest(name=name):
                    expected = copy.deepcopy(defaults if config is None else config)
                    expected.setdefault('chest', {})['duration-seconds'] = 0
                    expected.setdefault('updates', {})['auto-check'] = False
                    # Bukkit YamlConfiguration treats null as an absent legacy alias.
                    expected['auto-update'] = None
                    folder = base / name / 'plugins/DeadChest'
                    self.assertEqual(expected, yaml.safe_load((folder / 'config.yml').read_text()))
                    self.assertEqual(b'keep chest and player data\n', (folder / 'data-sentinel').read_bytes())


if __name__ == '__main__':
    unittest.main()
