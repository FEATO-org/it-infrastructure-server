"""Offline startup tests with the official JAR and mc-image-helper's Jackson libraries.

VALHALLA_JAR=/path/ValhallaMMO_1.10.3.jar MC_HELPER_LIB=/path/helper/lib python3 script/test_valhalla_salvage.py
No server, player profiles or production volumes are used.
"""
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'minecraft/java/startup/ValhallaSalvage.java'
FILES = ['grid_recipes.json', 'grid_recipes_1_21_9+.json', 'grid_recipes_26_1+.json', 'grid_recipes_1_21_11+.json']


class SalvageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.jar = Path(os.environ['VALHALLA_JAR']).resolve()
        cls.libs = str(Path(os.environ['MC_HELPER_LIB']).resolve()) + '/*'
        assert hashlib.sha256(cls.jar.read_bytes()).hexdigest() == 'a3e94b75cf3d050769bba63dcf1a10df1db0b286c28cc2e11a2ff85acba403fc'
        with zipfile.ZipFile(cls.jar) as jar:
            cls.defaults = {f: json.loads(jar.read('recipes/' + f)) for f in FILES}
        cls.build = tempfile.TemporaryDirectory(prefix='salvage-classes-')
        subprocess.run(['javac', '-cp', cls.libs, '-d', cls.build.name, str(SOURCE)], check=True)
        cls.cp = cls.build.name + ':' + cls.libs
        cls.official = next(r for r in cls.defaults[FILES[0]] if r['name'] == 'salvage_diamond_helmet')
        cls.craft = next(r for r in cls.defaults[FILES[0]] if not r['name'].startswith('salvage_'))

    @classmethod
    def tearDownClass(cls):
        cls.build.cleanup()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='salvage-test-')
        self.addCleanup(self.temp.cleanup)
        self.plugins = Path(self.temp.name) / 'plugins'
        self.folder = self.plugins / 'ValhallaMMO/recipes'
        self.folder.mkdir(parents=True)
        shutil.copyfile(self.jar, self.plugins / 'ValhallaMMO_1.10.3.jar')
        for file in FILES:
            self.write([], file)
        self.sentinel = self.plugins / 'ValhallaMMO/profile-sentinel'
        self.sentinel.write_bytes(b'keep profile data')

    def write(self, recipes, file=FILES[0]):
        path = self.folder / file
        path.write_text(json.dumps(recipes, ensure_ascii=False))
        return path

    def run_patch(self, success=True):
        result = subprocess.run(['java', '-cp', self.cp, 'ValhallaSalvage', str(self.plugins)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0 if success else 1, result.stdout + result.stderr)
        self.assertEqual(self.sentinel.read_bytes(), b'keep profile data')
        return result

    def test_only_official_salvage_and_unknown_fields(self):
        salvage = copy.deepcopy(self.official)
        salvage['unknown'] = {'nested': [1, False, '維持'], 'large': 123456789012345678901234567890}
        salvage['modifiers'].append({'MOD_TYPE': 'custom', 'DATA': {'value': 37}})
        records = [salvage, self.craft]
        path = self.write(records)
        result = self.run_patch()
        expected = copy.deepcopy(records)
        expected[0]['requireValhallaTools'] = False
        self.assertEqual(json.loads(path.read_text()), expected)
        self.assertIn('inspected=1 changed=1 unchanged=0 skipped=0', result.stdout)

    def test_similar_custom_name(self):
        custom = copy.deepcopy(self.official)
        custom['name'] += '_custom'
        path = self.write([custom])
        before = path.read_bytes()
        result = self.run_patch()
        self.assertEqual(path.read_bytes(), before)
        self.assertIn('unrecognized-identity-review-required', result.stdout)

    def test_same_name_different_identity(self):
        for change in ['key', 'choice']:
            with self.subTest(change=change):
                custom = copy.deepcopy(self.official)
                if change == 'key':
                    custom['shapedKey']['namespace'] = 'feato'
                else:
                    custom['items']['4']['option']['CHOICE'] = 'custom.ExactChoice'
                path = self.write([custom])
                before = path.read_bytes()
                self.run_patch()
                self.assertEqual(path.read_bytes(), before)

    def test_false_and_repeated_execution_do_not_write(self):
        path = self.write([self.official])
        self.run_patch()
        before, mtime = path.read_bytes(), path.stat().st_mtime_ns
        for _ in range(3):
            result = self.run_patch()
            self.assertIn('inspected=1 changed=0 unchanged=1', result.stdout)
            self.assertEqual((path.read_bytes(), path.stat().st_mtime_ns), (before, mtime))

    def test_invalid_json_does_not_change_any_file(self):
        path = self.write([self.official])
        bad = self.folder / FILES[2]
        for value in ['{broken', 'null', '{}', '[{"name":"x","name":"y"}]', '[] []', '[{"name":"x"},{"name":"x"}]']:
            with self.subTest(value=value):
                bad.write_text(value)
                before = {p: p.read_bytes() for p in self.folder.iterdir()}
                self.run_patch(False)
                self.assertEqual({p: p.read_bytes() for p in self.folder.iterdir()}, before)
                self.assertFalse(list(self.folder.glob('.salvage-*')))

    def test_missing_flag_fails_safely(self):
        for value in [None, 'true', 1]:
            record = copy.deepcopy(self.official)
            record['requireValhallaTools'] = value
            path = self.write([record])
            before = path.read_bytes()
            self.run_patch(False)
            self.assertEqual(path.read_bytes(), before)

    def test_fresh_seed_full_official_recipes(self):
        for p in self.folder.iterdir():
            p.unlink()
        self.folder.rmdir()
        self.run_patch()
        total = 0
        for file in FILES[:3]:
            expected = copy.deepcopy(self.defaults[file])
            for r in expected:
                if r['name'].startswith('salvage_'):
                    total += 1
                    r['requireValhallaTools'] = False
            self.assertEqual(json.loads((self.folder / file).read_text()), expected)
        self.assertEqual(total, 86)
        self.assertFalse((self.folder / FILES[3]).exists())
        snapshots = {p: p.read_bytes() for p in self.folder.iterdir()}
        self.run_patch()
        self.assertEqual({p: p.read_bytes() for p in self.folder.iterdir()}, snapshots)

    def test_empty_existing_files_do_not_recreate_deleted_recipes(self):
        self.run_patch()
        for file in FILES:
            self.assertEqual((self.folder / file).read_text(), '[]')

    def test_merged_version_recipes_in_base_and_legacy_file(self):
        recipes = [r for file in FILES[:3] for r in self.defaults[file] if r['name'].startswith('salvage_')]
        path = self.write(recipes)
        self.write(self.defaults[FILES[3]], FILES[3])
        self.run_patch()
        self.assertEqual(sum(not r['requireValhallaTools'] for r in json.loads(path.read_text())), 86)
        self.assertTrue(all(not r['requireValhallaTools'] for r in json.loads((self.folder / FILES[3]).read_text()) if r['name'].startswith('salvage_')))

    def test_runtime_item_serialization_preserved(self):
        record = copy.deepcopy(self.official)
        record['items']['4']['exactIngredient'] = 'runtime-reencoded-item'
        path = self.write([record])
        self.run_patch()
        actual = json.loads(path.read_text())[0]
        record['requireValhallaTools'] = False
        self.assertEqual(actual, record)

    def test_file_mode_preserved(self):
        path = self.write([self.official])
        path.chmod(0o640)
        self.run_patch()
        self.assertEqual(path.stat().st_mode & 0o777, 0o640)

    def test_unreviewed_jar_or_updater_refused(self):
        updater = self.plugins / 'update'
        updater.mkdir()
        staged = updater / 'ValhallaMMO_new.jar'
        staged.write_bytes(b'new jar')
        self.run_patch(False)
        staged.unlink()
        (self.plugins / 'ValhallaMMO_1.10.3.jar').write_bytes(b'unknown jar')
        self.run_patch(False)
        self.assertEqual((self.folder / FILES[0]).read_text(), '[]')

    def test_symlink_refused(self):
        path = self.folder / FILES[0]
        path.unlink()
        target = Path(self.temp.name) / 'target.json'
        target.write_text(json.dumps([self.official]))
        path.symlink_to(target)
        before = target.read_bytes()
        self.run_patch(False)
        self.assertEqual(target.read_bytes(), before)

    def test_production_source_launcher_and_version_guard(self):
        wrapper = (ROOT / 'minecraft/java/startup/valhalla-salvage.sh').read_text()
        wrapper = wrapper.replace('/usr/share/mc-image-helper/lib/*', self.libs).replace('/data/plugins', str(self.plugins))
        local = Path(self.temp.name) / 'startup'
        local.mkdir()
        shutil.copyfile(SOURCE, local / SOURCE.name)
        script = local / 'valhalla-salvage.sh'
        script.write_text(wrapper)
        path = self.write([self.official])
        result = subprocess.run(['sh', str(script)], env={**os.environ, 'VERSION': '26.2'}, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(json.loads(path.read_text())[0]['requireValhallaTools'])
        before = path.read_bytes()
        result = subprocess.run(['sh', str(script)], env={**os.environ, 'VERSION': '27.1'}, capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(path.read_bytes(), before)
        prepare = (ROOT / 'minecraft/java/prepare-paper-plugins.sh').read_text()
        self.assertIn('sh /extras/startup/valhalla-salvage.sh', prepare)
        self.assertIn('minecraft/java/startup:/extras/startup:ro', (ROOT / 'deploys/app/compose.yml').read_text())

    def test_decimal_precision_preserved(self):
        path = self.write([self.official])
        path.write_text(path.read_text().replace('"requireValhallaTools": true', '"precise": 0.123456789012345678901234567890, "requireValhallaTools": true'))
        self.run_patch()
        import decimal
        self.assertEqual(json.loads(path.read_text(), parse_float=decimal.Decimal)[0]['precise'], decimal.Decimal('0.123456789012345678901234567890'))


if __name__ == '__main__':
    unittest.main()
