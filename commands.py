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


class Manual:
    help = f"""   {colibri.Style.BRIGHT}Help{colibri.Style.RESET_ALL} - help
        Get help for commands and arguments"""
    version = f"""   {colibri.Style.BRIGHT}Version{colibri.Style.RESET_ALL} - version
        Displays the current Nexus and API version(s)"""
    genptkey = f"""   {colibri.Style.BRIGHT}Generate PT-key{colibri.Style.RESET_ALL} - genptkey {colibri.Fore.LIGHTMAGENTA_EX}filename{colibri.Fore.RESET} {colibri.Fore.LIGHTMAGENTA_EX}server{colibri.Fore.RESET} {colibri.Fore.LIGHTMAGENTA_EX}login{colibri.Fore.RESET} {colibri.Fore.LIGHTMAGENTA_EX}password{colibri.Fore.RESET} [{colibri.Fore.BLUE}auth{colibri.Fore.RESET}]
        Generate a PT-key. (for Nexus-SSH)
        PT-keys are used for quick Nexus-SSH connections.
        
        {colibri.Style.UNDERLINE}Arguments{colibri.Style.RESET_ALL}:
        {colibri.Fore.GREEN}filename{colibri.Fore.RESET}   : Key-filename   ----|
        {colibri.Fore.GREEN}server{colibri.Fore.RESET}     : Target server  -------> {colibri.Style.UNDERLINE}All of these must be invoked together{colibri.Style.RESET_ALL}
        {colibri.Fore.GREEN}login{colibri.Fore.RESET}      : SSH-username   ----|
        {colibri.Fore.GREEN}password{colibri.Fore.RESET}   : SSH-password   ----|
        
        {colibri.Fore.GREEN}auth{colibri.Fore.RESET}       : Key-password {colibri.Fore.LIGHTBLACK_EX}(optional){colibri.Fore.RESET}

        """
    ssh = f"""   {colibri.Style.BRIGHT}Nexus-SSH{colibri.Style.RESET_ALL} - ssh [{colibri.Fore.BLUE}-l{colibri.Fore.RESET} {colibri.Fore.GREEN}login{colibri.Fore.RESET}] [{colibri.Fore.BLUE}-p{colibri.Fore.RESET} {colibri.Fore.GREEN}password{colibri.Fore.RESET}] [{colibri.Fore.BLUE}-s{colibri.Fore.RESET} {colibri.Fore.GREEN}server{colibri.Fore.RESET}] [{colibri.Fore.BLUE}-lf{colibri.Fore.RESET} {colibri.Fore.GREEN}login-file{colibri.Fore.RESET}]
    Establish a connection to an SSH server.
    Uses the paramiko module.
        
    {colibri.Style.UNDERLINE}Arguments{colibri.Style.RESET_ALL}:
        {colibri.Fore.GREEN}login{colibri.Fore.RESET} ({colibri.Fore.BLUE}-l{colibri.Fore.RESET})       : SSH-username   ----|
        {colibri.Fore.GREEN}password{colibri.Fore.RESET} ({colibri.Fore.BLUE}-p{colibri.Fore.RESET})    : SSH-password   -------> {colibri.Style.UNDERLINE}All of these must be invoked together{colibri.Style.RESET_ALL}
        {colibri.Fore.GREEN}server{colibri.Fore.RESET} ({colibri.Fore.BLUE}-s{colibri.Fore.RESET})      : Target server  ----|

        {colibri.Fore.GREEN}login-file{colibri.Fore.RESET} ({colibri.Fore.BLUE}-lf{colibri.Fore.RESET}) : Credentials file (generate using 'genptkey')
                         V If you use a .pt file for authentication it may require a password to open the file."""
    pam = f'''   {colibri.Style.BRIGHT}PackageManager{colibri.Style.RESET_ALL} - pam [{colibri.Fore.BLUE}-i{colibri.Fore.RESET} {colibri.Fore.GREEN}install{colibri.Fore.RESET}] [{colibri.Fore.BLUE}-r{colibri.Fore.RESET} {colibri.Fore.GREEN}remove{colibri.Fore.RESET}] [{colibri.Fore.BLUE}-u{colibri.Fore.RESET} {colibri.Fore.GREEN}unpack{colibri.Fore.RESET}] [{colibri.Fore.BLUE}-o{colibri.Fore.RESET} {colibri.Fore.GREEN}output{colibri.Fore.RESET}] [{colibri.Fore.BLUE}-l{colibri.Fore.RESET} {colibri.Fore.GREEN}--local{colibri.Fore.RESET}]
    
    Downloads and installs packages to %APPDATA%/nexus/packages/
    Requires an internet connection.
    
    {colibri.Style.UNDERLINE}Package management options{colibri.Style.RESET_ALL}
        {colibri.Fore.GREEN}-i{colibri.Style.RESET_ALL} / {colibri.Fore.GREEN}install{colibri.Style.RESET_ALL} <{colibri.Fore.BLUE}package{colibri.Style.RESET_ALL}>   : Install package
        {colibri.Fore.GREEN}-r{colibri.Style.RESET_ALL} / {colibri.Fore.GREEN}remove{colibri.Style.RESET_ALL}  <{colibri.Fore.BLUE}package{colibri.Style.RESET_ALL}>   : Remove package from IPD (Installed packages directory)
        {colibri.Fore.GREEN}-u{colibri.Style.RESET_ALL} / {colibri.Fore.GREEN}unpack{colibri.Style.RESET_ALL}              : Unpack downloaded package ({colibri.Style.UNDERLINE}Requires install{colibri.Style.RESET_ALL})

    {colibri.Style.UNDERLINE}Downloading options{colibri.Style.RESET_ALL}
        {colibri.Fore.GREEN}-o{colibri.Style.RESET_ALL} / {colibri.Fore.GREEN}output{colibri.Style.RESET_ALL} <{colibri.Fore.BLUE}package{colibri.Style.RESET_ALL}>    : Change output directory
        {colibri.Fore.GREEN}-l{colibri.Style.RESET_ALL} / {colibri.Fore.GREEN}--local{colibri.Style.RESET_ALL}             : Unpack downloaded package
'''
    man = f'''   {colibri.Style.BRIGHT}Manual{colibri.Style.RESET_ALL} - man {colibri.Fore.LIGHTMAGENTA_EX}command{colibri.Fore.RESET}
    
    Gets extra information about a command
    {colibri.Style.UNDERLINE}Arguments{colibri.Style.RESET_ALL}:
        {colibri.Fore.GREEN}command{colibri.Fore.RESET}   : Name of the command
    '''
    ypp = f'''   {colibri.Style.BRIGHT}Yupiter-Project{colibri.Style.RESET_ALL} - ypp {colibri.Fore.LIGHTMAGENTA_EX}mode{colibri.Fore.RESET} [{colibri.Fore.LIGHTGREEN_EX}name version author {colibri.Fore.LIGHTCYAN_EX}*dependencies{colibri.Fore.RESET}] [{colibri.Fore.MAGENTA}auth{colibri.Fore.RESET}]
    
    Compile files to a .ypp file.
    YPP-files are used for easy package management with PAM.
    Please note: YPP-files have no protection. The content of all files get written to
                 one central file and compressed using zstandard.
    YPP-files also carry metadata like version, author and dependencies.
    They get expanded (decompressed) into a folder
    
    {colibri.Style.UNDERLINE}Arguments{colibri.Style.RESET_ALL}:
        {colibri.Fore.GREEN}mode{colibri.Fore.RESET}         : YPP utilization mode. 
                       Has to be one of :
                           - {colibri.Fore.MAGENTA}expand{colibri.Fore.RESET} : Decompress from a .ypp file to a folder
                           - {colibri.Fore.MAGENTA}dump  {colibri.Fore.RESET} : Dump files into a .ypp file
    {colibri.Style.UNDERLINE}DUMP Arguments{colibri.Style.RESET_ALL}:         
        {colibri.Fore.GREEN}name{colibri.Fore.RESET}          : YPP-name
        {colibri.Fore.GREEN}version{colibri.Fore.RESET}       : YPP-version
        {colibri.Fore.GREEN}author{colibri.Fore.RESET}        : Project author/creator
        {colibri.Fore.GREEN}pattern{colibri.Fore.RESET}       : Pattern of the files to compile
       {colibri.Fore.LIGHTCYAN_EX}*dependencies{colibri.Fore.RESET}  : YPPs needed for this project
    {colibri.Style.UNDERLINE}EXPAND Arguments{colibri.Style.RESET_ALL}:
        {colibri.Fore.GREEN}filename{colibri.Fore.RESET}       : Name of the .ypp file (does not have to be .ypp)
    '''

    cd = f'''   {colibri.Style.BRIGHT}Change dir{colibri.Style.RESET_ALL} - cd {colibri.Fore.LIGHTMAGENTA_EX}directory{colibri.Fore.RESET}
   
   Change CWD to another directory.
   Example 'cd path' changes dir to CWD/path
   
   Leave arguments blank to head to C:/ (or equivalent)
   
   {colibri.Style.UNDERLINE}Arguments{colibri.Style.RESET_ALL}:
       {colibri.Fore.GREEN}directory{colibri.Fore.RESET}   : Valid directory name 
    '''

    loc = f'''   {colibri.Style.BRIGHT}Locate{colibri.Style.RESET_ALL} - loc {colibri.Fore.LIGHTMAGENTA_EX}filepattern{colibri.Fore.RESET}
    
    Searches for the file pattern and lists the
    found files
    
    {colibri.Style.UNDERLINE}Arguments{colibri.Style.RESET_ALL}:
        {colibri.Fore.GREEN}filepattern{colibri.Fore.RESET}   : File pattern (for example "*.py")
'''

    rmdir = f'''   {colibri.Style.BRIGHT}Remove directory{colibri.Style.RESET_ALL} - rmdir {colibri.Fore.LIGHTCYAN_EX}*dirname{colibri.Fore.RESET}

    Remove a directory, it may contain files and subdirectories

    {colibri.Style.UNDERLINE}Arguments{colibri.Style.RESET_ALL}:
        {colibri.Fore.GREEN}dirname{colibri.Fore.RESET}   : Valid directory name
'''

    mkdir = f'''   {colibri.Style.BRIGHT}Make directory{colibri.Style.RESET_ALL} - mkdir {colibri.Fore.LIGHTCYAN_EX}*dirname{colibri.Fore.RESET}

    Creates an empty directory

    {colibri.Style.UNDERLINE}Arguments{colibri.Style.RESET_ALL}:
        {colibri.Fore.GREEN}dirname{colibri.Fore.RESET}   : Valid directory name
    '''

    rem = f'''   {colibri.Style.BRIGHT}Remove{colibri.Style.RESET_ALL} - rem {colibri.Fore.LIGHTCYAN_EX}*filename{colibri.Fore.RESET}

    Remove a file

    {colibri.Style.UNDERLINE}Arguments{colibri.Style.RESET_ALL}:
        {colibri.Fore.GREEN}filename{colibri.Fore.RESET}   : Valid file name
'''

    sleep = f'''   {colibri.Style.BRIGHT}Sleep{colibri.Style.RESET_ALL} - sleep {colibri.Fore.LIGHTMAGENTA_EX}seconds{colibri.Fore.RESET}

    Sleeps for a certain amount of time

    {colibri.Style.UNDERLINE}Arguments{colibri.Style.RESET_ALL}:
        {colibri.Fore.GREEN}seconds{colibri.Fore.RESET}   : (numeric) amount of time in seconds
'''

    purge = f'''   {colibri.Style.BRIGHT}Purge{colibri.Style.RESET_ALL} - purge {colibri.Fore.LIGHTMAGENTA_EX}lines{colibri.Fore.RESET}

    Remove a certain number of lines

    {colibri.Style.UNDERLINE}Arguments{colibri.Style.RESET_ALL}:
        {colibri.Fore.GREEN}lines{colibri.Fore.RESET}   : (numeric) number of lines ("all" for all lines)
    '''

    size = f'''   {colibri.Style.BRIGHT}Path-size{colibri.Style.RESET_ALL} - size {colibri.Fore.LIGHTCYAN_EX}*pathname{colibri.Fore.RESET}

    Gets the size of a file or a directory

    {colibri.Style.UNDERLINE}Arguments{colibri.Style.RESET_ALL}:
        {colibri.Fore.GREEN}pathname{colibri.Fore.RESET}   : Path leading to the file or directory
    '''

    con = f'''   {colibri.Style.BRIGHT}Content spot{colibri.Style.RESET_ALL} - con {colibri.Fore.LIGHTCYAN_EX}*pathname{colibri.Fore.RESET} [{colibri.Fore.BLUE}-r{colibri.Fore.RESET} {colibri.Fore.GREEN}--recursive{colibri.Fore.RESET}]
    
    Gets the size of a file or a directory
    
    {colibri.Style.UNDERLINE}Arguments{colibri.Style.RESET_ALL}:
        {colibri.Fore.LIGHTCYAN_EX}*pathname{colibri.Fore.RESET}         : Path leading to the file or directory
        {colibri.Fore.GREEN}-r{colibri.Style.RESET_ALL} / {colibri.Fore.GREEN}--recursive{colibri.Style.RESET_ALL}  : Include subdirectories
        '''

    pex = f'''   {colibri.Style.BRIGHT}PY-Execute{colibri.Style.RESET_ALL} - pex {colibri.Fore.LIGHTCYAN_EX}*pathname{colibri.Fore.RESET} [{colibri.Fore.BLUE}-r{colibri.Fore.RESET} {colibri.Fore.GREEN}--recursive{colibri.Fore.RESET}]

    Executes a Python file using the NXPY runtime.

    {colibri.Style.UNDERLINE}Arguments{colibri.Style.RESET_ALL}:
        {colibri.Fore.LIGHTCYAN_EX}*pathname{colibri.Fore.RESET}         : Path leading to the file or directory
        {colibri.Fore.GREEN}-r{colibri.Style.RESET_ALL} / {colibri.Fore.GREEN}--recursive{colibri.Style.RESET_ALL}  : Include subdirectories
        '''

    cmds = {
        "help": help,
        "version": version,
        "ssh": ssh,
        "genptkey": genptkey,
        "pam": pam,
        "man": man,
        "ypp": ypp,
        "cd": cd,
        "rem": rem,
        "mkdir": mkdir,
        "rmdir": rmdir,
        "sleep": sleep,
        "purge": purge,
        "size": size,
        "con": con,
        "pex": pex
    }
