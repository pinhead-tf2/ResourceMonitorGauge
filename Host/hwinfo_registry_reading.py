import winreg
import re
hwinfo_gadget_data = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'SOFTWARE\HWiNFO64\VSB')
hwinfo_data_length = winreg.QueryInfoKey(hwinfo_gadget_data)[1]

required_values = ['Core Usage', 'Physical Memory Load']
key_ids = []

for i in range(hwinfo_data_length):
    key, value, data_type = winreg.EnumValue(hwinfo_gadget_data, i)

    if value in required_values:
        value_id = re.search(r'\d+$', key).group()
        key_ids.append([value, value_id])
print(key_ids)

# cpu_usage = winreg.QueryValueEx(hwinfo_gadget_data, r'ValueRaw1')
# print(cpu_usage)
