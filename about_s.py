import psutil
from platform import uname


def correct_size(bts, ending='iB'):
    size = 1024
    for item in ["", "K", "M", "G", "T", "P"]:
        if bts < size:
            return f"{bts:.2f}{item}{ending}"
        bts /= size


def creating_file():
    collect_info_dict = dict()
    if 'info' not in collect_info_dict:
        collect_info_dict['info'] = dict()
        collect_info_dict['info']['system_info'] = dict()
        collect_info_dict['info']['system_info'] = {'system': {'comp_name': uname().node,
                                                               'os_name': f"{uname().system} {uname().release}",
                                                               'version': uname().version,
                                                               'machine': uname().machine},
                                                    'processor': {'name': uname().processor,
                                                                  'phisycal_core': psutil.cpu_count(logical=False),
                                                                  'all_core': psutil.cpu_count(logical=True),
                                                                  'freq_max': f"{psutil.cpu_freq().max:.2f}Мгц"},
                                                    'ram': {'volume': correct_size(psutil.virtual_memory().total),
                                                            'aviable': correct_size(psutil.virtual_memory().available),
                                                            'used': correct_size(psutil.virtual_memory().used)}}
    # for partition in psutil.disk_partitions():
    #     try:
    #         partition_usage = psutil.disk_usage(partition.mountpoint)
    #     except PermissionError:
    #         continue
    #     if 'disk_info' not in collect_info_dict['info']:
    #         collect_info_dict['info']['disk_info'] = dict()
    #     if f"'device': {partition.device}" not in collect_info_dict['info']['disk_info']:
    #         collect_info_dict['info']['disk_info'][partition.device] = dict()
    #         collect_info_dict['info']['disk_info'][partition.device] = {'file_system': partition.fstype,
    #                                                                     'size_total': correct_size(
    #                                                                         partition_usage.total),
    #                                                                     'size_used': correct_size(
    #                                                                         partition_usage.used),
    #                                                                     'size_free': correct_size(
    #                                                                         partition_usage.free),
    #                                                                     'percent':
    #                                                                         f'{partition_usage.percent}'}
    #
    # for interface_name, interface_address in psutil.net_if_addrs().items():
    #     if interface_name == 'Loopback Pseudo-Interface 1':
    #         continue
    #     else:
    #         if 'net_info' not in collect_info_dict['info']:
    #             collect_info_dict['info']['net_info'] = dict()
    #         if interface_name not in collect_info_dict['info']['net_info']:
    #             collect_info_dict['info']['net_info'][interface_name] = dict()
    #             collect_info_dict['info']['net_info'][interface_name] = {
    #                 'mac': interface_address[0].address.replace("-", ":"),
    #                 'ipv4': interface_address[1].address}
    #
    return collect_info_dict


def await_info(dict_info):
    s = ''
    for item in dict_info['info']:
        if item == "system_info":
            for elem in dict_info['info'][item]:
                if elem == 'system':
                    s += f"[+] Информация о системе\n\
                          \t- Имя компьютера: {dict_info['info'][item][elem]['comp_name']}\n\
                          \t- Опереционная система: {dict_info['info'][item][elem]['os_name']}\n\
                          \t- Сборка: {dict_info['info'][item][elem]['version']}\n\
                          \t- Архитектура: {dict_info['info'][item][elem]['machine']}\n"
                if elem == 'processor':
                    s += f"[+] Информация о процессоре\n\
                          \t- Семейство: {dict_info['info'][item][elem]['name']}\n\
                          \t- Физические ядра: {dict_info['info'][item][elem]['phisycal_core']}\n\
                          \t- Всего ядер: {dict_info['info'][item][elem]['all_core']}\n\
                          \t- Максимальная частота: {dict_info['info'][item][elem]['freq_max']}\n"
                if elem == 'ram':
                    s += f"[+] Оперативная память\n\
                          \t- Объем: {dict_info['info'][item][elem]['volume']}\n\
                          \t- Доступно: {dict_info['info'][item][elem]['aviable']}\n\
                          \t- Используется: {dict_info['info'][item][elem]['used']}\n"
        # if item == "disk_info":
        #     for elem in dict_info['info'][item]:
        #         s += f"[+] Информация о дисках\n\
        #               \t- Имя диска: {elem}\n\
        #               \t- Файловая система: {dict_info['info'][item][elem]['file_system']}\n\
        #               \t- Объем диска: {dict_info['info'][item][elem]['size_total']}\n\
        #               \t- Занято: {dict_info['info'][item][elem]['size_used']}\n\
        #               \t- Свободно: {dict_info['info'][item][elem]['size_free']}\n\
        #               \t- Заполненность: {dict_info['info'][item][elem]['percent']}%\n"
        # if item == "net_info":
        #     for elem in dict_info['info'][item]:
        #         s += f"[+] Информация о сети\n\
        #               \t- Имя интерфейса: {elem}\n\
        #               \t- MAC-адрес: {dict_info['info'][item][elem]['mac']}\n\
        #               \t- IPv4: {dict_info['info'][item][elem]['ipv4']}\n"

    return s
