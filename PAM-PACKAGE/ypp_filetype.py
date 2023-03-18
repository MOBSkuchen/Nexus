import io
import os
import zstandard


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

    def _check_files(self):
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
        with open(filename, 'wb') as file:
            file.write(_comp(content))

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
        content = content[len(author + name + version)+3:]
        dependencies, content = content.split(b'\n===\n', 1)
        dependencies = dependencies.split(b'\n')
        if dependencies[0] == b'':
            dependencies = []
        files, content = content.split(b'=A=', 1)
        files = files.split(b'|')
        file_openings = content.split(b'\n===\n')
        return YPP(name.decode(), version.decode(), author.decode(), list(f.decode() for f in files), dependencies, file_openings, False)

    def expand(self):
        """
        IMPORTANT : Only works with loaded from file

        Creates the project
        :return:
        None
        """
        if os.path.exists(self.name):
            raise FileExistsError(f'Directory {self.name} already exists')
        os.mkdir(self.name)
        self.files.append('main')
        self.files_with_opener.append(f"{self.name}\n{self.version}\n{self.author}".encode())
        for i in range(len(self.files)):
            file = self.files[i]
            v = self.files_with_opener[i]
            with open(os.path.join(self.name, file), 'wb') as filex:
                filex.write(v)


def main():
    ypp = YPP('PAM-PACKAGE', '1.0', 'MOBSkuchen', ['server.py', 'pam.py', 'ypp_filetype.py'])
    ypp.dump('file.ypp')
    # ypp = YPP.from_file('file.ypp')
    # ypp.expand()


if __name__ == '__main__':
    main()
