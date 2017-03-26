import unittest
import sys

import logbook

from orchestrator import docker_utils


MANAGER_HOSTNAME = ''
MANAGER_SSH_PRIVATE_KEY_FILE = ''

WORKER_HOSTNAME = ''
WORKER_SSH_PRIVATE_KEY_FILE = ''

SSH_USERNAME = 'docker'
SSH_PORT = 22


logger = logbook.Logger('test')
logbook.StreamHandler(sys.stderr).push_application()


class DockerUtilsTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_execute_command(self):
        stdout, return_code = docker_utils.execute_command(
            'docker info',
            hostname=MANAGER_HOSTNAME,
            ssh_port=SSH_PORT,
            ssh_username=SSH_USERNAME,
            ssh_private_key_file=MANAGER_SSH_PRIVATE_KEY_FILE,
            executor='test',
            logger=logger,
        )

        print(stdout)

    def test_clean(self):
        docker_utils.clean(
            hostname=MANAGER_HOSTNAME,
            ssh_port=SSH_PORT,
            ssh_username=SSH_USERNAME,
            ssh_private_key_file=MANAGER_SSH_PRIVATE_KEY_FILE,
            executor='test',
            logger=logger,
        )

    def test_swarm_init(self):
        docker_utils.swarm_init(
            hostname=MANAGER_HOSTNAME,
            ssh_port=SSH_PORT,
            ssh_username=SSH_USERNAME,
            ssh_private_key_file=MANAGER_SSH_PRIVATE_KEY_FILE,
            executor='test',
            logger=logger,
        )

    def test_swarm_token(self):
        manager_token = docker_utils.swarm_token(
            role='manager',
            hostname=MANAGER_HOSTNAME,
            ssh_port=SSH_PORT,
            ssh_username=SSH_USERNAME,
            ssh_private_key_file=MANAGER_SSH_PRIVATE_KEY_FILE,
            executor='test',
            logger=logger,
        )
        print(manager_token)

        worker_token = docker_utils.swarm_token(
            role='worker',
            hostname=MANAGER_HOSTNAME,
            ssh_port=SSH_PORT,
            ssh_username=SSH_USERNAME,
            ssh_private_key_file=MANAGER_SSH_PRIVATE_KEY_FILE,
            executor='test',
            logger=logger,
        )
        print(worker_token)

    def test_swarm_join(self):
        worker_token = docker_utils.swarm_token(
            role='worker',
            hostname=MANAGER_HOSTNAME,
            ssh_port=SSH_PORT,
            ssh_username=SSH_USERNAME,
            ssh_private_key_file=MANAGER_SSH_PRIVATE_KEY_FILE,
            executor='test',
            logger=logger,
        )

        docker_utils.swarm_join(
            token=worker_token,
            manager_hostname=MANAGER_HOSTNAME,
            hostname=WORKER_HOSTNAME,
            ssh_port=SSH_PORT,
            ssh_username=SSH_USERNAME,
            ssh_private_key_file=WORKER_SSH_PRIVATE_KEY_FILE,
            executor='test',
            logger=logger,
        )

    def test_swarm_leave(self):
        docker_utils.swarm_leave(
            hostname=MANAGER_HOSTNAME,
            ssh_port=SSH_PORT,
            ssh_username=SSH_USERNAME,
            ssh_private_key_file=MANAGER_SSH_PRIVATE_KEY_FILE,
            executor='test',
            logger=logger,
        )

        docker_utils.swarm_leave(
            hostname=WORKER_HOSTNAME,
            ssh_port=SSH_PORT,
            ssh_username=SSH_USERNAME,
            ssh_private_key_file=WORKER_SSH_PRIVATE_KEY_FILE,
            executor='test',
            logger=logger,
        )

    def test_service_create(self):
        docker_utils.service_create(
            name='helloworld',
            replicas='4',
            image='alpine',
            command='ping docker.com',
            hostname=MANAGER_HOSTNAME,
            ssh_port=SSH_PORT,
            ssh_username=SSH_USERNAME,
            ssh_private_key_file=WORKER_SSH_PRIVATE_KEY_FILE,
            executor='test',
            logger=logger,
        )

    def test_service_count_running(self):
        count = docker_utils.service_count_running(
            name='helloworld',
            hostname=MANAGER_HOSTNAME,
            ssh_port=SSH_PORT,
            ssh_username=SSH_USERNAME,
            ssh_private_key_file=WORKER_SSH_PRIVATE_KEY_FILE,
            executor='test',
            logger=logger,
        )
        print(count)

    def test_service_destroy(self):
        docker_utils.service_destroy(
            name='helloworld',
            hostname=MANAGER_HOSTNAME,
            ssh_port=SSH_PORT,
            ssh_username=SSH_USERNAME,
            ssh_private_key_file=WORKER_SSH_PRIVATE_KEY_FILE,
            executor='test',
            logger=logger,
        )
