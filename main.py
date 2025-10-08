# Вариант №29

import os
import socket

START_SCRIPT_FILEPATH = "start_script.txt"
VFS_FILEPATH = os.get_exec_path()[0]


def execute(instruction):
    if str(instruction)[0] != '$':
        parts = str(instruction).split()
        if not parts:
            return

        cmd = parts[0]
        args = parts[1:]

        if cmd == "exit":
            exit()
        elif cmd == "ls":
            print(f"ls {' '.join(args)}")
        elif cmd == "cd":
            print(f"cd {' '.join(args)}")
        elif cmd == "conf-dump":
            print("Start script filepath: " + START_SCRIPT_FILEPATH)
            print("VFS filepath: " + VFS_FILEPATH)
        else:
            print(f"Error: unknown command '{cmd}'")
            return -1
    else:
        print(os.getenv(instruction[1:]))

    return 0


def run_script(script_path):
    try:
        with open(script_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    print("Script executed")
                    break

                prompt = f"{os.getlogin()}@{socket.gethostname()}:~$ "
                print(prompt + line)

                if execute(line) != 0:
                    print("Script stopped due to error")
                    exit(1)

    except FileNotFoundError:
        print(f"Error: script file '{script_path}' not found")
        exit(1)


run_script(START_SCRIPT_FILEPATH)
while True:
    command = input(f"{os.getlogin()}@{socket.gethostname()}:~$ ")
    execute(command)
