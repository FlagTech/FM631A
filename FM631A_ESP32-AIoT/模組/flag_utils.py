import binascii
from hashlib import sha1

# Clone form
# https://github.com/micropython/micropython-lib/blob/master/base64/base64.py
# Importing the original base64 module would make error while importing
# the re module. So as a workaround, I take the b64encode() funciton along.def b64encode(s, altchars=None):

bytes_types = (bytes, bytearray)  # Types acceptable as binary data

def b64encode(s, altchars=None):
    """Encode a byte string using Base64.

    s is the byte string to encode.  Optional altchars must be a byte
    string of length 2 which specifies an alternative alphabet for the
    '+' and '/' characters.  This allows an application to
    e.g. generate url or filesystem safe Base64 strings.

    The encoded byte string is returned.
    """
    if not isinstance(s, bytes_types):
        raise TypeError("expected bytes, not %s" % s.__class__.__name__)
    # Strip off the trailing newline
    encoded = binascii.b2a_base64(s)[:-1]
    if altchars is not None:
        if not isinstance(altchars, bytes_types):
            raise TypeError("expected bytes, not %s"
                            % altchars.__class__.__name__)
        assert len(altchars) == 2, repr(altchars)
        return encoded.translate(bytes.maketrans(b'+/', altchars))
    return encoded

# Clone form
# https://learn.adafruit.com/circuitpython-totp-otp-2fa-authy-authenticator-friend/software
# The HMAC module in micropython-lib
# (https://github.com/micropython/micropython-lib/tree/master/hmac)
# isn't compatible with sha1 in the hashlib.
# As a workaround, I use the code sample for circuitpython.

def HMAC_sha1(k, m):
    SHA1_BLOCK_SIZE = 64
    KEY_BLOCK = k + (b'\0' * (SHA1_BLOCK_SIZE - len(k)))
    KEY_INNER = bytes((x ^ 0x36) for x in KEY_BLOCK)
    KEY_OUTER = bytes((x ^ 0x5C) for x in KEY_BLOCK)
    inner_message = KEY_INNER + m
    outer_message = KEY_OUTER + sha1(inner_message).digest()
    return sha1(outer_message)

weekdays = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')
months = (
    'Jan', 'Feb', 'Mar',
    'Apr', 'May', 'Jun',
    'Jul', 'Aug', 'Set',
    'Oct', 'Nov', 'Dec'
)

def to_x_date(localtime):
    x_date = b'x-date: {}, {:02d} {} {:04d} {:02d}:{:02d}:{:02d} GMT'.format(
        weekdays[localtime[6]], # weekday
        localtime[2],           # date
        months[localtime[1] - 1],   # month
        localtime[0],           # year
        localtime[3],           # hour
        localtime[4],           # mineute
        localtime[5],           # seconds
    )
    return x_date






