import os
import json

import bcrypt

from constants import *

def verify_key(key):
	salt = bcrypt.gensalt()

	try:
		with open(f"{DB_FOLDER}/{DB_MASTER}", "r") as f:
			content = json.load(f)
			stored_hash = content["hash"]
	except Exception:
		return False
	else:
		if bcrypt.checkpw(key, stored_hash.encode()):
			return True
		else:
			return False

def write_key(key):
	salt = bcrypt.gensalt()
	key_hash = bcrypt.hashpw(key, salt)
	content = {"hash": key_hash.decode()}

	with open(f"{DB_FOLDER}/{DB_MASTER}", "w") as f:
		json.dump(content, f)