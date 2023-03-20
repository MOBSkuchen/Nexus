# Version is in utils.py
import io_pack as io
import ntl
import errors as xsErrors
import launcher
import pam
from options import optionloader
from utils import __version__
import commands as xsCmds
from logger import logger
import colibri
import sys
import paramiko
import multiprocessing as mp


def command_not_found(use, *args, fix):
    tb = optionloader.try_launch(use, args)
    if tb == 0:
        xsErrors.stderr(15,
                        msg=f"This command does not exist {colibri.Fore.LIGHTBLACK_EX}({optionloader.prt_ctx}){colibri.Fore.RESET}")
        if fix:
            io.output(f'{colibri.Style.BRIGHT}{colibri.Fore.LIGHTGREEN_EX}Maybe you meant {colibri.Style.RESET_ALL}: {xsErrors.errFormat(fix, 18)}')


def execute_command(cmd, args):
    cmds = [
        "access_man",
        "access_pam",
        "access_cd",
        "access_rem",
        "access_rmdir",
        "access_mkdir",
        "access_size",
        "access_restart",
        "access_exit",
        "access_version",
        "access_sleep",
        "access_purge",
        "access_pex",
        "access_ssh",
        "access_genptkey",
        "access_sftp",
        "access_con",
        "access_loc",
        "access_ypp",
        "access_ls"
    ]
    if cmd not in cmds:
        if optionloader["cmd-matching"]:
            fix = ntl.ntl.multi_distance(cmd[7:], cmds, optionloader["cmd-threshold"])
        else:
            fix = []
        command_not_found(cmd, *args, fix=fix)
    else:
        func = getattr(xsCmds, cmd)
        func(args)


def parse_inputs(args, _input):
    global ctx
    if len(_input) == 0:
        return
    else:
        if len(args) == 0:
            _adder = _input
            args = []  # not necessary, lol
        else:
            _adder = args.pop(0)
        cmd = "access_" + _adder  # This is to protect other functions
        optionloader.prt_ctx = cmd[7:len(cmd)]
        ctx = cmd
        execute_command(cmd, args)


def create_interface():
    from options import init_manualloader
    init_manualloader()
    while True:
        _input = io.input_gather()
        inputs = _input.split()
        parse_inputs(inputs, _input)
        logger.dump()


def version_func():
    io.output(
        f'{colibri.Fore.BLUE}{colibri.Style.BRIGHT}Nexus{colibri.Style.RESET_ALL} {colibri.Fore.MAGENTA}{__version__}{colibri.Fore.RESET}')
    io.output(
        f'{colibri.Fore.MAGENTA}{colibri.Style.BRIGHT}PaM{colibri.Style.RESET_ALL} {colibri.Fore.MAGENTA}{pam.__version__}{colibri.Fore.RESET}')
    io.output(
        f'{colibri.Fore.YELLOW}{colibri.Style.BRIGHT}Paramiko{colibri.Style.RESET_ALL} {colibri.Fore.MAGENTA}{paramiko.__version__}{colibri.Fore.RESET}')
    io.output(
        f'{colibri.Fore.GREEN}{colibri.Style.BRIGHT}Python{colibri.Style.RESET_ALL} {colibri.Fore.MAGENTA}{sys.version.split(" ")[0]}{colibri.Fore.RESET}')
    io.output(
        f'{colibri.Fore.RED}{colibri.Style.BRIGHT}NTL{colibri.Style.RESET_ALL} {colibri.Fore.MAGENTA}{ntl.__version__}{colibri.Fore.RESET}')
    io.output(
        f'{colibri.Fore.LIGHTYELLOW_EX}{colibri.Style.BRIGHT}PEx{colibri.Style.RESET_ALL} {colibri.Fore.MAGENTA}{launcher.__version__}{colibri.Fore.RESET}')


def help_func():
    io.output(f'''    {colibri.Style.BRIGHT}{colibri.Style.UNDERLINE}Nexus{colibri.Style.RESET_ALL} - V{__version__}
    - by MOBSkuchen

    {colibri.Style.UNDERLINE}Startup Arguments{colibri.Style.RESET_ALL}
        {colibri.Fore.GREEN}-h{colibri.Style.RESET_ALL} / {colibri.Fore.GREEN}--help{colibri.Style.RESET_ALL}     : Show this help message
        {colibri.Fore.GREEN}-v{colibri.Style.RESET_ALL} / {colibri.Fore.GREEN}--version{colibri.Style.RESET_ALL}  : Get version
        {colibri.Fore.GREEN}-q{colibri.Style.RESET_ALL} / {colibri.Fore.GREEN}--quiet{colibri.Style.RESET_ALL}    : Do not show title
        {colibri.Fore.GREEN}-d{colibri.Style.RESET_ALL} / {colibri.Fore.GREEN}--debug{colibri.Style.RESET_ALL}    : Start in debug mode
    
    {colibri.Style.UNDERLINE}Commands{colibri.Style.RESET_ALL}
        {colibri.Fore.GREEN}pam{colibri.Style.RESET_ALL}       : PackageManager
        {colibri.Fore.GREEN}help{colibri.Style.RESET_ALL}      : Get help
        {colibri.Fore.GREEN}version{colibri.Style.RESET_ALL}   : Get version
        {colibri.Fore.GREEN}genptkey{colibri.Style.RESET_ALL}  : Generate a PT-key
        {colibri.Fore.GREEN}ssh{colibri.Style.RESET_ALL}       : Establish an SSH-Connection
        {colibri.Fore.GREEN}man{colibri.Style.RESET_ALL}       : Command manual
        {colibri.Fore.GREEN}mkdir{colibri.Style.RESET_ALL}     : Create directory
        {colibri.Fore.GREEN}rmdir{colibri.Style.RESET_ALL}     : Delete directory
        {colibri.Fore.GREEN}rem{colibri.Style.RESET_ALL}       : Delete file
        {colibri.Fore.GREEN}sleep{colibri.Style.RESET_ALL}     : Sleep for a certain amount of time
        {colibri.Fore.GREEN}purge{colibri.Style.RESET_ALL}     : Remove a certain number of lines
        {colibri.Fore.GREEN}size{colibri.Style.RESET_ALL}      : Get file / directory size
        {colibri.Fore.GREEN}con{colibri.Style.RESET_ALL}       : Search for pattern in files
        {colibri.Fore.GREEN}restart{colibri.Style.RESET_ALL}   : Restart Nexus
        {colibri.Fore.GREEN}exit{colibri.Style.RESET_ALL}      : Exit
    ''')


def debug_func():
    xsErrors.debug = True


suppress_ = False


def suppress():
    global suppress_
    suppress_ = True


def title():
    if not suppress_:
        io.title_screen()


def parse_args():
    from argparser import ArgumentParser
    parser = ArgumentParser(trim=True)
    parser.add_argument("help", action=help_func, calls=["--help", "-h"])
    parser.add_argument("version", action=version_func, calls=["--version", "-v"])
    parser.add_argument("debug", action=debug_func, calls=["--debug", "-b"])
    parser.add_argument("quiet", action=suppress, calls=["--quiet", "-q"])

    parser()


def bootstrap(pa):
    if pa:
        parse_args()
    title()
    create_interface()


def main(pa):
    try:
        bootstrap(pa)
    except KeyboardInterrupt:
        xsErrors.sys_exit(0, lc=True)
    except EOFError:
        xsErrors.sys_exit(0, lc=True)
    except PermissionError as ex:
        if xsErrors.debug:
            raise ex
        xsErrors.internal_error("Permission denied by OS", unexpected=False)  # It is unexpected, but shhhh
    except Exception as ex:
        if xsErrors.debug:
            raise ex
        tb = ex.__traceback__
        while tb.tb_next:
            tb = tb.tb_next
        filename = tb.tb_frame.f_code.co_filename.replace("\\", "/").split("/")
        filename = filename[len(filename) - 1]
        lineno = tb.tb_lineno
        name = tb.tb_frame.f_code.co_name
        _tb = ex.with_traceback(None)
        content = f'{colibri.Style.UNDERLINE}Internal error, please open an issue with the following traceback{colibri.Style.RESET_ALL} :\nIn {filename}::{name} [{lineno}]: \n{_tb}'
        io.output(content)
        io.output('=' * len(str(_tb)))


if __name__ == '__main__':
    mp.freeze_support()
    main(True)
