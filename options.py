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
        self.directories = ["packages", "logs", "manual"]

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


optionloader = OptionLoader()
from logger import logger
import errors as xsErrors


class ManualLoader:
    def __init__(self, path):
        self.makes = {}
        self.expected = ["man", "version", "NXPY"]
        self.reals = glob(os.path.join(path, "*.man").replace("\\", "/"))

        self.make()

    def file_load(self, path):
        with open(path, 'r') as file:
            content = file.read()
        return content

    def make(self):
        for real in self.reals:
            self.makes[optionloader.get_filename(real, 4)] = self.file_load(real)

        for i in self.expected:
            if i not in self.makes:
                logger.add(f"Unable to load MAN:{i}", "error")

    def __getitem__(self, item):
        try:
            return self.makes[item]
        except Exception as ex:
            xsErrors.internal_error(f"Error while loading config", num=-3)


manualoader = ManualLoader(optionloader.make_path(optionloader.directories[2]))
