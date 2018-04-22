#!/usr/bin/env python

import re
import json
from glob import glob


# 4yevz5pgquikitar.onion
# -----BEGIN RSA PRIVATE KEY-----
# MIICXgIBAAKBgQCqAppcmMtkvKqMZtu2o6dNUNIzqfhuKonvF3XHl4434emji5R/
# fo/foyHaZh5IAK8GBIJdyJna26lviYPXVkW8Wv9x/lzLSrD8+30Pu7f5ogo1QbLd
# vgRunow6Uts/t4NE6EKLj8BlgWGDiXyEVV26KKLluoVq5JNAwZMUdVpv0wIEAQAA
# AQKBgARTNMlqIMkMIS+GGdwXHXjFmAb/oUaODkEajb8RW5TDMvDtyGEgfSTqzuvY
# 4awSuM/IbuQhST9lHNvU6W9MqEr3v5Ozg6F3AESLJrTibgWTxn07uFSBtq9D3NFk
# bKX4ycDqC86rryuTpCY3qybn9z64PQoCzHu39H3vwMDLa0FhAkEA31FYdtxkZbbu
# 4QUaMhktTUgzEyfM4TnCygAFtfuEdiU/g/cCm19RVzUYrvzCWbCGMT6bqyRRPTUH
# QcT8Wm5bQwJBAMLkE1fr0AXyef3AcEhYKtsy69ELTugHSf7Sh4xz0S/4WzTko4y8
# RdMKuan+jmd+4auI3P+GYw0ivrneRXFdqDECQQCiUHHD5sHsqiDHl2xRjqXRc6mr
# cachRx4UfjU4Hv0Q3w0+MqTkj3cubOG3q/F9fOeiUwGsSZC1//Ivi9MKGzXvAkEA
# iiZrUw+vT7OJHUX5CmY0gKDVS/syiDr+MczOn2kHdJvBdHPkIY5OTlG/OziARxEe
# 4UaipMPogFsNWcaLeFx0AQJALl27PDsxtVXLaxeGcfyDw240R/nYNZePqw7B6/Tp
# 9zWCqhw2uRGMdXDoz5Urm8WEIGprh4H/6ARUWE77IyXMKw==
# -----END RSA PRIVATE KEY-----

kheader = r'[-]+BEGIN\s*RSA\s*PRIVATE\s*KEY[-]+'
kfooter = r'[-]+END\s*RSA\s*PRIVATE\s*KEY[-]+\s\n'

expression = r"\s*\n?".join([
    '[-]{64}',
    r'(?P<hostname>\w+[.]onion)',
    # '(?P<key>.*?)+?'.format(kheader, kfooter)
    '\n*\s*(?P<key>(({kheader}\s*\n?|([a-zA-Z0-9+\/-]+|\s*\n*)|{kfooter})\s*\n)+?)\s*\n'.format(**locals()),

])

regex = re.compile(
    expression,
    re.M
)

# name = '0palace.txt'
print "["
for name in glob('*.txt'):
    found = regex.finditer(open(name).read())
    for item in found:
        data = item.groupdict()
        data['key'] = data.pop('key', '').strip()
        result = json.dumps(data, indent=2)
        print "".join([result, ","])

print "]"
