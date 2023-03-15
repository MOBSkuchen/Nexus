import os
import zstandard
import colorama as colora
import errors as xsErrors
from utils import erase
from logger import logger
from utils import yes_no
import io_pack as io
from glob import iglob


def _comp(content):
    return zstandard.compress(content)


def _decomp(content):
    return zstandard.decompress(content)


class YPP:
    def __init__(self, name, version, author, include_files, dependencies=[], file_openings=[], check=False):
        self.name = name
        self.version = version
        self.author = author

        self.files = include_files
        if check:
            self._check_files()
        self.dependencies = dependencies

        self.files_with_opener = file_openings

        logger.add("Instance created", "YPP")

    def _check_files(self):
        logger.add("File check", "YPP")
        for file in self.files:
            if not os.path.exists(file):
                raise FileNotFoundError(f"File not found '{file}'")

    def _get_files(self):
        def get_file(name):
            with open(name, 'rb') as file:
                content = file.read()
            return content

        return b"\n===\n".join(get_file(file) for file in self.files)

    def dump(self, filename):
        """
        IMPORTANT : Dump only works when created from scratch (because of YPP._get_files)

        Dumps a file using zstandard compression
        :param filename:
        File to dump to
        :return:
        None
        """

        dep = "\n".join(self.dependencies)
        fil = "|".join(f for f in self.files)
        content = f"{self.name}\n{self.version}\n{self.author}\n{dep}\n===\n{fil}=A=\n".encode() + self._get_files()
        if os.path.exists(filename):
            io.output(f'The file [{filename}] already exists, are you sure you want to replace it?')
            if not yes_no():
                return
        with open(filename, 'wb') as file:
            file.write(_comp(content))
        logger.add(f"Dump to {filename}", "YPP")

    @staticmethod
    def from_file(filename):
        """
        Loads a .ypp file to an YPP object
        :param filename:
        File to read
        :return:
        Finished object
        """
        with open(filename, 'rb') as file:
            content = _decomp(file.read())

        name, version, author = content.split(maxsplit=3)[:3]
        content = content[len(author + name + version) + 3:]
        dependencies, content = content.split(b'\n===\n', 1)
        dependencies = dependencies.split(b'\n')
        if dependencies[0] == b'':
            dependencies = []
        files, content = content.split(b'=A=', 1)
        files = files.split(b'|')
        file_openings = content.split(b'\n===\n')
        logger.add(f"Loaded from {filename}", "YPP")
        return YPP(name.decode(), version.decode(), author.decode(), list(f.decode() for f in files), dependencies,
                   file_openings, False)

    def expand(self, name=None):
        """
        IMPORTANT : Only works with loaded from file

        Creates the project
        :return:
        None
        """
        try:
            name = name if name else self.name
            logger.add(f"Expanding to {name}", "YPP")
            if os.path.exists(name):
                raise FileExistsError(f'Directory {self.name} already exists')
            os.mkdir(name)
            self.files.append('main')
            self.files_with_opener.append(f"{self.name}\n{self.version}\n{self.author}".encode())
            for i in range(len(self.files)):
                file = os.path.basename(self.files[i])
                v = self.files_with_opener[i]
                with open(os.path.join(name, file), 'wb') as filex:
                    filex.write(v)
                    logger.add(f"Writing {file} (ypp_filetype.py:107)", "YPP")
        except Exception as ex:
            logger.add(str(ex), "error")
            io.print_out("Error while expanding, maybe the package is damaged?")


def expand(i):
    io.output(f'{colora.Fore.YELLOW}YPP{colora.Fore.RESET} : Loading...')
    ypp = YPP.from_file(i)
    erase(1)
    io.output(f'{colora.Fore.YELLOW}YPP{colora.Fore.RESET} : Loaded\nNAME : {ypp.name} V{ypp.version} (by {ypp.author})')
    try:
        io.output(f'{colora.Fore.YELLOW}YPP{colora.Fore.RESET} : {colora.Fore.GREEN}Decompressing')
        dump = os.path.join(os.path.dirname(i), ypp.name)
        ypp.expand(dump)
        erase(1)
        io.output(f'{colora.Fore.YELLOW}YPP{colora.Fore.RESET} : {colora.Fore.GREEN}Decompressed')
    except FileExistsError:
        xsErrors.stderr(12, msg="Cannot decompress YPP",
                        cause=["The directory (to be dumped to) already exists"],
                        fix=["Delete the directory"])


def dump(name, version, author, folder, deps):
    ypp = YPP(name, version, author, include_files=folder, dependencies=deps)
    ypp.dump(name + ".ypp")


def main(params):
    if not (len(params) < 2):
        mode = params.pop(0)
        name = params.pop(0)
    else:
        xsErrors.stderr(8,
                        msg=f"The command 'ypp' requires {colora.Fore.CYAN}>1{colora.Fore.RESET}({colora.Fore.CYAN}2{colora.Fore.RESET}) {colora.Fore.RED}arguments!")
        return

    match mode:
        case "expand":
            if not os.path.exists(name):
                xsErrors.stderr(16,
                                msg=f"YPP file not found {colora.Fore.LIGHTBLACK_EX}{name}{colora.Fore.RESET}")
                return
            expand(name)
        case "dump":
            if not (len(params) < 2):
                version = params.pop(0)
                author = params.pop(0)
                folder = list(iglob(params.pop(0)))
                io.output(f'{colora.Fore.YELLOW}YPP{colora.Fore.RESET} : Converting [{name} V{version} by {author}]\n'
                      f'{" + ".join(folder)}\n{" + ".join(params)}')
                dump(name, version, author, folder, params)
            else:
                xsErrors.stderr(8,
                                msg=f"'ypp'::dump requires {colora.Fore.CYAN}>2{colora.Fore.RESET}({colora.Fore.CYAN}3{colora.Fore.RESET}) {colora.Fore.CYAN}arguments!")
                return
        case _:
            xsErrors.stderr(8,
                            msg=f"The command 'ypp' requires its first argument to be expand or dump!")
            return
