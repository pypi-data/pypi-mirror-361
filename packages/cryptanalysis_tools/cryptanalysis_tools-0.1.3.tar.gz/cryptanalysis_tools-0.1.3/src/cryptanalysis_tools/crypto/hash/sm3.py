# The SM3 Cryptographic Hash Function draft-oscca-cfrg-sm3-02
# https://datatracker.ietf.org/doc/html/draft-oscca-cfrg-sm3-02.html
import builtins
from math import floor
from struct import pack, unpack

from ..utils.rotl import rotl

DIGEST_LENGTH = 256

# 4.  Primitives And Functions
IV = [
    0x7380166f, 0x4914b2b9, 0x172442d7, 0xda8a0600,
    0xa96f30bc, 0x163138aa, 0xe38dee4d, 0xb0fb0e4e,
]  # fmt: skip


def T_j(j):
    if 0 <= j <= 15:
        return 0x79CC4519
    elif 16 <= j <= 63:
        return 0x7A879D8A
    raise ValueError(f"Invalid T_j value: {j}")


def FF_j(x: int, y: int, z: int, j: int):
    if 0 <= j <= 15:
        return x ^ y ^ z
    elif 16 <= j <= 63:
        return (x & y) | (x & z) | (y & z)
    raise ValueError(f"Invalid FF_j value: {j}")


def GG_j(x: int, y: int, z: int, j: int):
    if 0 <= j <= 15:
        return x ^ y ^ z
    elif 16 <= j <= 63:
        return (x & y) | ((~x) & z)
    raise ValueError(f"Invalid GG_j value: {j}")


def P_0(x):
    return x ^ (rotl(x, 9)) ^ (rotl(x, 17))


def P_1(x):
    return x ^ (rotl(x, 15)) ^ (rotl(x, 23))


# 5.  Algorithm
# 5.2.  Padding PAD
def padding(msg: bytes) -> bytes:
    # l = bitlen(m)
    # L = num2str(l, 64)
    # k = 512 - (((l mod 512) + 1 + 64) mod 512)
    # K = num2str(0, k)
    # m' = m || 1 || K || L
    ll = len(msg) * 8
    k = 512 - (((ll % 512) + 1 + 64) % 512)
    return (
        msg
        + b"\x80"
        + int.to_bytes(0, length=floor(k / 8))
        + int.to_bytes(ll, length=8)
    )


# 5.3.  Iterative Hashing
# 5.3.2.  Message Expansion Function ME
def ME(B_i: bytes) -> tuple[list[int], list[int]]:
    W_ = list(unpack(">16I", B_i))
    for j in range(16, 67 + 1):
        W_.append(
            P_1(W_[j - 16] ^ W_[j - 9] ^ (rotl(W_[j - 3], 15)))
            ^ (rotl(W_[j - 13], 7))
            ^ W_[j - 6]
        )
    W_1_ = []
    for j in range(0, 63 + 1):
        W_1_.append(W_[j] ^ W_[j + 4])
    return (W_, W_1_)


# 5.3.3.  Compression Function CF
def CF(v_i: list[int], w_: list[int], w_1_: list[int]):
    a, b, c, d, e, f, g, h = v_i

    for j in range(0, 64):
        SS1 = rotl(((rotl(a, 12)) + e + (rotl(T_j(j), j % 32))) & 0xFFFFFFFF, 7)
        SS2 = SS1 ^ (rotl(a, 12))
        TT1 = (FF_j(a, b, c, j) + d + SS2 + w_1_[j]) & 0xFFFFFFFF
        TT2 = (GG_j(e, f, g, j) + h + SS1 + w_[j]) & 0xFFFFFFFF
        d = c
        c = rotl(b, 9)
        b = a
        a = TT1
        h = g
        g = rotl(f, 19)
        f = e
        e = P_0(TT2)

        a, b, c, d, e, f, g, h = map(lambda x: x & 0xFFFFFFFF, [a, b, c, d, e, f, g, h])

    v_j = [a, b, c, d, e, f, g, h]
    return [v_j[i] ^ v_i[i] for i in range(8)]


# 5.3.1.  Iterative Compression Process
def hash(msg: bytes | str) -> bytes:
    match type(msg):
        case builtins.str:
            msg_bytes = msg.encode("utf-8")  # type: ignore
        case builtins.bytes:
            msg_bytes = msg
        case _:
            raise ValueError(f"Invalid type: {type}")

    msg_bytes = padding(msg_bytes)  # type: ignore

    group_count = round(len(msg_bytes) / 64)

    B = [msg_bytes[i : i + 64] for i in range(0, len(msg_bytes), 64)]

    V = IV
    for i in range(0, group_count):
        w_, w_1_ = ME(B[i])
        V = CF(V, w_, w_1_)

    result = pack(">8I", *V)
    return result
