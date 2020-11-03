#!/usr/bin/env python3

import yaml
from getpass import getpass
from netmiko import ConnectHandler, NetmikoTimeoutException
from paramiko import SSHException
from datetime import datetime


password = getpass()
devices = []

with open("netgears.yml", "r") as f:
    devices = yaml.load(f)

# Print results table
layout = "|{:^15}|{:^21}|{:^35}|"
print(layout.format("-"*15,"-"*20,"-"*32))
print(layout.format("Device","Source","Time"))
print(layout.format("-"*15,"-"*20,"-"*32))

for device in devices:
    try:
        devices[device]["username"] = "admin"
        devices[device]["password"] = password
        devices[device]["secret"] = ""
        devices[device]["timeout"] = 3

        # Connect to device
        net_connect = ConnectHandler(**devices[device])
        net_connect.enable()
        clock_output = net_connect.send_command("show clock")

        # Seperate the time and source
        time, source = clock_output.splitlines()
        print(layout.format(device, source, time))

        cfg = [
            "no sntp client mode",
            "clock summer-time recurring EU offset 60 zone \"GMT\"",
            'clock timezone 0 minutes 0 zone "GMT"',
            "clock set %s" % datetime.now().strftime("%m/%d/%Y") ,
            "clock set %s" % datetime.now().strftime("%H:%M:%S") ,
            "sntp client mode unicast",
        ]

        print(net_connect.send_config_set(cfg))

        # Check the values and output it again
        clock_output = net_connect.send_command("show clock")

        # Seperate the time and source
        time, source = clock_output.splitlines()
        print(layout.format(device, source, time)+" Updated")
        print(layout.format("-"*15,"-"*20,"-"*32))

        print(net_connect.save_config())
        print(net_connect.disconnect())
    except NetmikoTimeoutException as ex:
        print(ex)
    except SSHException as ex:
        print(ex)
