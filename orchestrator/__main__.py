import sys
import csv

import click
import logbook

from orchestrator import utils
from orchestrator.provider_drivers.virtualbox_provider_driver import VirtualboxProviderDriver
from orchestrator.provider_drivers.openstack_cloud_provider_driver import OpenStackCloudProviderDriver
from orchestrator.provider_drivers.amazon_cloud_provider_driver import AmazonCloudProviderDriver


NODE_NAME_PREFIX = 'ccube'
NODE_NAME_LENGTH = 8

NODE_CREATE_CSV_FIELDS = [
    'name',
    'ip',
    'creation_time',
    'provision_time',
]

logger = logbook.Logger('orchestrator')
logbook.StreamHandler(sys.stderr).push_application()


@click.group()
def cli():
    pass


@cli.group()
def node():
    """
    Groups the commands to allocate nodes on cloud providers.
    """
    pass


@node.command()
@click.option('--number', '-n', 'nodes_number', type=int, default=1)
@click.option('--provider', '-p', 'provider_name', type=click.Choice(['virtualbox', 'openstack', 'amazon']), default='virtualbox')
@click.option('--configuration', '-c', 'configuration_file_path', type=click.Path(exists=True), required=False)
@click.option('--csv', '-C', 'print_csv', is_flag=True)
@click.option('--debug', '-D', 'debug', is_flag=True)
def create(nodes_number, provider_name, configuration_file_path, print_csv, debug):
    """
    Creates the nodes using a specific driver.

    :param nodes_number: the number of nodes to create
    :type nodes_number: int

    :param provider_name: the provider name
    :type provider_name: str

    :param configuration_file_path: the configuration YAML file
    :type configuration_file_path: str

    :param print_csv: enables the print of node names and execution times on the STDOUT
    :type print_csv: bool

    :param debug: activates the debug
    :type debug: bool
    """
    logger.level = logbook.DEBUG if debug else logbook.INFO

    # Retrieves the configuration.
    configuration = get_configuration(configuration_file_path)

    # Recognizes the correct driver.
    driver = get_driver(provider_name, configuration)

    # Creates the node.
    output = driver.create_nodes(
        number=nodes_number,
        name_prefix=NODE_NAME_PREFIX,
        name_length=NODE_NAME_LENGTH,
    )

    # Print the CSV on the STDOUT.
    if print_csv:
        csv_writer = csv.DictWriter(sys.stdout, NODE_CREATE_CSV_FIELDS, quoting=csv.QUOTE_NONNUMERIC, lineterminator='\n')
        csv_writer.writeheader()
        for key, value in output.items():
            csv_writer.writerow({
                'name': key,
                'ip': value['ip'],
                'creation_time': value['creation_time'],
                'provision_time': value['provision_time'],
            })


@node.command()
@click.option('--provider', '-p', 'provider_name', type=click.Choice(['virtualbox', 'openstack', 'amazon']), default='virtualbox')
@click.option('--configuration', '-c', 'configuration_file_path', type=click.Path(exists=True), required=False)
@click.option('--debug', '-D', 'debug', is_flag=True)
@click.argument('node_name', type=str, required=True)
def destroy(node_name, provider_name, configuration_file_path, debug):
    """
    Creates the nodes using a specific driver.

    :param node_name: the name prefix to delete
    :type node_name: str

    :param provider_name: the provider name
    :type provider_name: str

    :param configuration_file_path: the configuration YAML file
    :type configuration_file_path: str

    :param debug: activates the debug
    :type debug: bool
    """
    logger.level = logbook.DEBUG if debug else logbook.INFO

    # Retrieves the configuration file.
    configuration = get_configuration(configuration_file_path)

    # Recognizes the correct driver.
    driver = get_driver(provider_name, configuration)

    # Launches the destroy action.
    output = driver.destroy_nodes(
        name=node_name,
    )


@node.command()
@click.option('--provider', '-p', 'provider_name', type=click.Choice(['virtualbox', 'openstack', 'amazon']), default='virtualbox')
@click.option('--configuration', '-c', 'configuration_file_path', type=click.Path(exists=True), required=False)
@click.option('--debug', '-D', 'debug', is_flag=True)
@click.argument('node_name', type=str, required=True)
def clean(node_name, provider_name, configuration_file_path, debug):
    """
    Cleans the node contents.

    :param node_name: the name of the node to clean
    :type node_name: str

    :param provider_name: the provider name
    :type provider_name: str

    :param configuration_file_path: the configuration YAML file
    :type configuration_file_path: str

    :param debug: activates the debug
    :type debug: bool
    """
    logger.level = logbook.DEBUG if debug else logbook.INFO

    # Retrieves the configuration file.
    configuration = get_configuration(configuration_file_path)

    # Recognizes the correct driver.
    driver = get_driver(provider_name, configuration)

    # Clean the nodes.
    output = driver.clean_node(
        name=node_name,
    )

    print(output)


@node.command()
@click.option('--provider', '-p', 'provider_name', type=click.Choice(['virtualbox', 'openstack', 'amazon']), default='virtualbox')
@click.option('--configuration', '-c', 'configuration_file_path', type=click.Path(exists=True), required=False)
@click.option('--debug', '-D', 'debug', is_flag=True)
@click.argument('node_name', type=str, required=True)
def ip(node_name, provider_name, configuration_file_path, debug):
    """
    Retrieves the node IP address.

    :param node_name: the name of the node
    :type node_name: str

    :param provider_name: the provider name
    :type provider_name: str

    :param configuration_file_path: the configuration YAML file
    :type configuration_file_path: str

    :param debug: activates the debug
    :type debug: bool
    """
    logger.level = logbook.DEBUG if debug else logbook.INFO

    # Retrieves the configuration file.
    configuration = get_configuration(configuration_file_path)

    # Recognizes the correct driver.
    driver = get_driver(provider_name, configuration)

    # Retrieves the IP.
    output = driver.get_node_ip(
        name=node_name,
    )

    print(output)


@node.command()
@click.option('--provider', '-p', 'provider_name', type=click.Choice(['virtualbox', 'openstack', 'amazon']), default='virtualbox')
@click.option('--configuration', '-c', 'configuration_file_path', type=click.Path(exists=True), required=False)
@click.option('--debug', '-D', 'debug', is_flag=True)
@click.argument('node_name', type=str, required=True)
def list(node_name, provider_name, configuration_file_path, debug):
    """
    Retrieves the nodes list.

    :param node_name: the name prefix to delete
    :type node_name: str

    :param provider_name: the provider name
    :type provider_name: str

    :param configuration_file_path: the configuration YAML file
    :type configuration_file_path: str

    :param debug: activates the debug
    :type debug: bool
    """
    logger.level = logbook.DEBUG if debug else logbook.INFO

    # Retrieves the configuration file.
    configuration = get_configuration(configuration_file_path)

    # Recognizes the correct driver.
    driver = get_driver(provider_name, configuration)

    # Retrieves the list.
    output = driver.list(
        name=node_name,
    )

    for node in output:
        print(node)


@cli.group()
def cluster():
    """
    Groups the commands to manage the clusters.
    """
    pass


@cluster.command()
@click.option('--provider', '-p', 'provider_name', type=click.Choice(['virtualbox', 'openstack', 'amazon']), default='virtualbox')
@click.option('--configuration', '-c', 'configuration_file_path', type=click.Path(exists=True), required=False)
@click.option('--debug', '-D', 'debug', is_flag=True)
@click.argument('node_name', type=str, required=True)
def init(node_name, provider_name, configuration_file_path, debug):
    """
    Initializes a cluster making a node as manager.

    :param node_name: the name of the node to initialize the cluster
    :type node_name: str

    :param provider_name: the provider name
    :type provider_name: str

    :param configuration_file_path: the configuration YAML file
    :type configuration_file_path: str

    :param debug: activates the debug
    :type debug: bool
    """
    logger.level = logbook.DEBUG if debug else logbook.INFO

    # Retrieves the configuration file.
    configuration = get_configuration(configuration_file_path)

    # Recognizes the correct driver.
    driver = get_driver(provider_name, configuration)

    # Initializes the cluster.
    driver.init_cluster(
        node_name=node_name,
    )


@cluster.command()
@click.option('--role', '-r', 'role', type=click.Choice(['manager', 'worker']), default='worker')
@click.option('--provider', '-p', 'provider_name', type=click.Choice(['virtualbox', 'openstack', 'amazon']), default='virtualbox')
@click.option('--configuration', '-c', 'configuration_file_path', type=click.Path(exists=True), required=False)
@click.option('--debug', '-D', 'debug', is_flag=True)
@click.argument('manager_name', type=str, required=True)
def token(manager_name, role, provider_name, configuration_file_path, debug):
    """
    Retrieves the token from a manager for the provided role, worker or manager.

    :param manager_name: the name of a manager
    :type manager_name: str

    :param role: the role for the token, worker or manager
    :type role: str

    :param provider_name: the provider name
    :type provider_name: str

    :param configuration_file_path: the configuration YAML file
    :type configuration_file_path: str

    :param debug: activates the debug
    :type debug: bool
    """
    logger.level = logbook.DEBUG if debug else logbook.INFO

    # Retrieves the configuration file.
    configuration = get_configuration(configuration_file_path)

    # Recognizes the correct driver.
    driver = get_driver(provider_name, configuration)

    # Prints the token.
    output_token = driver.get_cluster_token(
        manager_name=manager_name,
        role=role,
    )
    print(output_token)


@cluster.command()
@click.option('--token', '-t', 'token', type=str, required=True)
@click.option('--manager', '-m', 'manager_hostname', type=str, required=True)
@click.option('--provider', '-p', 'provider_name', type=click.Choice(['virtualbox', 'openstack', 'amazon']), default='virtualbox')
@click.option('--configuration', '-c', 'configuration_file_path', type=click.Path(exists=True), required=False)
@click.option('--debug', '-D', 'debug', is_flag=True)
@click.argument('nodes_names', type=str, required=True, nargs=-1)
def join(nodes_names, token, manager_hostname, provider_name, configuration_file_path, debug):
    """
    Lets a node join to a cluster either as a worker or a manager, based on the token provided.

    :param nodes_names: the list of nodes to let join
    :type nodes_names: list[str]

    :param token: the token to use to join, as a worker or manager
    :type token: str

    :param manager_hostname: the hostname of the manager
    :type manager_hostname: str

    :param provider_name: the provider name
    :type provider_name: str

    :param configuration_file_path: the configuration YAML file
    :type configuration_file_path: str

    :param debug: activates the debug
    :type debug: bool
    """
    logger.level = logbook.DEBUG if debug else logbook.INFO

    # Retrieves the configuration file.
    configuration = get_configuration(configuration_file_path)

    # Recognizes the correct driver.
    driver = get_driver(provider_name, configuration)

    # Prints the token.
    driver.join_cluster(
        nodes_names=nodes_names,
        token=token,
        manager_hostname=manager_hostname,
    )


@cli.group()
def service():
    """
    Groups the commands to manage the service.
    """
    pass


@service.command()
@click.option('--image', '-i', 'image', type=str, required=True)
@click.option('--command', '-C', 'command', type=str)
@click.option('--extra', '-e', 'extra', type=str)
@click.option('--replicas', '-r', 'replicas', type=str, default=1)
@click.option('--manager', '-m', 'manager_name', type=str, required=True)
@click.option('--provider', '-p', 'provider_name', type=click.Choice(['virtualbox', 'openstack', 'amazon']), default='virtualbox')
@click.option('--configuration', '-c', 'configuration_file_path', type=click.Path(exists=True), required=False)
@click.option('--debug', '-D', 'debug', is_flag=True)
@click.argument('service_name', type=str, required=True)
def create(service_name, replicas, image, command, extra, manager_name, provider_name, configuration_file_path, debug):
    """
    Creates a service with replicas.

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

    :param manager_name: the name of a manager
    :type manager_name: str

    :param provider_name: the provider name
    :type provider_name: str

    :param configuration_file_path: the configuration YAML file
    :type configuration_file_path: str

    :param debug: activates the debug
    :type debug: bool
    """
    logger.level = logbook.DEBUG if debug else logbook.INFO

    # Retrieves the configuration file.
    configuration = get_configuration(configuration_file_path)

    # Recognizes the correct driver.
    driver = get_driver(provider_name, configuration)

    # Create the service replicas.
    driver.create_service(
        service_name=service_name,
        replicas=replicas,
        image=image,
        command=command,
        extra=extra,
        manager_name=manager_name,
    )


@service.command()
@click.option('--manager', '-m', 'manager_name', type=str, required=True)
@click.option('--provider', '-p', 'provider_name', type=click.Choice(['virtualbox', 'openstack', 'amazon']), default='virtualbox')
@click.option('--configuration', '-c', 'configuration_file_path', type=click.Path(exists=True), required=False)
@click.option('--debug', '-D', 'debug', is_flag=True)
@click.argument('service_name', type=str, required=True)
def destroy(service_name, manager_name, provider_name, configuration_file_path, debug):
    """
    Destroys a service.

    :param service_name: the name of the service
    :type service_name: str

    :param manager_name: the name of a manager
    :type manager_name: str

    :param provider_name: the provider name
    :type provider_name: str

    :param configuration_file_path: the configuration YAML file
    :type configuration_file_path: str

    :param debug: activates the debug
    :type debug: bool
    """
    logger.level = logbook.DEBUG if debug else logbook.INFO

    # Retrieves the configuration file.
    configuration = get_configuration(configuration_file_path)

    # Recognizes the correct driver.
    driver = get_driver(provider_name, configuration)

    # Create the service replicas.
    driver.destroy_service(
        service_name=service_name,
        manager_name=manager_name,
    )


def get_driver(provider_name, configuration):
    if provider_name == 'virtualbox':
        return VirtualboxProviderDriver(logger)
    elif provider_name == 'openstack':
        return OpenStackCloudProviderDriver(configuration, logger)
    elif provider_name == 'amazon':
        return AmazonCloudProviderDriver(configuration, logger)


def get_configuration(configuration_file_path):
    if configuration_file_path:
        return utils.parse_yaml(configuration_file_path)
    else:
        return {}


if __name__ == '__main__':
    cli()
