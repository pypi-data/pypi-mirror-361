
import os
import base64
import hashlib
from pathlib import Path
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


class JaguarEncryptor:
    def __init__(self):
        self.defaultKey = None

    def createEncryptionKey(self, fpath):
        key = os.urandom(32)
        encoded = "U0" + base64.b64encode(key).decode('utf-8')
        try:
            with open(fpath, 'w') as f:
                f.write(encoded)
            return encoded
        except Exception as e:
            print(f"Failed to write key to file: {e}")
            return ""

    def setDefaultEncryptionKey(self, fpath):
        try:
            with open(fpath, 'r') as f:
                content = f.read().strip()
                if not content.startswith("U0"):
                    return -1
                self.defaultKey = base64.b64decode(content[2:])
                return 0
        except Exception as e:
            print(f"Error setting default key: {e}")
            return -1

    def readEncryptionKey(self, fpath):
        try:
            with open(fpath, 'r') as f:
                return f.read().strip()
        except Exception as e:
            print(f"Error reading key: {e}")
            return ""

    def _generateIv(self, plaintext):
        return hashlib.sha256(plaintext.encode()).digest()[:16]

    def _encrypt(self, plaintext, key):
        iv = self._generateIv(plaintext)
        padder = padding.PKCS7(128).padder()
        paddedData = padder.update(plaintext.encode()) + padder.finalize()
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(paddedData) + encryptor.finalize()
        return "U0" + base64.b64encode(iv + ciphertext).decode('utf-8')

    def _decrypt(self, base64Input, key):
        if not base64Input.startswith("U0"):
            raise ValueError("Unsupported key format")
        decoded = base64.b64decode(base64Input[2:])
        iv, ciphertext = decoded[:16], decoded[16:]
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        paddedPlaintext = decryptor.update(ciphertext) + decryptor.finalize()
        unpadder = padding.PKCS7(128).unpadder()
        plaintext = unpadder.update(paddedPlaintext) + unpadder.finalize()
        return plaintext.decode('utf-8')

    def encryptWithDefaultKey(self, plaintext):
        if not self.defaultKey:
            raise ValueError("Default key not set")
        return self._encrypt(plaintext, self.defaultKey)

    def decryptWithDefaultKey(self, ciphertext):
        if not self.defaultKey:
            raise ValueError("Default key not set")
        return self._decrypt(ciphertext, self.defaultKey)

    def encryptWithGivenKey(self, plaintext, combinedKey):
        if not combinedKey.startswith("U0"):
            raise ValueError("Invalid key format")
        key = base64.b64decode(combinedKey[2:])
        return self._encrypt(plaintext, key)

    def decryptWithGivenKey(self, ciphertext, combinedKey):
        if not combinedKey.startswith("U0"):
            raise ValueError("Invalid key format")
        key = base64.b64decode(combinedKey[2:])
        return self._decrypt(ciphertext, key)

    def encryptFileWithGivenKey(self, inputFile, combinedKey, outputFile):
        try:
            with open(inputFile, 'rb') as f:
                data = f.read()
            key = base64.b64decode(combinedKey[2:])
            cipher = Cipher(algorithms.AES(key), modes.CBC(bytes(16)), backend=default_backend())
            encryptor = cipher.encryptor()
            padder = padding.PKCS7(128).padder()
            padded = padder.update(data) + padder.finalize()
            ciphertext = encryptor.update(padded) + encryptor.finalize()
            with open(outputFile, 'wb') as f:
                f.write(ciphertext)
            return True
        except Exception as e:
            print(f"Error encrypting file: {e}")
            return False

    def decryptFileWithGivenKey(self, inputFile, combinedKey, outputFile):
        try:
            with open(inputFile, 'rb') as f:
                data = f.read()
            key = base64.b64decode(combinedKey[2:])
            cipher = Cipher(algorithms.AES(key), modes.CBC(bytes(16)), backend=default_backend())
            decryptor = cipher.decryptor()
            padded = decryptor.update(data) + decryptor.finalize()
            unpadder = padding.PKCS7(128).unpadder()
            plaintext = unpadder.update(padded) + unpadder.finalize()
            with open(outputFile, 'wb') as f:
                f.write(plaintext)
            return True
        except Exception as e:
            print(f"Error decrypting file: {e}")
            return False

    def encryptFileWithDefaultKey(self, inputFile, outputFile):
        if not self.defaultKey:
            raise ValueError("Default key not set")
        return self.encryptFileWithGivenKey(inputFile, "U0" + base64.b64encode(self.defaultKey).decode(), outputFile)

    def decryptFileWithDefaultKey(self, inputFile, outputFile):
        if not self.defaultKey:
            raise ValueError("Default key not set")
        return self.decryptFileWithGivenKey(inputFile, "U0" + base64.b64encode(self.defaultKey).decode(), outputFile)



