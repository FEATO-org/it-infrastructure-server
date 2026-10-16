"""Guard node_exporter_metrics paths against Fluent Bit 5.1.2 rootfs prefixing."""
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / 'fluentbit/fluent-bit.conf'


def node_metrics_paths(config):
    section = next(
        block for block in config.split('[INPUT]')
        if 'Name              node_exporter_metrics' in block
    )
    settings = {}
    for line in section.splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[0].startswith('Path.'):
            settings[parts[0]] = parts[1]
    # Fluent Bit 5.1.2 prefixes procfs/sysfs paths with Path.Rootfs.
    rootfs = settings.get('Path.Rootfs', '/')
    procfs = settings.get('Path.Procfs', '/proc')
    sysfs = settings.get('Path.Sysfs', '/sys')
    return rootfs, rootfs.rstrip('/') + '/' + procfs.lstrip('/'), rootfs.rstrip('/') + '/' + sysfs.lstrip('/')


class FluentBitNodeMetricsPathsTest(unittest.TestCase):
    def test_procfs_and_sysfs_resolve_to_mounted_host_paths(self):
        rootfs, procfs, sysfs = node_metrics_paths(CONFIG.read_text())
        self.assertEqual(rootfs, '/')
        self.assertEqual(procfs, '/host/proc')
        self.assertEqual(sysfs, '/host/sys')

    def test_host_paths_are_not_prefixed_with_host_root(self):
        old_configuration = '''
          Path.Procfs       /host/proc
          Path.Sysfs        /host/sys
          Path.Rootfs       /host/root
        '''
        self.assertEqual(
            node_metrics_paths('[INPUT] Name              node_exporter_metrics' + old_configuration),
            ('/host/root', '/host/root/host/proc', '/host/root/host/sys'),
        )


if __name__ == '__main__':
    unittest.main()
