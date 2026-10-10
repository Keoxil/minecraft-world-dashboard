"""Cifrado opcional de los datos que sirve la página (AES-256-GCM, sin dependencias externas).

Si existe un archivo de clave de acceso, los .js con datos se escriben CIFRADOS: quien llegue a la página (o a la
carpeta sincronizada, o a Cloudflare) solo ve texto cifrado. El navegador descifra con la clave que escribe el
visitante; la clave nunca viaja al servidor.

  clave de acceso  -> PBKDF2-HMAC-SHA256 (600 000 vueltas, sal propia de esta instalación) -> clave AES de 256 bits
  cifrado          -> AES-256-GCM, IV aleatorio de 12 bytes por escritura, el nombre del dato va como AAD

El archivo de clave vive FUERA de la carpeta del proyecto (que puede estar en OneDrive):
  %LOCALAPPDATA%\\MinecraftWorldDashboard\\access_key.txt   (o la ruta de la variable MCDASH_KEY_FILE)

Si hay clave pero no se puede cifrar, se lanza un error: nunca se escribe en claro en silencio.
"""
import base64
import ctypes
import hashlib
import os
import sys

KDF_ITER = 600_000


class CryptoUnavailable(RuntimeError):
    pass


def key_file():
    if os.environ.get("MCDASH_KEY_FILE"):
        return os.path.abspath(os.environ["MCDASH_KEY_FILE"])
    if sys.platform.startswith("win"):
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    else:
        base = os.path.join(os.path.expanduser("~"), ".local", "share")
    return os.path.join(base, "MinecraftWorldDashboard", "access_key.txt")


def passphrase():
    """La clave de acceso configurada, o None si el cifrado no está activado."""
    try:
        with open(key_file(), encoding="utf-8") as fh:
            p = fh.readline()
        p = "".join(p.split()).replace("-", "").upper()      # igual que normaliza el navegador
        return p or None
    except OSError:
        return None


def _salt():
    path = os.path.join(os.path.dirname(key_file()), "access_salt.bin")
    try:
        s = open(path, "rb").read()
        if len(s) == 16:
            return s
    except OSError:
        pass
    s = os.urandom(16)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as fh:
        fh.write(s)
    return s


_cache = {}


def derive(passphrase_text, salt):
    k = (passphrase_text, salt)
    if k not in _cache:
        _cache.clear()
        _cache[k] = hashlib.pbkdf2_hmac("sha256", passphrase_text.encode("utf-8"), salt, KDF_ITER, dklen=32)
    return _cache[k]


# ------------------------------------------------------------------------------------ AES-GCM
def _gcm_windows(key, iv, plaintext, aad):
    from ctypes import POINTER, byref, c_ubyte, c_ulong, c_ulonglong, c_void_p, wintypes

    class AuthInfo(ctypes.Structure):
        _fields_ = [("cbSize", c_ulong), ("dwInfoVersion", c_ulong),
                    ("pbNonce", c_void_p), ("cbNonce", c_ulong),
                    ("pbAuthData", c_void_p), ("cbAuthData", c_ulong),
                    ("pbTag", c_void_p), ("cbTag", c_ulong),
                    ("pbMacContext", c_void_p), ("cbMacContext", c_ulong),
                    ("cbAAD", c_ulong), ("cbData", c_ulonglong), ("dwFlags", c_ulong)]

    bc = ctypes.WinDLL("bcrypt")
    bc.BCryptOpenAlgorithmProvider.argtypes = [POINTER(c_void_p), wintypes.LPCWSTR, wintypes.LPCWSTR, c_ulong]
    bc.BCryptSetProperty.argtypes = [c_void_p, wintypes.LPCWSTR, c_void_p, c_ulong, c_ulong]
    bc.BCryptGenerateSymmetricKey.argtypes = [c_void_p, POINTER(c_void_p), c_void_p, c_ulong, c_void_p, c_ulong, c_ulong]
    bc.BCryptEncrypt.argtypes = [c_void_p, c_void_p, c_ulong, c_void_p, c_void_p, c_ulong, c_void_p, c_ulong, POINTER(c_ulong), c_ulong]
    bc.BCryptDestroyKey.argtypes = [c_void_p]
    bc.BCryptCloseAlgorithmProvider.argtypes = [c_void_p, c_ulong]

    alg, hkey = c_void_p(), c_void_p()
    if bc.BCryptOpenAlgorithmProvider(byref(alg), "AES", None, 0) != 0:
        raise CryptoUnavailable("BCrypt: no se pudo abrir AES")
    try:
        mode = ctypes.create_unicode_buffer("ChainingModeGCM")
        if bc.BCryptSetProperty(alg, "ChainingMode", ctypes.cast(mode, c_void_p), (len("ChainingModeGCM") + 1) * 2, 0) != 0:
            raise CryptoUnavailable("BCrypt: no se pudo activar GCM")
        kbuf = ctypes.create_string_buffer(key, len(key))
        if bc.BCryptGenerateSymmetricKey(alg, byref(hkey), None, 0, ctypes.cast(kbuf, c_void_p), len(key), 0) != 0:
            raise CryptoUnavailable("BCrypt: clave no válida")
        try:
            nonce = ctypes.create_string_buffer(iv, len(iv))
            tag = ctypes.create_string_buffer(16)
            aadb = ctypes.create_string_buffer(aad, max(1, len(aad)))
            pt = ctypes.create_string_buffer(plaintext, max(1, len(plaintext)))
            out = ctypes.create_string_buffer(max(1, len(plaintext)))
            ai = AuthInfo()
            ai.cbSize = ctypes.sizeof(AuthInfo)
            ai.dwInfoVersion = 1
            ai.pbNonce, ai.cbNonce = ctypes.cast(nonce, c_void_p), len(iv)
            ai.pbAuthData, ai.cbAuthData = ctypes.cast(aadb, c_void_p), len(aad)
            ai.pbTag, ai.cbTag = ctypes.cast(tag, c_void_p), 16
            done = c_ulong(0)
            st = bc.BCryptEncrypt(hkey, ctypes.cast(pt, c_void_p), len(plaintext), byref(ai), None, 0,
                                  ctypes.cast(out, c_void_p), len(plaintext), byref(done), 0)
            if st != 0:
                raise CryptoUnavailable("BCrypt: error de cifrado 0x%08X" % (st & 0xFFFFFFFF))
            return out.raw[:len(plaintext)] + tag.raw
        finally:
            bc.BCryptDestroyKey(hkey)
    finally:
        bc.BCryptCloseAlgorithmProvider(alg, 0)


def _gcm_openssl(key, iv, plaintext, aad):
    import ctypes.util
    from ctypes import byref, c_int, c_void_p
    names = ["libcrypto-3-x64.dll", "libcrypto-3.dll", "libcrypto.so.3", "libcrypto.so", "libcrypto.dylib", ctypes.util.find_library("crypto")]
    lib = None
    for n in names:
        if not n:
            continue
        try:
            lib = ctypes.CDLL(n)
            break
        except OSError:
            continue
    if lib is None:
        raise CryptoUnavailable("no hay libcrypto")
    lib.EVP_CIPHER_CTX_new.restype = c_void_p
    lib.EVP_aes_256_gcm.restype = c_void_p
    ctx = c_void_p(lib.EVP_CIPHER_CTX_new())
    try:
        if lib.EVP_EncryptInit_ex(ctx, c_void_p(lib.EVP_aes_256_gcm()), None, None, None) != 1:
            raise CryptoUnavailable("libcrypto: init")
        lib.EVP_CIPHER_CTX_ctrl(ctx, 0x9, len(iv), None)              # EVP_CTRL_AEAD_SET_IVLEN
        if lib.EVP_EncryptInit_ex(ctx, None, None, key, iv) != 1:
            raise CryptoUnavailable("libcrypto: clave/iv")
        n = c_int(0)
        if aad:
            lib.EVP_EncryptUpdate(ctx, None, byref(n), aad, len(aad))
        out = ctypes.create_string_buffer(len(plaintext) + 16)
        if lib.EVP_EncryptUpdate(ctx, out, byref(n), plaintext, len(plaintext)) != 1:
            raise CryptoUnavailable("libcrypto: cifrado")
        total = n.value
        fin = ctypes.create_string_buffer(16)
        lib.EVP_EncryptFinal_ex(ctx, fin, byref(n))
        tag = ctypes.create_string_buffer(16)
        lib.EVP_CIPHER_CTX_ctrl(ctx, 0x10, 16, tag)                    # EVP_CTRL_AEAD_GET_TAG
        return out.raw[:total] + tag.raw
    finally:
        lib.EVP_CIPHER_CTX_free(ctx)


def aes_gcm_encrypt(key, iv, plaintext, aad=b""):
    """Devuelve texto cifrado + etiqueta de 16 bytes (el formato que espera WebCrypto)."""
    if sys.platform.startswith("win"):
        try:
            return _gcm_windows(key, iv, plaintext, aad)
        except (OSError, AttributeError) as e:
            raise CryptoUnavailable(str(e))
    return _gcm_openssl(key, iv, plaintext, aad)


def seal(name, text):
    """Cifra `text` (str) para la ranura `name` y devuelve el diccionario que se publica."""
    p = passphrase()
    if p is None:
        raise CryptoUnavailable("sin clave de acceso")
    salt = _salt()
    iv = os.urandom(12)
    ct = aes_gcm_encrypt(derive(p, salt), iv, text.encode("utf-8"), name.encode("ascii"))
    b = lambda x: base64.b64encode(x).decode("ascii")
    return {"v": 1, "kdf": "pbkdf2-sha256", "it": KDF_ITER, "s": b(salt), "i": b(iv), "c": b(ct)}
