import os
import colibri

std_path = None
import io_pack as io
import sys

__version__ = '0.9.3'


def erase(n):  # https://www.quora.com/How-can-I-delete-the-last-printed-line-in-Python-language
    n = int(n)
    for i in range(n):
        sys.stdout.write(colibri.CURSOR_UP_ONE)
        sys.stdout.write(colibri.ERASE_LINE)
    trunc_stdout(n)


def clr():
    sys.stdout.write(colibri.ERASE_LINE)


def trunc_stdout(n):  # Generated by ChatGPT
    s = io._dummy_stdout
    pos = s.tell()

    s.seek(0)
    lines = s.readlines()
    s.seek(pos)

    del lines[-n:]

    s.seek(0)
    s.truncate(0)
    s.writelines(lines)
    s.seek(0)

    return s


def stdout_size(inlines=True):
    if inlines:
        return len(io._dummy_stdout.getvalue().splitlines())
    else:
        return len(io._dummy_stdout.getvalue())


def yes_no():
    answer = input('[Y/N] > ').lower()
    erase(2)
    if answer not in ["y", "yes"]:
        if answer not in ["n", "no"]:
            io.output(f'Invalid input ({answer}). Please try again')
            return yes_no()
        else:
            return False
    else:
        return True


def fmt_file(file, abs=True):
    from options import optionloader
    if not optionloader["format-file"]:
        if abs:
            return os.path.abspath(file)
        else:
            return file
    file = os.path.abspath(file).replace('\\', '/')
    if len(file) < 10:
        return file
    return file.split('/')[0] + '/.../' + file.split('/')[file.count('/')]


def help_func():
    io.output(f'''    {colibri.Style.BRIGHT}{colibri.Style.UNDERLINE}Nexus{colibri.Style.RESET_ALL} - V{__version__}
    - by MOBSkuchen

    {colibri.Style.UNDERLINE}Runtime options{colibri.Style.RESET_ALL}
        
        
    {colibri.Style.UNDERLINE}Other options{colibri.Style.RESET_ALL}
        {colibri.Fore.GREEN}-h{colibri.Style.RESET_ALL} / {colibri.Fore.GREEN}--help{colibri.Style.RESET_ALL}     : Show this help message
        {colibri.Fore.GREEN}-v{colibri.Style.RESET_ALL} / {colibri.Fore.GREEN}--version{colibri.Style.RESET_ALL}  : Get version
    ''')


def sizeof_fmt(num, suffix="B"):
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


def map_type(p, _type):
    def _(x):
        return _type(x)

    return list(map(_, p))
