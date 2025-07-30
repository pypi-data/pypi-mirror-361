import sys
import unittest

sys.path.append("./src")
from crypto.symmetric import modes


class TestModes(unittest.TestCase):
    def __init__(self, methodName: str = "TestModes") -> None:
        super().__init__(methodName)
        print(methodName)
        self.plaintext1 = b'\x01\x23\x45\x67\x89\xab\xcd\xef\xfe\xdc\xba\x98\x76\x54\x32\x10'
        self.key1 = b'\x01\x23\x45\x67\x89\xab\xcd\xef\xfe\xdc\xba\x98\x76\x54\x32\x10'

        self.plaintext2 = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
        self.key2 = b'\xfe\xdc\xba\x98\x76\x54\x32\x10\x01\x23\x45\x67\x89\xab\xcd\xef'

        self.plaintext3 = b'hello'
        self.key3 = b'worldworldworldw'

        self.plaintext4 = "你好".encode('utf-8')
        self.key4 = b'1234567812345678'

    def test_ecb_modes(self):
        excepted_ciphertext1 = b"\x68\x1e\xdf\x34\xd2\x06\x96\x5e\x86\xb3\xe9\x4f\x53\x6e\x42\x46\x00\x2a\x8a\x4e\xfa\x86\x3c\xca\xd0\x24\xac\x03\x00\xbb\x40\xd2"
        self.assertEqual(
            modes.ecb_encrypt('sm4', self.plaintext1, self.key1),
            excepted_ciphertext1,
        )
        self.assertEqual(
            modes.ecb_decrypt('sm4', excepted_ciphertext1, self.key1),
            self.plaintext1,
        )

        excepted_ciphertext2 = b"\xf7\x66\x67\x8f\x13\xf0\x1a\xde\xac\x1b\x3e\xa9\x55\xad\xb5\x94\xa2\x51\x49\x20\x93\xf8\xf6\x42\x89\xb7\x8d\x6e\x8a\x28\xb1\xc6"
        self.assertEqual(
            modes.ecb_encrypt('sm4', self.plaintext2, self.key2),
            excepted_ciphertext2,
        )
        self.assertEqual(
            modes.ecb_decrypt('sm4', excepted_ciphertext2, self.key2),
            self.plaintext2,
        )

        excepted_ciphertext3 = b"\x61\xb4\x06\xa9\xb0\x7a\x7e\x6a\x51\x47\xa7\x9e\xe6\x67\x13\xa4"
        self.assertEqual(
            modes.ecb_encrypt('sm4', self.plaintext3, self.key3),
            excepted_ciphertext3,
        )
        self.assertEqual(
            modes.ecb_decrypt('sm4', excepted_ciphertext3, self.key3),
            self.plaintext3,
        )

        excepted_ciphertext4 = b"\xba\xfd\xd9\xb1\x6d\x6c\x48\x4d\x81\xc9\x78\x5a\x54\xb6\x04\xe1"
        self.assertEqual(
            modes.ecb_encrypt('sm4', self.plaintext4, self.key4),
            excepted_ciphertext4,
        )
        self.assertEqual(
            modes.ecb_decrypt('sm4', excepted_ciphertext4, self.key4),
            self.plaintext4,
        )

    def test_cbc_modes(self):
        excepted_ciphertext1 = b"\x26\x77\xf4\x6b\x09\xc1\x22\xcc\x97\x55\x33\x10\x5b\xd4\xa2\x2a\x3b\x88\x0e\x68\x67\x77\x25\x22\xae\x55\xd2\xf0\xae\x74\x78\xae"
        self.assertEqual(
            modes.cbc_encrypt('sm4', self.plaintext1, self.key1, self.key1),
            excepted_ciphertext1,
        )
        self.assertEqual(
            modes.cbc_decrypt('sm4', excepted_ciphertext1, self.key1, self.key1),
            self.plaintext1,
        )

        excepted_ciphertext2 = b"\xf7\x04\x23\x72\xa6\x9f\x4d\xc2\xa3\xc6\xd1\xed\xe6\x97\x6c\x7a\x77\xf8\x50\x25\xe3\x9e\x48\xcc\x86\x8d\x81\x83\x0f\xcc\x40\x94"
        self.assertEqual(
            modes.cbc_encrypt('sm4', self.plaintext2, self.key2, self.key2),
            excepted_ciphertext2,
        )
        self.assertEqual(
            modes.cbc_decrypt('sm4', excepted_ciphertext2, self.key2, self.key2),
            self.plaintext2,
        )

        excepted_ciphertext3 = b"\x11\x0b\x5e\xf9\x0c\x02\xd5\x3b\x5b\x62\x98\x85\x66\x9b\x75\x50"
        self.assertEqual(
            modes.cbc_encrypt('sm4', self.plaintext3, self.key3, self.key3),
            excepted_ciphertext3,
        )
        self.assertEqual(
            modes.cbc_decrypt('sm4', excepted_ciphertext3, self.key3, self.key3),
            self.plaintext3,
        )

        excepted_ciphertext4 = b"\x5c\x9e\x7e\xf6\xb5\x18\xc1\x88\x18\x64\xd6\xd4\x69\xd3\xe3\x56"
        self.assertEqual(
            modes.cbc_encrypt('sm4', self.plaintext4, self.key4, self.key4),
            excepted_ciphertext4,
        )
        self.assertEqual(
            modes.cbc_decrypt('sm4', excepted_ciphertext4, self.key4, self.key4),
            self.plaintext4,
        )
