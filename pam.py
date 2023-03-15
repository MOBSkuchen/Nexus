import os
import threading
import time
from utils import fmt_file, sizeof_fmt, erase as _erase, yes_no
import argparser as ap
import sys
import socket
import colibri
import errors as xsErrors
from logger import logger
import zstandard as zst
from options import optionloader
import io_pack as io
from ypp_filetype import YPP


__version__ = '1.5'
colibri.Style.UNDERLINE = "\033[4m"
colibri.CURSOR_UP_ONE = '\x1b[1A'
colibri.ERASE_LINE = '\x1b[2K'
addr = ('suprime.sonvogel.com', 25582)


class PackageInstaller:
    def __init__(self, _addr=addr):
        self.pkg_size = 10240
        self.addr = _addr
        self.connection = socket.socket()
        # self.connection.settimeout(0.5)

        # Protected members
        self._got_resp = False
        self._got_accepted = False
        # ========================

        self._contact()

    def _server_dead(self):
        _.failed = 9
        xsErrors.stderr(9,
                        msg="Connection could NOT be established",
                        cause=["Server could not be reached"],
                        fix=["Check your internet connection",
                             "Update Nexus (PaM)"]
                        )

    def _server_refused(self):
        _.failed = 9
        xsErrors.stderr(9, msg="Server refused connection",
                        cause=["The Server currently does not expect/want a connection with you"],
                        fix=["Please wait a bit"])

    def _contact(self):
        try:
            self.connection.connect(self.addr)
        except ConnectionRefusedError:
            self._server_dead()
            return
        self.connection.send(b'0')
        response = self.connection.recv(1)
        if response == b'1':
            sys.stdout.write('\r                                                                     ')
            sys.stdout.write(f'\r{colibri.Fore.LIGHTGREEN_EX}Connected to '
                             f'{colibri.Style.BRIGHT}Nexus-Server {colibri.Style.RESET_ALL}         \n')
        elif response == b'0':
            self._server_refused()
        else:
            self._server_dead()

    def list(self, pattern):
        self.connection.send(b'1')
        self.connection.send(pattern.encode())
        response = self.connection.recv(100).decode()
        return response

    def exists(self, name):
        self.connection.send(b'2')
        self.connection.send(name.encode("utf-8"))
        response = self.connection.recv(1).decode()
        return response == "1"

    def download(self, filename, name):
        self.connection.send(b'3')
        self.connection.recv(1)
        self.connection.send(name.encode())
        self.connection.send(b'1')
        size = int(self.connection.recv(100).decode())
        s_ = sizeof_fmt(size)
        logger.add(f"Download package : {name}")
        io.output(f'Downloading package [{name} - {s_}] to {fmt_file(filename)}')
        done = 0
        with open(filename, 'wb') as filewriter:
            try:
                while True:
                    data = self.connection.recv(self.pkg_size)
                    got = len(data)
                    done += got
                    p = f'\r{sizeof_fmt(done)} / {s_}'
                    sys.stdout.write(p)
                    filewriter.write(data)
                    if got != self.pkg_size:
                        sys.stdout.write('\r')
                        _erase(1)
                        io.output(f'Downloaded package [{name} - {s_}] to {fmt_file(filename)}')
                        logger.add(f"Download finished")
                        break
                    time.sleep(0.05)
                    self.connection.send(b'O')
            except KeyboardInterrupt:
                self.connection.close()
                logger.add(f"Download interrupted")
                sys.stdout.write(f'\r{colibri.Fore.RED}Connection closed due to interrupt{colibri.Fore.RESET}')
                sys.exit(-2)
            self.connection.send(b'1')


def make_path(file):
    return os.path.join(optionloader.make_path(optionloader.directories[0]), file) if not _.local else file


def install(i):
    if not _.output:
        o = i
    else:
        o = _.output
    if not _.active:
        _.active = True
        tb = pam_make("Nexus-Server")
        if tb == 1:
            return
    if not pam.exists(i):
        xsErrors.stderr(11, msg=f"Package [{i}] does not exist on server")
        return 0
    if os.path.exists(make_path(o)):
        io.output(f'The package [{o}] already exists, are you sure you want to replace it?')
        if yes_no():
            sys.stdout.write('\r')
            pam.download(make_path(o), i)
            return make_path(o)
        else:
            io.output('Alright, canceling...')
            return 0
    else:
        pam.download(make_path(o), i)
        return make_path(o)


def remove(i):
    i = make_path(i)
    if not os.path.exists(i):
        xsErrors.stderr(11, msg=f"Package [{fmt_file(i)}] does not exist", cause=["The file was not found in the IPD",
                                                                                  "Maybe you did not download the file"])
    os.remove(i)


def m_inst(i):
    tb = install(i)
    if tb == 0:
        return
    if tb.endswith(".ypp"):
        unpack(tb)
        os.remove(tb)


def unpack(i):
    if i.endswith('.zst'):
        o = i[:(len(i) - 4)] if not _.output else _.output
        dctx = zst.ZstdDecompressor()
        io.output(f'{colibri.Fore.YELLOW}ZSTANDARD{colibri.Fore.RESET} : Unpacking {i}...')
        with open(i, 'rb') as ifh, open(o, 'wb') as ofh:
            dctx.copy_stream(ifh, ofh)
        io.output(f'{colibri.Fore.YELLOW}ZSTANDARD{colibri.Fore.RESET} : Unpacked to {o}...')
    elif i.endswith('.ypp'):
        io.output(f'{colibri.Fore.YELLOW}YPP{colibri.Fore.RESET} : Loading...')
        ypp = YPP.from_file(i)
        # _erase(1)
        io.output(f'{colibri.Fore.YELLOW}YPP{colibri.Fore.RESET} : Loaded\nNAME : {ypp.name} V{ypp.version} (by {ypp.author})')
        try:
            io.output(f'{colibri.Fore.YELLOW}YPP{colibri.Fore.RESET} : {colibri.Fore.GREEN}Decompressing')
            if _.output:
                dump = _.output
            elif _.local:
                dump = os.path.join(os.path.curdir, ypp.name)
            else:
                dump = os.path.join(os.path.dirname(i), ypp.name)
            ypp.expand(dump)
            # _erase(1)
            io.output(f'{colibri.Fore.YELLOW}YPP{colibri.Fore.RESET} : {colibri.Fore.GREEN}Decompressed')
            if ypp.dependencies:
                io.output(f'{colibri.Fore.YELLOW}YPP{colibri.Fore.RESET} : This package has {len(ypp.dependencies)}'
                      f' dependencies, do you wish to install them')
                if not yes_no():
                    return
                for dep in ypp.dependencies:
                    m_inst(dep.decode())

        except FileExistsError:
            xsErrors.stderr(12, msg="Cannot decompress YPP",
                            cause=["The directory (to be dumped to) already exists"],
                            fix=["Delete the directory"])
    else:
        xsErrors.stderr(13, msg="Filetype is not supported",
                        cause=["The file is not of type .ypp or .zst"])


class _:
    failed = False
    local = False
    output = None
    active = False


def argsparser(args):
    if len(args) == 0:
        io.output(f'{colibri.Fore.BLUE}{colibri.Style.BRIGHT}PAM{colibri.Style.RESET_ALL} : {colibri.Fore.MAGENTA}{__version__}{colibri.Fore.RESET}')
        io.output(f'{colibri.Fore.RED}Please pass in some arguments{colibri.Fore.RESET}')
        return
    parser = ap.ArgumentParser(args, check=True)
    parser.add_argument("install", calls=["-i", "install"], exclusives=["remove", "update"], input_=True)
    parser.add_argument("remove", calls=["-r", "remove"], exclusives=["install", "unpack"], input_=True)
    parser.add_argument("unpack", calls=["-u", "--unpack"], exclusives=["remove"])

    parser.add_argument("local", calls=["-l", "--local"])
    parser.add_argument("output", calls=["-o", "--output"], input_=True)

    options = parser()
    return options


def _main(options):
    options_l = options.keys()
    if "local" in options_l:
        _.local = True
    if "output" in options_l and "unpack" not in options_l:
        _.output = options["output"]
    if "install" in options_l:
        tb = install(options["install"])
        if "unpack" in options_l and tb:
            if "output" in options_l:
                _.output = options["output"]
            unpack(tb)
            os.remove(tb)
    elif "remove" in options_l:
        remove(options["remove"])
    if "unpack" in options_l and "install" not in options_l:
        io.output(f'{colibri.Fore.RED}You tried to unpack without installing.')
        io.output(
            f'{colibri.Fore.BLUE}You need to install and unpack{colibri.Fore.RESET} : {colibri.Style.BRIGHT}pam{colibri.Style.RESET_ALL} unpack {colibri.Style.UNDERLINE}install package.ypp{colibri.Style.RESET_ALL}.')


def _pam_init_():
    global pam
    pam = PackageInstaller(addr)


def pam_make(servername):
    logger.add(f"Making connection to Nexus-Server")
    sys.stdout.write(f'\r{colibri.Fore.CYAN}Establishing connection to {servername}{colibri.Fore.RESET}\n')
    p2 = threading.Thread(target=_pam_init_)
    p2.start()
    while "pam" not in globals().keys():
        if _.failed:
            p2.join()
            return 1
    return 0


def main(args):
    args = argsparser(args)
    _main(args)


def find_installation(name):
    o = make_path(name)
    return os.path.exists(o)
