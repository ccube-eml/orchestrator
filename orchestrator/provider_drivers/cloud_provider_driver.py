from abc import ABCMeta, abstractmethod

from orchestrator.provider_drivers.provider_driver import ProviderDriver


class CloudProviderDriver(ProviderDriver):
    """
    Defines a driver for cloud providers.
    """

    __metaclass__ = ABCMeta

    def __init__(
            self,
            configuration,
            logger,
    ):
        super().__init__(configuration, logger)

    @abstractmethod
    def _create_cloud_driver(self):
        """
        Creates a cloud cloud driver.

        :return: the cloud driver
        :rtype: object
        """
        pass

    @abstractmethod
    def _create_node(
            self,
            name,
    ):
        pass

    def destroy_nodes(
            self,
            name,
    ):
        super().destroy_nodes(name)

        nodes = self._get_nodes(name)
        for node in nodes:
            node.destroy()

    def get_node_ip(
            self,
            name,
    ):
        node = self._get_nodes(name)[0]
        return node.public_ips[0]

    def list(self, name):
        super().list(name)
        nodes = self._get_nodes(name)
        return [node.name for node in nodes]

    def _get_nodes(
            self,
            name_prefix,
    ):
        """
        Retrieves the list of nodes starting with a given prefix.

        :param name_prefix: the prefix of the name
        :type name_prefix: str

        :return: the list of nodes
        :rtype: object
        """
        cloud_driver = self._create_cloud_driver()
        nodes = cloud_driver.list_nodes()
        return [node for node in nodes if node.name.startswith(name_prefix)]
