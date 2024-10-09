#
# This file is part of pysnmp software.
#
# Copyright (c) 2005-2020, Ilya Etingof <etingof@gmail.com>
# License: https://www.pysnmp.com/pysnmp/license.html
#
import sys

from pyasn1.type import univ
from pysnmp import debug, error, nextid
from pysnmp.entity.engine import SnmpEngine
from pysnmp.entity.rfc3413 import config
from pysnmp.proto import errind
from pysnmp.proto.api import v2c
from pysnmp.proto.error import StatusInformation
from pysnmp.proto.proxy import rfc2576

getNextHandle = nextid.Integer(0x7FFFFFFF)  # noqa: N816


class CommandGenerator:
    """SNMP command generator."""

    _null = univ.Null("")

    def __init__(self, **options):
        """Create a command generator object."""
        self.__options = options
        self.__pendingReqs = {}

    def processResponsePdu(
        self,
        snmpEngine,
        messageProcessingModel,
        securityModel,
        securityName,
        securityLevel,
        contextEngineId,
        contextName,
        pduVersion,
        PDU,
        statusInformation,
        sendPduHandle,
        cbCtx,
    ):
        """Process SNMP response."""
        origSendRequestHandle, cbFun, cbCtx = cbCtx

        # 3.1.1
        if sendPduHandle not in self.__pendingReqs:
            raise error.PySnmpError("Missing sendPduHandle %s" % sendPduHandle)

        (
            origTransportDomain,
            origTransportAddress,
            origMessageProcessingModel,
            origSecurityModel,
            origSecurityName,
            origSecurityLevel,
            origContextEngineId,
            origContextName,
            origPduVersion,
            origPdu,
            origTimeout,
            origRetryCount,
            origRetries,
            origDiscoveryRetries,
        ) = self.__pendingReqs.pop(sendPduHandle)

        snmpEngine.transportDispatcher.jobFinished(id(self))

        # 3.1.3
        if statusInformation:
            debug.logger & debug.FLAG_APP and debug.logger(
                f"processResponsePdu: sendPduHandle {sendPduHandle}, statusInformation {statusInformation}"
            )

            errorIndication = statusInformation["errorIndication"]

            if errorIndication in (errind.notInTimeWindow, errind.unknownEngineID):
                origDiscoveryRetries += 1
                origRetries = 0
            else:
                origDiscoveryRetries = 0
                origRetries += 1

            if (
                origRetries > origRetryCount
                or origDiscoveryRetries > self.__options.get("discoveryRetries", 4)
            ):
                debug.logger & debug.FLAG_APP and debug.logger(
                    "processResponsePdu: sendPduHandle %s, retry count %d exceeded"
                    % (sendPduHandle, origRetries)
                )
                cbFun(snmpEngine, origSendRequestHandle, errorIndication, None, cbCtx)
                return

            # User-side API assumes SMIv2
            if origMessageProcessingModel == 0:
                reqPDU = rfc2576.v2ToV1(origPdu)
                pduVersion = 0
            else:
                reqPDU = origPdu
                pduVersion = 1

            try:
                sendPduHandle = snmpEngine.msgAndPduDsp.sendPdu(
                    snmpEngine,
                    origTransportDomain,
                    origTransportAddress,
                    origMessageProcessingModel,
                    origSecurityModel,
                    origSecurityName,
                    origSecurityLevel,
                    origContextEngineId,
                    origContextName,
                    pduVersion,
                    reqPDU,
                    True,
                    origTimeout,
                    self.processResponsePdu,
                    (origSendRequestHandle, cbFun, cbCtx),
                )

                snmpEngine.transportDispatcher.jobStarted(id(self))

                self.__pendingReqs[sendPduHandle] = (
                    origTransportDomain,
                    origTransportAddress,
                    origMessageProcessingModel,
                    origSecurityModel,
                    origSecurityName,
                    origSecurityLevel,
                    origContextEngineId,
                    origContextName,
                    origPduVersion,
                    origPdu,
                    origTimeout,
                    origRetryCount,
                    origRetries,
                    origDiscoveryRetries,
                )
                return

            except StatusInformation:
                statusInformation = sys.exc_info()[1]
                debug.logger & debug.FLAG_APP and debug.logger(
                    "processResponsePdu: origSendRequestHandle {}, _sendPdu() failed with {!r}".format(
                        sendPduHandle, statusInformation
                    )
                )
                cbFun(
                    snmpEngine,
                    origSendRequestHandle,
                    statusInformation["errorIndication"],  # type: ignore
                    None,
                    cbCtx,
                )
                return

        if (
            origMessageProcessingModel != messageProcessingModel
            or origSecurityModel != securityModel
            or origSecurityName != origSecurityName
            or origContextEngineId
            and origContextEngineId != contextEngineId
            or origContextName
            and origContextName != contextName
            or origPduVersion != pduVersion
        ):
            debug.logger & debug.FLAG_APP and debug.logger(
                "processResponsePdu: sendPduHandle %s, request/response data mismatch"
                % sendPduHandle
            )

            cbFun(snmpEngine, origSendRequestHandle, "badResponse", None, cbCtx)
            return

        # User-side API assumes SMIv2
        if messageProcessingModel == 0:
            PDU = rfc2576.v1ToV2(PDU, origPdu)

        # 3.1.2
        if v2c.apiPDU.getRequestID(PDU) != v2c.apiPDU.getRequestID(origPdu):
            debug.logger & debug.FLAG_APP and debug.logger(
                "processResponsePdu: sendPduHandle %s, request-id/response-id mismatch"
                % sendPduHandle
            )
            cbFun(snmpEngine, origSendRequestHandle, "badResponse", None, cbCtx)
            return

        cbFun(snmpEngine, origSendRequestHandle, None, PDU, cbCtx)

    def sendPdu(
        self,
        snmpEngine: SnmpEngine,
        targetName,
        contextEngineId,
        contextName,
        PDU,
        cbFun,
        cbCtx,
    ):
        """Send SNMP PDU."""
        (
            transportDomain,
            transportAddress,
            timeout,
            retryCount,
            messageProcessingModel,
            securityModel,
            securityName,
            securityLevel,
        ) = config.getTargetInfo(snmpEngine, targetName)

        if snmpEngine.transportDispatcher is None:
            raise error.PySnmpError("No transport dispatcher available")
        # Convert timeout in seconds into timeout in timer ticks
        timeoutInTicks = (
            float(timeout) / 100 / snmpEngine.transportDispatcher.getTimerResolution()
        )

        SnmpEngineID, SnmpAdminString = snmpEngine.msgAndPduDsp.mibInstrumController.mibBuilder.importSymbols(  # type: ignore
            "SNMP-FRAMEWORK-MIB", "SnmpEngineID", "SnmpAdminString"
        )

        # Cast possible strings into bytes
        if contextEngineId:
            contextEngineId = SnmpEngineID(contextEngineId)
        contextName = SnmpAdminString(contextName)

        origPDU = PDU

        # User-side API assumes SMIv2
        if messageProcessingModel == 0:
            PDU = rfc2576.v2ToV1(PDU)
            pduVersion = 0
        else:
            pduVersion = 1

        sendRequestHandle = getNextHandle()

        # 3.1
        sendPduHandle = snmpEngine.msgAndPduDsp.sendPdu(
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
            PDU,
            True,
            timeoutInTicks,
            self.processResponsePdu,
            (sendRequestHandle, cbFun, cbCtx),
        )

        snmpEngine.transportDispatcher.jobStarted(id(self))

        self.__pendingReqs[sendPduHandle] = (
            transportDomain,
            transportAddress,
            messageProcessingModel,
            securityModel,
            securityName,
            securityLevel,
            contextEngineId,
            contextName,
            pduVersion,
            origPDU,
            timeoutInTicks,
            retryCount,
            0,
            0,
        )

        debug.logger & debug.FLAG_APP and debug.logger(
            "sendPdu: sendPduHandle %s, timeout %d*10 ms/%d ticks, retry 0 of %d"
            % (sendPduHandle, timeout, timeoutInTicks, retryCount)
        )

        return sendRequestHandle


class GetCommandGenerator(CommandGenerator):
    """SNMP GET command generator."""

    def processResponseVarBinds(
        self, snmpEngine, sendRequestHandle, errorIndication, PDU, cbCtx
    ):
        """Process SNMP GET response."""
        cbFun, cbCtx = cbCtx

        cbFun(
            snmpEngine,
            sendRequestHandle,
            errorIndication,
            PDU and v2c.apiPDU.getErrorStatus(PDU) or 0,
            PDU and v2c.apiPDU.getErrorIndex(PDU, muteErrors=True) or 0,
            PDU and v2c.apiPDU.getVarBinds(PDU) or (),
            cbCtx,
        )

    def sendVarBinds(
        self,
        snmpEngine,
        targetName,
        contextEngineId,
        contextName,
        varBinds,
        cbFun,
        cbCtx=None,
    ):
        """Send SNMP GET request."""
        reqPDU = v2c.GetRequestPDU()
        v2c.apiPDU.setDefaults(reqPDU)

        v2c.apiPDU.setVarBinds(reqPDU, varBinds)

        return self.sendPdu(
            snmpEngine,
            targetName,
            contextEngineId,
            contextName,
            reqPDU,
            self.processResponseVarBinds,
            (cbFun, cbCtx),
        )


class SetCommandGenerator(CommandGenerator):
    """SNMP SET command generator."""

    def processResponseVarBinds(
        self, snmpEngine, sendRequestHandle, errorIndication, PDU, cbCtx
    ):
        """Process SNMP SET response."""
        cbFun, cbCtx = cbCtx

        cbFun(
            snmpEngine,
            sendRequestHandle,
            errorIndication,
            PDU and v2c.apiPDU.getErrorStatus(PDU) or 0,
            PDU and v2c.apiPDU.getErrorIndex(PDU, muteErrors=True) or 0,
            PDU and v2c.apiPDU.getVarBinds(PDU) or (),
            cbCtx,
        )

    def sendVarBinds(
        self,
        snmpEngine,
        targetName,
        contextEngineId,
        contextName,
        varBinds,
        cbFun,
        cbCtx=None,
    ):
        """Send SNMP SET request."""
        reqPDU = v2c.SetRequestPDU()
        v2c.apiPDU.setDefaults(reqPDU)

        v2c.apiPDU.setVarBinds(reqPDU, varBinds)

        return self.sendPdu(
            snmpEngine,
            targetName,
            contextEngineId,
            contextName,
            reqPDU,
            self.processResponseVarBinds,
            (cbFun, cbCtx),
        )


class NextCommandGeneratorSingleRun(CommandGenerator):
    """Single-run SNMP GETNEXT command generator."""

    def processResponseVarBinds(
        self, snmpEngine, sendRequestHandle, errorIndication, PDU, cbCtx
    ):
        """Process SNMP GETNEXT response."""
        targetName, contextEngineId, contextName, reqPDU, cbFun, cbCtx = cbCtx

        cbFun(
            snmpEngine,
            sendRequestHandle,
            errorIndication,
            PDU and v2c.apiPDU.getErrorStatus(PDU) or 0,
            PDU and v2c.apiPDU.getErrorIndex(PDU, muteErrors=True) or 0,
            PDU and v2c.apiPDU.getVarBinds(PDU) or (),
            cbCtx,
        )

    def sendVarBinds(
        self,
        snmpEngine,
        targetName,
        contextEngineId,
        contextName,
        varBinds,
        cbFun,
        cbCtx=None,
    ):
        """Send SNMP GETNEXT request."""
        reqPDU = v2c.GetNextRequestPDU()
        v2c.apiPDU.setDefaults(reqPDU)

        v2c.apiPDU.setVarBinds(reqPDU, varBinds)

        return self.sendPdu(
            snmpEngine,
            targetName,
            contextEngineId,
            contextName,
            reqPDU,
            self.processResponseVarBinds,
            (targetName, contextEngineId, contextName, reqPDU, cbFun, cbCtx),
        )


class NextCommandGenerator(NextCommandGeneratorSingleRun):
    """SNMP GETNEXT command generator."""

    def processResponseVarBinds(
        self, snmpEngine, sendRequestHandle, errorIndication, PDU, cbCtx
    ):
        """Process SNMP GETNEXT response."""
        targetName, contextEngineId, contextName, reqPDU, cbFun, cbCtx = cbCtx

        if errorIndication:
            cbFun(snmpEngine, sendRequestHandle, errorIndication, 0, 0, (), cbCtx)
            return

        varBinds = v2c.apiPDU.getVarBinds(PDU)

        if v2c.apiPDU.getErrorStatus(PDU):
            errorIndication, varBinds = None, ()
        elif not varBinds:
            errorIndication, varBinds = errind.emptyResponse, ()

        if not cbFun(
            snmpEngine,
            sendRequestHandle,
            errorIndication,
            v2c.apiPDU.getErrorStatus(PDU),
            v2c.apiPDU.getErrorIndex(PDU, muteErrors=True),
            varBinds,
            cbCtx,
        ):
            debug.logger & debug.FLAG_APP and debug.logger(
                "processResponseVarBinds: sendRequestHandle %s, app says to stop walking"
                % sendRequestHandle
            )
            return  # app says enough

        if not varBinds:
            return  # no more objects available


class BulkCommandGeneratorSingleRun(CommandGenerator):
    """Single-run SNMP GETBULK command generator."""

    def processResponseVarBinds(
        self, snmpEngine, sendRequestHandle, errorIndication, PDU, cbCtx
    ):
        """Process SNMP GETBULK response."""
        (
            targetName,
            nonRepeaters,
            maxRepetitions,
            contextEngineId,
            contextName,
            reqPDU,
            cbFun,
            cbCtx,
        ) = cbCtx

        cbFun(
            snmpEngine,
            sendRequestHandle,
            errorIndication,
            PDU and v2c.apiPDU.getErrorStatus(PDU) or 0,
            PDU and v2c.apiPDU.getErrorIndex(PDU, muteErrors=True) or 0,
            PDU and v2c.apiPDU.getVarBinds(PDU) or (),
            cbCtx,
        )

    def sendVarBinds(
        self,
        snmpEngine,
        targetName,
        contextEngineId,
        contextName,
        nonRepeaters,
        maxRepetitions,
        varBinds,
        cbFun,
        cbCtx=None,
    ):
        """Send SNMP GETBULK request."""
        reqPDU = v2c.GetBulkRequestPDU()
        v2c.apiBulkPDU.setDefaults(reqPDU)

        v2c.apiBulkPDU.setNonRepeaters(reqPDU, nonRepeaters)
        v2c.apiBulkPDU.setMaxRepetitions(reqPDU, maxRepetitions)

        v2c.apiBulkPDU.setVarBinds(reqPDU, varBinds)

        return self.sendPdu(
            snmpEngine,
            targetName,
            contextEngineId,
            contextName,
            reqPDU,
            self.processResponseVarBinds,
            (
                targetName,
                nonRepeaters,
                maxRepetitions,
                contextEngineId,
                contextName,
                reqPDU,
                cbFun,
                cbCtx,
            ),
        )


class BulkCommandGenerator(BulkCommandGeneratorSingleRun):
    """Bulk SNMP GET command generator."""

    def processResponseVarBinds(
        self, snmpEngine, sendRequestHandle, errorIndication, PDU, cbCtx
    ):
        """Process SNMP GETBULK response."""
        (
            targetName,
            nonRepeaters,
            maxRepetitions,
            contextEngineId,
            contextName,
            reqPDU,
            cbFun,
            cbCtx,
        ) = cbCtx

        if errorIndication:
            cbFun(snmpEngine, sendRequestHandle, errorIndication, 0, 0, (), cbCtx)
            return

        varBinds = v2c.apiBulkPDU.getVarBinds(PDU)

        if v2c.apiBulkPDU.getErrorStatus(PDU):
            errorIndication, varBinds = None, ()
        elif not varBinds:
            errorIndication, varBinds = errind.emptyResponse, ()

        if not cbFun(
            snmpEngine,
            sendRequestHandle,
            errorIndication,
            v2c.apiBulkPDU.getErrorStatus(PDU),
            v2c.apiBulkPDU.getErrorIndex(PDU, muteErrors=True),
            varBinds,
            cbCtx,
        ):
            debug.logger & debug.FLAG_APP and debug.logger(
                "processResponseVarBinds: sendRequestHandle %s, app says to stop walking"
                % sendRequestHandle
            )
            return  # app says enough

        if not varBinds:
            return  # no more objects available
