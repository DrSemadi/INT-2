import logging
import network_parser
import logging_control
import SQL_control
import ssh_transport
from tkinter.ttk import Progressbar

class Core():
    def __init__(self) -> None:
        logging_control.configure_logging()
        self.m_network = network_parser.Network_Scanner()
        self.m_transport = ssh_transport.Transport_SSH()
        self.m_sql = SQL_control.Database_Connector()
        self.network_ready = False
        self.transport_ready = False
        self.sql_ready = False
        self.sql_address = None
        self.sql_password = None
        self.sql_user = None
        self.sql_db = None
        self.sql_schema = None
        self.sql_table = None
        self.network = None
        self.ports = None
        self.exclusions =  None
        self.target = None
        self.port = None
        self.ssh_user = None
        self.ssh_password = None
    
    def run(self, network_mode:int, database_mode:bool, progress:Progressbar ,*args, **kwargs) -> int:
        progress.config(value=10)
        if self.sql_address and self.sql_password and self.sql_user and self.sql_db and self.sql_schema and self.sql_table:
            if self.ssh_user and self.ssh_password:
                if network_mode == 0:
                    if self.target and self.port:
                        progress.config(value=30)
                        progress.update()
                        self.m_transport.connection(self.target, self.port, self.ssh_user, self.ssh_password)
                        result_info = [self.target]
                        result_info.extend(self.perform_scan())
                        progress.config(value=60)
                        progress.update()
                        self.m_sql.run(self.sql_address, self.sql_user, self.sql_password, self.sql_db, self.sql_schema, self.sql_table, database_mode)
                        self.m_sql.write_values(result_info)
                        progress.config(value=80)
                        progress.update()
                        self.m_sql.close_connection()
                elif network_mode == 1:
                    if self.network and self.ports:
                        progress.config(value=30)
                        progress.update()
                        ports = []
                        for port in self.ports:
                            ports.append(int(port))
                        self.m_network.configure(self.network.strip(), self.exclusions)
                        progress.config(value=40)
                        progress.update()
                        to_scan = self.m_network.scan(ports)
                        self.m_sql.run(self.sql_address, self.sql_user, self.sql_password, self.sql_db, self.sql_schema, self.sql_table, database_mode)
                        progress.config(value=50)
                        progress.update()
                        for entry in to_scan:
                            self.m_transport.connection(entry[0], entry[1], self.ssh_user, self.ssh_password)
                            result_info = [entry[0]]
                            result_info.extend(self.perform_scan())
                            self.m_sql.write_values(result_info)
                        progress.config(value=90)
                        progress.update()
                        self.m_sql.close_connection()
                else: return -3
            else: return -2
        else: return -1
    def get_table(self) -> list:
        self.m_sql.connect(self.sql_address, self.sql_user, self.sql_password, database = self.sql_db)
        self.m_sql.get_table()
        return self.m_sql.cursor.fetchall()

    def perform_scan(self) -> list[str]:
        os_unparsed = ""
        version_unparsed = ""
        arch_unparsed = ""
        for line in self.m_transport.execute("cat /etc/os-release").split('\n')[:-1]:
            key, value = line.split("=")
            if key == "NAME": os_unparsed = value.strip('"')
            elif key == "VERSION" : version_unparsed = value.strip('"')
        if version_unparsed == "" or "Manjaro" in os_unparsed:
            for line in self.m_transport.execute("cat /etc/lsb-release").split('\n')[:-1]:
                key, value = line.split("=")
                if "RELEASE" in key: version_unparsed = value.strip('"')
        arch_unparsed = self.m_transport.execute("uname -m").strip('\n')
        if "ubuntu" in os_unparsed.lower():
            os = "Ubuntu"
        elif "debian" in os_unparsed.lower():
            os = "Debian"
        elif "manjaro" in os_unparsed.lower():
            os = "Manjaro"
        else:
            os = "Other Linux"
        self.m_transport.connection_close()
        return [os, version_unparsed, arch_unparsed]
                
                
                
                