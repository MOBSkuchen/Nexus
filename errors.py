import colibri
import sys
from utils import clr
from logger import logger
import io_pack as io


def sys_exit(num, *, lc=False):
    logger.dump()
    clr()
    io.output(f'\r{colibri.Style.NORMAL}Exited with code {colibri.Fore.CYAN}{num}', end="")
    sys.stdout.write(colibri.Style.RESET_ALL)
    if not lc:
        sys.exit(num)
    else:
        exit(num)


alerts = False
debug = False
errorDict = {
    1: "NameError",
    2: "ValueError",
    3: "IllegalCharacter",
    4: "SemanticError",
    5: "SyntaxError",
    6: "ImportError",
    7: "OverloadError",
    8: "ArgumentError",
    9: "NetworkError",
    10: "TypeError",
    11: "PackageError",
    12: "DecompressionError",
    13: "NotSupported",
    14: "OptionError",
    15: "CommandNotFound",
    16: "PathError",
    17: "AuthError",
    18: "SSHError",
    19: "ExtensionError",
    20: "LibraryError",
    21: "SupportError",
    22: "SFTPError"
}


def _errFormat(item, x):
    end = [item.pop(0)]
    for i in item:
        end.append(' ' * x + i)
    return "\n".join(end)


def crit_err(num, name=None, msg=None, cause=None, fix=None, lc=True):
    logger.add(f'Critical error {num} : {msg}')
    if not name:
        name = errorDict[num]
    io.output(
        f'{colibri.Fore.LIGHTRED_EX}{colibri.Style.BRIGHT}{name} {colibri.Style.RESET_ALL}: {colibri.Fore.RED}{msg}{colibri.Fore.RESET}')
    if cause:
        io.output(f'{colibri.Style.BRIGHT}{colibri.Fore.RED}This error was caused by{colibri.Style.RESET_ALL} : {_errFormat(cause, 27)}')
    if fix:
        io.output(f'{colibri.Style.BRIGHT}{colibri.Fore.LIGHTGREEN_EX}This may fix it {colibri.Style.RESET_ALL}: {_errFormat(fix, 18)}')
    sys_exit(num, lc=lc)


def stderr(num, name=None, msg=None, cause=None, fix=None):
    logger.add(f'STD error {num} : {msg}')
    if not name:
        name = errorDict[num]
    io.output(
        f'{colibri.Fore.LIGHTRED_EX}{colibri.Style.BRIGHT}{name} {colibri.Style.RESET_ALL}: {colibri.Fore.RED}{msg}{colibri.Fore.RESET}')
    if cause:
        io.output(f'{colibri.Style.BRIGHT}{colibri.Fore.RED}This error was caused by{colibri.Style.RESET_ALL} : {_errFormat(cause, 27)}')
    if fix:
        io.output(f'{colibri.Style.BRIGHT}{colibri.Fore.LIGHTGREEN_EX}This may fix it {colibri.Style.RESET_ALL}: {_errFormat(fix, 18)}')


def internal_error(msg, num=-1, unexpected=True, crit=True):
    logger.add(f'Internal error {num} : {msg}')
    io.output(f'{colibri.Fore.LIGHTRED_EX}{colibri.Style.BRIGHT}SYSTEM ERROR {colibri.Style.RESET_ALL}: {msg}')
    if unexpected:
        io.output(f'If this issue keeps appearing, please open an issue on github')
    logger.add(f'System error {num} : {msg}')
    if crit:
        sys_exit(num)


def stdwarning(msg):
    if alerts:
        io.output(f'{colibri.Fore.LIGHTYELLOW_EX}WARNING{colibri.Fore.RESET} : {colibri.Fore.MAGENTA}{msg}{colibri.Fore.RESET}')
