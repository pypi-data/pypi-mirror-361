import random
import sys
import unittest

sys.path.append("./src")
from crypto.asymmetric import sm2
from crypto.hash import sm3
from Crypto.Util.number import bytes_to_long, long_to_bytes
from crypto.utils.types import asn1_str
from Cryptodome.Util.asn1 import DerInteger, DerSequence


class TestSM2(unittest.TestCase):
    def __init__(self, methodName: str = "TestSM2") -> None:
        super().__init__(methodName)
        print(methodName)
        self.sm2 = sm2.SM2()
        self.private_key = 1
        self.public_key = (
            0x32C4AE2C1F1981195F9904466A39C9948FE30BBFF2660BE1715A4589334C74C7,
            0xBC3736A2F4F6779C59BDCEE36B692153D0A9877CC62A474002DF32E52139F0A0,
        )
        self.private_key2 = (
            0x08686EDC7F9CDE89AD201587F7A813F6502ACA801393B6FE192BC7A0D77D4F8D
        )
        self.public_key2 = (
            0x44143060D58A126D69AB606C3AB14E7479474FE3ACEEA8F35C5C1525D5D8893E,
            0x0BD10636AE04EBE00D02A0263AFB226C51B003788B98EA1824E695DBD3AE5398,
        )

    def test_sign_with_sm3(self):
        signature = self.sm2.sign_with_sm3(
            b"hello world", self.private_key, self.public_key
        )
        result = self.sm2.verify_with_sm3(
            asn1_str(signature), b"hello world", self.public_key
        )
        self.assertTrue(result)

    def test_sign_with_sm3_ID(self):
        signature = self.sm2.sign_with_sm3(
            b"hello world", self.private_key, self.public_key, "8765432112345678"
        )
        result = self.sm2.verify_with_sm3(
            asn1_str(signature), b"hello world", self.public_key, "8765432112345678"
        )
        self.assertTrue(result)

    def test_sign_with_sm3_fixed_k(self):
        signature = self.sm2.sign_with_sm3(
            b"hello world", self.private_key, self.public_key, "8765432112345678", 0x12
        )
        result = self.sm2.verify_with_sm3(
            asn1_str(signature), b"hello world", self.public_key, "8765432112345678"
        )
        self.assertTrue(result)

    def test_sign_with_random_k(self):
        signature = self.sm2.sign(b"hello world", self.private_key)
        result = self.sm2.verify(asn1_str(signature), b"hello world", self.public_key)
        self.assertTrue(result)

    def test_sign_with_fixed_k(self):
        signature = self.sm2.sign(b"hello world", self.private_key, 0x1234567812345678)
        result = self.sm2.verify(asn1_str(signature), b"hello world", self.public_key)
        self.assertTrue(result)

    def test_encrypt_decrypt(self):
        cipher = self.sm2.encrypt(b"hello world", self.public_key)
        res = self.sm2.decrypt(asn1_str(cipher), self.private_key)
        self.assertEqual(res, b"hello world")

    def test_recover_privateKey_by_kAndrs(self):
        r = 0x37AF670C4742BD0C8D7CF68FCEBFE61885AA630695D50A15DF279CD64327466F
        r = bytes_to_long(long_to_bytes(r)[::-1])
        s = 0x6701CFB5F356887B9441323FDC08FBA900E1050109FD95F024DC9C178CEBE7A4
        s = bytes_to_long(long_to_bytes(s)[::-1])
        k = 0xD2D569D2A7250B2B27DF909C9AFC1FD9E0A555AEC4BFB5D80CD71F70ADACF414
        d = self.sm2.recover_privateKey_by_kAndrs(k, r, s)
        self.assertEqual(
            d, 0xE711E7FEE2F7DB4DE74F94B4D818718FDAF86291150227E7CB5323CDD7FF3B75
        )

    def test_recover_privateKey_by_fixedk_and_2rs(self):
        # P = {
        #     "x": 0xE83E542C594496D1F75A7C07841F2DE773DB59CA8A277CC77BAB2FD1BA90B858,
        #     "y": 0x5F7CC3C9863D129D4DDFACD1B529A31CCB81463AF8A8BB5AB480A3F8BB7DA737,
        # }
        # e11 = 0x875817FFC25231A88B68696273AEECE852A10CCDE93C19476482EBA4D4877322
        # e12 = 0x8FB2B63B9CF9ED7842CC0E0A204B36A3ED5C45936B6148646A26915120F6C7D2
        r1 = 0x1260185C3D7437E6A63F1E18FD810A314A5E27D67884A83F1283D72F1009F699
        s1 = 0x0E9F423B578A8707C83C1A0A3982F52D0FF718C2B481966E4D839CD566EE7209
        r2 = 0x1ABAB698181BF3B65DA2C2C0AA1D53ECE519609BFAA9D75C18277CDB5C794B49
        s2 = 0xEBB541CA42C5CCA5FA1324DDC32D3F352546FE4EECE8034E1D64A2848E2A93B9
        d = self.sm2.recover_privateKey_by_fixedk_and_2rs(r1, s1, r2, s2)
        self.assertEqual(
            d, 0x3B90F86F263049ADBAE06CBB1E2F8EFEF2142F2CC4979050A3D3109DF7D83714
        )

    def test_recover_publicKey_by_eAndrs(self):
        P = {
            "x": 0xE83E542C594496D1F75A7C07841F2DE773DB59CA8A277CC77BAB2FD1BA90B858,
            "y": 0x5F7CC3C9863D129D4DDFACD1B529A31CCB81463AF8A8BB5AB480A3F8BB7DA737,
        }
        e11 = 0x875817FFC25231A88B68696273AEECE852A10CCDE93C19476482EBA4D4877322
        e12 = 0x8FB2B63B9CF9ED7842CC0E0A204B36A3ED5C45936B6148646A26915120F6C7D2
        r1 = 0x1260185C3D7437E6A63F1E18FD810A314A5E27D67884A83F1283D72F1009F699
        s1 = 0x0E9F423B578A8707C83C1A0A3982F52D0FF718C2B481966E4D839CD566EE7209
        r2 = 0x1ABAB698181BF3B65DA2C2C0AA1D53ECE519609BFAA9D75C18277CDB5C794B49
        s2 = 0xEBB541CA42C5CCA5FA1324DDC32D3F352546FE4EECE8034E1D64A2848E2A93B9

        public_keys1 = self.sm2.recover_publicKeys_by_eAndrs(e11, r1, s1)
        self.assertIn((P["x"], P["y"]), public_keys1)
        for public_key in public_keys1:
            ret = self.sm2.verify(
                asn1_str(DerSequence([DerInteger(r1), DerInteger(s1)]).encode().hex()),
                long_to_bytes(e11),
                public_key,
            )
            self.assertTrue(ret)

        public_keys2 = self.sm2.recover_publicKeys_by_eAndrs(e12, r2, s2)
        self.assertIn((P["x"], P["y"]), public_keys2)
        for public_key in public_keys2:
            ret = self.sm2.verify(
                asn1_str(DerSequence([DerInteger(r2), DerInteger(s2)]).encode().hex()),
                long_to_bytes(e12),
                public_key,
            )
            self.assertTrue(ret)

    def test_is_same_k(self):
        e1 = 0x875817FFC25231A88B68696273AEECE852A10CCDE93C19476482EBA4D4877322
        e2 = 0x8FB2B63B9CF9ED7842CC0E0A204B36A3ED5C45936B6148646A26915120F6C7D2
        r1 = 0x1260185C3D7437E6A63F1E18FD810A314A5E27D67884A83F1283D72F1009F699
        r2 = 0x1ABAB698181BF3B65DA2C2C0AA1D53ECE519609BFAA9D75C18277CDB5C794B49
        self.assertTrue(self.sm2.is_same_k(r1, e1, r2, e2))

    def test_recover_private_key_by_liner_k(self):
        # k2 = k1 * 167 + 100
        sig1 = self.sm2.sign_with_sm3(
            b"hello world",
            self.private_key2,
            self.public_key2,
            randomk=0x11223344556677889900AABBCCDDEEFF112233445566778899,
        )
        r1 = 0xB99264F02A62CED3E15CD9FDDDC7E9E6AAE1EA3DE3A7FF1862DDADBEE0DD1552
        s1 = 0x979009120D425DC863E67FF3DE0F2F667EAA2139FD8EEFC089C69EBFCAFBDD7D

        sig2 = self.sm2.sign_with_sm3(
            b"hello world",
            self.private_key2,
            self.public_key2,
            randomk=0xB2D4F7193B5D7FA1BCF6F6082A4C6E8642D4F7193B5D7FA1C33,
        )
        r2 = 0x0813AFAE0180E82F6BE2CC91FA908CECE80B6DB47667321A0D9FBA6D828C7C66
        s2 = 0x120DBE91124920B60A0251B85F1CF0788AB56600F12FF48D9E78E95F71BE879C
        d = self.sm2.recover_private_key_by_liner_k(r1, s1, r2, s2, 167, 100)
        self.assertEqual(d, self.private_key2)

    def test_forge_e_signature1(self):
        r1 = 0xB99264F02A62CED3E15CD9FDDDC7E9E6AAE1EA3DE3A7FF1862DDADBEE0DD1552
        s1 = 0x979009120D425DC863E67FF3DE0F2F667EAA2139FD8EEFC089C69EBFCAFBDD7D
        # t = r + s
        e, r, s = self.sm2.forge_e_signature(self.public_key2, s1, r1 + s1)
        ZA = self.sm2.compute_ZA(self.public_key2)
        self.assertEqual(long_to_bytes(e), sm3.hash(ZA + b"hello world"))
        self.assertEqual(r, r1)
        self.assertEqual(s, s1)
        self.assertTrue(
            self.sm2.verify(
                asn1_str(DerSequence([DerInteger(r), DerInteger(s)]).encode().hex()),
                long_to_bytes(e),
                self.public_key2,
            )
        )

    def test_forge_e_signature2(self):
        r1 = random.randint(
            0x1111111111111111111111111111111111111111111111111111111111111111,
            self.sm2.curve.field.n - 1,
        )
        s1 = random.randint(
            0x1111111111111111111111111111111111111111111111111111111111111111,
            self.sm2.curve.field.n - 1,
        )
        # t = r + s
        e, r, s = self.sm2.forge_e_signature(self.public_key2, s1, r1 + s1)
        self.assertEqual(r, r1)
        self.assertEqual(s, s1)
        self.assertTrue(
            self.sm2.verify(
                asn1_str(DerSequence([DerInteger(r), DerInteger(s)]).encode().hex()),
                long_to_bytes(e),
                self.public_key2,
            )
        )
