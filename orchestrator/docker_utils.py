from orchestrator import utils


DOCKER_INSTALL_COMMAND = 'curl -sSL https://get.docker.com/ | sh'
DOCKER_INSTALL_USERMOD_COMMAND = 'sudo usermod -aG docker {ssh_username_}'

DOCKER_CLEAN_COMMAND = 'docker service rm $(docker service ls -q); ' \
                       'docker stop $(docker ps -a -q); ' \
                       'docker rm $(docker ps -a -q); ' \
                       'docker volume rm $(docker volume ls -qf dangling=true); ' \
                       'docker rmi $(docker images -q)'

DOCKER_SWARM_INIT_COMMAND = 'docker swarm init --advertise-addr {hostname_}'
DOCKER_SWARM_TOKEN_COMMAND = 'docker swarm join-token --quiet {role_}'
DOCKER_SWARM_JOIN_COMMAND = 'docker swarm join --token {token_} {manager_hostname_}:2377'
DOCKER_SWARM_LEAVE_COMMAND = 'docker swarm leave --force'

DOCKER_NETWORK_CREATE_COMMAND = 'docker network create --driver overlay ccube'
DOCKER_SERVICE_CREATE_COMMAND = 'docker service create --name {name_} --replicas {replicas_} --network ccube {extra_} {image_} {command_}'
DOCKER_SERVICE_PS_RUNNING_COMMAND = 'docker service ps {name_} | grep -E \'Running [0-9]+\' | wc -l'
DOCKER_SERVICE_DESTROY_COMMAND = 'docker service remove {name_}'


def install_docker(
        hostname,
        ssh_port,
        ssh_username,
        ssh_private_key_file,
        executor,
        logger,
):
    stdout, return_code = utils.execute_ssh_command(
        DOCKER_INSTALL_COMMAND,
        environment_variables=None,
        hostname=hostname,
        ssh_port=ssh_port,
        ssh_username=ssh_username,
        ssh_private_key_file=ssh_private_key_file,
        executor=executor,
        logger=logger,
    )

    stdout, return_code = utils.execute_ssh_command(
        DOCKER_INSTALL_USERMOD_COMMAND.format(
            ssh_username_=ssh_username,
        ),
        environment_variables=None,
        hostname=hostname,
        ssh_port=ssh_port,
        ssh_username=ssh_username,
        ssh_private_key_file=ssh_private_key_file,
        executor=executor,
        logger=logger,
    )


def execute_command(
        command,
        hostname,
        ssh_port,
        ssh_username,
        ssh_private_key_file,
        executor,
        logger,
):
    stdout, return_code = utils.execute_ssh_command(
        command,
        environment_variables=None,
        hostname=hostname,
        ssh_port=ssh_port,
        ssh_username=ssh_username,
        ssh_private_key_file=ssh_private_key_file,
        executor=executor,
        logger=logger,
    )

    return stdout, return_code


def clean(
        hostname,
        ssh_port,
        ssh_username,
        ssh_private_key_file,
        executor,
        logger,
):
    execute_command(
        DOCKER_CLEAN_COMMAND,
        hostname=hostname,
        ssh_port=ssh_port,
        ssh_username=ssh_username,
        ssh_private_key_file=ssh_private_key_file,
        executor=executor,
        logger=logger,
    )


def swarm_init(
        hostname,
        ssh_port,
        ssh_username,
        ssh_private_key_file,
        executor,
        logger,
):
    execute_command(
        DOCKER_SWARM_INIT_COMMAND.format(
            hostname_=hostname,
        ),
        hostname=hostname,
        ssh_port=ssh_port,
        ssh_username=ssh_username,
        ssh_private_key_file=ssh_private_key_file,
        executor=executor,
        logger=logger,
    )

    execute_command(
        DOCKER_NETWORK_CREATE_COMMAND,
        hostname=hostname,
        ssh_port=ssh_port,
        ssh_username=ssh_username,
        ssh_private_key_file=ssh_private_key_file,
        executor=executor,
        logger=logger,
    )


def swarm_token(
        role,
        hostname,
        ssh_port,
        ssh_username,
        ssh_private_key_file,
        executor,
        logger,
):
    stdout, return_code = execute_command(
        DOCKER_SWARM_TOKEN_COMMAND.format(
            role_=role,
        ),
        hostname=hostname,
        ssh_port=ssh_port,
        ssh_username=ssh_username,
        ssh_private_key_file=ssh_private_key_file,
        executor=executor,
        logger=logger,
    )

    return stdout


def swarm_join(
        token,
        manager_hostname,
        hostname,
        ssh_port,
        ssh_username,
        ssh_private_key_file,
        executor,
        logger,
):
    stdout, return_code = execute_command(
        DOCKER_SWARM_JOIN_COMMAND.format(
            token_=token,
            manager_hostname_=manager_hostname,
        ),
        hostname=hostname,
        ssh_port=ssh_port,
        ssh_username=ssh_username,
        ssh_private_key_file=ssh_private_key_file,
        executor=executor,
        logger=logger,
    )

    return stdout


def swarm_leave(
        hostname,
        ssh_port,
        ssh_username,
        ssh_private_key_file,
        executor,
        logger,
):
    stdout, return_code = execute_command(
        DOCKER_SWARM_LEAVE_COMMAND,
        hostname=hostname,
        ssh_port=ssh_port,
        ssh_username=ssh_username,
        ssh_private_key_file=ssh_private_key_file,
        executor=executor,
        logger=logger,
    )


def service_create(
        name,
        replicas,
        image,
        command,
        extra,
        hostname,
        ssh_port,
        ssh_username,
        ssh_private_key_file,
        executor,
        logger,
):
    command = command if command else ''
    extra = extra if extra else ''

    stdout, return_code = execute_command(
        DOCKER_SERVICE_CREATE_COMMAND.format(
            name_=name,
            replicas_=replicas,
            image_=image,
            command_=command,
            extra_=extra,
        ),
        hostname=hostname,
        ssh_port=ssh_port,
        ssh_username=ssh_username,
        ssh_private_key_file=ssh_private_key_file,
        executor=executor,
        logger=logger,
    )


def service_count_running(
        name,
        hostname,
        ssh_port,
        ssh_username,
        ssh_private_key_file,
        executor,
        logger,
):
    stdout, return_code = execute_command(
        DOCKER_SERVICE_PS_RUNNING_COMMAND.format(
            name_=name,
        ),
        hostname=hostname,
        ssh_port=ssh_port,
        ssh_username=ssh_username,
        ssh_private_key_file=ssh_private_key_file,
        executor=executor,
        logger=logger,
    )

    return int(stdout)


def service_destroy(
        name,
        hostname,
        ssh_port,
        ssh_username,
        ssh_private_key_file,
        executor,
        logger,
):
    stdout, return_code = execute_command(
        DOCKER_SERVICE_DESTROY_COMMAND.format(
            name_=name,
        ),
        hostname=hostname,
        ssh_port=ssh_port,
        ssh_username=ssh_username,
        ssh_private_key_file=ssh_private_key_file,
        executor=executor,
        logger=logger,
    )
