import sys
from utils import fmt_file
import os
import colibri
from io import StringIO
from pathlib import Path
import utils as _utils

_dummy_stdout = StringIO()
lines_printed = 0


def output(*args, end="\n"):
    global lines_printed
    out = " ".join(args) + end
    lines_printed += 1
    _dummy_stdout.write(out)
    sys.stdout.write(out)


def crit_err(num, name, msg=None, cause: str = None):
    output(
        f'{colibri.Fore.LIGHTRED_EX}{colibri.Style.BRIGHT}{name} {colibri.Style.RESET_ALL}: {colibri.Fore.RED}{msg}{colibri.Fore.RESET}')
    if cause:
        output(f'{colibri.Style.BRIGHT}{colibri.Fore.RED}This error was caused by{colibri.Style.RESET_ALL} : {cause}')
    output(f"\n{colibri.Fore.LIGHTRED_EX}{colibri.Style.BRIGHT}THIS ERROR IS NOT FIXABLE {colibri.Style.RESET_ALL}")
    sys.exit(num)


if sys.platform == 'win32':
    # Windows
    _utils.std_path = os.path.join(os.environ['APPDATA'], 'nexus')
elif sys.platform == 'linux':
    # Linux
    home = Path.home()
    _utils.std_path = os.path.join(home, "nexus")
else:
    crit_err(21, "SupportError", msg=f"You OS is not currently supported by Nexus: {sys.platform}")
    sys.exit(21)


def title_screen():
    output(f"""
{colibri.Fore.CYAN}███╗   ██╗  {colibri.Fore.MAGENTA}███████╗ {colibri.Fore.YELLOW}   ██╗  ██╗{colibri.Fore.GREEN}    ██╗   ██╗{colibri.Fore.LIGHTBLUE_EX}   ███████╗
{colibri.Fore.CYAN}████╗  ██║  {colibri.Fore.MAGENTA}██╔════╝ {colibri.Fore.YELLOW}   ╚██╗██╔╝{colibri.Fore.GREEN}    ██║   ██║{colibri.Fore.LIGHTBLUE_EX}   ██╔════╝
{colibri.Fore.CYAN}██╔██╗ ██║  {colibri.Fore.MAGENTA}█████╗{colibri.Fore.LIGHTBLACK_EX}       {colibri.Fore.YELLOW}╚███╔╝     {colibri.Fore.GREEN}██║   ██║   {colibri.Fore.LIGHTBLUE_EX}███████╗
{colibri.Fore.CYAN}██║╚██╗██║  {colibri.Fore.MAGENTA}██╔══╝   {colibri.Fore.YELLOW}    ██╔██╗ {colibri.Fore.GREEN}    ██║   ██║{colibri.Fore.LIGHTBLUE_EX}   ╚════██║
{colibri.Fore.CYAN}██║ ╚████║  {colibri.Fore.MAGENTA}███████╗ {colibri.Fore.YELLOW}   ██╔╝ ██╗{colibri.Fore.GREEN}    ╚██████╔╝{colibri.Fore.LIGHTBLUE_EX}   ███████║
{colibri.Fore.CYAN}╚═╝  ╚═══╝  {colibri.Fore.MAGENTA}╚══════╝ {colibri.Fore.YELLOW}   ╚═╝  ╚═╝{colibri.Fore.GREEN}     ╚═════╝ {colibri.Fore.LIGHTBLUE_EX}   ╚══════╝
    """)


def man_logger(x):
    from logger import logger
    logger.add(x)


def input_gather():
    from options import optionloader
    _start = f"{colibri.Fore.LIGHTBLACK_EX}{fmt_file(os.curdir) if optionloader['show-curdir'] else ''}>{colibri.Fore.RESET} "
    _input = input(f'{_start}')
    man_logger(f"User input : {_input}")
    return _input


def cmd_input(name):
    _start = f"{colibri.Fore.LIGHTBLACK_EX}{name}{colibri.Fore.MAGENTA}>{colibri.Fore.RESET} "
    _input = input(f'{_start}')
    man_logger(f"CMD-USER input : {_input}")
    return _input


def print_out(*msg, conc=" "):
    msg = conc.join(msg)
    man_logger(f"Sys response : {msg}")
    output(f'{colibri.Fore.MAGENTA}>>{colibri.Fore.RESET} {msg}')


def set_output(_io_):
    sys.stdout = _io_
    man_logger(f'Redirect IO to : {_io_}')


def primitive_warning(msg):
    output(
        f'{colibri.Fore.LIGHTYELLOW_EX}WARNING{colibri.Fore.RESET} : {colibri.Fore.MAGENTA}{msg}{colibri.Fore.RESET}')
