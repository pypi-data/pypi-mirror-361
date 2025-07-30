import sys
import unittest

sys.path.append("./src")
from crypto.symmetric import sm4


class TestSM4(unittest.TestCase):
    def __init__(self, methodName: str = "TestSM4") -> None:
        super().__init__(methodName)
        print(methodName)

    def test_symmetric_sm4(self):
        plaintext1 = b'\x01\x23\x45\x67\x89\xab\xcd\xef\xfe\xdc\xba\x98\x76\x54\x32\x10'
        key1 = b'\x01\x23\x45\x67\x89\xab\xcd\xef\xfe\xdc\xba\x98\x76\x54\x32\x10'
        excepted_ciphertext1 = "681edf34d206965e86b3e94f536e4246"

        self.assertEqual(
            sm4.encrypt(plaintext1, key1).hex(),
            excepted_ciphertext1,
        )
        self.assertEqual(
            sm4.decrypt(bytes.fromhex(excepted_ciphertext1), key1),
            plaintext1,
        )

        plaintext2 = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
        key2 = b'\xfe\xdc\xba\x98\x76\x54\x32\x10\x01\x23\x45\x67\x89\xab\xcd\xef'
        excepted_ciphertext2 = "f766678f13f01adeac1b3ea955adb594"

        self.assertEqual(
            sm4.encrypt(plaintext2, key2).hex(),
            excepted_ciphertext2,
        )
        self.assertEqual(
            sm4.decrypt(bytes.fromhex(excepted_ciphertext2), key2),
            plaintext2,
        )

    @unittest.skip('跳过test_symmetric_sm4_iter')
    def test_symmetric_sm4_iter(self):
        plaintext = b'\x01\x23\x45\x67\x89\xab\xcd\xef\xfe\xdc\xba\x98\x76\x54\x32\x10'
        key = b'\x01\x23\x45\x67\x89\xab\xcd\xef\xfe\xdc\xba\x98\x76\x54\x32\x10'
        excepted_ciphertext = "595298c7c6fd271f0402f804c33d3f66"

        calcCipher = plaintext
        for _ in range(1000000):
            calcCipher = sm4.encrypt(calcCipher, key)

        self.assertEqual(
            calcCipher.hex(),
            excepted_ciphertext,
        )
