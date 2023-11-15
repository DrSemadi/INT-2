import logging
import struct
import socket
import fcntl
import logging_control
from ssh_transport import Transport_SSH

class Network_Scanner:
    def __init__(self) -> None:
        pass
    
    def configure(self, network:str, exclusions:str) -> None:
        self.exclusion_str = exclusions
        # получение адреса сети из переданного адреса
        self.network = self._get_net_from_ip(network)
        # получение списка сетевых интерфейсов хоста
        self.get_host_ifaces()
        # формирование списка исключений адресов устройств
        self.form_exclusion_list()
        # формирование списка адресов устройств для сканирования
        self.form_scan_list()
        # объект для транспорта
        self.transport = Transport_SSH()
        
    # получает битовую маску и возвращает маску в формате с точками
    def _get_mask_from_bits(self, bits:int) -> str:
        count = 0
        for i in range(32-int(bits),32):
            count |= (1 << i)
        return "%d.%d.%d.%d" % ((count & 0xff000000) >> 24, (count & 0xff0000) >> 16, (count & 0xff00) >> 8 , (count & 0xff))
    
    # преобразовывает адрес 
    def _get_net_from_ip(self, cidr:str) -> str:
        netstruct = struct.Struct(">I")
        ip, bit_mask = cidr.split('/')
        ip, = netstruct.unpack(socket.inet_aton(ip))
        mask, = netstruct.unpack(socket.inet_aton(self._get_mask_from_bits(bit_mask)))
        return socket.inet_ntoa(netstruct.pack(ip & mask)) + f"/{bit_mask}"
    
    # возвращает список адресов между двумя адресами
    def _get_ip_span(self, start:str, end:str) -> list[str]:
        ipstruct = struct.Struct('>I')
        start, = ipstruct.unpack(socket.inet_aton(start))
        end, = ipstruct.unpack(socket.inet_aton(end))
        return [socket.inet_ntoa(ipstruct.pack(i)) for i in range(start, end+1)]
    
    # проверяет, принадлежит ли адрес сети
    def _check_ip_in_net(self, ip:str) -> bool:
        ipaddr = struct.unpack('=L',socket.inet_aton(ip))[0]
        netaddr,bits = self.network.split('/')
        netmask = struct.unpack('=L',socket.inet_aton(self._get_mask_from_bits(bits)))[0]
        network = struct.unpack('=L',socket.inet_aton(netaddr))[0] & netmask
        return (ipaddr & netmask) == (network & netmask)
    
    # получает IPv4 адрес сетевого интерфейса
    def get_iface_address(self, ifname:str) -> str:
        logging.info(f"Network: Getting IPv4 of network interface {ifname}")
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            res = str(socket.inet_ntoa(fcntl.ioctl(
                s.fileno(),
                0x8915,
                struct.pack('256s',  bytes(ifname[:15], 'utf-8'))
            )[20:24]))
            s.close()
            logging.info(f"Network: IPv4 for {ifname} is {res}")
            return res
        except Exception as error:
            logging.error(f"Network: An error occured while getting {ifname} address")
            logging.error(f"Network: Error: {error}")
            return -1
            
    # получение списка сетевых интерфейсов, чтобы в последующем исключить собственный адрес из сканирования
    def get_host_ifaces(self) -> int:
        logging.info("Network: Getting list of host network interfaces")
        try:
            self.host_ifaces = [str(pair[-1]) for pair in socket.if_nameindex()]
            logging.info("Network: List of interfaces formed successfully")
            logging.info("Network: Interfaces: " + " ".join(item for item in self.host_ifaces))
            return 0
        except Exception as error:
            logging.error("Network: An error occured while fetching a list of network interfaces")
            logging.error(f"Network: Error: {error}")
            return -1

    # парсер для списка исключаемых IP-адресов. Список передается как строка в определенной нотации
    # нотация поддерживает одиночные адреса и интервалы
    # пример: "10.10.10.0, 10.10.10.1, 10.10.10.7-10.10.10.50, 10.10.10.52, 10.10.10.55-10.10.10.255"
    def form_exclusion_list(self) -> int:
        logging.info("Network: Forming list of IP-exclusions")
        try: 
            exclusions_raw = self.exclusion_str.split(',')
            exclusions_strings = []
            self.exclusions = []
            
            # поиск интерфейса, смотрящего на сканируемую сеть и удаление его адреса из списка на сканирование
            logging.info(f"Network: Searhing for interface in network {self.network}")
            for iface in self.host_ifaces:
                iface_ip = self.get_iface_address(iface)
                if self._check_ip_in_net(iface_ip):
                    logging.info(f"Network: Found interface {iface} with IP {iface_ip}. Adding to exclusions...")
                    self.exclusions.append(iface_ip)
                    
            # парсинг строки с исключениями
            for line in exclusions_raw: exclusions_strings.append(line.strip())
            for entry in exclusions_strings:
                if '-' in entry:
                    start, end = entry.split('-')
                    ret = self._get_ip_span(start,end)
                    for line in ret: 
                        if line not in self.exclusions: self.exclusions.append(line)
                else: 
                    if entry not in self.exclusions: self.exclusions.append(entry)
            logging.info("Network: List of exclusions formed successfully")
            logging.info("Network: Exclusions: " + " ".join(item for item in self.exclusions))
            return 0
        except Exception as error:
            logging.error("Network: An error occured while forming list of IP-exclusions")
            logging.error(f"Network: Error: {error}")
            return -1
            
    def form_scan_list(self) -> int:
        logging.info("Network: Forming list of possible hosts on network")
        self.scan_list_wExclusions = []
        try:
            (ip, cidr) = self.network.split('/')
            cidr = int(cidr)
            host_bits = 32 - cidr
            i = struct.unpack('>I', socket.inet_aton(ip))[0]
            start = (i >> host_bits) << host_bits
            end = start | ((1 << host_bits))
            for i in range(start, end):
                self.scan_list_wExclusions.append(str(socket.inet_ntoa(struct.pack('>I',i))))
            logging.info("Network: Host list successfully formed")
        except Exception as error:
            logging.error("Network: An error occured while forming list of network hosts")
            logging.error(f"Network: Error: {error}")
        
        logging.info("Network: Applying exclusions to hosts")
        try:
            for exclusion in self.exclusions:
                self.scan_list_wExclusions.remove(exclusion)
            logging.info("Network: Exclusions applied successfully")
        except Exception as error:
            logging.error("Network: An error occured while applying exclusions")
            logging.error(f"Network: Error: {error}")

    def scan(self, port_list:list[int]) -> int:
        self.viable_ssh_list = []
        logging.info(f"SSH: Beginning scan of target network. Ports to scan: " + " ".join("%s" % item for item in port_list))
        for host in self.scan_list_wExclusions:
            for port in port_list:
                try:
                    if self.transport.check(host, port): 
                        self.viable_ssh_list.append((host, port))
                        logging.info(f"SSH: Port is open")
                    else:
                        logging.info(f"SSH: Port is closed")
                except Exception as error:
                    logging.error("SSH: An error occured while applying exclusions")
                    logging.error(f"SSH: Error: {error}")
        return self.viable_ssh_list
