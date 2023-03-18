import os
import threading
import time
from utils import fmt_file
import argparser as ap
import sys
import socket
import colorama as colora
import errors as xsErrors
import zstandard as zst
from ypp_filetype import YPP

__version__ = '1.0'
colora.Style.UNDERLINE = "\033[4m"
addr = ('suprime.sonvogel.com', 25580)


def sizeof_fmt(num, suffix="B"):
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


class PackageInstaller:
    def __init__(self, _addr=addr):
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
        xsErrors.crit_err(9,
                          msg="Connection could NOT be established",
                          cause=["Server could not be reached"],
                          fix=["Check your internet connection",
                               "Maybe update Yupiter"]
                          )

    def _server_refused(self):
        _.failed = 9
        xsErrors.crit_err(9, msg="Server refused connection",
                          cause=["The Server currently does not expect/want a connection with you"],
                          fix=["Please wait a bit"])

    def _contact(self):
        try:
            self.connection.connect(self.addr)
        except ConnectionRefusedError:
            self._server_dead()
        self.connection.send(b'0')
        response = self.connection.recv(1)
        if response == b'1':
            sys.stdout.write('\r                                                                     ')
            sys.stdout.write(f'\r{colora.Fore.LIGHTGREEN_EX}Connected to '
                             f'{colora.Style.BRIGHT}PAM-Server {colora.Style.RESET_ALL}         \n')
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
        self.connection.send(name.encode())
        response = self.connection.recv(1).decode()
        return response == "1"

    def download(self, filename, name):
        self.connection.send(b'3')
        self.connection.recv(1)
        self.connection.send(name.encode())
        self.connection.send(b'1')
        size = int(self.connection.recv(100).decode())
        s_ = sizeof_fmt(size)
        print(f'Downloading package [{name} - {s_}] to {filename}')
        done = 0
        with open(filename, 'wb') as filewriter:
            try:
                while True:
                    data = self.connection.recv(1024)
                    got = len(data)
                    done += got
                    p = f'\r{sizeof_fmt(done)} / {s_}'
                    sys.stdout.write(p)
                    filewriter.write(data)
                    if got != 1024:
                        sys.stdout.write(f'\rDONE {" "* (len(p)-5)}')
                        break
                    time.sleep(0.05)
                    self.connection.send(b'O')
            except KeyboardInterrupt:
                self.connection.close()
                sys.stdout.write(f'\r{colora.Fore.RED}Connection closed due to interrupt{colora.Fore.RESET}')
                exit(-2)
            self.connection.send(b'1')


def version_func():
    print(
        f'{colora.Fore.BLUE}{colora.Style.BRIGHT}PAM{colora.Style.RESET_ALL} {colora.Fore.MAGENTA}{__version__}{colora.Fore.RESET}')
    print(
        f'{colora.Fore.GREEN}{colora.Style.BRIGHT}Python{colora.Style.RESET_ALL} {colora.Fore.MAGENTA}{sys.version.split(" ")[0]}{colora.Fore.RESET}')


def make_path(file):
    return os.path.join(os.environ['APPDATA'], 'pam', 'packages', file)


def help_func():
    print(f'''    {colora.Style.BRIGHT}{colora.Style.UNDERLINE}PackageManager{colora.Style.RESET_ALL} - V{__version__}
    - by MOBSkuchen

    {colora.Style.UNDERLINE}Package management options{colora.Style.RESET_ALL}
        {colora.Fore.GREEN}-i{colora.Style.RESET_ALL} / {colora.Fore.GREEN}install{colora.Style.RESET_ALL} <{colora.Fore.CYAN}package{colora.Style.RESET_ALL}>   : Install package
        {colora.Fore.GREEN}-r{colora.Style.RESET_ALL} / {colora.Fore.GREEN}remove{colora.Style.RESET_ALL}  <{colora.Fore.CYAN}package{colora.Style.RESET_ALL}>   : Remove package from IPD (Installed packages directory)
        
    {colora.Style.UNDERLINE}Other options{colora.Style.RESET_ALL}
        {colora.Fore.GREEN}-h{colora.Style.RESET_ALL} / {colora.Fore.GREEN}--help{colora.Style.RESET_ALL}     : Show this help message
        {colora.Fore.GREEN}-v{colora.Style.RESET_ALL} / {colora.Fore.GREEN}--version{colora.Style.RESET_ALL}  : Get version
    ''')


def yes_no():
    answer = input("[Y/N] > ").lower()
    if answer not in ["y", "yes"]:
        if answer not in ["n", "no"]:
            print(f'Invalid input. Please try again')
            return yes_no()
        else:
            return False
    else:
        return True


def install(i):
    pam_make()
    if not pam.exists(i):
        xsErrors.crit_err(11, msg=f"Package [{i}] does not exist on server")
        return 0
    if os.path.exists(make_path(i)):
        print(f'The package [{i}] already exists, are you sure you want to replace it')
        if yes_no():
            pam.download(make_path(i), i)
            return make_path(i)
        else:
            print('Alright, canceling...')
            return 0
    return 0


def remove(i):
    i = make_path(i)
    if not os.path.exists(i):
        xsErrors.crit_err(11, msg=f"Package [{fmt_file(i)}] does not exist", cause=["The file was not found in the IPD",
                                                                          "Maybe you did not download the file"])
    os.remove(i)


def unpack(i):
    if i.endswith('.zst'):
        dctx = zst.ZstdDecompressor()
        print(f'ZSTANDARD : Unpacking {i}...')
        with open(i, 'rb') as ifh, open(i[:(len(i)-4)], 'wb') as ofh:
            dctx.copy_stream(ifh, ofh)
        print(f'ZSTANDARD : Unpacked to {i[:(len(i)-4)]}...')
    elif i.endswith('.ypp'):
        print('YPP : Loading...')
        ypp = YPP.from_file(i)
        print(f'YPP : Loaded\nNAME : {ypp.name} V{ypp.version} (by {ypp.author})')
        try:
            print('YPP : Decompressing...')
            ypp.expand()
            print('YPP : Decompressed')
        except FileExistsError:
            xsErrors.crit_err(12, msg="Cannot decompress YPP",
                              cause=["The directory (to be dumped to) already exists"],
                              fix=["Delete the directory"])
    else:
        xsErrors.crit_err(13, msg="Filetype is not supported",
                          cause=["The file is not of type .ypp or .zst"])


class _:
    failed = False


def argsparser():
    if len(sys.argv) - 1 == 0:
        print(f'PAM - V{__version__}')
        print(f'Please pass in some arguments')
        return
    parser = ap.ArgumentParser(check=True)
    parser.add_argument("install", calls=["-i", "install"], exclusives=["remove", "update"], input_=True)
    parser.add_argument("remove", calls=["-r", "remove"], exclusives=["install", "unpack"], input_=True)
    parser.add_argument("unpack", calls=["-u", "unpack"], exclusives=["remove"])

    parser.add_argument("help", calls=["-h", "--help"], action=help_func)
    parser.add_argument("version", calls=["-v", "--version"], action=version_func)

    options = parser()
    options_l = options.keys()
    if "install" in options_l:
        tb = install(options["install"])
        if "unpack" in options_l and tb:
            unpack(tb)
    if "remove" in options_l:
        remove(options["remove"])


def check_pp_dir():
    check_pkm_dir()
    if not os.path.exists(p := os.path.join(os.environ['APPDATA'], 'pam', 'packages')):
        print('INFO : PAM/packages dir not found, creating...')
        os.mkdir(p)


def check_pkm_dir():
    if not os.path.exists(p := os.path.join(os.environ['APPDATA'], 'pam')):
        print('INFO : PAM dir not found, creating...')
        os.mkdir(p)


def _pam_init_():
    global pam
    pam = PackageInstaller(addr)


def pam_make():
    sys.stdout.write(f'\r{colora.Fore.CYAN}Establishing connection to PAM-server{colora.Fore.RESET}')
    p2 = threading.Thread(target=_pam_init_, daemon=True)
    p2.start()
    while "pam" not in globals().keys():
        if _.failed:
            exit()


def main():
    check_pp_dir()
    argsparser()


if __name__ == '__main__':
    main()
