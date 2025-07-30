rotl = lambda x, n: ((x << n) & 0xFFFFFFFF) | ((x >> (32 - n)) & 0xFFFFFFFF)  # noqa: E731
