import copy
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('tls_sync', Path(__file__).parents[1] / 'script/sync_portainer_tls.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class TLSDesiredStateTests(unittest.TestCase):
    def setUp(self):
        self.stack = {
            'Name': 'system', 'Type': 1, 'Status': 1,
            'Env': [{'name': 'TLS_FULLCHAIN_SECRET', 'value': 'old'},
                    {'name': 'GRAFANA_API_KEY', 'value': 'test-only-placeholder'}],
            'GitConfig': {'ReferenceName': 'refs/heads/main', 'TLSSkipVerify': False,
                          'Authentication': {'Username': 'reader', 'Password': 'never-copy',
                                             'AuthorizationType': 0}},
            'AutoUpdate': {'Webhook': 'test-id', 'ForceUpdate': True, 'ForcePullImage': True},
            'Option': {'Prune': False},
        }

    def test_preserves_settings_and_unrelated_environment(self):
        original = copy.deepcopy(self.stack)
        payload = module.tls_payload(self.stack, 'new-chain', 'new-key')
        env = {p['name']: p['value'] for p in payload['Env']}
        self.assertEqual(env, {'TLS_FULLCHAIN_SECRET': 'new-chain',
                              'TLS_PRIVATE_KEY_SECRET': 'new-key',
                              'GRAFANA_API_KEY': 'test-only-placeholder'})
        self.assertEqual(payload['AutoUpdate'], original['AutoUpdate'])
        self.assertEqual(payload['RepositoryReferenceName'], 'refs/heads/main')
        self.assertTrue(payload['RepositoryAuthentication'])
        self.assertEqual(payload['RepositoryUsername'], 'reader')
        self.assertEqual(payload['RepositoryPassword'], '')
        self.assertEqual(self.stack, original)

    def test_refuses_wrong_target_and_inactive_stack(self):
        for key, value in [('Name', 'app'), ('Type', 2), ('Status', 2), ('GitConfig', None)]:
            with self.subTest(key=key):
                stack = dict(self.stack, **{key: value})
                with self.assertRaises(ValueError):
                    module.tls_payload(stack, 'chain', 'key')

    def test_public_git_keeps_authentication_disabled(self):
        self.stack['GitConfig']['Authentication'] = None
        payload = module.tls_payload(self.stack, 'chain', 'key')
        self.assertFalse(payload['RepositoryAuthentication'])


if __name__ == '__main__':
    unittest.main()
