import sys
import errors as xsErrors


class ArgumentParser:
    def __init__(self, args=None, trim=False, check=False):
        """
        Initialize the parser
        (run using parser())
        :param args:
        Arguments to be fed into the parser
        :param trim:
        Removes the first value in the argument list
        :param check:
        Check whether the arguments
        which require inputs actually have inputs
        """
        if args is None:
            args = sys.argv
        if trim:
            args.pop(0)
        self._check = check
        if self._check:
            self._rec_args = args.copy()
        self.args = args
        self._r_arg = None
        self._parsed_args = {}
        self._registered_args = {}
        self._call_map = {}
        self._failed = False

    def _check_inputs_correctness(self):
        d = {}
        x = []
        for arg_name in self._rec_args:
            x.append(arg_name)
            if arg_name not in self._call_map:
                continue
            arg_name = self._call_map[arg_name]
            arg = self._registered_args[arg_name]
            if arg["dependencies"]:
                d[arg_name] = arg["dependencies"]
            if arg['input'] and arg_name in self._parsed_args.keys():
                arg_ = self._parsed_args[arg_name]
                if arg_ == True:
                    self._failed = True
                    xsErrors.stderr(8, msg=f"Argument [{arg_name}] requires an input",
                                    cause=["The argument requires an input, but the argument has no assigned value",
                                           "If your value starts with a '-', it may have been interpreted as a flag"],
                                    fix=["Add a value behind this argument",
                                         "If the second cause is the case, please change the name (value)"])
        for s in d.keys():
            b = d[s]
            for _ in b:
                if _ in x:
                    self._failed = True
                    xsErrors.stderr(8, msg=f"Argument [{s}] requires {_} to be invoked")

    def __call__(self, *args, **kwargs):
        """
        Parse argument to a dict
        :return:
        Arguments with specs (dict)
        Format:
        {"name": value, ...}
        value is either a bool (whether it was triggered) or a string (the value of the argument)
        """
        for i in range(len(self.args)):
            arg = self.args.pop(0)
            self._parse_arg(arg)
        if self._check:
            self._check_inputs_correctness()
        return self._parsed_args

    def _parse_arg(self, value):
        if (nn := self._r_arg) and not value.startswith('-'):
            self._r_arg = None
            self._parsed_args[nn] = value
            return
        if value not in self._call_map:
            self._failed = True
            xsErrors.stderr(8, msg=f"Argument [{value}] does not exist",
                            cause=["Argument is not under registered args"],
                            fix=["Check valid arguments", "Check your spelling"])
            return
        name = self._call_map[value]
        exclusives = self._registered_args[name]['exclusives']
        for e in exclusives:
            if e in self._parsed_args.keys():
                self._failed = True
                xsErrors.stderr(8, msg=f"Argument [{name}] is exclusive with {e}",
                                cause=["Both arguments were passed in while only one of them is allowed"],
                                fix=["Only pass in one of them"])
                return
        if self._registered_args[name]['input']:
            if len(self.args) == 0:
                self._failed = True
                xsErrors.stderr(8, msg=f"Argument [{name}] requires an input",
                                cause=["The argument requires an input, but the arguments end after this one"],
                                fix=["Add a value behind this argument"])
                return
            self._r_arg = name

        self._parsed_args[name] = True

        if self._registered_args[name]['action']:
            self._registered_args[name]['action']()

    def add_argument(self, name, calls: list[str], input_: bool = False, exclusives: list[str] = None,
                     action: callable = None, dependencies: list[str] = None):
        """
        Add an argument
        :param dependencies:
        Arguments required in order for this argument to be invoked
        :param name:
        Argument name
        (appears on parsed list as 'name': ...)
        :param calls:
        Name alias
        :param input_:
        Wheter or not the argument has an input value attached to it
        :param exclusives:
        List of exclusive arguments
        :param action:
        Function to execute
        :return:
        None
        """
        if exclusives is None:
            exclusives = []
        if dependencies is None:
            dependencies = []
        _ = {
            "calls": calls,
            "dependencies": dependencies,
            "exclusives": exclusives,
            "action": action,
            "input": input_
        }
        self._registered_args[name] = _

        for call in calls:
            self._call_map[call] = name

    @property
    def failed(self):
        return self._failed