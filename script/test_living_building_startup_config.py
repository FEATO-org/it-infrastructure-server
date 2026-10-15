"""Exercise production startup patches in disposable Docker data, without starting Paper.

Requires PyYAML, Docker, and a local minecraft-server image (TEST_MINECRAFT_IMAGE).
"""
import copy
import json
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


class LivingBuildingStartupTest(unittest.TestCase):
    def test_restarts_preserve_settings_and_data(self):
        specs = {
            'CraftBook': ('craftbook-mechanisms.yml', 'craftbook-life.json', 'mechanisms.yml'),
            'GSit': ('gsit-config.yml', 'gsit-life.json', 'config.yml'),
            'EasyArmorStands': ('easyarmorstands-config.yml', 'easyarmorstands-life.json', 'config.yml'),
        }
        script = (JAVA / 'prepare-paper-plugins.sh').read_text()
        block = script[script.index('# Keep mechanic settings'):script.index('# Pin the official Spigot')]
        with tempfile.TemporaryDirectory(prefix='living-building-') as temp:
            base = Path(temp)
            extras = base / 'extras'
            extras.mkdir()
            for pattern in ['config-seeds/*', 'patches/*']:
                for source in JAVA.glob(pattern):
                    shutil.copy2(source, extras / source.name)
            (extras / 'test.sh').write_text('#!/bin/sh\nset -eu\n' + block)
            originals = {}
            for case in ['fresh', 'custom', 'minimal']:
                for plugin, (seed, patch, filename) in specs.items():
                    folder = base / case / 'plugins' / plugin
                    folder.mkdir(parents=True)
                    config = yaml.safe_load((JAVA / 'config-seeds' / seed).read_text())
                    if case == 'custom':
                        config['custom'] = {'sentinel': [1, 'keep']}
                        if plugin == 'CraftBook':
                            config['mechanics'] = {
                                'Chairs': {'blocks': ['OAK_STAIRS'], 'custom': 17},
                                'Bridge': {'custom': True},
                                'BetterLeads': {'custom': 'retain', 'mob-repel': True},
                                'HeadDrops': {'drop-rate': 0.99, 'custom': 'retain'},
                            }
                        if plugin == 'GSit':
                            config['Options']['Sit']['SitMaterials'] = ['oak_stairs']
                        if plugin == 'EasyArmorStands':
                            config['editor']['tool']['type'] = 'stick'
                            config['_version']['config'] = 99
                    elif case == 'minimal':
                        config = {'custom': True}
                    if case != 'fresh':
                        (folder / filename).write_text(yaml.safe_dump(config))
                    originals[case, plugin] = copy.deepcopy(config)
                    (folder / 'data-sentinel').write_bytes(b'keep user data\n')
                if case != 'fresh':
                    (base / case / 'plugins/CraftBook/books.txt').write_text('既存の文章を保持。\n')
            subprocess.run([
                'docker', 'run', '--rm', '--network', 'none', '--entrypoint', 'sh',
                '-v', f'{base}:/checks', '-v', f'{extras}:/extras:ro', IMAGE, '-ec',
                'for name in fresh custom minimal; do '
                'ln -s /checks/$name/plugins /data/plugins; '
                'sh /extras/test.sh; cp -r /data/plugins /checks/$name-first; '
                'sh /extras/test.sh; diff -r /checks/$name-first /data/plugins; '
                'rm /data/plugins; done',
            ], check=True, timeout=180)
            for case in ['fresh', 'custom', 'minimal']:
                for plugin, (seed, patch, filename) in specs.items():
                    expected = originals[case, plugin]
                    patches = [patch]
                    if plugin == 'CraftBook':
                        patches.insert(0, 'craftbook-chairs.json')
                    for patch_name in patches:
                        for op in json.loads((JAVA / 'patches' / patch_name).read_text())['ops']:
                            put = op['$put']
                            target = expected
                            for key in put['path'].split('.')[1:]:
                                target = target.setdefault(key, {})
                            target[put['key']] = put['value']
                    folder = base / case / 'plugins' / plugin
                    self.assertEqual(expected, yaml.safe_load((folder / filename).read_text()))
                    self.assertEqual(b'keep user data\n', (folder / 'data-sentinel').read_bytes())
                books = (base / case / 'plugins/CraftBook/books.txt').read_text()
                self.assertEqual(books, (JAVA / 'config-seeds/craftbook-books.txt').read_text()
                                 if case == 'fresh' else '既存の文章を保持。\n')

    def test_permissions_without_contacting_server(self):
        with tempfile.TemporaryDirectory(prefix='living-permissions-') as temp:
            base = Path(temp)
            docker = base / 'docker'
            docker.write_text('#!/bin/sh\nif [ "$1" = ps ]; then echo fixture; '
                              'else printf "%s\\n" "$*" >> "$PERMISSION_LOG"; fi\n')
            docker.chmod(0o755)
            log = base / 'commands'
            run = [
                'docker', 'run', '--rm', '--network', 'none', '--entrypoint', 'bash',
                '-v', f'{base}:/checks', '-v', f'{ROOT}:/repo:ro',
                '-e', 'PATH=/checks:/usr/local/bin:/usr/bin:/bin',
                '-e', 'PERMISSION_LOG=/checks/commands', IMAGE,
                '/repo/script/setup_minecraft_permissions.sh',
            ]
            subprocess.run(run + ['players', 'admins'], check=True, capture_output=True)
            commands = log.read_text().splitlines()
            spark_commands = [c for c in commands if ' permission set spark' in c]
            self.assertCountEqual(spark_commands, [
                'exec fixture rcon-cli lp group players permission set spark.tps true',
                'exec fixture rcon-cli lp group players permission set spark.ping true',
            ])
            allows = ['essentials.balance', 'essentials.pay', 'EconomyShopGUI.shop.feato_shop',
                      'GSit.Sit', 'GSit.Lay', 'GSit.LegsUp', 'GSit.BellyFlop', 'GSit.Spin',
                      'GSit.Crawl', 'craftableinvframes.craft', 'craftableinvframes.place',
                      'craftbook.mech.leads', 'craftbook.mech.signcopy.use',
                      'craftbook.mech.bookshelf.use', 'craftbook.mech.headdrops.kill',
                      'craftbook.mech.headdrops.break']
            denies = ['GSit.SitClick', 'GSit.PlayerSit', 'GSit.Kick.*', 'GSit.ByPass.*',
                      'GSit.Reload', 'craftbook.mech.signcopy.edit',
                      'easyarmorstands.survival', 'easyarmorstands.creative']
            for node in allows:
                self.assertIn(f'exec fixture rcon-cli lp group players permission set {node} true', commands)
            for node in denies:
                self.assertIn(f'exec fixture rcon-cli lp group players permission set {node} false', commands)
                self.assertIn(f'exec fixture rcon-cli lp group admins permission set {node} true', commands)
            self.assertFalse(any('lp group players permission set craftableinvframes.' in c
                                 and not any(n in c for n in ['.craft ', '.place ']) for c in commands))
            for group, node in [
                ('admins', 'essentials.eco'),
                ('mayor', 'feato.mayor'), ('mayor', 'ei.item.mayor_flag'),
                ('mayor', 'slots.admin'),
                ('guard_captain', 'feato.guard_captain'),
                ('guard_captain', 'ei.item.guard_captain_flag'),
                ('town_clerk', 'feato.town_clerk'),
                ('town_clerk', 'essentials.kits.administrative_enforcement_order'),
            ]:
                self.assertIn(f'exec fixture rcon-cli lp group {group} permission set {node} true', commands)
            for group in ['mayor', 'guard_captain', 'town_clerk']:
                self.assertIn(f'exec fixture rcon-cli lp creategroup {group}', commands)
            for group in ['admins', 'mayor', 'town_clerk']:
                self.assertIn(f'exec fixture rcon-cli lp group {group} permission set fancyholograms.admin true', commands)
            self.assertIn('exec fixture rcon-cli lp group mayor meta setprefix 100 &9[村長] ', commands)
            self.assertFalse(any(' parent ' in c for c in commands))
            self.assertEqual(len(commands), len(set(commands)))
            log.unlink()
            subprocess.run(run + ['players', 'admins'], check=True, capture_output=True)
            self.assertEqual(commands, log.read_text().splitlines())
            log.unlink()
            for args in [[], ['players'], ['players', 'admins', 'extra'], ['same', 'same']]:
                with self.subTest(args=args):
                    result = subprocess.run(run + args, capture_output=True)
                    self.assertEqual(2, result.returncode)
                    self.assertFalse(log.exists())


if __name__ == '__main__':
    unittest.main()
