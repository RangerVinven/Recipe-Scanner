import hashlib

def hash_string(string_to_hash):
    # Hashes the password
    hex_object = hashlib.sha256(string_to_hash.encode("utf-8"))
    return hex_object.hexdigest()

