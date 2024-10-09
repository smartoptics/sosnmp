#
# This file is part of pysnmp software.
#
# Copyright (c) 2005-2020, Ilya Etingof <etingof@gmail.com>
# License: https://www.pysnmp.com/pysnmp/license.html
#
from pysnmp.proto import error
from pysnmp.proto.errind import ErrorIndication
from pysnmp.proto.secmod import cache


class AbstractSecurityModel:
    """Abstract security model class."""

    SECURITY_MODEL_ID = None
    _cache: cache.Cache

    def __init__(self):
        """Create a security model object."""
        self._cache = cache.Cache()

    def processIncomingMsg(
        self,
        snmpEngine,
        messageProcessingModel,
        maxMessageSize,
        securityParameters,
        securityModel,
        securityLevel,
        wholeMsg,
        msg,
    ):
        """Process an incoming message."""
        raise error.ProtocolError("Security model %s not implemented" % self)

    def generateRequestMsg(
        self,
        snmpEngine,
        messageProcessingModel,
        globalData,
        maxMessageSize,
        securityModel,
        securityEngineID,
        securityName,
        securityLevel,
        scopedPDU,
    ):
        """Generate a request message."""
        raise error.ProtocolError("Security model %s not implemented" % self)

    def generateResponseMsg(
        self,
        snmpEngine,
        messageProcessingModel,
        globalData,
        maxMessageSize,
        securityModel,
        securityEngineID,
        securityName,
        securityLevel,
        scopedPDU,
        securityStateReference,
        ctx: ErrorIndication,
    ):
        """Generate a response message."""
        raise error.ProtocolError("Security model %s not implemented" % self)

    def releaseStateInformation(self, stateReference):
        """Release state information."""
        self._cache.pop(stateReference)

    def receiveTimerTick(self, snmpEngine, timeNow):
        """Process a timer tick."""
        pass

    def _close(self):
        """
        Close the security model to test memory leak.

        This method is intended for unit testing purposes only.
        It closes the security model and checks if all associated resources are released.
        """
        raise error.ProtocolError("Security model %s not implemented" % self)
