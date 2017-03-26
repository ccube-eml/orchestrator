import unittest
import os

from click.testing import CliRunner

from orchestrator import __main__


CONFIGURATION_FILE_PATH = '../openstack-configuration.yml'


DOCKER_PATH = '/usr/local/bin'


class OpenstackCloudProviderTest(unittest.TestCase):
    def setUp(self):
        os.environ['PATH'] += os.pathsep + DOCKER_PATH

        self.runner = CliRunner()

    def tearDown(self):
        pass

    def test_create(self):
        result = self.runner.invoke(
            __main__.cli,
            [
                'node', 'create',
                '--number', '1',
                '--provider', 'openstack',
                '--configuration', os.path.join(CONFIGURATION_FILE_PATH),
            ],
            catch_exceptions=False,
        )
        print(result.output)

    def test_destroy(self):
        result = self.runner.invoke(
            __main__.cli,
            [
                'node', 'destroy',
                '--provider', 'openstack',
                '--configuration', os.path.join(CONFIGURATION_FILE_PATH),
                'ccube-',
            ],
            catch_exceptions=False,
        )
        print(result.output)
