import base64
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ScraperSelectionTest(unittest.TestCase):
    def run_deploy(self, nodes, selected=None, existing_config=None, node_list_fails=False):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            docker = path / 'docker'
            docker.write_text('''#!/usr/bin/env bash
set -eu
case "$1 $2" in
  "info --format") echo true ;;
  "node ls")
    [[ $# -eq 6 && "$3" == --filter && "$4" == node.label=minecraft-data=true && "$5" == --format && "$6" == '{{.ID}}' ]] || exit 2
    [[ "${TEST_NODE_LIST_FAIL:-}" != 1 ]] || exit 1
    printf '%s' "${TEST_NODES}" ;;

  "config inspect")
    [[ -n "${TEST_CONFIG_B64:-}" ]] || exit 1
    if [[ "${3:-}" == --format ]]; then
      case "$4" in
        *Templating*) printf '%s\n' golang ;;
        *Data*) printf '"%s"\n' "$TEST_CONFIG_B64" ;;
        *) exit 2 ;;
      esac
    fi ;;

  "config create") [[ "$3" == --template-driver && "$4" == golang ]] ;;
  "network inspect"|"secret inspect") exit 0 ;;
  "compose --file"|"stack config"|"stack services") exit 0 ;;
  "stack deploy") printf '%s\\n' "$FORGE_JVM_SCRAPE_NODE_ID" >> "$TEST_TRACE" ;;
  *) exit 2 ;;
esac
''')
            docker.chmod(0o755)
            env = os.environ.copy()
            env.update({name: 'dummy' for name in (
                'DISCORD_TOKEN', 'GUILD_IDS', 'APP_MODE', 'NOTIFY_CHANNEL_ID',
                'NOTIFY_WEBHOOK_URL', 'ERROR_WEBHOOK_URL', 'LOKI_USER_ID',
                'PROM_USER_ID', 'GRAFANA_API_KEY', 'TLS_FULLCHAIN_SECRET',
                'TLS_PRIVATE_KEY_SECRET', 'CONFIG_VERSION')})
            env.update(PATH=str(path) + os.pathsep + env['PATH'], TEST_NODES=nodes,
                       TEST_TRACE=str(path / 'trace'), ENV_FILE=str(path / 'missing'),
                       TLS_STATE_FILE=str(path / 'missing'))
            if existing_config is not None:
                env['TEST_CONFIG_B64'] = base64.b64encode(existing_config).decode()
            else:
                env.pop('TEST_CONFIG_B64', None)
            env['TEST_NODE_LIST_FAIL'] = '1' if node_list_fails else '0'
            env.pop('FORGE_JVM_SCRAPE_NODE_ID', None)
            if selected is not None:
                env['FORGE_JVM_SCRAPE_NODE_ID'] = selected
            result = subprocess.run(['bash', str(ROOT / 'script/deploy_swarm.sh')],
                                    env=env, text=True, capture_output=True)
            trace = (path / 'trace').read_text().splitlines() if (path / 'trace').exists() else []
            return result, trace

    def test_single_node_is_selected(self):
        result, trace = self.run_deploy('node-a\n')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(trace, ['node-a'] * 3)

    def test_multiple_nodes_require_a_selection(self):
        result, trace = self.run_deploy('node-a\nnode-b\n')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(trace, [])

    def test_explicit_node_and_disabled(self):
        for selected in ('node-b', 'disabled'):
            result, trace = self.run_deploy('node-a\nnode-b\n', selected)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(trace, [selected] * 3)

    def test_existing_template_is_reused_only_when_contents_match(self):
        contents = (ROOT / 'fluentbit/forge-jvm.conf').read_bytes()
        result, trace = self.run_deploy('node-a\n', existing_config=contents)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(trace, ['node-a'] * 3)
        result, trace = self.run_deploy('node-a\n', existing_config=b'different')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(trace, [])

    def test_node_list_failure_reports_the_actual_error(self):
        result, trace = self.run_deploy('', node_list_fails=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Failed to list Swarm nodes', result.stderr)
        self.assertNotIn('No node has minecraft-data=true', result.stderr)
        self.assertEqual(trace, [])

    def test_invalid_or_missing_nodes_fail_closed(self):
        for nodes, selected in (('', None), ('node-a\n', 'node-b')):
            result, trace = self.run_deploy(nodes, selected)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(trace, [])


if __name__ == '__main__':
    unittest.main()
