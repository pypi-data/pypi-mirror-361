import random
from typing import List, Tuple

from Cryptodome.Util.asn1 import DerInteger, DerOctetString, DerSequence
from sympy import sqrt_mod
from tinyec import ec

from ..hash import sm3
from ..utils import kdf
from ..utils.types import asn1_str


class SM2(object):
    def __init__(self):
        sm2_curve_param = {
            "h": 0x01,
            "n": 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFF7203DF6B21C6052B53BBF40939D54123,
            "p": 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFF,
            "g": {
                "x": 0x32C4AE2C1F1981195F9904466A39C9948FE30BBFF2660BE1715A4589334C74C7,
                "y": 0xBC3736A2F4F6779C59BDCEE36B692153D0A9877CC62A474002DF32E52139F0A0,
            },
            "a": 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFC,
            "b": 0x28E9FA9E9D9F5E344D5A9E4BCF6509A7F39789F515AB8F92DDBCBD414D940E93,
        }
        field = ec.SubGroup(
            sm2_curve_param["p"],
            (sm2_curve_param["g"]["x"], sm2_curve_param["g"]["y"]),
            sm2_curve_param["n"],
            sm2_curve_param["h"],
        )
        self.curve = ec.Curve(
            sm2_curve_param["a"], sm2_curve_param["b"], field, "sm2Curve"
        )

    def sign(self, data: bytes, private_key: int, k: int | None = None):
        e = int.from_bytes(data)
        if k is None:
            k = random.randint(1, self.curve.field.n - 1)

        kG = k * self.curve.g
        r: int = (e + kG.x) % self.curve.field.n  # type: ignore
        if r == 0 or r + k == self.curve.field.n:
            raise Exception(
                "internal error, invaid random k ${k}, r == 0 or r + k == n, pls try again"
            )

        s: int = (
            pow(1 + private_key, -1, self.curve.field.n) * (k - r * private_key)
        ) % self.curve.field.n
        if s == 0:
            raise Exception("invaid d ${private_key}, s == 0")

        return DerSequence([DerInteger(r), DerInteger(s)]).encode().hex()

    def verify(self, signature: asn1_str, data: bytes, public_key: Tuple[int, int]):
        r, s = DerSequence().decode(bytes.fromhex(signature))
        if r < 1 or r > self.curve.field.n - 1 or s < 1 or s > self.curve.field.n - 1:  # type: ignore
            raise Exception("invalid signature")

        public_key_point = ec.Point(self.curve, public_key[0], public_key[1])

        e = int.from_bytes(data)
        t = (r + s) % self.curve.field.n  # type: ignore
        if t == 0:
            raise Exception("signature error, r + s is zero")

        verifyPoint = s * self.curve.g + t * public_key_point
        return r == ((e + verifyPoint.x) % self.curve.field.n)

    def compute_ZA(
        self,
        public_key: Tuple[int, int],
        ID: str | None = None,
    ):
        if ID is None:
            ID = "1234567812345678"
        z = (
            (len(ID) * 8).to_bytes(2)
            + ID.encode("utf-8")
            + self.curve.a.to_bytes(32)
            + self.curve.b.to_bytes(32)
            + self.curve.g.x.to_bytes(32)
            + self.curve.g.y.to_bytes(32)
            + public_key[0].to_bytes(32)
            + public_key[1].to_bytes(32)
        )
        ZA = sm3.hash(z)
        return ZA

    def sign_with_sm3(
        self,
        data: bytes,
        private_key: int,
        public_key: Tuple[int, int],
        ID: str | None = None,
        randomk: int | None = None,
    ):
        ZA = self.compute_ZA(public_key, ID)
        signature = self.sign(sm3.hash(ZA + data), private_key, randomk)
        return signature

    def verify_with_sm3(
        self,
        signature: asn1_str,
        data: bytes,
        public_key: Tuple[int, int],
        ID: str | None = None,
    ):
        ZA = self.compute_ZA(public_key, ID)
        return self.verify(signature, sm3.hash(ZA + data), public_key)

    def encrypt(self, msg: bytes, public_key: Tuple[int, int], k: int | None = None):
        public_key_point = ec.Point(self.curve, public_key[0], public_key[1])
        s = self.curve.field.h * public_key_point
        if isinstance(s, ec.Inf):
            raise Exception("invalid public key")
        if k is None:
            k = random.randint(1, self.curve.field.n - 1)
        c1 = k * self.curve.g
        secret_point = k * public_key_point

        t = kdf.ansi_x963_with_nosalt_kdf(
            secret_point.x.to_bytes(32) + secret_point.y.to_bytes(32),  # type: ignore
            len(msg) * 8,
        )
        if int.from_bytes(t) == 0:
            raise Exception("error, kdf return 0")

        c2 = int.from_bytes(msg) ^ int.from_bytes(t)

        c3 = sm3.hash(
            int.to_bytes(secret_point.x, 32) + msg + int.to_bytes(secret_point.y, 32)  # type: ignore
        )
        return (
            DerSequence(
                [
                    DerInteger(c1.x),  # type: ignore
                    DerInteger(c1.y),
                    DerOctetString(c3),
                    DerOctetString(int.to_bytes(c2, len(msg))),
                ]
            )
            .encode()
            .hex()
        )

    def decrypt(self, cipher_txt: asn1_str, private_key: int):
        c1x, c1y, c3, c2 = DerSequence().decode(bytes.fromhex(cipher_txt))
        c3 = DerOctetString().decode(c3).payload  # type: ignore
        c2 = DerOctetString().decode(c2).payload  # type: ignore

        c1 = ec.Point(self.curve, c1x, c1y)
        s = self.curve.field.h * c1
        if c1.on_curve is False or isinstance(s, ec.Inf):
            raise Exception("invalid cipher text c1")

        secret_point = private_key * c1

        t = kdf.ansi_x963_with_nosalt_kdf(
            secret_point.x.to_bytes(32) + secret_point.y.to_bytes(32),  # type: ignore
            len(c2) * 8,
        )
        if int.from_bytes(t) == 0:
            raise Exception("error, kdf return 0")

        plain_txt = int.from_bytes(t) ^ int.from_bytes(c2)
        plain_txt = int.to_bytes(plain_txt, len(c2))

        u = sm3.hash(
            int.to_bytes(secret_point.x, 32)  # type: ignore
            + plain_txt
            + int.to_bytes(secret_point.y, 32)  # type: ignore
        )
        if u != c3:
            raise Exception("invalid cipher text c3, u != c3")

        return plain_txt

    def recover_privateKey_by_kAndrs(self, k: int, r: int, s: int):
        if r < 1 or r > self.curve.field.n - 1 or s < 1 or s > self.curve.field.n - 1:  # type: ignore
            raise Exception("invalid signature")
        # d = (k-s)(r + s)^-1 mod n
        return (k - s) * pow(r + s, -1, self.curve.field.n) % self.curve.field.n

    def recover_privateKey_by_fixedk_and_2rs(self, r1: int, s1: int, r2: int, s2: int):
        if (
            r1 < 1
            or r1 > self.curve.field.n - 1
            or s1 < 1
            or s1 > self.curve.field.n - 1
        ):  # type: ignore
            raise Exception("invalid signature r1 s1")
        if (
            r2 < 1
            or r2 > self.curve.field.n - 1
            or s2 < 1
            or s2 > self.curve.field.n - 1
        ):  # type: ignore
            raise Exception("invalid signature r2 s2")
        # r = x1 + e mod n
        # k = s + (r + s) d mod n
        # s1 + (r1 + s1) d = s2 + (r2 + s2) d mod n
        # s1 - s2 = (r2 + s2 - r1 - s1) d mod n
        return self.recover_private_key_by_liner_k(r1, s1, r2, s2, 1, 0)

    def recover_publicKeys_by_eAndrs(self, e: int, r: int, s: int):
        if r < 1 or r > self.curve.field.n - 1 or s < 1 or s > self.curve.field.n - 1:  # type: ignore
            raise Exception("invalid signature")

        x1: int = (r - e) % self.curve.field.n
        # () is necessary
        square_y = (x1**3 + self.curve.a * x1 + self.curve.b) % self.curve.field.p
        y1_roots = sqrt_mod(square_y, self.curve.field.p, True)
        if y1_roots is None:
            raise Exception("y1's value is None")
        elif type(y1_roots) is int:
            y1_roots = [y1_roots]

        public_keys: List[Tuple[int, int]] = []
        t = (r + s) % self.curve.field.n
        t_1 = pow(t, -1, self.curve.field.n)
        for y1 in y1_roots:  # type: ignore
            K = ec.Point(self.curve, x1, y1)
            # assert K.on_curve
            # t = r + s mod n
            # K = sG + tP
            public_key = t_1 * (K - s * self.curve.g)
            public_keys.append((public_key.x, public_key.y))
        # so you can use diffterent public key to verify the same signature
        return public_keys

    def is_same_k(self, r1, e1, r2, e2):
        # r = (e + x1) mod n
        if (
            r1 < 1
            or r1 > self.curve.field.n - 1
            or r2 < 1
            or r2 > self.curve.field.n - 1
        ):  # type: ignore
            raise Exception("invalid signature")

        return (r1 - e1) % self.curve.field.n == (r2 - e2) % self.curve.field.n

    # Thanks https://github.com/GoldSaintEagle/ECDSA-SM2-Signing-Attack/blob/master/attack.go#L108
    def recover_private_key_by_liner_k(
        self, r1: int, s1: int, r2: int, s2: int, a: int, b: int
    ):
        if (
            r1 < 1
            or r1 > self.curve.field.n - 1
            or r2 < 1
            or r2 > self.curve.field.n - 1
            or s1 < 1
            or s1 > self.curve.field.n - 1
            or s2 < 1
            or s2 > self.curve.field.n - 1
        ):  # type: ignore
            raise Exception("invalid signature")
        # k2 = ak1 + b
        # K2 = aK1 + bG
        # K1 = (x1,y1) = s1G + t1P
        # K2 = (x2,y2) = s2G + t2P
        # s2G + t2P = a(s1G + t1P) + bG
        # s2 + t2d = a(s1 + t1d) + b
        # d (t2-at1) = b - s2 + as1
        t1 = (r1 + s1) % self.curve.field.n
        t2 = (r2 + s2) % self.curve.field.n
        return (
            (b - s2 + a * s1)
            * pow(t2 - a * t1, -1, self.curve.field.n)
            % self.curve.field.n
        )

    def forge_e_signature(self, public_key: Tuple[int, int], s: int, t: int):
        K = s * self.curve.g + t * ec.Point(self.curve, *public_key)
        r: int = (t - s) % self.curve.field.n
        e: int = (r - K.x) % self.curve.field.n  # type: ignore
        return e, r, s
