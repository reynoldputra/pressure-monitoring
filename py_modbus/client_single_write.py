#!/usr/bin/env python3

from pyModbusTCP.client import ModbusClient

# Initialize Modbus client
# modbus_client = ModbusClient(host="192.168.246.242", auto_open=True)
# modbus_client = ModbusClient(host="0.0.0.0", auto_open=True)
modbus_client= ModbusClient(host="10.10.100.254",auto_open=True,timeout=10)

def send_to_modbus():
    try:
        # Get user input
        addr = 0
        value = int(input("Enter the value to write to the Modbus register: "))

        # Write to Modbus register
        success = modbus_client.write_single_register(addr, value)

        # Display the result
        if success:
            print(f"Successfully wrote {value} to register {addr}")
        else:
            print("Failed to write to Modbus register.")
    except ValueError:
        print("Invalid input. Please enter numeric values only.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    while True:
        send_to_modbus()
        cont = input("Do you want to send another value? (yes/no): ").strip().lower()
        if cont not in ("yes", "y"):
            print("Exiting...")
            break
