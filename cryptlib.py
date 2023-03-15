from cryptography.fernet import Fernet
import base64


class Crypto:
	def __init__(self, key):
		self.str_key = key
		self.key = self._gen_key(self.str_key)
		self.fernet = Fernet(self.key)

	def _gen_key(self, _key):
		length = len(_key)
		new = ""
		for i in range(32 // length):
			new += _key
		new += "=" * (32 - len(new))
		return base64.urlsafe_b64encode(new.encode())

	def encrypt(self, data):
		return self.fernet.encrypt(data)

	def decrypt(self, data):
		return self.fernet.decrypt(data)

