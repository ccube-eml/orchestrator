from abc import ABCMeta, abstractmethod
import time
from threading import Thread

from orchestrator import utils
from orchestrator import docker_utils


SSH_PORT = 22


class ProviderDriver(object):
    """
    Defines an interface for providers.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(
            self,
            configuration,
            logger,
    ):
        """
        Initializes the driver.

        :param configuration: the configuration dictionary for the provider
        :type configuration: dict[str, str]
        """
        self._configuration = configuration
        self._logger = logger

    def get_ssh_username(self, node_name):
        return self._configuration.get('ssh_username')

    def get_ssh_private_key_file(self, node_name):
        return self._configuration.get('ssh_private_key_file')

    def create_nodes(
            self,
            number,
            name_prefix,
            name_length,
    ):
        """
        Creates a bunch of nodes.

        :param number: the number of nodes to create
        :type number: int

        :param name_prefix: the node name prefix
        :type name_prefix: str

        :param name_length: the node name length
        :type name_length: int

        :return: a dictionary containing the results of creation of each node
        :rtype: dict
        """

        output = {}

        # Defines the thread function.
        def launch_thread(node_name):
            # Records the start time.
            creation_start_time = time.time()

            # Creates the node and waits for it running.
            self._logger.info('{}: contacting provider for node creation'.format(node_name))
            ip = self._create_node(node_name)
            self._logger.info('{}: node running, waiting for SSH port'.format(node_name))

            # Waits until the SSH interface is ready.
            utils.wait_until_ssh_ready(
                hostname=ip,
                ssh_port=SSH_PORT,
                ssh_username=self.get_ssh_username(node_name),
                ssh_private_key_file=self.get_ssh_private_key_file(node_name),
            )
            self._logger.info('{}: SSH port ready'.format(node_name))

            # Records the finish time.
            creation_finish_time = time.time()

            # Computes the total time for creation.
            creation_time = int((creation_finish_time - creation_start_time) * 1000)
            self._logger.info('{}: node created in {} ms'.format(node_name, creation_time))

            # Provisions the node with Docker.
            provision_start_time = time.time()
            self._logger.info('{}: provisioning node'.format(node_name))
            self._provision_node(node_name, ip)
            self._logger.info('{}: provision finished'.format(node_name))
            provision_finish_time = time.time()
            provision_time = int((provision_finish_time - provision_start_time) * 1000)
            self._logger.info('{}: provisioned in {} ms'.format(node_name, provision_time))

            # Stores the output.
            output[node_name] = {
                'ip': ip,
                'creation_time': creation_time,
                'provision_time': provision_time,
            }

        # Prepares the threads.
        threads = []
        digits = len(str(number - 1))
        common_name = utils.generate_random_string(name_length)
        for machine_index in [str(i).zfill(digits) for i in range(number)]:
            # Generates the name, including the prefix and suffix.
            name = self._generate_node_name(name_prefix, common_name, machine_index)

            threads.append(Thread(target=launch_thread, args=[name]))

        # Launches the threads.
        for thread in threads:
            time.sleep(1)
            thread.start()

        # Waits for the threads.
        for thread in threads:
            thread.join()

        # Returns the output.
        return output

    @abstractmethod
    def _create_node(
            self,
            name,
    ):
        """
        Creates a single node.

        :param name: the name of the node
        :type name: str
        """
        pass

    def _provision_node(
            self,
            name,
            hostname,
    ):
        """
        Provisions a node with Docker using SSH.
        """
        docker_utils.install_docker(
            hostname=hostname,
            ssh_port=SSH_PORT,
            ssh_username=self.get_ssh_username(name),
            ssh_private_key_file=self.get_ssh_private_key_file(name),
            executor=name,
            logger=self._logger,
        )

    @abstractmethod
    def destroy_nodes(
            self,
            name,
    ):
        """
        Destroys the nodes having the provided prefix name.

        :param name: the prefix of the name
        :type name: str
        """
        pass

    def clean_node(
            self,
            name,
    ):
        """
        Cleans the contents of a node.

        :param name: the node name
        :type name: str
        """
        # Gets the node IP address.
        ip = self.get_node_ip(name)

        # Deletes the images.
        docker_utils.clean(
            hostname=ip,
            ssh_port=SSH_PORT,
            ssh_username=self.get_ssh_username(name),
            ssh_private_key_file=self.get_ssh_private_key_file(name),
            executor=name,
            logger=self._logger,
        )

    @abstractmethod
    def list(
            self,
            name,
    ):
        """
        Retrieves the list of nodes starting the given name.

        :param name: the prefix of the name
        :type name: str
        """
        pass

    @abstractmethod
    def get_node_ip(
            self,
            name,
    ):
        """
        Retrieves the IP address of the node with the given name.

        :param name: the name of the node
        :type name: str
        """
        pass

    def init_cluster(
            self,
            node_name,
    ):
        """
        Initializes a cluster setting a node as the manager.

        :param node_name: the name of the node to set as manager
        :type node_name: str
        """
        # Gets the node IP address.
        ip = self.get_node_ip(node_name)

        # Initializes the swarm.
        docker_utils.swarm_init(
            hostname=ip,
            ssh_port=SSH_PORT,
            ssh_username=self.get_ssh_username(node_name),
            ssh_private_key_file=self.get_ssh_private_key_file(node_name),
            executor=node_name,
            logger=self._logger,
        )

    def get_cluster_token(
            self,
            manager_name,
            role,
    ):
        """
        Gets the cluster node for the given role (manager or worker).

        :param manager_name: the name of manager node
        :type manager_name: str

        :param role: the role (manager or worker)
        :type role: str
        """
        # Gets the node IP address.
        ip = self.get_node_ip(manager_name)

        # Gets the token.
        token = docker_utils.swarm_token(
            role=role,
            hostname=ip,
            ssh_port=SSH_PORT,
            ssh_username=self.get_ssh_username(manager_name),
            ssh_private_key_file=self.get_ssh_private_key_file(manager_name),
            executor=manager_name,
            logger=self._logger,
        )

        return token

    def join_cluster(
            self,
            nodes_names,
            token,
            manager_hostname,
    ):
        """
        Let a node join a cluster.

        :param nodes_names: the list of nodes to let join
        :type nodes_names: list[str]

        :param token: the token to use to join, as a worker or manager
        :type token: str

        :param manager_hostname: the hostname of the manager
        :type manager_hostname: str
        """
        for node_name in nodes_names:
            # Gets the node IP address.
            ip = self.get_node_ip(node_name)

            # Gets the token.
            token = docker_utils.swarm_join(
                token=token,
                manager_hostname=manager_hostname,
                hostname=ip,
                ssh_port=SSH_PORT,
                ssh_username=self.get_ssh_username(node_name),
                ssh_private_key_file=self.get_ssh_private_key_file(node_name),
                executor=node_name,
                logger=self._logger,
            )

    def leave_cluster(
            self,
            nodes_names,
    ):
        """
        Let a node leave a cluster.

        :param nodes_names: the list of nodes to let join
        :type nodes_names: list[str]
        """
        for node_name in nodes_names:
            # Gets the node IP address.
            ip = self.get_node_ip(node_name)

            # Gets the token.
            docker_utils.swarm_leave(
                hostname=ip,
                ssh_port=SSH_PORT,
                ssh_username=self.get_ssh_username(node_name),
                ssh_private_key_file=self.get_ssh_private_key_file(node_name),
                executor=node_name,
                logger=self._logger,
            )

    def create_service(
            self,
            service_name,
            replicas,
            image,
            command,
            extra,
            manager_name,
    ):
        """
        Creates a service in the cluster and waits until all the replicas are running.

        :param service_name: the name of the service
        :type service_name: str

        :param replicas: the number of replicas
        :type replicas: int

        :param image: the name of the image
        :type image: str

        :param command: the command to execute on each reaplica
        :type command: str

        :param extra: an extra string for service parameters
        :type extra: str

        :param manager_name: the name of the manager
        :type manager_name: str
        """
        # Gets the node IP address.
        ip = self.get_node_ip(manager_name)

        ssh_username = self.get_ssh_username(manager_name)
        ssh_private_key_file = self.get_ssh_private_key_file(manager_name)

        # Creates the service.
        docker_utils.service_create(
            name=service_name,
            replicas=replicas,
            image=image,
            command=command,
            extra=extra,
            hostname=ip,
            ssh_port=SSH_PORT,
            ssh_username=ssh_username,
            ssh_private_key_file=ssh_private_key_file,
            executor=manager_name,
            logger=self._logger,
        )

        i = 0

        # Waits until all the replicas are running.
        while True:
            count = docker_utils.service_count_running(
                name=service_name,
                hostname=ip,
                ssh_port=SSH_PORT,
                ssh_username=ssh_username,
                ssh_private_key_file=ssh_private_key_file,
                executor=manager_name,
                logger=self._logger,
            )
            if int(count) == int(replicas):
                break
            time.sleep(1)

    def destroy_service(
            self,
            service_name,
            manager_name,
    ):
        """
        Creates a service in the cluster and waits until all the replicas are running.

        :param service_name: the name of the service
        :type service_name: str

        :param manager_name: the name of the manager
        :type manager_name: str
        """
        # Gets the node IP address.
        ip = self.get_node_ip(manager_name)

        ssh_username = self.get_ssh_username(manager_name)
        ssh_private_key_file = self.get_ssh_private_key_file(manager_name)

        # Creates the service.
        docker_utils.service_destroy(
            name=service_name,
            hostname=ip,
            ssh_port=SSH_PORT,
            ssh_username=ssh_username,
            ssh_private_key_file=ssh_private_key_file,
            executor=manager_name,
            logger=self._logger,
        )

        # Waits until all the replicas are not running anymore.
        while True:
            count = docker_utils.service_count_running(
                name=service_name,
                hostname=ip,
                ssh_port=SSH_PORT,
                ssh_username=ssh_username,
                ssh_private_key_file=ssh_private_key_file,
                executor=manager_name,
                logger=self._logger,
            )
            if count == 0:
                break
            time.sleep(1)

    def _generate_node_name(
            self,
            prefix,
            middle,
            suffix,
    ):
        """
        Generates a random name for the node.

        :param prefix: the prefix for the name
        :type prefix: str

        :param middle: the middle part
        :type middle: str

        :param suffix: the suffix for the name
        :type suffix: str

        :return: the generated name
        :rtype: str
        """
        name = ''
        if prefix:
            name += prefix + '-'
        name += middle
        if suffix:
            name += '-' + suffix

        return name
