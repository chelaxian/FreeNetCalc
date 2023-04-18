# Импортируем необходимые библиотеки
import ipaddress
import math
from ipaddress import IPv4Network, summarize_address_range, IPv4Address


def input_with_validation(prompt, validator):
    """
    Запрашивает ввод у пользователя, применяет к нему функцию-валидатор и возвращает значение,
    только если оно удовлетворяет условиям валидации
    """
    while True:
        value = input(prompt).strip()
        if validator(value):
            return value
        print("\n-------------------------------------------\n\nНекорректный ввод. Попробуйте еще раз.")


def is_valid_cidr(value):
    """
    Возвращает True, если строка является корректным CIDR-адресом, иначе False
    """
    try:
        ipaddress.IPv4Interface(value)
        return True
    except ValueError:
        return False


def is_valid_n(value):
    """
    Возвращает True, если строка является целым числом, большим либо равным 1, иначе False
    """
    try:
        n = int(value)
        return n >= 1
    except ValueError:
        return False


# Функция проверки на корректность ввода типа сортировки
def is_valid_sort_type(user_input):
    return user_input in ['1', '2', '3', '4']


# Функция проверки на корректность ввода опции меню
def is_valid_menu_option(user_input):
    return user_input in ['1', '2', '3', '4', '5', '0']


# Функция исключения подсетей из исходной сети
def exclude_subnets():
    main_network = IPv4Network(input_with_validation(
        '\n-------------------------------------------\n\n\nВведите исходную сеть в формате CIDR\n(например, 0.0.0.0/0):\n\nВвод: ',
        is_valid_cidr))
    N = int(input_with_validation(
        '\n-------------------------------------------\n\nВведите количество исключаемых подсетей:\n\nВвод: ',
        is_valid_n))

    exclude_networks = []
    for i in range(N):
        while True:
            exclude = IPv4Network(input_with_validation(
                f'\n-------------------------------------------\n\nВведите исключаемую сеть/маску {i + 1} в формате CIDR\n(например, 172.16.0.0/12):\n\nВвод: ',
                is_valid_cidr))
            if exclude.overlaps(main_network):
                exclude_networks.append(exclude)
                break
            else:
                print(
                    "\n-------------------------------------------\n\nОшибка: введенная подсеть не пересекается с исходной сетью. Введите другую.")

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
        '\n-------------------------------------------\n\nВведите номер типа сортировки результата:\n1 - по возрастанию адреса сети,\n2 - по возрастанию ширины маски,\n3 - по убыванию ширины маски,\n4 - по убыванию адреса сети.\n\nВвод: ',
        is_valid_sort_type)
    if sort_type == '1':
        result.sort(key=lambda x: int(x.network_address))
    elif sort_type == '2':
        result.sort(key=lambda x: x.prefixlen, reverse=True)
    elif sort_type == '3':
        result.sort(key=lambda x: x.prefixlen)
    elif sort_type == '4':
        result.sort(key=lambda x: int(x.network_address), reverse=True)

    print('\n-------------------------------------------\n\nСписок оставшихся подсетей:\n')
    for net in result:
        print(str(net))
    print('\n')


# Функция проверки на корректность ввода IP-адреса с маской в формате CIDR
def is_valid_ip_with_cidr(user_input):
    try:
        ip, prefix = user_input.split('/')
        IPv4Address(ip)
        int_prefix = int(prefix)
        return 0 <= int_prefix <= 32
    except ValueError:
        return False


# Функция определения типа сети
def network_type(network):
    private_blocks = [IPv4Network('10.0.0.0/8'), IPv4Network('172.16.0.0/12'), IPv4Network('192.168.0.0/16')]

    if network.is_loopback:
        return "петлевая (loopback)"
    elif network.is_multicast:
        return "мультикаст"
    elif network.network_address == IPv4Address('0.0.0.0') or network.is_reserved:
        return "зарезервированная"
    elif any(network.subnet_of(private_block) for private_block in private_blocks):
        return "частная"
    elif network.is_global:
        return "глобальная"
    else:
        return "неопределенная"


# Функция вывода информации о сети
def get_network_info():
    ip_with_cidr = input_with_validation(
        '\n-------------------------------------------\n\nВведите IP-адрес с маской в формате CIDR\n(например, 192.168.0.156/24):\n\nВвод: ',
        is_valid_ip_with_cidr)
    ip, prefix = ip_with_cidr.split('/')
    network = IPv4Network(f"{IPv4Address(ip)}/{prefix}", strict=False)
    subnet_mask_bits = int(prefix)
    min_subnet_prefix = 31
    network_class = None

    print(f"\n-------------------------------------------\n\nМаска сети: {network.netmask}")
    print(f"Wildcard маска: {network.hostmask}")
    print(f"Сетевой адрес: {network.network_address}")
    print(f"Broadcast адрес: {network.broadcast_address}")

    if int(prefix) == 32:
        min_host = max_host = network.network_address
        print(f"Мин. хост в сети: {min_host}")
        print(f"Макс. хост в сети: {max_host}")
    elif int(prefix) == 31:
        min_host = max_host = network.network_address
        print(f"Мин. хост в сети: {min_host}")
        print(f"Макс. хост в сети: {max_host}")
    else:
        print(f"Мин. хост в сети: {network.network_address + 1}")
        print(f"Макс. хост в сети: {network.broadcast_address - 1}")

    if int(prefix) < 31:
        max_hosts = 2 ** (32 - int(prefix)) - 2
    elif int(prefix) == 31:
        max_hosts = 2
    else:
        max_hosts = 1
    print(f"Кол-во хостов в сети: {max_hosts}")

    min_subnet_prefix = 31
    if int(prefix) < 32:
        max_subnets_31 = 2 ** (min_subnet_prefix - int(prefix))
        print(f"Кол-во подсетей /31 в сети: {max_subnets_31}")
    else:
        print("Кол-во подсетей /31 в сети: 0")

    min_subnet_prefix = 30
    if int(prefix) < 31:
        max_subnets_30 = 2 ** (min_subnet_prefix - int(prefix))
        print(f"Макс. кол-во подсетей /30 в сети: {max_subnets_30}")
    else:
        print("Макс. кол-во подсетей /30 в сети: 0")

    first_octet = int(ip.split('.')[0])
    if 0 <= first_octet <= 127:
        network_class = "A"
    elif 128 <= first_octet <= 191:
        network_class = "B"
    elif 192 <= first_octet <= 223:
        network_class = "C"
    elif 224 <= first_octet <= 239:
        network_class = "D"
    else:
        network_class = "E"

    print(f"Класс сети: {network_class} - {network_type(network)} сеть")
    print('\n')


# Функция разделения исходной сети на подсети
def subnet_splitter():
    subnet_cidr = input_with_validation(
        '\n-------------------------------------------\n\nВведите адрес исходной сети в формате CIDR\n(например 10.0.0.0/8):\n\nВвод: ',
        is_valid_cidr)
    subnet = IPv4Network(subnet_cidr)

    print("\n-------------------------------------------\n\nСписок масок и кол-ва дробных подсетей:")
    for i in range(subnet.prefixlen + 1, 33):
        print(f"({i - subnet.prefixlen})    /{i}    -    {2 ** (i - subnet.prefixlen)} подсетей")

    mask_choice = int(input_with_validation(
        '\n-------------------------------------------\n\nВыберите (номер) пункта с кол-во подсетей:\n\nВвод: ',
        is_valid_n))

    new_prefixlen = subnet.prefixlen + mask_choice
    if new_prefixlen > 32:
        print(
            "\n-------------------------------------------\n\nНевозможно разделить подсеть на указанное кол-во подсетей.")
        return

    new_subnets = subnet.subnets(new_prefix=new_prefixlen)

    print("\n-------------------------------------------\n\nСписок подсетей после дробления:")
    for i, new_subnet in enumerate(new_subnets, start=1):
        print(f"{new_subnet}")

    print('\n')


# Функция суммаризации подсетей
def summarize_networks():
    N = int(
        input_with_validation('\n-------------------------------------------\n\nВведите количество сетей:\n\nВвод: ',
                              is_valid_n))

    networks = []
    for i in range(N):
        network = IPv4Network(input_with_validation(
            f'\n-------------------------------------------\n\nВведите сеть {i + 1} в формате CIDR\n(например, 192.168.0.0/24):\n\nВвод: ',
            is_valid_cidr))
        networks.append(network)

    # Найдите самый нижний и самый высокий IP-адрес из всех сетей
    min_ip = min([net.network_address for net in networks])
    max_ip = max([net.broadcast_address for net in networks])

    # Рассчитайте максимальную общую маску подсети
    address_range = int(max_ip) - int(min_ip) + 1
    prefix_length = 32 - math.ceil(math.log2(address_range))

    # Создайте новую сеть с общей маской
    summary = IPv4Network((min_ip, prefix_length), strict=False)

    # Проверьте последний IP-адрес суммаризованной сети
    while summary.broadcast_address < max_ip:
        prefix_length -= 1
        summary = IPv4Network((min_ip, prefix_length), strict=False)

    print('\n-------------------------------------------\n\nСуммаризация сетей:\n')
    print(str(summary))

    print('\n')


# Функция определения классовой маски A/B/C для тиражирования подсетей

def get_subnet_mask(ip_address):
    octets = ip_address.split('.')
    num_octets = len(octets)
    if num_octets == 4 and all(octet.isdigit() for octet in octets):
        if octets[0] == '0':
            return '0.0.0.0'
        elif octets[1] == '0':
            return '255.0.0.0'
        elif octets[2] == '0':
            return '255.255.0.0'
        elif octets[3] == '0':
            return '255.255.255.0'
        else:
            return '255.255.255.255'
    else:
        raise ValueError("\n-------------------------------------------\n\nНекорректный IP-адрес")


# Функция тиражирования подсетей

def subnet_tirazh():
    while True:
        start_ip_str = input_with_validation(
            "\n-------------------------------------------\n\nВведите начальный IP-адрес сети (без маски):\n\nВвод: ",
            is_valid_cidr)
        if '/' in start_ip_str:
            print("\n-------------------------------------------\n\nНекорректный ввод! Попробуйте снова.")
            continue
        try:
            start_ip = ipaddress.IPv4Address(start_ip_str)
        except ValueError:
            print("\n-------------------------------------------\n\nНекорректный IP-адрес! Попробуйте снова.")
            continue
        else:
            break

    required_mask = get_subnet_mask(str(start_ip))
    required_network = ipaddress.IPv4Network(f"{start_ip}/{required_mask}", strict=False)
    required_hosts = required_network.num_addresses - 2
    max_hosts = 2 ** (32 - required_network.prefixlen) - 2
    if max_hosts == -1:
        max_num = 16777214
        max_ip = IPv4Address("255.255.255.255")
        available_ips2 = int(max_ip) - int(start_ip)
        max_hosts = min(available_ips2, max_num)
    prompt = f"\n-------------------------------------------\n\nВведите количество хостов в желаемой сети (от 1 до {max_hosts}):\n\nВвод: "
    required_hosts_input = int(input_with_validation(prompt, is_valid_n))

    prefix = 32 - int(math.ceil(math.log2(required_hosts_input + 2)))
    max_possible_subnets = (int(ipaddress.IPv4Address("255.255.255.255")) - int(start_ip)) // (
                required_hosts_input + 2) + 1

    while True:
        tirazh_count_str = input_with_validation(
            f"\n-------------------------------------------\n\nВведите количество тиражируемых подсетей (от 1 до {max_possible_subnets}):\n\nВвод: ",
            is_valid_n)
        if '/' in tirazh_count_str:
            print("\n-------------------------------------------\n\nНекорректный ввод! Попробуйте снова.")
            continue
        tirazh_count = int(tirazh_count_str)
        if 1 <= tirazh_count <= max_possible_subnets:
            break
        else:
            print(
                f"\n-------------------------------------------\n\nНекорректное значение! Введите число от 1 до {max_possible_subnets}.")

    networks = []
    for _ in range(tirazh_count):
        if int(start_ip) > 0xFFFFFFFF:
            raise ValueError("\n-------------------------------------------\n\nНекорректное количество подсетей")
        network = ipaddress.IPv4Network((start_ip, prefix), strict=False)
        next_start_ip = int(network[-1]) + 1
        if next_start_ip >= 2 ** 32:
            break
        start_ip = ipaddress.IPv4Address(next_start_ip)

        networks.append(network)

    print("\n-------------------------------------------\n\nРезультат:")
    for new_subnet in networks:
        print(new_subnet)


# Главное меню
def main_menu():
    menu_option = input_with_validation(
        "\n===========================================\n\nМЕНЮ:\n1 - Информация об адресе и сети\n2 - Дробление сетей\n3 - Исключение подсетей\n4 - Суммаризация подсетей\n5 - Тиражирование подсетей\n0 - Выход\n\n===========================================\n\nВыберете нужное действие:\n\nВвод: ",
        is_valid_menu_option)

    if menu_option == '1':
        get_network_info()
    elif menu_option == '2':
        subnet_splitter()
    elif menu_option == '3':
        exclude_subnets()
    elif menu_option == '4':
        summarize_networks()
    elif menu_option == '5':
        subnet_tirazh()
    elif menu_option == '0':
        print("\n-------------------------------------------\n\nВыход из программы")
        return

    main_menu()


# Точка входа в программу
if __name__ == "__main__":
    main_menu()
