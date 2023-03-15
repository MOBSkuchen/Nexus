import copy
import os
import subprocess as sbp
import sys
import colibri
import errors as xsErrors
from importlib.machinery import SourceFileLoader
from utils import fmt_file, erase
import io_pack as io
from argparser import ArgumentParser


__version__ = "1.6"


reg = {}
workings = {}


class SoftException(Exception):
    # Indicate an error has occurred
    pass


def run_cmd(name, args):
    try:
        p = sbp.Popen([name] + args[0])
        p.wait()
        if p.returncode != 0:
            erase(1)
            xsErrors.stderr(19, msg=f"Unable to run EXE [{fmt_file(name)}]",
                            cause=[f"SBP lib ran into an error during runtime [{p.returncode}]"])
    except SoftException:
        pass
    except Exception as ex:
        xsErrors.stderr(19, msg=f"Unable to run EXE [{fmt_file(name)}]",
                        cause=["SBP lib ran into an error during runtime: ", str(ex)])
    except KeyboardInterrupt:
        sys.stdout.write('\n')
        return


def f_run(func, args, name, lcls):
    global ctx

    class ctx:
        pass

    for i in lcls.keys():
        c = lcls[i]
        setattr(ctx, i, c)
    try:
        workings[name] = True
        func(args)
    except SoftException:
        pass
    except Exception as ex:
        workings[name] = False
        xsErrors.stderr(19, msg=f"Unable to run PY-EXT [{fmt_file(name)}]",
                        cause=["Python ran into an error during runtime:", str(ex)])


def save_reg(_locals):
    lcls = copy.copy(_locals)
    name = lcls["name"]
    reg[name] = lcls


def cached():
    io.print_out(f"Currently caching {colibri.Fore.CYAN}{len(reg.keys())}{colibri.Fore.RESET} extensions{':' if reg else ''}")
    for name in reg.keys():
        print(f'{name} => {"works" if workings[name] else "failed"}')


def drop(name):
    global reg, workings
    if name == "all":
        reg = {}
        workings = {}
    else:
        if name in reg:
            del reg[name]
            del workings[name]
        else:
            io.print_out(f"Skipping {name}, as it was not found")


__loaded_stb = """def main(args):
    io = ctx.get_lib("io_pack")
    io.print_out("Helllllooooo!!")"""


def main(params):
    ap = ArgumentParser(params)
    ap.add_argument("cached", ["-c", "--cached"], action=cached)
    ap.add_argument("execute", ["-e", "--exe"], input_=True)
    ap.add_argument("drop", ["-d", "--drop"], input_=True)
    ap.add_argument("new", ["-n", "--new"], input_=True)

    p = ap()
    if "new" in p.keys():
        name = p["new"]
        name = name + ".py" if not name.endswith(".py") else name
        with open(name, 'w') as file:
            file.write(__loaded_stb)
        io.print_out(f'Created {name}')
    if "drop" in p.keys():
        name = p["drop"]
        drop(name)
    if "execute" in p.keys():
        file = p["execute"]
        io.print_out(f"{colibri.Style.UNDERLINE}Executing '{p['execute']}'{colibri.Style.RESET_ALL}")
        py_launch(file,  [])


def py_launch(name, args):
    from logger import logger
    def get_lib(libname):
        exec(f"import {libname}")
        logger.add(f"Lib import: {libname}")
        return locals()[libname]

    def get_pkg(pkg_name):
        return os.path.join(os.path.dirname(name), pkg_name)

    def imp(_name):
        _name = get_pkg(_name)
        bn = os.path.basename(_name)
        bn = bn[:(len(bn) - 3)]
        if not os.path.exists(_name):
            workings[name] = False
            xsErrors.stderr(19, msg=f"Unable to run PY-EXT [{fmt_file(_name)}]",
                            cause=[f"The file {fmt_file(_name)} was not found"],
                            fix=[] if _name.endswith(".py") else ["Change the filename to end with .py"])
            raise SoftException()
        return SourceFileLoader(bn, _name).load_module()

    try:
        if name in reg.keys():
            logger.add(f"Loaded PY-EXT from cached {name}")
            func = reg[name]['main']
            f_run(func, args, name, reg[name])
            return
        with open(name, 'r') as filereader:
            content = filereader.read()
            exec(content)
            lcls = locals()
            if "main" not in lcls.keys():
                workings[name] = False
                xsErrors.stderr(19, msg=f"Unable to run PY-EXT [{fmt_file(name)}]",
                                cause=["PY-EXT has no entry function ('main')"])
            else:
                func = lcls["main"]
                save_reg(lcls)
                logger.add(f"Loaded PY-EXT {name}")
                f_run(func, args, name, locals())
    except SoftException:
        pass
    except Exception as ex:
        if xsErrors.debug:
            raise ex
        workings[name] = False
        xsErrors.stderr(19, msg=f"Unable to run PY-EXT [{fmt_file(name)}]",
                        cause=["Python ran into an error during startup:", str(ex)])
