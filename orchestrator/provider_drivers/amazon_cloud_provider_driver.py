from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver

from orchestrator.provider_drivers.cloud_provider_driver import CloudProviderDriver


class AmazonCloudProviderDriver(CloudProviderDriver):
    """
    Defines an Amazon driver.
    """

    def __init__(
            self,
            configuration,
            logger,
    ):
        super().__init__(configuration, logger)

        # Retrieves the provider data.
        cloud_driver = self._create_cloud_driver()
        self._node_image = [x for x in cloud_driver.list_images(ex_image_ids=[configuration.get('amazon_ami')])][0]
        self._node_size = [x for x in cloud_driver.list_sizes() if x.id == configuration.get('amazon_instance_type')][0]
        self._node_subnet = [x for x in cloud_driver.ex_list_subnets() if x.id == configuration.get('amazon_subnet_id')][0]

    def _create_cloud_driver(self):
        """
        Creates a cloud cloud driver.

        :return: the cloud driver
        :rtype: object
        """
        cls = get_driver(Provider.EC2)
        return cls(
            self._configuration.get('amazon_access_key'),
            self._configuration.get('amazon_secret_key'),
            region=self._configuration.get('amazon_region'),
        )

    def _create_node(
            self,
            name,
    ):
        super()._create_node(name)

        # Invokes the node creation.
        cloud_driver = self._create_cloud_driver()
        node = cloud_driver.create_node(
            name=name,
            image=self._node_image,
            size=self._node_size,
            ex_subnet=self._node_subnet,
            ex_keyname=self._configuration.get('amazon_keypair_name'),
            ex_security_group_ids=[self._configuration.get('amazon_security_group_id')],
        )

        # Waits until running.
        while True:
            try:
                ip = cloud_driver.wait_until_running([node])[0][1][0]
                break
            except Exception as e:
                pass

        # Returns the IP address of the node.
        return ip
