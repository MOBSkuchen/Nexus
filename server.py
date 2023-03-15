import socket
import sys
import threading as tr
import os
import threading
import time
from glob import glob

addr = ('suprime.sonvogel.com', 25580)


def format_addr(_addr):
    return f'{_addr[0]}:{_addr[1]}'


class Interpreter:
    def __init__(self, con):
        self.con = con
        self.pam = PackageManager()
        self.pkg_size = 1024

        while True:
            self._check()

    def _check(self):
        opener = self.con.recv(1).decode()
        match opener:
            case "0":
                self.greet()
            case "1":
                self.list()
            case "2":
                self.exists()
            case "3":
                self.send()
            case "4":
                self.send()

    def send(self):
        self.con.send(b'1')
        name = self.con.recv(100).decode()
        self.send_file(name)

    def greet(self):
        self.con.send(b'1')  # Accept connection

    def list(self):
        pattern = self.con.recv(100).decode()
        files = self.pam.list(pattern)
        self.con.send(";".join(files).encode())

    def exists(self):
        pattern = self.con.recv(100).decode()
        e = self.pam.exists(pattern)
        self.con.send(b'1' if e else b'0')

    def send_file(self, filename):
        self.con.recv(1)
        size = os.path.getsize(self.pam._make_path(filename))
        self.con.send(str(size).encode())
        with self.pam.get_reader(filename) as file:
            while True:
                by = file.read(1024)
                self.con.send(by)
                if len(by) != 1024:
                    break
                time.sleep(0.05)
                if self.con.recv(1) == b'C':
                    self.con.terminate()
                    exit(-2)  # Connection closed code
                else:
                    sys.stdout.write('\rOK')
        self.con.recv(1)
        sys.stdout.write('\rDONE')


class Server:
    def __init__(self, _addr):
        self.addr = _addr
        self.con = socket.socket()

        self._open()
        self._listen()

    def _open(self):
        self.con.bind(self.addr)

    def _listen(self, members=5):
        self.con.listen(members)

        while True:
            s, info = self.con.accept()
            print(f'Connected to {format_addr(info)}')
            thread = tr.Thread(target=self._init_interpreter, args=(s,))
            thread.start()

    def _init_interpreter(self, con):
        Interpreter(con)


class PackageManager:
    def __init__(self, directory='packages'):
        self.dir = self._make_path(directory, os.curdir)

    def _make_path(self, path, custom_dir=None):
        return os.path.join(self.dir if not custom_dir else custom_dir, path)

    def exists(self, name):
        return os.path.exists(self._make_path(name))

    @staticmethod
    def _get(path, mode):
        return open(path, mode)

    def get_reader(self, name):
        return self._get(self._make_path(name), 'rb')

    def get_writer(self, name):
        return self._get(self._make_path(name), 'wb')

    def list(self, pattern):
        def _(x):
            f = x.split('/')
            f = f[len(f) - 1]
            return f[:len(f) - 4]

        lst = glob(self._make_path(pattern))
        lst: list = map(_, lst)
        return lst


# For usage on nohup run
def _listen_end():
    def _st():
        while True:
            if os.path.exists('server.stop'):
                os._exit(100)  # Exit main program

    t = threading.Thread(target=_st)
    t.start()


def main():
    _listen_end()
    server = Server(addr)


if __name__ == '__main__':
    main()
