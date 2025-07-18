#!/usr/bin/env python3

""" Read 10 holding registers and print result on stdout. """

import time

from pyModbusTCP.client import ModbusClient

# init modbus client
# c = ModbusClient(host="192.168.246.242",auto_open=True)
# c = ModbusClient(host="10.10.100.254",auto_open=True,timeout=10)
# c = ModbusClient(host="192.168.1.100",auto_open=True,timeout=5)
c = ModbusClient(host="192.168.1.5",auto_open=True,timeout=5)

# main read loop
while True:
    # read 10 registers at address 0, store result in regs list
    regs_l = c.read_holding_registers(0, 1)

    # if success display registers
    if regs_l:
        print('reg ad #0 to 9: %s' % regs_l)
    else:
        print('unable to read registers')

    # sleep 2s before next polling
    time.sleep(1)
