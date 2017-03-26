from abc import ABCMeta, abstractmethod

from orchestrator.provider_drivers.provider_driver import ProviderDriver
from orchestrator import utils


DOCKER_MACHINE_CREATE_NODE = 'docker-machine create --driver virtualbox {name_}'
DOCKER_MACHINE_REMOVE_NODE = 'docker-machine rm --force {name_}'
DOCKER_MACHINE_LIST_NODES = 'docker-machine ls --quiet --filter \'name={name_}*\''
DOCKER_MACHINE_IP_NODE = 'docker-machine ip {name_}'
DOCKER_MACHINE_SSH_USERNAME_NODE = 'docker-machine inspect --format=\'{{{{.Driver.SSHUser}}}}\' {name_}'
DOCKER_MACHINE_SSH_PRIVATE_KEY_FILE_NODE = 'docker-machine inspect --format=\'{{{{.Driver.SSHKeyPath}}}}\' {name_}'


class VirtualboxProviderDriver(ProviderDriver):
    """
    Defines a driver for virtualbox.
    """

    __metaclass__ = ABCMeta

    def __init__(
            self,
            logger,
    ):
        super().__init__(None, logger)

    def get_ssh_username(self, node_name):
        stdout, return_code = utils.execute_command(
            command=DOCKER_MACHINE_SSH_USERNAME_NODE.format(
                name_=node_name,
            ),
            working_directory=None,
            environment_variables=None,
            executor=node_name,
            logger=self._logger,
        )
        return stdout

    def get_ssh_private_key_file(self, node_name):
        stdout, return_code = utils.execute_command(
            command=DOCKER_MACHINE_SSH_PRIVATE_KEY_FILE_NODE.format(
                name_=node_name,
            ),
            working_directory=None,
            environment_variables=None,
            executor=node_name,
            logger=self._logger,
        )
        return stdout

    def _create_node(
            self,
            name,
    ):
        utils.execute_command(
            command=DOCKER_MACHINE_CREATE_NODE.format(
                name_=name,
            ),
            working_directory=None,
            environment_variables=None,
            executor=name,
            logger=self._logger,
        )

        return self.get_node_ip(name)

    def _provision_node(self, name, hostname):
        pass

    def destroy_nodes(
            self,
            name,
    ):
        super().destroy_nodes(name)

        nodes = self._get_nodes(name)
        for node in nodes:
            utils.execute_command(
                command=DOCKER_MACHINE_REMOVE_NODE.format(
                    name_=node,
                ),
                working_directory=None,
                environment_variables=None,
                executor=name,
                logger=self._logger,
            )

    def get_node_ip(
            self,
            name,
    ):
        stdout, return_code = utils.execute_command(
            command=DOCKER_MACHINE_IP_NODE.format(
                name_=name,
            ),
            working_directory=None,
            environment_variables=None,
            executor=name,
            logger=self._logger,
        )

        return stdout

    def list(self, name):
        super().list(name)
        return self._get_nodes(name)

    def _get_nodes(
            self,
            name_prefix,
    ):
        """
        Retrieves the list of nodes starting with a given prefix.

        :param name_prefix: the prefix of the name
        :type name_prefix: str

        :return: the list of node names
        :rtype: list
        """
        stdout, return_code = utils.execute_command(
            command=DOCKER_MACHINE_LIST_NODES.format(
                name_=name_prefix,
            ),
            working_directory=None,
            environment_variables=None,
            executor=name_prefix,
            logger=self._logger,
        )

        return stdout.split() if stdout != '' else []
