"""Test the real BetterHorses startup block in disposable, offline Docker data.

Requires PyYAML and a local mc-image-helper image. Optional BETTERHORSES_DEFAULTS
points to config.yml extracted from the verified 6.4 JAR for a full-default test.
Does not start Paper or simulate horse growth and breeding.
"""
import copy
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

import yaml

JAVA = Path(__file__).resolve().parents[1] / 'minecraft/java'
IMAGE = os.environ.get('TEST_MINECRAFT_IMAGE', 'itzg/minecraft-server:java25-graalvm')


class BetterHorsesStartupTest(unittest.TestCase):
    def test_settings_preservation_and_repeated_start(self):
        minimal = {'settings': {'mounted-damage-boost': {'enabled': False}}}
        existing = {
            'horse-growth-settings': {'enabled': True, 'time-until-adult': 3,
                                      'max-size': 1.2, 'custom': 'retain'},
            'settings': {'breeding-cooldown': 300, 'male-ignore-cooldown': False,
                         'mounted-damage-boost': {'enabled': True, 'percentage': 42},
                         'custom': ['retain']},
            'traits': {'custom': 17}, 'training': {'enabled': True},
            'ownership': {'custom': 'retain'}, 'storage': {'custom': 'retain'},
        }
        missing_growth = copy.deepcopy(existing)
        del missing_growth['horse-growth-settings']
        fixtures = {'fresh': None, 'minimal': minimal, 'existing': existing,
                    'missing-growth': missing_growth}
        if os.environ.get('BETTERHORSES_DEFAULTS'):
            fixtures['defaults'] = yaml.safe_load(
                Path(os.environ['BETTERHORSES_DEFAULTS']).read_text())
        with tempfile.TemporaryDirectory(prefix='betterhorses-startup-') as temp:
            base = Path(temp)
            extras = base / 'extras'
            extras.mkdir()
            shutil.copy2(JAVA / 'patches/betterhorses-horsemanship.json', extras)
            script = (JAVA / 'prepare-paper-plugins.sh').read_text()
            block = script[script.index('config=/data/plugins/BetterHorses/config.yml'):
                           script.index('# Keep mechanic settings')]
            (extras / 'test.sh').write_text('#!/bin/sh\nset -eu\n' + block)
            for name, config in fixtures.items():
                folder = base / name / 'plugins/BetterHorses'
                folder.mkdir(parents=True)
                if config is not None:
                    (folder / 'config.yml').write_text(yaml.safe_dump(config))
                (folder / 'data-sentinel').write_bytes(b'keep horse data\n')
            invalid = base / 'empty/plugins/BetterHorses'
            invalid.mkdir(parents=True)
            (invalid / 'config.yml').touch()
            subprocess.run([
                'docker', 'run', '--rm', '--network', 'none', '--entrypoint', 'sh',
                '-v', f'{base}:/checks', '-v', f'{extras}:/extras:ro', IMAGE, '-ec',
                'for name in ' + ' '.join(fixtures) + '; do '
                'ln -s /checks/$name/plugins /data/plugins; '
                'sh /extras/test.sh; cp /data/plugins/BetterHorses/config.yml /checks/$name-first.yml; '
                'sh /extras/test.sh; sh /extras/test.sh; '
                'cmp /checks/$name-first.yml /data/plugins/BetterHorses/config.yml; '
                'rm /data/plugins; done; '
                'ln -s /checks/empty/plugins /data/plugins; '
                'if sh /extras/test.sh; then echo "Empty config was accepted" >&2; exit 1; fi; '
                'test ! -s /data/plugins/BetterHorses/config.yml',
            ], check=True, timeout=180)
            for name, config in fixtures.items():
                with self.subTest(name=name):
                    expected = copy.deepcopy(minimal if config is None else config)
                    expected.setdefault('horse-growth-settings', {})['time-until-adult'] = 60
                    expected['settings']['breeding-cooldown'] = 21600
                    expected['settings']['male-ignore-cooldown'] = True
                    expected['settings']['mounted-damage-boost']['enabled'] = False
                    folder = base / name / 'plugins/BetterHorses'
                    actual = yaml.safe_load((folder / 'config.yml').read_text())
                    self.assertEqual(expected, actual)
                    self.assertIs(actual['settings']['male-ignore-cooldown'], True)
                    self.assertIs(actual['settings']['mounted-damage-boost']['enabled'], False)
                    self.assertEqual(b'keep horse data\n', (folder / 'data-sentinel').read_bytes())


if __name__ == '__main__':
    unittest.main()
