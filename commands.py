import time
import colibri
import io_pack as io
import errors as xsErrors
from logger import logger
from main import version_func, help_func
from pam import main as pam_main_trigger
from pt_filetype import main as pt_main_trigger
from ssh import main as ssh_main_trigger
import options as sys_opts
import logger as sys_logger_pkg
from ypp_filetype import main as ypp_ft_trigger
from utils import fmt_file, yes_no, erase as sys_erase, stdout_size as sys_stdout_size, sizeof_fmt
import os
from pathlib import Path
from ntl import ntl
from sftp import main as sftp_main_trigger
from launcher import main as launcher_main_trigger
from shutil import rmtree


def access_help(params):
    if len(params) > 0:
        xsErrors.stdwarning(
            f"The command 'help' requires {colibri.Fore.CYAN}0{colibri.Fore.RESET} to {colibri.Fore.CYAN}1{colibri.Fore.RESET} argument(s)!")

    help_func()


def access_version(params):
    if len(params) > 0:
        xsErrors.stdwarning(f"The command 'version' requires {colibri.Fore.CYAN}0{colibri.Fore.RESET} arguments!")

    version_func()


def access_size(params):
    name = " ".join(params)
    if name == "":
        name = os.getcwd()
    if not os.path.exists(name):
        xsErrors.stderr(16,
                        msg=f"The file / directory [{fmt_file(name)}] could not be found not found")
        return
    else:
        if os.path.isfile(name):
            size = len(ntl.file_get(name))
        else:
            size = ntl.rec_size(name)
        io.print_out(f"The file / directory {colibri.Fore.LIGHTBLACK_EX}[{fmt_file(name)}]{colibri.Fore.RESET} has a total size of {colibri.Fore.CYAN}{sizeof_fmt(size)}{colibri.Fore.RESET}")


def access_restart(params):
    pid = str(sys_stdout_size())
    sys_erase(pid)

    logger.dump()

    # CLOSED

    sys_opts.optionloader = sys_opts.OptionLoader()
    sys_logger_pkg.logger = sys_logger_pkg.Logger()

    from main import main
    io.title_screen()
    main(False)


def access_exit(params):
    xsErrors.sys_exit(0)


def access_sleep(params):
    if len(params) == 0:
        xsErrors.stderr(8,
                        msg=f"The command 'sleep' requires {colibri.Fore.CYAN}1{colibri.Fore.RESET} argument!")
        return

    if len(params) > 0:
        xsErrors.stdwarning(f"The command 'sleep' requires {colibri.Fore.CYAN}1{colibri.Fore.RESET} argument!")

    pid = params.pop(0)

    if not pid.isnumeric():
        xsErrors.stderr(2, msg=f"This value must be numeric, not {pid}")
        return
    logger.add(f"Sleeping for {pid}")
    time.sleep(int(pid))


def access_purge(params):
    if len(params) == 0:
        xsErrors.stderr(8,
                        msg=f"The command 'purge' requires {colibri.Fore.CYAN}1{colibri.Fore.RESET} argument!")
        return

    if len(params) > 0:
        xsErrors.stdwarning(f"The command 'purge' requires {colibri.Fore.CYAN}1{colibri.Fore.RESET} argument!")

    pid = params.pop(0)

    if pid == 'all':
        pid = str(sys_stdout_size())

    if not pid.isnumeric():
        xsErrors.stderr(2, msg=f"This value must be numeric, not {pid}")
        return
    sys_erase(pid)


def access_mkdir(params):
    if len(params) == 0:
        xsErrors.stderr(8,
                        msg=f"The command 'mkdir' requires {colibri.Fore.CYAN}1{colibri.Fore.RESET} argument!")
        return
    name = " ".join(params)
    if os.path.exists(name):
        io.print_out(f"The directory [{name}] already exists, do you want to replace it?")
        if yes_no():
            rmtree(name)
        else:
            io.print_out("Cancelled")
            return
    os.mkdir(name)


def access_rmdir(params):
    if len(params) == 0:
        xsErrors.stderr(8,
                        msg=f"The command 'rmdir' requires {colibri.Fore.CYAN}1{colibri.Fore.RESET} argument!")
        return
    name = " ".join(params)
    if not os.path.exists(name):
        io.print_out(f"The directory to delete does not exist, skipping...")
        return
    io.print_out(f"Do you really want to delete the directory [{name}]?")
    if yes_no():
        rmtree(name)
    else:
        io.print_out("Cancelled")
        return


def access_rem(params):
    if len(params) == 0:
        xsErrors.stderr(8,
                        msg=f"The command 'rem' requires {colibri.Fore.CYAN}1{colibri.Fore.RESET} argument!")
        return
    name = " ".join(params)
    if not os.path.exists(name):
        io.print_out(f"The file to delete does not exist, skipping...")
        return
    io.print_out(f"Do you really want to delete the file [{name}]?")
    if yes_no():
        os.remove(name)
    else:
        io.print_out("Cancelled")
        return


def access_man(params):
    if len(params) > 1:
        xsErrors.stdwarning(
            f"The command 'man' requires {colibri.Fore.CYAN}1{colibri.Fore.RESET} argument!")
    if len(params) == 0:
        xsErrors.stderr(8,
                        msg=f"The command 'man' requires {colibri.Fore.CYAN}1{colibri.Fore.RESET} argument!")
        return
    cmd = params.pop(0)
    if cmd in sys_opts.manualoader.makes.keys():
        io.print_out(f"Viewing help for {cmd} :")
        io.output(colibri.format(sys_opts.manualoader[cmd]))
    else:
        xsErrors.stderr(2, msg=f"The command [{cmd}] has no manual",
                        cause=["options.py->manualoader has no item cmd"],
                        fix=["Provide one of the commands shown in help"])


def access_pam(params):
    pam_main_trigger(params)


def access_cd(params):
    if len(params) == 0:
        os.chdir(os.path.splitdrive(os.getcwd())[0] + "/")
        return
    path = " ".join(params)
    path = os.path.join(os.getcwd(), path)
    if not os.path.exists(path):
        xsErrors.stderr(16, msg=f"Cannot cd to path {colibri.Fore.LIGHTBLACK_EX}({path}){colibri.Fore.RESET}")
        return
    os.chdir(path)


def access_genptkey(params):
    pt_main_trigger(params)


def access_pex(params):
    launcher_main_trigger(params)


def access_ssh(params):
    ssh_main_trigger(params)


def access_sftp(params):
    sftp_main_trigger(params)


def _mapping(i):
    def _(h):
        return os.path.relpath(str(h).replace("\\", "/"))

    return list(map(_, i))


def access_con(params):
    if "-r" in params:
        i = params.index("-r")
        params.pop(i)
        r = True
    elif "--recursive" in params:
        i = params.index("--recursive")
        params.pop(i)
        r = True
    else:
        r = False
    pattern = " ".join(params)
    if r:
        paths = ntl.rec_path_search(".", pattern)
        total = 0
        io.print_out(f"Searching for '{pattern}' in {colibri.Fore.CYAN}{len(paths)}{colibri.Fore.RESET} files")
        for path in paths:
            total += path.amount
            if path.amount:
                io.print_out(f"Found {colibri.Fore.CYAN}{path.amount}{colibri.Fore.RESET} in {fmt_file(path.name)}")
        io.print_out(f"Found a total of {colibri.Fore.CYAN}{total}{colibri.Fore.RESET} matches")
        return
    else:
        paths = list(os.listdir(os.getcwd()))
    io.print_out(f"Searching for '{pattern}' in {colibri.Fore.CYAN}{len(paths)}{colibri.Fore.RESET} files")
    total = 0
    for path in paths:
        points = ntl.file_search(path, pattern)
        points = len(points)
        total += points
        if points:
            io.print_out(f"Found {colibri.Fore.CYAN}{points}{colibri.Fore.RESET} in {fmt_file(path)}")
        elif points == -1:
            xsErrors.stdwarning(f"NTL::file_search ran into an error")
    io.print_out(f"Found a total of {colibri.Fore.CYAN}{total}{colibri.Fore.RESET} matches")


def access_loc(params):
    if "-r" in params:
        i = params.index("-r")
        params.pop(i)
        r = True
    elif "--recursive" in params:
        i = params.index("--recursive")
        params.pop(i)
        r = True
    else:
        r = False
    pattern = " ".join(params)
    if r:
        paths = list(Path(os.getcwd()).rglob(pattern))
    else:
        paths = list(Path(os.getcwd()).glob(pattern))
    paths = _mapping(paths)
    fs = ""
    for i, fn in enumerate(paths):
        if i % 4 == 0 and i > 0:
            fs += "\n"
        fs += f"{colibri.Fore.RESET}{fn} "
    io.print_out(
        f"Found {colibri.Fore.CYAN}{len(paths)}{colibri.Fore.RESET} matches{' (recursive)' if r else ''}:\n" + fs)


def access_ypp(params):
    ypp_ft_trigger(params)


def access_ls(params):
    def _empty(name):
        return len(os.listdir(name)) == 0

    if len(params) > 0:
        xsErrors.stdwarning(f"The command 'ls' requires {colibri.Fore.CYAN}0{colibri.Fore.RESET} arguments!")
    io.print_out(f"Viewing all files and directories in {fmt_file(os.getcwd())}")
    fs = ""
    paths = os.listdir(os.getcwd())
    for i, fn in enumerate(paths):
        if i % 4 == 0 and i > 0:
            fs += "\n"
        if os.path.isdir(fn):
            fs += f"{colibri.Fore.BLUE}{fn} " if not _empty(fn) else f"{colibri.Fore.BLACK}{fn} "
        else:
            fs += f"{colibri.Fore.RESET}{fn} "

    if len(paths) % 4 != 0:
        fs += "\n"

    for line in fs.splitlines():
        io.print_out(line)
