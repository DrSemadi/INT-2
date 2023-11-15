import socket
import paramiko
import logging
import logging_control


class Transport_SSH:
    def __init__(self) -> None:
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy)

    def check(self, ip:str, port:int) -> bool:
        logging.info(f"SSH: Scanning {ip}:{port} for listening SSH-server")
        test_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = test_connection.connect_ex((ip,port))
        if result == 0: return True
        else: return False
        
    def connection(self, ip:str, port:int, user:str, password:str) -> int:
        logging.info(f"SSH: Trying SSH connection to {ip}:{port} as user {user}")
        logging.debug(f"SSH: Password: {password}")
        self.target_ip = ip
        self.target_port = port
        self.username = user
        self.password = password
        try: 
            self.ssh_client.connect(hostname=ip, port=port, username=user, password=password)
            logging.info(f"SSH: Connection established successfully")
            return 0
        except Exception as error:
            logging.error(f"SSH: An error occured while connecting to SSH Server.")
            logging.debug(f"SSH: Username:{self.username}, password: {self.password}")
            logging.error(f"SSH: Error: {error}")
            return -1
    
    def execute(self, command:str) -> str:
        try:
            logging.info(f"SSH: Executin command {command}")
            _, command_res, _ = self.ssh_client.exec_command(command)
            dec_result = command_res.read().decode()
            logging.info(f"SSH: Command output: {dec_result}")
            return dec_result
        except Exception as error:
            logging.error(f"SSH: An error occured while executing commands")
            logging.error(f"SSH: Error: {error}")
            return -1
            
    def connection_close(self) -> int:
        logging.info(f"SSH: Terminating connection to {self.target_ip}:{self.target_port}")
        try:
            self.ssh_client.close()
            #self.ssh_client = -1
            self.target_ip = ""
            self.target_port = -1
            self.username = ""
            self.password = ""
            logging.info("SSH: Connection terminated successfully")
        except Exception as error:
            logging.error("SSH: An error occured while terminating connection to SSH Server")
            
            