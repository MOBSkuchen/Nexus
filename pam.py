import os
import time
from utils import fmt_file, sizeof_fmt, erase as _erase, yes_no
import argparser as ap
import sys
import socket
import colibri
import errors as xsErrors
import requests
from logger import logger
import zstandard as zst
from options import optionloader
import io_pack as io
from ypp_filetype import YPP
from zipfile import ZipFile

__version__ = '1.7'
pkg_size = 25000
addr = ('suprime.sonvogel.com', 25583)


class NexusServerConnector:
    def __init__(self, _addr=addr, _pkg_size=pkg_size):
        self.pkg_size = _pkg_size
        self.addr = _addr
        self.connection = socket.socket()
        # self.connection.settimeout(0.5)

        # Protected members
        self._got_resp = False
        self._got_accepted = False
        # ========================

        self._contact()

    def __del__(self):
        self.connection.close()
        del self

    def _server_dead(self):
        _.failed = 9
        xsErrors.stderr(9,
                        msg="Connection could NOT be established",
                        cause=["Server could not be reached"],
                        fix=["Check your internet connection",
                             "Update Nexus (PaM)"]
                        )
        xsErrors.sys_exit(_.failed)

    def _server_refused(self):
        _.failed = 9
        xsErrors.stderr(9, msg="Server refused connection",
                        cause=["The Server currently does not expect/want a connection with you"],
                        fix=["Please wait a bit"])
        xsErrors.sys_exit(_.failed)

    def _contact(self):
        try:
            self.connection.connect(self.addr)
        except ConnectionRefusedError:
            self._server_dead()
            return
        _erase(1)
        sys.stdout.write(
            f'\r{colibri.Fore.LIGHTGREEN_EX}Connected to {colibri.Style.BRIGHT}Nexus-Server{colibri.Style.RESET_ALL}\n')
        self.connection.send(b'0')
        response = self.connection.recv(1)
        if response == b'1':
            _erase(1)
        elif response == b'0':
            self._server_refused()
        else:
            print(response)
            print(response)
            print(response)
            self._server_dead()

    def get_manual(self, name):
        self.connection.send(b'5')
        self.connection.recv(1)
        self.connection.send(name.encode())
        return self.connection.recv(2048)

    def list_manuals(self, pattern):
        self.connection.send(b'6')
        self.connection.recv(1)
        self.connection.send(pattern.encode())
        response = self.connection.recv(1024).decode().split(";")
        return response

    def report(self, content: str):
        self.connection.send(b'4')
        self.connection.recv(1)
        self.connection.send(content.encode())

    def list(self, pattern):
        self.connection.send(b'1')
        self.connection.recv(1)
        self.connection.send(pattern.encode())
        response = self.connection.recv(100).decode().split(";")
        return response

    def exists(self, name):
        self.connection.send(b'2')
        self.connection.recv(1)
        self.connection.send(name.encode("utf-8"))
        response = self.connection.recv(1).decode()
        return response == "1"

    @staticmethod
    def show(cur, size):  # https://stackoverflow.com/questions/3160699/python-progress-bar
        render_size = 40
        x = int(render_size * cur / size)
        print(
            f"{colibri.Fore.LIGHTGREEN_EX}Downloading{colibri.Fore.RESET}: {colibri.Fore.LIGHTBLACK_EX}[{colibri.Fore.RESET}{(colibri.Fore.WHITE + u'█' + colibri.Fore.RESET) * x}{((colibri.Fore.BLACK + u'█' + colibri.Fore.RESET) * (render_size - x))}{colibri.Fore.LIGHTBLACK_EX}]{colibri.Fore.RESET} {sizeof_fmt(cur)}/{sizeof_fmt(size)}     ",
            end='\r', file=sys.stdout
            , flush=True)

    def download(self, filename, name):
        self.connection.send(b'3')
        self.connection.recv(1)
        self.connection.send(name.encode())
        self.connection.recv(3)  # After 2 hours of debugging, this fixes it for some reason
        size = int(self.connection.recv(100).decode())
        self.connection.send(b'1')
        s_ = sizeof_fmt(size)
        logger.add(f"Download package : {name}")
        io.output(
            f'{colibri.Fore.LIGHTWHITE_EX}Downloading package{colibri.Fore.RESET} [{name} - {s_}] to {fmt_file(filename)}')
        done = 0
        with open(filename, 'wb') as filewriter:
            try:
                while True:
                    data = self.connection.recv(self.pkg_size)
                    got = len(data)
                    done += got
                    self.show(done, size)
                    filewriter.write(data)
                    if got != self.pkg_size:
                        # sys.stdout.write('')
                        io.output(
                            f'{colibri.ERASE_LINE}{colibri.CURSOR_UP_ONE}{colibri.ERASE_LINE}{colibri.Fore.GREEN}Downloaded package{colibri.Fore.RESET} [{name} - {s_}] to {fmt_file(filename)}')
                        logger.add(f"Download finished")
                        self.connection.send(b'1')
                        break
                    time.sleep(0.05)
                    self.connection.send(b'O')
            except KeyboardInterrupt:
                self.connection.close()
                logger.add(f"Download interrupted")
                io.output(
                    f'{colibri.Fore.RED}Connection closed due to interrupt{colibri.Fore.RESET}                                    ')
                if not filewriter.closed:
                    filewriter.close()
                return 0
            if not filewriter.closed:
                filewriter.close()


def make_path(file):
    return os.path.join(optionloader.make_path(optionloader.directories[0]), file) if not _.local else file


def custom_download(url, path):
    with requests.get(url, stream=True) as r:
        with open(path, 'wb') as filewriter:
            try:
                if "Content-Length" not in r.headers:
                    xsErrors.stderr(23, msg=f"Invalid headers ('Content-Length' not in headers)",
                                    cause=["The URL headers do not include 'Content-Length' and thus are invalid"],
                                    fix=["Provide a downloadable URL"])
                    filewriter.close()
                    return 0
                size = int(r.headers.get('Content-Length'))
                io.output(
                    f'{colibri.Fore.LIGHTWHITE_EX}Downloading package{colibri.Fore.RESET} [{url} - {sizeof_fmt(size)}] to {fmt_file(path)}')
                for i, chunk in enumerate(r.iter_content(chunk_size=pkg_size)):
                    cur = i * pkg_size
                    filewriter.write(chunk)
                    NexusServerConnector.show(cur, size)
                    time.sleep(.1)
                    sys.stdout.flush()
            except KeyboardInterrupt:
                io.output(
                    f'{colibri.Fore.RED}Connection closed due to interrupt{colibri.Fore.RESET}                                    ')
                if not filewriter.closed:
                    filewriter.close()
                return 0
            if not filewriter.closed:
                filewriter.close()
        io.output(
            f'{colibri.ERASE_LINE}{colibri.CURSOR_UP_ONE}{colibri.ERASE_LINE}{colibri.Fore.GREEN}Downloaded package{colibri.Fore.RESET} [{url} - {sizeof_fmt(size)}] to {fmt_file(path)}')
        logger.add(f"Download finished")


def get_url_filename(url):
    fragment_removed = url.split("#")[0]  # keep to left of first #
    query_string_removed = fragment_removed.split("?")[0]
    scheme_removed = query_string_removed.split("://")[-1].split(":")[-1]
    if scheme_removed.find("/") == -1:
        return "download"
    bn = os.path.basename(scheme_removed)
    return bn if bn else "download"


def install(i):
    if not _.output:
        if _.custom:
            o = get_url_filename(i)
        else:
            o = i
    else:
        o = _.output
    if _.custom:
        tb = custom_download(i, make_path(o))
        return make_path(o) if tb != 0 else tb
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
        if pam.download(make_path(o), i) == 0:
            return 0
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
        _erase(1)
        io.output(f'{colibri.Fore.YELLOW}YPP{colibri.Fore.RESET} : Loaded')
        try:
            _erase(1)
            io.output(f'{colibri.Fore.YELLOW}YPP{colibri.Fore.RESET} : {colibri.Fore.GREEN}Decompressing')
            if _.output:
                dump = _.output
            elif _.local:
                dump = os.path.join(os.path.curdir, ypp.name)
            else:
                dump = os.path.join(os.path.dirname(i), ypp.name)
            ypp.expand(dump)
            _erase(2)
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
    elif i.endswith('.zip'):
        o = i[:(len(i) - 4)] if not _.output else _.output
        logger.add(f'Decompressing ZIP-file {i} to {o}')
        try:
            io.output(f'{colibri.Fore.YELLOW}ZIP{colibri.Fore.RESET} : {colibri.Fore.GREEN}Decompressing')
            with open(i, 'rb') as filereader:
                zf = ZipFile(filereader)
                zf.extractall(o)
            _erase(1)
            io.output(f'{colibri.Fore.YELLOW}ZIP{colibri.Fore.RESET} : {colibri.Fore.GREEN}Decompressed')
        except Exception as ex:
            logger.add(str(ex), tone="ZIP")
            xsErrors.stderr(12, msg=f"Cannot decompress ZIP",
                            cause=["zipfile::ZipFile.extractall() raised an error (dumped to log)"],
                            fix=["See log"])
    else:
        xsErrors.stderr(13, msg="Filetype is not supported",
                        cause=["The file is not of type .ypp or .zst"])


class _:
    failed = False
    custom = False
    local = False
    output = None
    active = False


def argsparser(args):
    if len(args) == 0:
        io.output(
            f'{colibri.Fore.BLUE}{colibri.Style.BRIGHT}PAM{colibri.Style.RESET_ALL} : {colibri.Fore.MAGENTA}{__version__}{colibri.Fore.RESET}')
        io.output(f'{colibri.Fore.RED}Please pass in some arguments{colibri.Fore.RESET}')
        return
    parser = ap.ArgumentParser(args, check=True)
    parser.add_argument("install", calls=["-i", "install"], exclusives=["remove", "update"], input_=True)
    parser.add_argument("remove", calls=["-r", "remove"], exclusives=["install", "unpack"], input_=True)
    parser.add_argument("unpack", calls=["-u", "--unpack"], exclusives=["remove"])

    parser.add_argument("local", calls=["-l", "--local"])
    parser.add_argument("custom", calls=["-c", "--custom"])
    parser.add_argument("output", calls=["-o", "--output"], input_=True)
    parser.add_argument("size", calls=["-s", "--size"], input_=True)

    options = parser()
    return options


def get_manual(name):
    nsc = NexusServerConnector()
    return nsc.get_manual(name)


def list_manuals() -> list[str]:
    nsc = NexusServerConnector()
    return nsc.list_manuals("*")


def _main(options):
    if not options:
        return
    options_l = options.keys()
    if "local" in options_l:
        _.local = True
    if "output" in options_l and "unpack" not in options_l:
        _.output = options["output"]
    if "custom" in options_l:
        _.custom = True
    if "size" in options_l:
        global pkg_size
        if not _.custom:
            xsErrors.stderr(14, msg=f"Size may not be used on a Nexus-Package", cause=["Size invoked without custom"])
        else:
            if not options["size"].isnumeric():
                xsErrors.stderr(14, msg=f"Invalid Size [{options['size']}]", cause=["Size must be numeric"])
            else:
                pkg_size = int(options["size"])
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
    _.active = False
    if "pam" in globals().keys():
        del globals()["pam"]


def _pam_init_():
    global pam
    pam = NexusServerConnector(addr)


def pam_make(servername):
    logger.add(f"Making connection to Nexus-Server")
    sys.stdout.write(f'\r{colibri.Fore.CYAN}Establishing connection to {servername}{colibri.Fore.RESET}\n')
    _pam_init_()
    if _.failed:
        return 1


def main(args):
    args = argsparser(args)
    _main(args)


def find_installation(name):
    o = make_path(name)
    return os.path.exists(o)
