import ipaddress
import math
from ipaddress import IPv4Network, summarize_address_range, IPv4Address

# Constants
MENU_OPTIONS = {
    '1': 'Информация об адресе и сети',
    '2': 'Дробление сетей',
    '3': 'Исключение подсетей',
    '4': 'Суммаризация подсетей',
    '5': 'Тиражирование подсетей',
    '0': 'Выход'
}

PRIVATE_BLOCKS = [
    IPv4Network('10.0.0.0/8'),
    IPv4Network('172.16.0.0/12'),
    IPv4Network('192.168.0.0/16')
]

# Helper function to repeat characters
def repeat_char(char, count):
    return char * count

# Common separators
SEPARATOR = repeat_char('-', 43)
MENU_SEPARATOR = repeat_char('=', 43)

def input_with_validation(prompt, validator):
    """Generic input validation function"""
    while True:
        value = input(prompt).strip()
        if validator(value):
            return value
        print(f"\n{SEPARATOR}\n\nНекорректный ввод. Попробуйте еще раз.")

def is_valid_cidr(value):
    """Validate CIDR notation"""
    try:
        ipaddress.IPv4Interface(value)
        return True
    except ValueError:
        return False

def is_valid_n(value):
    """Validate positive integer"""
    try:
        return int(value) >= 1
    except ValueError:
        return False

def is_valid_menu_option(value):
    """Validate menu option"""
    return value in MENU_OPTIONS

def get_network_type(network):
    """Determine network type"""
    if network.is_loopback:
        return "петлевая (loopback)"
    if network.is_multicast:
        return "мультикаст"
    if network.network_address == IPv4Address('0.0.0.0') or network.is_reserved:
        return "зарезервированная"
    if any(network.subnet_of(private_block) for private_block in PRIVATE_BLOCKS):
        return "частная"
    if network.is_global:
        return "глобальная"
    return "неопределенная"

def display_network_info(network):
    """Display detailed network information"""
    print(f"\n{SEPARATOR}\n\nМаска сети: {network.netmask}")
    print(f"Wildcard маска: {network.hostmask}")
    print(f"Сетевой адрес: {network.network_address}")
    print(f"Broadcast адрес: {network.broadcast_address}")

    if network.prefixlen == 32:
        print(f"Мин. хост в сети: {network.network_address}")
        print(f"Макс. хост в сети: {network.network_address}")
    elif network.prefixlen == 31:
        print(f"Мин. хост в сети: {network.network_address}")
        print(f"Макс. хост в сети: {network.network_address + 1}")
    else:
        print(f"Мин. хост в сети: {network.network_address + 1}")
        print(f"Макс. хост в сети: {network.broadcast_address - 1}")

    max_hosts = 2 ** (32 - network.prefixlen) - 2 if network.prefixlen < 31 else 2 if network.prefixlen == 31 else 1
    print(f"Кол-во хостов в сети: {max_hosts}")

    if network.prefixlen < 32:
        for prefix in [31, 30]:
            if network.prefixlen < prefix:
                max_subnets = 2 ** (prefix - network.prefixlen)
                print(f"Кол-во подсетей /{prefix} в сети: {max_subnets}")
            else:
                print(f"Кол-во подсетей /{prefix} в сети: 0")

    first_octet = int(str(network.network_address).split('.')[0])
    network_class = "A" if 0 <= first_octet <= 127 else \
                   "B" if 128 <= first_octet <= 191 else \
                   "C" if 192 <= first_octet <= 223 else \
                   "D" if 224 <= first_octet <= 239 else "E"
    
    print(f"Класс сети: {network_class} - {get_network_type(network)} сеть")
    print('\n')

def get_network_info():
    """Get and display network information"""
    ip_with_cidr = input_with_validation(
        f"\n{SEPARATOR}\n\nВведите IP-адрес с маской в формате CIDR\n(например, 192.168.0.156/24):\n\nВвод: ",
        is_valid_cidr)
    network = IPv4Network(ip_with_cidr, strict=False)
    display_network_info(network)

def subnet_splitter():
    """Split network into subnets"""
    subnet_cidr = input_with_validation(
        f"\n{SEPARATOR}\n\nВведите адрес исходной сети в формате CIDR\n(например 10.0.0.0/8):\n\nВвод: ",
        is_valid_cidr)
    subnet = IPv4Network(subnet_cidr)

    print(f"\n{SEPARATOR}\n\nСписок масок и кол-ва дробных подсетей:")
    for i in range(subnet.prefixlen + 1, 33):
        print(f"({i - subnet.prefixlen})    /{i}    -    {2 ** (i - subnet.prefixlen)} подсетей")

    mask_choice = int(input_with_validation(
        f"\n{SEPARATOR}\n\nВыберите (номер) пункта с кол-во подсетей:\n\nВвод: ",
        is_valid_n))

    new_prefixlen = subnet.prefixlen + mask_choice
    if new_prefixlen > 32:
        print(f"\n{SEPARATOR}\n\nНевозможно разделить подсеть на указанное кол-во подсетей.")
        return

    print(f"\n{SEPARATOR}\n\nСписок подсетей после дробления:")
    for i, new_subnet in enumerate(subnet.subnets(new_prefix=new_prefixlen), start=1):
        print(f"{new_subnet}")
    print('\n')

def exclude_subnets():
    """Exclude subnets from main network"""
    main_network = IPv4Network(input_with_validation(
        f"\n{SEPARATOR}\n\n\nВведите исходную сеть в формате CIDR\n(например, 0.0.0.0/0):\n\nВвод: ",
        is_valid_cidr))
    N = int(input_with_validation(
        f"\n{SEPARATOR}\n\nВведите количество исключаемых подсетей:\n\nВвод: ",
        is_valid_n))

    exclude_networks = []
    for i in range(N):
        while True:
            exclude = IPv4Network(input_with_validation(
                f"\n{SEPARATOR}\n\nВведите исключаемую сеть/маску {i + 1} в формате CIDR\n(например, 172.16.0.0/12):\n\nВвод: ",
                is_valid_cidr))
            if exclude.overlaps(main_network):
                exclude_networks.append(exclude)
                break
            print(f"\n{SEPARATOR}\n\nОшибка: введенная подсеть не пересекается с исходной сетью. Введите другую.")

    result = [main_network]
    for exclude in exclude_networks:
        new_result = []
        for net in result:
            if exclude.overlaps(net):
                if exclude.network_address > net.network_address:
                    new_result.extend(summarize_address_range(net.network_address, exclude.network_address - 1))
                if exclude.broadcast_address < net.broadcast_address:
                    new_result.extend(summarize_address_range(exclude.broadcast_address + 1, net.broadcast_address))
            else:
                new_result.append(net)
        result = new_result

    sort_type = input_with_validation(
        f"\n{SEPARATOR}\n\nВведите номер типа сортировки результата:\n1 - по возрастанию адреса сети,\n2 - по возрастанию ширины маски,\n3 - по убыванию ширины маски,\n4 - по убыванию адреса сети.\n\nВвод: ",
        lambda x: x in ['1', '2', '3', '4'])
    
    sort_key = {
        '1': lambda x: int(x.network_address),
        '2': lambda x: x.prefixlen,
        '3': lambda x: -x.prefixlen,
        '4': lambda x: -int(x.network_address)
    }[sort_type]
    
    result.sort(key=sort_key)
    print(f"\n{SEPARATOR}\n\nСписок оставшихся подсетей:\n")
    for net in result:
        print(str(net))
    print('\n')

def summarize_networks():
    """Summarize multiple networks"""
    N = int(input_with_validation(
        f"\n{SEPARATOR}\n\nВведите количество сетей:\n\nВвод: ",
        is_valid_n))

    networks = [IPv4Network(input_with_validation(
        f"\n{SEPARATOR}\n\nВведите сеть {i + 1} в формате CIDR\n(например, 192.168.0.0/24):\n\nВвод: ",
        is_valid_cidr)) for i in range(N)]

    min_ip = min(net.network_address for net in networks)
    max_ip = max(net.broadcast_address for net in networks)
    address_range = int(max_ip) - int(min_ip) + 1
    prefix_length = 32 - math.ceil(math.log2(address_range))

    summary = IPv4Network((min_ip, prefix_length), strict=False)
    while summary.broadcast_address < max_ip:
        prefix_length -= 1
        summary = IPv4Network((min_ip, prefix_length), strict=False)

    print(f"\n{SEPARATOR}\n\nСуммаризация сетей:\n")
    print(str(summary))
    print('\n')

def subnet_tirazh():
    """Create multiple subnets"""
    while True:
        start_ip_str = input_with_validation(
            f"\n{SEPARATOR}\n\nВведите начальный IP-адрес сети (без маски):\n\nВвод: ",
            lambda x: '/' not in x and is_valid_cidr(f"{x}/32"))
        try:
            start_ip = IPv4Address(start_ip_str)
            break
        except ValueError:
            print(f"\n{SEPARATOR}\n\nНекорректный IP-адрес! Попробуйте снова.")

    required_mask = '255.0.0.0' if start_ip_str.split('.')[1] == '0' else \
                   '255.255.0.0' if start_ip_str.split('.')[2] == '0' else \
                   '255.255.255.0' if start_ip_str.split('.')[3] == '0' else '255.255.255.255'
    
    required_network = IPv4Network(f"{start_ip}/{required_mask}", strict=False)
    max_hosts = 2 ** (32 - required_network.prefixlen) - 2
    if max_hosts == -1:
        max_hosts = min(int(IPv4Address("255.255.255.255")) - int(start_ip), 16777214)

    required_hosts_input = int(input_with_validation(
        f"\n{SEPARATOR}\n\nВведите количество хостов в желаемой сети (от 1 до {max_hosts}):\n\nВвод: ",
        is_valid_n))

    prefix = 32 - int(math.ceil(math.log2(required_hosts_input + 2)))
    max_possible_subnets = (int(IPv4Address("255.255.255.255")) - int(start_ip)) // (required_hosts_input + 2) + 1

    tirazh_count = int(input_with_validation(
        f"\n{SEPARATOR}\n\nВведите количество тиражируемых подсетей (от 1 до {max_possible_subnets}):\n\nВвод: ",
        lambda x: x.isdigit() and 1 <= int(x) <= max_possible_subnets))

    networks = []
    current_ip = start_ip
    for _ in range(tirazh_count):
        if int(current_ip) > 0xFFFFFFFF:
            raise ValueError(f"\n{SEPARATOR}\n\nНекорректное количество подсетей")
        network = IPv4Network((current_ip, prefix), strict=False)
        networks.append(network)
        current_ip = IPv4Address(int(network[-1]) + 1)

    print(f"\n{SEPARATOR}\n\nРезультат:")
    for new_subnet in networks:
        print(new_subnet)

def main_menu():
    """Display main menu and handle user input"""
    while True:
        menu_option = input_with_validation(
            f"\n{MENU_SEPARATOR}\n\nМЕНЮ:\n" +
            "\n".join(f"{k} - {v}" for k, v in MENU_OPTIONS.items()) +
            f"\n\n{MENU_SEPARATOR}\n\nВыберете нужное действие:\n\nВвод: ",
            is_valid_menu_option)

        if menu_option == '0':
            print(f"\n{SEPARATOR}\n\nВыход из программы")
            break

        {
            '1': get_network_info,
            '2': subnet_splitter,
            '3': exclude_subnets,
            '4': summarize_networks,
            '5': subnet_tirazh
        }[menu_option]()

if __name__ == "__main__":
    main_menu()
