import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'minecraft/forge/configure-jmx.sh'
AGENT = '-javaagent:/data/monitoring/jmx_prometheus_javaagent-1.7.0.jar=FORGE_JMX_BIND:9404:/forge-jmx/config.yml'


class ConfigureJmxTest(unittest.TestCase):
    def run_case(self, mode='ok', args=None, missing=False):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            for command, body in {
                'getent': '[[ "$TEST_MODE" != dns ]] || exit 1; echo "10.2.0.4 STREAM system_fluent-bit"',
                'ip': '''if [[ "$*" == "-4 route show default" ]]; then
  echo 'default via 10.1.0.1 dev eth0'
elif [[ "$TEST_MODE" == route ]]; then exit 1
elif [[ "$TEST_MODE" == backend ]]; then echo '10.2.0.4 dev eth0 src 10.1.0.8'
else echo '10.2.0.4 dev eth1 src 10.2.0.8'; fi''',
            }.items():
                file = path / command
                file.write_text('#!/usr/bin/env bash\n' + body + '\n')
                file.chmod(0o755)
            argfile = path / 'args'
            if not missing:
                argfile.write_text(args if args is not None else '-Xms1G ' + AGENT + ' -Xmx8G\n')
            env = dict(os.environ, PATH=str(path) + os.pathsep + os.environ['PATH'], JVM_OPTS=AGENT, TEST_MODE=mode)
            result = subprocess.run(['bash', str(SCRIPT), str(argfile)], env=env, text=True, capture_output=True)
            return result, argfile.read_text() if argfile.exists() else None

    def test_monitoring_route_and_flags(self):
        result, args = self.run_case()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('=10.2.0.8:9404:', args)
        self.assertIn('-Xms1G', args)
        self.assertIn('-Xmx8G', args)
        self.assertNotIn('FORGE_JMX_BIND', args)

    def test_failure_disables_only_agent(self):
        for mode in ('dns', 'route', 'backend'):
            with self.subTest(mode=mode):
                result, args = self.run_case(mode)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn('JMX monitoring disabled', result.stderr)
                self.assertNotIn('javaagent', args)
                self.assertEqual(args.split(), ['-Xms1G', '-Xmx8G'])

    def test_missing_and_unexpected_arguments(self):
        result, _ = self.run_case(missing=True)
        self.assertNotEqual(result.returncode, 0)
        result, _ = self.run_case(args='-Xms1G -Xmx8G\n')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('argument missing', result.stderr)
        result, _ = self.run_case(args='-javaagent:unknown=FORGE_JMX_BIND:9404\n')
        self.assertNotEqual(result.returncode, 0)


if __name__ == '__main__':
    unittest.main()
