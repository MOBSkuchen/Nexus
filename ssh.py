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
from utils import erase, __version__
import socket

client = ssh.SSHClient()
client.set_missing_host_key_policy(ssh.AutoAddPolicy())


def connect(password, login, server):
    sys.stdout.write(f'\r{colibri.Fore.CYAN}Establishing connection to {colibri.Style.BRIGHT}{server}{colibri.Style.RESET_ALL}')
    try:
        sys.stdout.write('\n')
        client.connect(server, username=login, password=password)
        sys.stdout.write(f'\r{colibri.Fore.LIGHTGREEN_EX}Connected to '
                         f'{colibri.Style.BRIGHT}{server}{colibri.Style.RESET_ALL}                 \n')
        while True:
            inp = io.cmd_input(f"{login}@{server}")
            stdin, stdout, stderr = client.exec_command(inp)
            if o:=stderr.read():
                out = o.decode()
                for i in out.splitlines():
                    io.print_out(i)
            else:
                out = stdout.read().decode()
                for i in out.splitlines():
                    io.print_out(i)
    except socket.gaierror:
        sys.stdout.write('\n')
        xsErrors.stderr(18, msg=f"Connection could not be established because GAI failed",
                        cause=["The server was not found or does not exist"])
    except KeyboardInterrupt:
        erase(1)
        io.print_out(f"Closed SSH-Connection")
        client.close()
    except Exception:
        xsErrors.stderr(18, msg=f"Unexpected error during SSH-Connection")
    client.close()


def argparser(args):
    if len(args) == 0:
        print(f'{colibri.Fore.BLUE}{colibri.Style.BRIGHT}Nexus-SSH{colibri.Style.RESET_ALL} : {colibri.Fore.MAGENTA}{__version__}{colibri.Fore.RESET}')
        print(f'{colibri.Fore.RED}Please pass in some arguments{colibri.Fore.RESET}')
        return
    parser = ArgumentParser(args)
    parser.add_argument(name='login-file', calls=['--login_file', '-lf'], input_=True)
    parser.add_argument(name='login', calls=['--login', '-l'], input_=True, dependencies=["server", "password"])
    parser.add_argument(name='password', calls=['--password', '-p'], input_=True, dependencies=["server", "login"])
    parser.add_argument(name='server', calls=['--server', '-s'], input_=True, dependencies=["login", "password"])

    ag: dict = parser()
    if parser.failed:
        return
    ags = ag.keys()

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

    if 'login' in ags or 'password' in ags or 'server' in ags:
        connect(ag['password'], ag['login'], ag['server'])


def main(params):
    argparser(params)
