#
# This file is part of pysnmp software.
#
# Copyright (c) 2005-2020, Ilya Etingof <etingof@gmail.com>
# License: https://www.pysnmp.com/pysnmp/license.html
#
from pysnmp.proto import error


class AbstractEncryptionService:
    """Abstract encryption service."""

    SERVICE_ID = None
    KEY_SIZE = 0

    def hashPassphrase(self, authProtocol, privKey):
        """Hash authentication key."""
        raise error.ProtocolError("no encryption")

    def localizeKey(self, authProtocol, privKey, snmpEngineID):
        """Localize privacy key."""
        raise error.ProtocolError("no encryption")

    def encryptData(self, encryptKey, privParameters, dataToEncrypt):
        """Encrypt data."""
        raise error.ProtocolError("no encryption")

    def decryptData(self, decryptKey, privParameters, encryptedData):
        """Decrypt data."""
        raise error.ProtocolError("no encryption")
