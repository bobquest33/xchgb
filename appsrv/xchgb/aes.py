import base64, random, string
from django.conf import settings
from Crypto.Cipher import AES

# the block size for the cipher object; must be 16, 24, or 32 for AES
BLOCK_SIZE = 32

# the character used for padding--with a block cipher such as AES, the value
# you encrypt must be a multiple of BLOCK_SIZE in length.  This character is
# used to ensure that your value is always a multiple of BLOCK_SIZE
PADDING = '{'

# one-liner to sufficiently pad the text to be encrypted
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING

# one-liners to encrypt/encode and decrypt/decode a string
# encrypt with AES, encode with base64
EncodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))
DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)

def encrypt(s, k=settings.SECRET_KEY):
    iv = "".join(random.sample(string.letters + string.digits, 16))
    cipher = AES.new(k[:BLOCK_SIZE], AES.MODE_CFB, iv)
    return iv, EncodeAES(cipher, s)

def decrypt(s, iv, k=settings.SECRET_KEY):
    cipher = AES.new(k[:BLOCK_SIZE], AES.MODE_CFB, iv)
    return DecodeAES(cipher, s)