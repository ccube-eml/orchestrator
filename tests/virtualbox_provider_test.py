import unittest
import os

from click.testing import CliRunner

from orchestrator import __main__


DOCKER_PATH = '/usr/local/bin'


class VirtualboxProviderTest(unittest.TestCase):
    def setUp(self):
        os.environ['PATH'] += os.pathsep + DOCKER_PATH

        self.runner = CliRunner()

    def tearDown(self):
        pass

    def test_node_create(self):
        result = self.runner.invoke(
            __main__.cli,
            [
                'node', 'create',
                '--number', '1',
                '--provider', 'virtualbox',
                '--debug',
            ],
            catch_exceptions=False,
        )
        print(result.output)

    def test_node_destroy(self):
        result = self.runner.invoke(
            __main__.cli,
            [
                'node', 'destroy',
                '--provider', 'virtualbox',
                '--debug',
                'ccube-',
            ],
            catch_exceptions=False,
        )
        print(result.output)

    def test_service_create(self):
        result = self.runner.invoke(
            __main__.cli,
            [
                'service', 'create',
                '--replicas', 1,
                '--image', 'postgres',
                '--extra', '--env POSTGRES_PASSWORD=postgres',
                '--manager', 'ccube-manager1',
                '--provider', 'virtualbox',
                '--debug',
                'postgresql',
            ],
            catch_exceptions=False,
        )
        print(result.output)

    def test_node_clean(self):
        result = self.runner.invoke(
            __main__.cli,
            [
                'node', 'clean',
                '--provider', 'virtualbox',
                '--debug',
                'ccube-manager1',
            ],
            catch_exceptions=False,
        )
        print(result.output)