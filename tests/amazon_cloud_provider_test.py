import unittest
import os

from click.testing import CliRunner

from orchestrator import __main__


CONFIGURATION_FILE_PATH = '../amazon-configuration.yml'


DOCKER_PATH = '/usr/local/bin'


class AmazonCloudProviderTest(unittest.TestCase):
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
                '--provider', 'amazon',
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
                '--provider', 'amazon',
                '--configuration', os.path.join(CONFIGURATION_FILE_PATH),
                'ccube-',
            ],
            catch_exceptions=False,
        )
        print(result.output)

    def test_node_ip(self):
        result = self.runner.invoke(
            __main__.cli,
            [
                'node', 'ip',
                '--provider', 'amazon',
                '--configuration', os.path.join(CONFIGURATION_FILE_PATH),
                '--debug',
                'ccube-6h7rc2q2-00',
            ],
            catch_exceptions=False,
        )
        print(result.output)