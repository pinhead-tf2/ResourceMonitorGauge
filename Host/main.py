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
transmit_interval = 0.5
log_transmitted_values = True

# other
console = Console()
try:
    hwinfo_registry = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'SOFTWARE\HWiNFO64\VSB')
except FileNotFoundError:
    console.print(f"[bold red]HWiNFO Registry Not Found[/bold red]\n"
                  f"Ensure HWiNFO is started, Gadget is enabled, and values are chosen")
    exit(1)


def current_time():
    # prints out the colored current time with ms for console-like output
    return f"[aquamarine3][{datetime.now().strftime('%T.%f')[:-3]}][/aquamarine3] "


async def print_system_info():
    console.print(f"{current_time()}[#2196F3]Resource Monitor Gauge - Host Device[/#2196F3]\n"
                  f"   Gathers system resource information, and transmits it to a receiving device.\n")
    platform_info = uname()
    cpu_info = get_cpu_info()
    cpu_speed = round(float(cpu_info['hz_advertised_friendly'][0:6]), 2)
    console.print(f"{current_time()}[purple]System Information[/purple]\n"
                  f"   [bold blue]OS:[/bold blue] {platform_info.system} {platform_info.release} ({platform_info.version})\n"
                  f"   [bold blue]CPU:[/bold blue] {cpu_info['brand_raw']} ({cpu_speed} GHz)\n"
                  f"   [bold blue]Memory:[/bold blue] {round(psutil.virtual_memory().total / 1024.0 / 1024.0 / 1024.0, 1)} GB\n",
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
    return key_ids


async def get_resource_usage(legend):
    usage_values = []
    for pair in legend:
        registry_result = winreg.QueryValueEx(hwinfo_registry, f'ValueRaw{pair[1]}')
        usage_values.append(registry_result[0])
    return usage_values


async def main():
    await print_system_info()
    legend = await validate_registry_keys()
    # serial_connection = SerialWrapper(serial_device_name, 9600)

    while True:
        usages = await get_resource_usage(legend)
        converted_usages = {}
        for position, usage in enumerate(usages):
            converted_usages[legend[position][0]] = round(float(usage) / 100. * 4095)

        # serial_connection.send_data(packet)

        if log_transmitted_values:
            console.print(f"{current_time()}{converted_usages}")
        await asyncio.sleep(transmit_interval)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("Exiting...")
