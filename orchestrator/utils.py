import subprocess
import string
import random
import time

import yaml
import paramiko


def execute_command(
        command,
        working_directory,
        environment_variables,
        executor,
        logger,
):
    logger_prefix = ''
    if executor:
        logger_prefix = executor + ': '

    process = subprocess.Popen(
        command,
        cwd=working_directory,
        env=environment_variables,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
    )

    logger.debug(logger_prefix + 'command: ' + command)

    stdout = ''
    for line in iter(process.stdout.readline, b''):
        line = str(line, 'utf-8')
        stdout += line
        logger.debug(logger_prefix + 'command output: ' + line.rstrip())

    return_code = process.wait()

    stdout = stdout.rstrip()

    return stdout, return_code


def execute_ssh_command(
        command,
        environment_variables,
        hostname,
        ssh_port,
        ssh_username,
        ssh_private_key_file,
        executor,
        logger,
):
    logger_prefix = ''
    if executor:
        logger_prefix = executor + ': '

    logger.debug(logger_prefix + 'command: ' + command)

    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ssh_client.connect(
        hostname=hostname,
        port=ssh_port,
        username=ssh_username,
        key_filename=ssh_private_key_file,
        look_for_keys=False,
    )

    stdin, stdout, stderr = ssh_client.exec_command(
        command,
        environment=environment_variables,
    )

    stdout_string = ''
    for line in stdout:
        stdout_string += line
        logger.debug(logger_prefix + 'command stdout: ' + line.rstrip())
    stdout_string = stdout_string.rstrip()

    for line in stderr:
        logger.debug(logger_prefix + 'command stderr: ' + line.rstrip())

    return_code = stdout.channel.recv_exit_status()

    ssh_client.close()

    return stdout_string, return_code


def parse_yaml(yaml_file_path):
    with open(yaml_file_path, mode='r', encoding='utf-8') as yaml_file:
        content = yaml.load(yaml_file)
    return content


def generate_random_string(length):
    chars = string.digits + string.ascii_lowercase
    return ''.join(random.choice(chars) for _ in range(length))


def wait_until_ssh_ready(
        hostname,
        ssh_port,
        ssh_username,
        ssh_private_key_file,
):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    while True:
        try:
            ssh_client.connect(
                hostname=hostname,
                port=ssh_port,
                username=ssh_username,
                key_filename=ssh_private_key_file,
                look_for_keys=False,
                timeout=2,
            )
            ssh_client.close()
            break
        except Exception as e:
            time.sleep(1)
