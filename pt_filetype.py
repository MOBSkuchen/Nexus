import base64
import json
import hashlib as hs
import pickle
import zstandard as zst
import io_pack as io
import errors as xsErrors
import colibri
from cryptlib import Crypto
from cryptography.fernet import InvalidToken, InvalidSignature


class Key:
    def __init__(self, server, name, password, prot_key=None):
        self.server = server
        self.name = name
        self.password = password
        self.prot_key = prot_key
        if prot_key is not None:
            self.prot_key = hs.sha256(prot_key.encode()).hexdigest()

    def _make_data(self) -> bytes:
        dictionary = {
            "server": self.server,
            "name": self.name,
            "password": self.password
        }

        if self.prot_key:
            dictionary["prot-key"] = self.prot_key

        data = json.dumps(dictionary).encode()
        if self.prot_key is None:
            return data
        c = Crypto(self.prot_key)
        return c.encrypt(data)

    @staticmethod
    def _get_data(data, key):
        if not key:
            return json.loads(data.decode())
        c = Crypto(key)
        try:
            data = c.decrypt(data)
        except InvalidToken:
            return None
        except InvalidSignature:
            return None
        return json.loads(data.decode())

    def dump(self, filename):
        d = {
            "data": base64.b64encode(self._make_data()).decode('ascii'),
            "protected": self.prot_key is not None
        }

        string = json.dumps(d)
        jar = pickle.dumps(string)
        enc = zst.compress(jar)

        with open(filename, 'wb') as file:
            file.write(enc)

        io.print_out(f"Wrote pt-key to {filename}")

    @staticmethod
    def load(js, key):
        data = base64.b64decode(js["data"])
        js = Key._get_data(data, key)
        login = js['name']
        password = js['password']
        server = js['server']
        if key:
            prot = js['prot-key']
        else:
            prot = None
        return Key(server, login, password, prot)

    @staticmethod
    def unpack(filename):
        with open(filename, 'rb') as file:
            enc = file.read()
        dec = zst.decompress(enc)
        x = pickle.loads(dec)
        js = json.loads(x)
        return js, js['protected']

    def __repr__(self):
        return f'{self.name} - {"*"*len(self.password)}{" [" + "*"*len(self.prot_key) + "]" if self.prot_key else ""}'


def main(params):
    if not (len(params) < 4):
        filename = params.pop(0)
        server = params.pop(0)
        login = params.pop(0)
        password = params.pop(0)
    else:
        xsErrors.stderr(8,
                        msg=f"The command 'genptkey' requires {colibri.Fore.CYAN}>3{colibri.Fore.RESET}({colibri.Fore.CYAN}4{colibri.Fore.RESET}) {colibri.Fore.RED}arguments!")
        return

    if len(params) >= 1:
        prot = params.pop(0)
    else:
        prot = None
    key = Key(server, login, password, prot)
    key.dump(filename)
