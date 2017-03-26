from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver

from orchestrator.provider_drivers.cloud_provider_driver import CloudProviderDriver


class OpenStackCloudProviderDriver(CloudProviderDriver):
    """
    Defines an OpenStack driver.
    """

    def __init__(
            self,
            configuration,
            logger,
    ):
        super().__init__(configuration, logger)

        # Retrieves the provider data.
        cloud_driver = self._create_cloud_driver()
        self._node_image = cloud_driver.get_image(configuration.get('openstack_image_id'))
        self._node_size = [x for x in cloud_driver.list_sizes() if x.name == configuration.get('openstack_instance_type')][0]

    def _create_cloud_driver(self):
        """
        Creates a cloud cloud driver.

        :return: the cloud driver
        :rtype: object
        """
        cls = get_driver(Provider.OPENSTACK)
        return cls(
            self._configuration.get('openstack_username'),
            self._configuration.get('openstack_password'),
            ex_force_auth_url=self._configuration.get('openstack_auth_url'),
            ex_force_auth_version='2.0_password',
            ex_force_service_region=self._configuration.get('openstack_region'),
            ex_tenant_name=self._configuration.get('openstack_tenant'),
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
            ex_keyname=self._configuration.get('openstack_keypair_name'),
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
