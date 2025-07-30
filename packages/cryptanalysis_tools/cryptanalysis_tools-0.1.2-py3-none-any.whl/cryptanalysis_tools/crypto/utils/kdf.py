from math import ceil

from ..hash import sm3


# /* X9.63 with no salt happens to match the KDF used in SM2 */
# Key derivation function from X9.63/SECG
# https://www.secg.org/sec1-v1.99.dif.pdf
# ANSI-X9.63-KDF
def ansi_x963_with_nosalt_kdf(z: bytes, klen):
    # TODO not support klen % 8 != 0
    if klen % 8 != 0:
        raise ValueError("klen must be multiple of 8, others not support now")
    Ha = b""
    ct = 0x0000000000000001
    for i in range(1, ceil(klen / sm3.DIGEST_LENGTH) + 1):
        Ha += sm3.hash(z + ct.to_bytes(4))
        ct += 1
    K = Ha
    return K[: ceil(klen / 8)]
