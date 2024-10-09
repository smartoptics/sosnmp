#
# This file is part of pysnmp software.
#
# Copyright (c) 2005-2020, Ilya Etingof <etingof@gmail.com>
# License: https://www.pysnmp.com/pysnmp/license.html
#
from hashlib import md5, sha1

from pyasn1.type import univ


def hashPassphrase(passphrase, hashFunc) -> univ.OctetString:
    """Return hash of passphrase using hashFunc hash function."""
    passphrase = univ.OctetString(passphrase).asOctets()
    # noinspection PyDeprecation,PyCallingNonCallable
    hasher = hashFunc()
    ringBuffer = passphrase * (64 // len(passphrase) + 1)
    # noinspection PyTypeChecker
    ringBufferLen = len(ringBuffer)
    count = 0
    mark = 0
    while count < 16384:
        e = mark + 64
        if e < ringBufferLen:
            hasher.update(ringBuffer[mark:e])
            mark = e
        else:
            hasher.update(
                ringBuffer[mark:ringBufferLen] + ringBuffer[0 : e - ringBufferLen]
            )
            mark = e - ringBufferLen
        count += 1
    digest = hasher.digest()
    return univ.OctetString(digest)


def passwordToKey(passphrase, snmpEngineId, hashFunc) -> univ.OctetString:
    """Return key from password."""
    return localizeKey(hashPassphrase(passphrase, hashFunc), snmpEngineId, hashFunc)


def localizeKey(passKey, snmpEngineId, hashFunc) -> univ.OctetString:
    """Localize passKey with snmpEngineId using hashFunc hash function."""
    passKey = univ.OctetString(passKey).asOctets()
    # noinspection PyDeprecation,PyCallingNonCallable
    digest = hashFunc(passKey + snmpEngineId.asOctets() + passKey).digest()
    return univ.OctetString(digest)


# RFC3414: A.2.1
def hashPassphraseMD5(passphrase) -> univ.OctetString:
    """Return MD5 hash of passphrase."""
    return hashPassphrase(passphrase, md5)


# RFC3414: A.2.2
def hashPassphraseSHA(passphrase) -> univ.OctetString:
    """Return SHA-1 hash of passphrase."""
    return hashPassphrase(passphrase, sha1)


def passwordToKeyMD5(passphrase, snmpEngineId) -> univ.OctetString:
    """Return MD5 key from password."""
    return localizeKey(hashPassphraseMD5(passphrase), snmpEngineId, md5)


def passwordToKeySHA(passphrase, snmpEngineId) -> univ.OctetString:
    """Return SHA-1 key from password."""
    return localizeKey(hashPassphraseSHA(passphrase), snmpEngineId, sha1)


def localizeKeyMD5(passKey, snmpEngineId) -> univ.OctetString:
    """Localize passKey with snmpEngineId using MD5 hash function."""
    return localizeKey(passKey, snmpEngineId, md5)


def localizeKeySHA(passKey, snmpEngineId) -> univ.OctetString:
    """Localize passKey with snmpEngineId using SHA1 hash function."""
    return localizeKey(passKey, snmpEngineId, sha1)
