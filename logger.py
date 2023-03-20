import os
import colibri
from utils import std_path
from datetime import datetime
from options import optionloader


class Logger:
    def __init__(self, base_path=std_path, time_fmt="%d.%m.%y/%H:%M:%S"):
        self.path = os.path.join(base_path, 'logs')
        self.log = []
        self._handle = "nexus-%d.%m.%y-%M-%S-%f.log"
        self._dt = datetime.now()
        self.time_fmt = time_fmt
        self.name = self._get_session_name()

        self._create_file()
        self._writer = self._create_writer()

    def _create_file(self):
        with open(self.name, 'w') as writer:
            writer.write("")

    def _create_writer(self):
        return open(self.name, 'w')

    def _in_log(self):
        self.add("Logger created")

    def _get_time(self, fmt):
        return self._dt.strftime(fmt)

    def _get_session_name(self):
        basename = os.path.join(self.path, self._get_time(self._handle))
        return basename

    def _add_log(self, message, tone):
        self.log.append(f'[{self._get_time(self.time_fmt)}] {tone.upper()} : {message}')

    def add(self, message, tone="info"):
        message += "\n"
        self._add_log(message, colibri.Fore.LIGHTRED_EX+tone+colibri.Fore.RESET if tone == "error" else tone)
        self.dump()
        self.log.clear()

    def __iadd__(self, other):
        self.add(other)

    def __call__(self, *args, **kwargs):
        self.dump()

    def dump(self):
        self._writer.write("\n".join(self.log))

    def flush(self, *args):
        self.dump()


logger = Logger()
logger()

