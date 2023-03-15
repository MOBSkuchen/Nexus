import os
import paramiko as ssh
import hashlib as hs
from pt_filetype import Key
import errors as xsErrors
import colibri
from argparser import ArgumentParser
import io_pack as io
import getpass as gp
import sys
from utils import erase
import socket

__version__ = "0.3"
client = ssh.SSHClient()
client.set_missing_host_key_policy(ssh.AutoAddPolicy())

sftp_con: ssh.SFTP = None


def connect(password, login, server):
    global sftp_con
    if sftp_con:
        io.print_out("SFTP is already connected, you must first terminate the session")
        return
    sys.stdout.write(f'\r{colibri.Fore.CYAN}Establishing connection to {colibri.Style.BRIGHT}{server}{colibri.Style.RESET_ALL}')
    try:
        sys.stdout.write('\n')
        client.connect(server, username=login, password=password)
        sys.stdout.write(f'\r{colibri.Fore.LIGHTGREEN_EX}Connected to '
                         f'{colibri.Style.BRIGHT}{server}{colibri.Style.RESET_ALL}                 \n')
        sftp_con = client.open_sftp()
    except socket.gaierror as ex:
        if xsErrors.debug:
            raise ex
        sys.stdout.write('\n')
        xsErrors.stderr(18, msg=f"Connection could not be established because GAI failed",
                        cause=["The server was not found or does not exist"])
    except KeyboardInterrupt:
        erase(1)
        io.print_out("Aborted")
        client.close()
    client.close()


def terminate():
    global sftp_con
    if not sftp_con:
        io.print_out("SFTP is already closed")
        return
    name = sftp_con
    sftp_con.close()
    sftp_con = None
    io.print_out(f"Closed SFTP to {name}")


def dir(name):
    if sftp_con is None:
        xsErrors.stderr(22, msg=f"Connection has not been established", fix=["Establish a connection using 'sftp -lf <pt-key>'"])
        return
    try:
        sftp_con.chdir(name)
    except IOError:
        xsErrors.stderr(22, msg=f"Unable to change directory", cause=["The directory does not exist on server"])


def argparser(args):
    if len(args) == 0:
        print(f'{colibri.Fore.BLUE}{colibri.Style.BRIGHT}Nexus-SFTP{colibri.Style.RESET_ALL} : {colibri.Fore.MAGENTA}{__version__}{colibri.Fore.RESET}')
        print(f'{colibri.Fore.RED}Please pass in some arguments{colibri.Fore.RESET}')
        return
    parser = ArgumentParser(args)
    parser.add_argument(name="terminate", calls=["-t", "--terminate"], exclusives=["connect"], action=terminate)
    parser.add_argument(name="connect", calls=['-c', '--connect'])
    parser.add_argument(name="dir", calls=["dir"], input_=True)
    parser.add_argument(name="upload", calls=["-u", "--upload"], input_=True)
    parser.add_argument(name='login-file', calls=['--login_file', '-lf'], input_=True, dependencies=["connect"])
    parser.add_argument(name='login', calls=['--login', '-l'], input_=True, dependencies=["server", "password", "connect"])
    parser.add_argument(name='password', calls=['--password', '-p'], input_=True, dependencies=["server", "login", "connect"])
    parser.add_argument(name='server', calls=['--server', '-s'], input_=True, dependencies=["login", "password", "connect"])

    ag: dict = parser()
    if parser.failed:
        return
    ags = ag.keys()
    if "dir" in ags:
        dir(ag["dir"])
    if 'connect' in ags:
        if 'login-file' in ags:
            if not os.path.exists(ag['login-file']):
                xsErrors.stderr(16, msg=f"Login file not found {colibri.Fore.LIGHTBLACK_EX}{ag['login-file']}{colibri.Fore.RESET}")
                return
            data, protected = Key.unpack(ag['login-file'])
            if protected:
                ent = gp.getpass('Login file requires authentication\n> ').encode()
                ent = hs.sha256(hs.sha256(ent).hexdigest().encode()).hexdigest()
                key = Key.load(data, ent)
                if key:
                    connect(key.password, key.name, key.server)
                    return
                else:
                    xsErrors.stderr(17,
                                    msg=f"Invalid password")
                    return
            else:
                key = Key.load(data, None)
            connect(key.password, key.name, key.server)
            return

        elif 'login' in ags and 'password' in ags and 'server' and ags:
            connect(ag['password'], ag['login'], ag['server'])
        else:
            io.print_out("Not connecting, because no or not enough auth-args have been given")


def main(params):
    argparser(params)
