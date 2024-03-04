import asyncio
import re
import winreg
from datetime import datetime
from platform import uname

import psutil
from cpuinfo import get_cpu_info
from rich.console import Console

from classes.serial_wrapper import SerialWrapper

# config values
serial_device_name = 'COM6'
tracked_statistics = ['Core Usage', 'Physical Memory Load', 'GPU Utilization']
cpu_registry_id = 1
memory_registry_id = 0
transmit_interval = 0.5
log_transmitted_values = False

# other
hwinfo_registry = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'SOFTWARE\HWiNFO64\VSB')
console = Console()


def current_time():
    # prints out the colored current time with ms for console-like output
    return f"[aquamarine3][{datetime.now().strftime('%T.%f')[:-3]}][/aquamarine3] "


async def initialize():
    console.print(f"{current_time()}[#2196F3]Resource Monitor Gauge - Trebuchet[/#2196F3]\n"
                  f"   Gathers system resource information, and transmits it to a receiving device.\n")
    platform_info = uname()
    cpu_info = get_cpu_info()
    console.print(f"{current_time()}[purple]System Information[/purple]\n"
                  f"   [bold]OS:[/bold] {platform_info.system} {platform_info.release} ({platform_info.version})\n"
                  f"   [bold]CPU:[/bold] {cpu_info['brand_raw']} ({round(float(cpu_info['hz_advertised_friendly'][0:6]), 2)} GHz)\n"
                  f"   [bold]Memory:[/bold] {round(psutil.virtual_memory().total / 1024.0 / 1024.0 / 1024.0, 1)} GB\n",
                  highlight=False)


async def validate_registry_keys():
    registry_length = winreg.QueryInfoKey(hwinfo_registry)[1]
    key_ids = []
    validation_statistics = tracked_statistics.copy()

    for i in range(registry_length):
        key, value, data_type = winreg.EnumValue(hwinfo_registry, i)

        if value in tracked_statistics:
            value_id = re.search(r'\d+$', key).group()
            key_ids.append([value, value_id])
            validation_statistics.remove(value)

    if len(key_ids) != len(tracked_statistics):
        console.print(f"{current_time()}[bold red]Registry key mismatch[/bold red]\n"
                      f"Tracked Statistics Count: {len(tracked_statistics)}\n"
                      f"Validated Statistics Count: {len(key_ids)}")
        exit(1)

    key_ids = sorted(key_ids, key=lambda x: tracked_statistics.index(x[0]))  # this is purely for my satisfaction :3


async def get_resource_usage():
    cpu_usage = winreg.QueryValueEx(hwinfo_registry, f'ValueRaw{cpu_registry_id}')
    memory_usage = winreg.QueryValueEx(hwinfo_registry, f'ValueRaw{memory_registry_id}')
    return cpu_usage[0], memory_usage[0]


async def main():
    await initialize()
    await validate_registry_keys()
    serial_connection = SerialWrapper(serial_device_name, 9600)

    connection_established = True

    # make a connection agent on both sides of the client and validate the order of the statistics before true data flow    

    while connection_established:
        usages = await get_resource_usage()
        converted_usages = []
        for usage in usages:
            converted_usages.append(round(float(usage) / 100. * 4095))  # 12 bit conversion

        packet = ','.join(map(str, converted_usages))

        serial_connection.send_data(packet)

        if log_transmitted_values:
            console.print(f"{current_time()}{packet}")
        await asyncio.sleep(transmit_interval)


if __name__ == '__main__':
    asyncio.run(main())
