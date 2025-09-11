import os
import socket

# Вариант №29




def main():
    username = os.getlogin()
    machineId = socket.gethostname()
    while True:
        try:
            command, *args = input(f"{username}@{machineId}:~$ ").split(" ")

            if command == "exit":
                break
            elif command == "ls":
                print(command + " " + " ".join(args))
            elif command == "cd":
                print(command + " " + " ".join(args))
            elif command.find("$") != -1:
                print(os.environ[str.replace(command, "$", "")])
            else:
                print("Unknown command: " + command)
        except Exception as err:
            print("Error: " + str(err))


if __name__ == '__main__':
    main()
