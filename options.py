import json
import os
from launcher import run_cmd, py_launch
from glob import glob
import colibri
import io_pack as io
from utils import std_path


class OptionLoader:
    def __init__(self, path=std_path):
        self.path = path
        self.directories = ["packages", "logs", "manuals"]

        self.prt_ctx = None

        self.default_settings = {
            "show-curdir": True,
            "format-file": False,
        }

        self.check_dirs()
        if not os.path.exists(self.make_path("config.json")):
            io.primitive_warning("Config missing, setting to default...")
            self.write_config(self.default_settings)

        self.settings = self.get_config()

        self.py_loaded = {}
        self.exe_loaded = {}

        self.load_ext()

    def try_launch(self, name, args):
        if name in self.exe_loaded.keys():
            path = self.exe_loaded[name]
            run_cmd(path, args)
            return 1
        elif name in self.py_loaded.keys():
            path = self.py_loaded[name]
            py_launch(path, args)
            return 1
        else:
            return 0

    def make_path(self, path):
        return os.path.join(self.path, path).replace("\\", "/")

    def get_filename(self, path, trim=3):
        l = path.replace("\\", "/").split("/")
        x = l[len(l) - 1]
        return x[:len(x) - trim]

    def load_ext(self):
        exe_files = glob(self.make_path(self.directories[0]) + "/*.exe")
        py_files = glob(self.make_path(self.directories[0]) + "/*.py")

        for item in exe_files:
            self.exe_loaded[self.get_filename(item, 4)] = item.replace("\\", "/")
        for item in py_files:
            self.py_loaded[self.get_filename(item, 3)] = item.replace("\\", "/")

    def check_dirs(self):
        def indi_check(_p):
            if not os.path.exists(path := os.path.join(std_path, _p)):
                io.output(
                    f'{colibri.Fore.RED}Directory not found {colibri.Fore.LIGHTBLACK_EX}({path}){colibri.Fore.RESET}, creating..')
                os.mkdir(path)

        indi_check(self.path)
        for p in self.directories:
            indi_check(p)

    def __getitem__(self, item):
        if item not in self.settings:
            import errors as xsErrors
            xsErrors.internal_error(f"Unexpected OptionLoader option ({item})", num=-2)
        return self.settings[item]

    def get_config(self):
        try:
            with open(self.make_path("config.json"), 'r') as file:
                return json.load(file)
        except Exception as ex:
            import errors as xsErrors
            xsErrors.internal_error(f"Error while loading config", num=-3)

    def write_config(self, config):
        with open(self.make_path("config.json"), 'w') as file:
            return json.dump(config, file)


class ManualLoader:
    def __init__(self, path):
        from pam import get_manual, list_manuals
        self.manuals = list_manuals()
        self.path = path
        self.get_manual = get_manual
        for manual in self.manuals:
            self.check(manual)

    def check(self, manual):
        path = os.path.join(self.path, manual + ".man")
        if not os.path.exists(path):
            with open(path, 'wb') as file:
                b = self.get_manual(manual + ".man")
                file.write(b)
            return b

    def get(self, item):
        if b := self.check(item):
            return b.decode()
        path = os.path.join(self.path, item + ".man")
        with open(path, 'rb') as file:
            b = file.read()
        return b.decode()

    def loadable(self):
        return self.manuals

    def __getitem__(self, item):
        return self.get(item)


optionloader = OptionLoader()


def init_manualloader():
    global manualoader
    manualoader = ManualLoader(optionloader.make_path(optionloader.directories[2]))
