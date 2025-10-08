# Вариант №29

import os
import socket


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
        else:
            print(f"Error: unknown command '{cmd}'")
    else:
        print(os.getenv(instruction[1:]))

while True:
    command = input(f"{os.getlogin()}@{socket.gethostname()}:~$ ")
    execute(command)
