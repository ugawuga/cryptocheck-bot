import hashlib
import uuid


def form_hash_key(key):
    salt = uuid.uuid4().hex
    hash_key = hashlib.sha224(salt.encode() + key.encode()).hexdigest()
    return hash_key


