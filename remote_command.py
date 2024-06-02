import paramiko
import logging

# Define logger
logger = logging.getLogger('poll_logger')


class RemoteCommand:
    
    def execute_remote_command(self, host, username, command):
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
