# Вариант №29

import os
import socket
import shutil

START_SCRIPT_FILEPATH = "start_script.txt"
VFS_FILEPATH = "C:/Work/Personal/Study/ConfigurationManagement_1/VFS PATH/"


class VFS:
    def __init__(self, source_path):
        self.root = {}
        self.cwd = "/"
        self.source_path = source_path
        self.load_from_disk(source_path)

    def load_from_disk(self, path):
        if not os.path.exists(path):
            self.root = {}
            return

        for root_dir, dirs, files in os.walk(path):
            current = self.root
            rel_path = os.path.relpath(root_dir, path)

            if rel_path != '.':
                for part in rel_path.split(os.sep):
                    if part:
                        current = current.setdefault(part, {})

            for dir_name in dirs:
                current[dir_name] = {}
            for file_name in files:
                full_file_path = os.path.join(root_dir, file_name)
                try:
                    with open(full_file_path, 'r', encoding='utf-8') as f:
                        current[file_name] = f.read()
                except UnicodeDecodeError:
                    current[file_name] = ""

    def save_to_disk(self, target_path):
        if os.path.exists(target_path):
            shutil.rmtree(target_path)
        os.makedirs(target_path)
        self._save_directory(self.root, target_path)

    def _save_directory(self, node, current_path):
        for name, content in node.items():
            full_path = os.path.join(current_path, name)
            if isinstance(content, dict):
                os.makedirs(full_path)
                self._save_directory(content, full_path)
            else:
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)

    def _normalize_path(self, path):
        if path.startswith('/'):
            parts = path.split('/')
        else:
            parts = self.cwd.split('/') + path.split('/')

        stack = []
        for part in parts:
            if part == '' or part == '.':
                continue
            elif part == '..':
                if stack:
                    stack.pop()
            else:
                stack.append(part)
        return '/' + '/'.join(stack) if stack else '/'

    def get_node(self, path):
        if path is None:
            path = self.cwd
        abs_path = self._normalize_path(path)
        if abs_path == '/':
            return self.root

        parts = [p for p in abs_path.split('/') if p]
        current = self.root

        for part in parts:
            if part not in current:
                return None
            current = current[part]
        return current

    def get_parent_and_name(self, path):
        abs_path = self._normalize_path(path)
        if abs_path == '/':
            return None, None

        parts = [p for p in abs_path.split('/') if p]
        if not parts:
            return None, None

        name = parts[-1]
        parent_parts = parts[:-1]

        current = self.root
        for part in parent_parts:
            if part not in current:
                return None, name
            current = current[part]

        return current, name

    def ls(self, path):
        target = self.get_node(path)
        if target is None:
            return f"ls: {path}: No such file or directory"
        if not isinstance(target, dict):
            return f"ls: {path}: Not a directory"

        return ' '.join(sorted(target.keys()))

    def cd(self, path):
        if path is None or path == "":
            self.cwd = "/"
            return None

        target = self.get_node(path)
        if target is None:
            return f"cd: {path}: No such file or directory"
        if not isinstance(target, dict):
            return f"cd: {path}: Not a directory"

        self.cwd = self._normalize_path(path)
        return None

    def mkdir(self, path):
        parent, name = self.get_parent_and_name(path)
        if parent is None and self._normalize_path(path) != '/':
            return f"mkdir: {path}: No such file or directory"
        if parent is None and self._normalize_path(path) == '/':
            return f"mkdir: {path}: File exists"

        if name in parent:
            return f"mkdir: {path}: File exists"

        parent[name] = {}
        return None

    def touch(self, path):
        parent, name = self.get_parent_and_name(path)
        if parent is None:
            return f"touch: {path}: No such file or directory"
        if not isinstance(parent, dict):
            return f"touch: {path}: Not a directory"

        parent[name] = ""
        return None


def execute(command, vfs):
    if not command.strip():
        return True

    if command[0] == '$':
        var_name = command[1:]
        value = os.getenv(var_name, "")
        print(value)
        return True

    parts = command.split()
    cmd = parts[0]
    args = parts[1:]

    if cmd == "exit":
        exit(0)
    elif cmd == "ls":
        result = vfs.ls(args[0] if args else None)
        print(result)
        return True
    elif cmd == "cd":
        result = vfs.cd(args[0] if args else None)
        if result:
            print(result)
            return False
        return True
    elif cmd == "mkdir":
        if not args:
            print("mkdir: missing operand")
            return False
        result = vfs.mkdir(args[0])
        if result:
            print(result)
            return False
        return True
    elif cmd == "touch":
        if not args:
            print("touch: missing file operand")
            return False
        result = vfs.touch(args[0])
        if result:
            print(result)
            return False
        return True
    elif cmd == "conf-dump":
        print(f"VFS path: {VFS_FILEPATH}")
        print(f"Script path: {START_SCRIPT_FILEPATH}")
        print(f"Current VFS directory: {vfs.cwd}")
        return True
    elif cmd == "vfs-save":
        save_path = args[0] if args else VFS_FILEPATH
        try:
            vfs.save_to_disk(save_path)
            print(f"VFS saved to {save_path}")
        except Exception as e:
            print(f"vfs-save: error saving to {save_path}: {e}")
            return False
        return True
    else:
        print(f"Error: unknown command '{cmd}'")
        return False


def run_script(script_path, vfs):
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                prompt = f"{os.getlogin()}@{socket.gethostname()}: {vfs.cwd} $ "
                print(prompt + line)

                if not execute(line, vfs):
                    print("Script stopped due to error")
                    exit(1)
    except FileNotFoundError:
        print(f"Error: script file '{script_path}' not found")
        exit(1)


def main():
    vfs = VFS(VFS_FILEPATH)
    if os.path.exists(START_SCRIPT_FILEPATH):
        run_script(START_SCRIPT_FILEPATH, vfs)

    while True:
        command = input(f"{os.getlogin()}@{socket.gethostname()}: {vfs.cwd} $ ")
        execute(command, vfs)


if __name__ == "__main__":
    main()