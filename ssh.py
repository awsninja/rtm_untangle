import paramiko
import logging
from sys import stdout


# Define logger
logger = logging.getLogger('ssh_logger')
logger.setLevel(logging.DEBUG) # set logger level
logFormatter = logging.Formatter\
("%(name)-12s %(asctime)s %(levelname)-8s %(filename)s:%(funcName)s %(message)s")
consoleHandler = logging.StreamHandler(stdout) #set streamhandler to stdout
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)


def execute_remote_command(host, username, command):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    k = paramiko.RSAKey.from_private_key_file("./ssh_private_key")
    try:
        ssh.connect(host, username=username, pkey=k)
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command)
        logger.info(ssh_stdout.read())
        logger.info(ssh_stderr.read())
        ssh_stdin.close()
    except:
        logger.info(f"Cound not connect via ssh to host {host}.")
