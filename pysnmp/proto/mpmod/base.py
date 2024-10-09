#
# This file is part of pysnmp software.
#
# Copyright (c) 2005-2020, Ilya Etingof <etingof@gmail.com>
# License: https://www.pysnmp.com/pysnmp/license.html
#
from pysnmp.proto import error
from pysnmp.proto.mpmod import cache


class AbstractMessageProcessingModel:
    """Create a message processing model object."""

    SNMP_MSG_SPEC = NotImplementedError

    def __init__(self):
        """Create a message processing model object."""
        self._snmpMsgSpec = self.SNMP_MSG_SPEC()  # local copy
        self._cache = cache.Cache()

    def prepareOutgoingMessage(
        self,
        snmpEngine,
        transportDomain,
        transportAddress,
        messageProcessingModel,
        securityModel,
        securityName,
        securityLevel,
        contextEngineId,
        contextName,
        pduVersion,
        pdu,
        expectResponse,
        sendPduHandle,
    ):
        """Prepare SNMP message for dispatch."""
        raise error.ProtocolError("method not implemented")

    def prepareResponseMessage(
        self,
        snmpEngine,
        messageProcessingModel,
        securityModel,
        securityName,
        securityLevel,
        contextEngineId,
        contextName,
        pduVersion,
        pdu,
        maxSizeResponseScopedPDU,
        stateReference,
        statusInformation,
    ):
        """Prepare SNMP message for response."""
        raise error.ProtocolError("method not implemented")

    def prepareDataElements(
        self, snmpEngine, transportDomain, transportAddress, wholeMsg
    ):
        """Prepare SNMP message data elements."""
        raise error.ProtocolError("method not implemented")

    def releaseStateInformation(self, sendPduHandle):
        """Release state information."""
        try:
            self._cache.popBySendPduHandle(sendPduHandle)
        except error.ProtocolError:
            pass  # XXX maybe these should all follow some scheme?

    def receiveTimerTick(self, snmpEngine, timeNow):
        """Process a timer tick."""
        self._cache.expireCaches()
