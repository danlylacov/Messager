import os
import hashlib

class Bcrypt:
    @staticmethod
    def generate_salt():
        return os.urandom(16)

    @staticmethod
    def bcrypt(password, salt, rounds):
        hashed = hashlib.sha256(salt + password).digest()  # Первый проход
        for _ in range(rounds - 1):
            hashed = hashlib.sha256(hashed).digest()  # Дополнительные проходы
        return hashed

    @staticmethod
    def hash_password(password, rounds=12):
        salt = Bcrypt.generate_salt()
        hashed = Bcrypt.bcrypt(password, salt, rounds)
        return salt + hashed

    @staticmethod
    def check_password(password, stored_hash):
        salt = stored_hash[:16]
        stored_hash = stored_hash[16:]
        new_hash = Bcrypt.bcrypt(password, salt, 12)
        return new_hash == stored_hash


