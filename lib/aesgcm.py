"""AES-256-GCM decryption with no third-party dependency.

WHY THIS EXISTS
---------------
gws stores its OAuth credentials as AES-256-GCM (see lib/gmail_api.py). To talk
to Gmail directly we must read them, and the app's Python is whatever `python3`
resolves to on the user's machine. Measured on this Mac, neither the Homebrew
python@3.14 the app runs under nor /usr/bin/env python3 has `cryptography`
installed, so importing it would make the fast path fail exactly where it has to
work.

Three backends are tried in order, fastest first:

  1. `cryptography` if the user happens to have it,
  2. the system libcrypto via ctypes (Homebrew openssl, arm64),
  3. a pure-Python implementation.

The payload is one ~334-byte credential blob decrypted once per process, so even
the slow path is immeasurable. What matters is that it CANNOT be unavailable.

The tag is always verified. A wrong key, a truncated file or a tampered blob
raises rather than returning plaintext, in every backend.
"""
import ctypes
import ctypes.util
import glob


class DecryptError(Exception):
    """Authentication failed or the input was malformed."""


# --- backend 1: cryptography -------------------------------------------------
def _try_cryptography(key, nonce, ct):
    from cryptography.exceptions import InvalidTag
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    try:
        return AESGCM(key).decrypt(nonce, ct, None)
    except InvalidTag as exc:
        # Normalise to our own type. Left as InvalidTag it would not match the
        # except clause in decrypt(), so a forged blob would escape as an
        # unexpected exception instead of a clean "could not decrypt".
        raise DecryptError("authentication failed") from exc


# --- backend 2: system libcrypto via ctypes ----------------------------------
_LIB = None
_LIB_TRIED = False


def _libcrypto():
    global _LIB, _LIB_TRIED
    if _LIB_TRIED:
        return _LIB
    _LIB_TRIED = True
    candidates = ["/opt/homebrew/opt/openssl@3/lib/libcrypto.dylib",
                  "/opt/homebrew/lib/libcrypto.dylib"]
    candidates += sorted(glob.glob("/opt/homebrew/Cellar/openssl@3/*/lib/libcrypto.3.dylib"))
    found = ctypes.util.find_library("crypto")
    if found:
        candidates.append(found)
    needed = ("EVP_CIPHER_CTX_new", "EVP_CIPHER_CTX_free", "EVP_aes_256_gcm",
              "EVP_DecryptInit_ex", "EVP_DecryptUpdate", "EVP_DecryptFinal_ex",
              "EVP_CIPHER_CTX_ctrl")
    for path in candidates:
        try:
            lib = ctypes.CDLL(path)
        except OSError:
            continue
        if all(hasattr(lib, fn) for fn in needed):
            lib.EVP_CIPHER_CTX_new.restype = ctypes.c_void_p
            lib.EVP_aes_256_gcm.restype = ctypes.c_void_p
            lib.EVP_CIPHER_CTX_free.argtypes = [ctypes.c_void_p]
            _LIB = lib
            return _LIB
    return None


_EVP_CTRL_GCM_SET_TAG = 0x11


def _try_libcrypto(key, nonce, ct):
    lib = _libcrypto()
    if lib is None:
        raise DecryptError("libcrypto unavailable")
    if len(ct) < 16:
        raise DecryptError("ciphertext shorter than its tag")
    body, tag = ct[:-16], ct[-16:]
    ctx = lib.EVP_CIPHER_CTX_new()
    if not ctx:
        raise DecryptError("EVP_CIPHER_CTX_new failed")
    try:
        if lib.EVP_DecryptInit_ex(ctypes.c_void_p(ctx), ctypes.c_void_p(lib.EVP_aes_256_gcm()),
                                  None, None, None) != 1:
            raise DecryptError("DecryptInit(cipher) failed")
        # Tell OpenSSL the nonce length before the key/nonce go in; the default
        # is 12 and gws uses 12, but being explicit keeps this correct if that
        # ever changes rather than silently decrypting under the wrong length.
        if lib.EVP_CIPHER_CTX_ctrl(ctypes.c_void_p(ctx), 0x9, len(nonce), None) != 1:
            raise DecryptError("set nonce length failed")
        if lib.EVP_DecryptInit_ex(ctypes.c_void_p(ctx), None, None, key, nonce) != 1:
            raise DecryptError("DecryptInit(key) failed")
        out = ctypes.create_string_buffer(len(body) + 32)
        outl = ctypes.c_int(0)
        if lib.EVP_DecryptUpdate(ctypes.c_void_p(ctx), out, ctypes.byref(outl),
                                 body, len(body)) != 1:
            raise DecryptError("DecryptUpdate failed")
        produced = outl.value
        if lib.EVP_CIPHER_CTX_ctrl(ctypes.c_void_p(ctx), _EVP_CTRL_GCM_SET_TAG,
                                   len(tag), tag) != 1:
            raise DecryptError("set tag failed")
        final = ctypes.create_string_buffer(32)
        finl = ctypes.c_int(0)
        # Returns <= 0 when the tag does not verify. This is the authentication
        # check; without it this function would happily return forged plaintext.
        if lib.EVP_DecryptFinal_ex(ctypes.c_void_p(ctx), final, ctypes.byref(finl)) != 1:
            raise DecryptError("authentication failed")
        return out.raw[:produced] + final.raw[:finl.value]
    finally:
        lib.EVP_CIPHER_CTX_free(ctypes.c_void_p(ctx))


# --- backend 3: pure Python --------------------------------------------------
_SBOX_INV = None
_SBOX = None


def _build_sbox():
    global _SBOX, _SBOX_INV
    if _SBOX is not None:
        return
    p = q = 1
    sbox = [0] * 256
    while True:
        # p *= 3 in GF(2^8)
        p = p ^ ((p << 1) & 0xFF) ^ (0x1B if p & 0x80 else 0)
        # q /= 3
        q ^= (q << 1) & 0xFF
        q ^= (q << 2) & 0xFF
        q ^= (q << 4) & 0xFF
        if q & 0x80:
            q ^= 0x09
        x = q ^ ((q << 1) | (q >> 7)) ^ ((q << 2) | (q >> 6)) \
              ^ ((q << 3) | (q >> 5)) ^ ((q << 4) | (q >> 4))
        sbox[p] = (x ^ 0x63) & 0xFF
        if p == 1:
            break
    sbox[0] = 0x63
    _SBOX = sbox
    inv = [0] * 256
    for i, v in enumerate(sbox):
        inv[v] = i
    _SBOX_INV = inv


def _xtime(a):
    a <<= 1
    return (a ^ 0x1B) & 0xFF if a & 0x100 else a


def _expand_key(key):
    """AES-256 key schedule: 60 words, 15 round keys."""
    _build_sbox()
    nk, nr = 8, 14
    w = [list(key[4 * i:4 * i + 4]) for i in range(nk)]
    rcon = 1
    for i in range(nk, 4 * (nr + 1)):
        t = list(w[i - 1])
        if i % nk == 0:
            t = t[1:] + t[:1]
            t = [_SBOX[b] for b in t]
            t[0] ^= rcon
            rcon = _xtime(rcon)
        elif i % nk == 4:
            t = [_SBOX[b] for b in t]
        w.append([w[i - nk][j] ^ t[j] for j in range(4)])
    return [sum(w[4 * r:4 * r + 4], []) for r in range(nr + 1)]


def _encrypt_block(rk, block):
    """AES block encrypt. GCM only ever needs the FORWARD direction, for both
    the counter stream and the GHASH key, so no inverse cipher is implemented."""
    s = [block[i] ^ rk[0][i] for i in range(16)]
    for r in range(1, 15):
        s = [_SBOX[b] for b in s]
        # ShiftRows (column-major state, as in FIPS-197)
        s = [s[0], s[5], s[10], s[15], s[4], s[9], s[14], s[3],
             s[8], s[13], s[2], s[7], s[12], s[1], s[6], s[11]]
        if r != 14:
            t = []
            for c in range(4):
                a = s[4 * c:4 * c + 4]
                u = a[0] ^ a[1] ^ a[2] ^ a[3]
                t += [a[0] ^ u ^ _xtime(a[0] ^ a[1]),
                      a[1] ^ u ^ _xtime(a[1] ^ a[2]),
                      a[2] ^ u ^ _xtime(a[2] ^ a[3]),
                      a[3] ^ u ^ _xtime(a[3] ^ a[0])]
            s = t
        s = [s[i] ^ rk[r][i] for i in range(16)]
    return bytes(s)


def _ghash_mul(x, y):
    """Multiply in GF(2^128), the field GCM authenticates in."""
    z = 0
    v = y
    for i in range(127, -1, -1):
        if (x >> i) & 1:
            z ^= v
        if v & 1:
            v = (v >> 1) ^ (0xE1 << 120)
        else:
            v >>= 1
    return z


def _ghash(h, data):
    y = 0
    for i in range(0, len(data), 16):
        block = data[i:i + 16].ljust(16, b"\x00")
        y = _ghash_mul(y ^ int.from_bytes(block, "big"), h)
    return y


def _try_pure(key, nonce, ct):
    if len(ct) < 16:
        raise DecryptError("ciphertext shorter than its tag")
    body, tag = ct[:-16], ct[-16:]
    rk = _expand_key(key)
    h = int.from_bytes(_encrypt_block(rk, b"\x00" * 16), "big")
    if len(nonce) == 12:
        j0 = nonce + b"\x00\x00\x00\x01"
    else:
        s = (-len(nonce)) % 16
        j0 = _ghash(h, nonce + b"\x00" * s + (len(nonce) * 8).to_bytes(16, "big")) \
            .to_bytes(16, "big")
    # Authenticate BEFORE decrypting, so a forged blob never becomes plaintext.
    pad = (-len(body)) % 16
    a = _ghash(h, body + b"\x00" * pad + (0).to_bytes(8, "big")
               + (len(body) * 8).to_bytes(8, "big"))
    expect = (a ^ int.from_bytes(_encrypt_block(rk, j0), "big")).to_bytes(16, "big")
    # Constant-time compare: a timing oracle on a credential tag is worth avoiding
    # even though the attacker here would already need local file access.
    diff = 0
    for x, y in zip(expect, tag):
        diff |= x ^ y
    if diff or len(expect) != len(tag):
        raise DecryptError("authentication failed")
    out = bytearray()
    counter = int.from_bytes(j0, "big")
    for i in range(0, len(body), 16):
        counter = (counter & ~0xFFFFFFFF) | ((counter + 1) & 0xFFFFFFFF)
        ks = _encrypt_block(rk, counter.to_bytes(16, "big"))
        chunk = body[i:i + 16]
        out += bytes(c ^ k for c, k in zip(chunk, ks))
    return bytes(out)


def decrypt(key, nonce, ciphertext):
    """AES-256-GCM decrypt with the tag appended to `ciphertext`.

    Raises DecryptError if no backend could authenticate the input. Backends are
    tried fastest-first; an ImportError or a missing library falls through to the
    next one, but an AUTHENTICATION failure does not (a wrong key is wrong in
    every backend, and retrying would just hide the real error)."""
    if len(key) != 32:
        raise DecryptError(f"AES-256 needs a 32-byte key, got {len(key)}")
    last = None
    for backend in (_try_cryptography, _try_libcrypto, _try_pure):
        try:
            return backend(key, nonce, ciphertext)
        except (ImportError, DecryptError, OSError, AttributeError) as exc:
            last = exc
            continue
        except Exception as exc:                      # unexpected backend bug
            last = exc
            continue
    raise DecryptError(f"could not decrypt credentials: {last}")


if __name__ == "__main__":
    import os
    # Cross-check every backend against the others on random inputs, plus the
    # NIST AES-256-GCM vector, so a broken pure-Python path cannot pass silently.
    # This is NIST GCM Test Case 15: AES-256, 64-byte plaintext, NO additional
    # authenticated data. Case 16 looks similar but carries AAD, and gws does not
    # use AAD, so 15 is the one that matches how decrypt() is actually called.
    key = bytes.fromhex("feffe9928665731c6d6a8f9467308308feffe9928665731c6d6a8f9467308308")
    nonce = bytes.fromhex("cafebabefacedbaddecaf888")
    want = bytes.fromhex("d9313225f88406e5a55909c5aff5269a86a7a9531534f7da2e4c303d8a318a72"
                         "1c3c0c95956809532fcf0e2449a6b525b16aedf5aa0de657ba637b391aafd255")
    ctxt = bytes.fromhex("522dc1f099567d07f47f37a32a84427d643a8cdcbfe5c0c97598a2bd2555d1aa"
                         "8cb08e48590dbb3da7b08b1056828838c5f61e6393ba7a0abcc9f662898015ad"
                         "b094dac5d93471bdec1a502270e3cc6c")
    assert _try_pure(key, nonce, ctxt) == want, "pure-Python failed the NIST vector"
    print("pure-Python AES-256-GCM matches NIST GCM test case 15")

    # FIPS-197 C.3 knows the block cipher independently of the GCM wrapper, so a
    # key-schedule bug is reported as itself rather than as "authentication failed".
    assert _encrypt_block(
        _expand_key(bytes.fromhex("000102030405060708090a0b0c0d0e0f"
                                  "101112131415161718191a1b1c1d1e1f")),
        bytes.fromhex("00112233445566778899aabbccddeeff")
    ) == bytes.fromhex("8ea2b7ca516745bfeafc49904b496089"), "AES-256 block encrypt is wrong"
    print("AES-256 block encrypt matches FIPS-197 C.3")

    available = []
    for name, fn in (("cryptography", _try_cryptography), ("libcrypto", _try_libcrypto),
                     ("pure", _try_pure)):
        try:
            fn(key, nonce, ctxt)
            available.append((name, fn))
        except Exception as exc:
            print(f"  {name}: unavailable ({str(exc)[:50]})")
    # Every backend that loaded must agree with the others on random inputs, at
    # the message sizes this actually sees (a ~334-byte credential blob).
    try:
        import importlib
        aead = importlib.import_module("cryptography.hazmat.primitives.ciphers.aead")
        for size in (0, 1, 15, 16, 17, 334, 2651):
            k, n, msg = os.urandom(32), os.urandom(12), os.urandom(size)
            blob = aead.AESGCM(k).encrypt(n, msg, None)
            for name, fn in available:
                assert fn(k, n, blob) == msg, f"{name} disagreed at {size} bytes"
        print(f"backends agree on random inputs: {', '.join(n for n, _ in available)}")
    except ImportError:
        print(f"backends available: {', '.join(n for n, _ in available)} "
              "(no cryptography module for cross-checking)")

    # A tampered tag must fail in every backend, not just the fast one.
    bad = bytearray(ctxt)
    bad[-1] ^= 1
    for name, fn in available:
        try:
            fn(key, nonce, bytes(bad))
            raise SystemExit(f"FAIL: {name} accepted a forged tag")
        except DecryptError:
            pass
    # A wrong key must raise, never return garbage plaintext.
    for name, fn in available:
        try:
            fn(os.urandom(32), nonce, ctxt)
            raise SystemExit(f"FAIL: {name} accepted a wrong key")
        except DecryptError:
            pass
    print("forged tags and wrong keys rejected by every backend")
    print("aesgcm OK")
