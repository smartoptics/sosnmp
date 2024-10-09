#
# This file is part of pysnmp software.
#
# Copyright (c) 2005-2020, Ilya Etingof <etingof@gmail.com>
# License: https://www.pysnmp.com/pysnmp/license.html
#
from pyasn1.type import univ
from pysnmp import nextid
from pysnmp.proto import error, rfc1155, rfc1157

# Shortcuts to SNMP types
Integer = univ.Integer
OctetString = univ.OctetString
Null = univ.Null
null = Null("")
ObjectIdentifier = univ.ObjectIdentifier

IpAddress = rfc1155.IpAddress
NetworkAddress = rfc1155.NetworkAddress
Counter = rfc1155.Counter
Gauge = rfc1155.Gauge
TimeTicks = rfc1155.TimeTicks
Opaque = rfc1155.Opaque

VarBind = rfc1157.VarBind
VarBindList = rfc1157.VarBindList
GetRequestPDU = rfc1157.GetRequestPDU
GetNextRequestPDU = rfc1157.GetNextRequestPDU
GetResponsePDU = rfc1157.GetResponsePDU
SetRequestPDU = rfc1157.SetRequestPDU
TrapPDU = rfc1157.TrapPDU
Message = rfc1157.Message


class VarBindAPI:
    """Var-bind API."""

    @staticmethod
    def setOIDVal(varBind, oidVal):
        """Set OID and value components of var-bind."""
        oid, val = oidVal[0], oidVal[1]
        varBind.setComponentByPosition(0, oid)
        if val is None:
            val = null
        varBind.setComponentByPosition(1).getComponentByPosition(1).setComponentByType(
            val.getTagSet(),
            val,
            verifyConstraints=False,
            matchTags=False,
            matchConstraints=False,
            innerFlag=True,
        )
        return varBind

    @staticmethod
    def getOIDVal(varBind):
        """Return OID and value components of var-bind."""
        return varBind[0], varBind[1].getComponent(1)


apiVarBind = VarBindAPI()  # noqa: N816

getNextRequestID = nextid.Integer(0xFFFFFF)  # noqa: N816


class PDUAPI:
    """SNMP PDU API."""

    _errorStatus = rfc1157.errorStatus.clone(0)
    _errorIndex = Integer(0)

    def setDefaults(self, pdu):
        """Set default values for SNMP PDU."""
        pdu.setComponentByPosition(
            0,
            getNextRequestID(),
            verifyConstraints=False,
            matchTags=False,
            matchConstraints=False,
        )
        pdu.setComponentByPosition(
            1,
            self._errorStatus,
            verifyConstraints=False,
            matchTags=False,
            matchConstraints=False,
        )
        pdu.setComponentByPosition(
            2,
            self._errorIndex,
            verifyConstraints=False,
            matchTags=False,
            matchConstraints=False,
        )
        varBindList = pdu.setComponentByPosition(3).getComponentByPosition(3)
        varBindList.clear()

    @staticmethod
    def getRequestID(pdu):
        """Return request ID component of SNMP PDU."""
        return pdu.getComponentByPosition(0)

    @staticmethod
    def setRequestID(pdu, value):
        """Set request ID component of SNMP PDU."""
        pdu.setComponentByPosition(0, value)

    @staticmethod
    def getErrorStatus(pdu):
        """Return error status component of SNMP PDU."""
        return pdu.getComponentByPosition(1)

    @staticmethod
    def setErrorStatus(pdu, value):
        """Set error status component of SNMP PDU."""
        pdu.setComponentByPosition(1, value)

    @staticmethod
    def getErrorIndex(pdu, muteErrors=False):
        """Return error index component of SNMP PDU."""
        errorIndex = pdu.getComponentByPosition(2)
        if errorIndex > len(pdu[3]):
            if muteErrors:
                return errorIndex.clone(len(pdu[3]))
            raise error.ProtocolError(
                f"Error index out of range: {errorIndex} > {len(pdu[3])}"
            )
        return errorIndex

    @staticmethod
    def setErrorIndex(pdu, value):
        """Set error index component of SNMP PDU."""
        pdu.setComponentByPosition(2, value)

    def setEndOfMibError(self, pdu, errorIndex):
        """Set end-of-MIB error status."""
        self.setErrorIndex(pdu, errorIndex)
        self.setErrorStatus(pdu, 2)

    def setNoSuchInstanceError(self, pdu, errorIndex):
        """Set no-such-instance error status."""
        self.setEndOfMibError(pdu, errorIndex)

    @staticmethod
    def getVarBindList(pdu):
        """Return var-bind list component of SNMP PDU."""
        return pdu.getComponentByPosition(3)

    @staticmethod
    def setVarBindList(pdu, varBindList):
        """Set var-bind list component of SNMP PDU."""
        pdu.setComponentByPosition(3, varBindList)

    @staticmethod
    def getVarBinds(pdu):
        """Return var-binds component of SNMP PDU."""
        return [
            apiVarBind.getOIDVal(varBind) for varBind in pdu.getComponentByPosition(3)
        ]

    @staticmethod
    def setVarBinds(pdu, varBinds):
        """Set var-binds component of SNMP PDU."""
        varBindList = pdu.setComponentByPosition(3).getComponentByPosition(3)
        varBindList.clear()
        for idx, varBind in enumerate(varBinds):
            if isinstance(varBind, VarBind):
                varBindList.setComponentByPosition(idx, varBind)
            else:
                varBindList.setComponentByPosition(idx)
                apiVarBind.setOIDVal(varBindList.getComponentByPosition(idx), varBind)

    def getResponse(self, reqPDU):
        """Build response PDU."""
        rspPDU = GetResponsePDU()
        self.setDefaults(rspPDU)
        self.setRequestID(rspPDU, self.getRequestID(reqPDU))
        return rspPDU

    def getVarBindTable(self, reqPDU, rspPDU):
        """Return var-bind table."""
        if apiPDU.getErrorStatus(rspPDU) == 2:
            varBindRow = [(vb[0], null) for vb in apiPDU.getVarBinds(reqPDU)]
        else:
            varBindRow = apiPDU.getVarBinds(rspPDU)
        return [varBindRow]

    def getNextVarBinds(self, varBinds, errorIndex=None):
        """Return next var-binds."""
        errorIndication = None

        if errorIndex:
            return errorIndication, []

        rspVarBinds = [(vb[0], null) for vb in varBinds]

        return errorIndication, rspVarBinds


apiPDU = PDUAPI()  # noqa: N816


class TrapPDUAPI:
    """SNMP trap PDU API."""

    _networkAddress = None
    _entOid = ObjectIdentifier((1, 3, 6, 1, 4, 1, 20408))
    _genericTrap = rfc1157.genericTrap.clone("coldStart")
    _zeroInt = univ.Integer(0)
    _zeroTime = TimeTicks(0)

    def setDefaults(self, pdu):
        """Set default values for SNMP trap PDU."""
        if self._networkAddress is None:
            try:
                import socket

                agentAddress = IpAddress(socket.gethostbyname(socket.gethostname()))
            except Exception:
                agentAddress = IpAddress("0.0.0.0")
            self._networkAddress = NetworkAddress().setComponentByPosition(
                0, agentAddress
            )
        pdu.setComponentByPosition(
            0,
            self._entOid,
            verifyConstraints=False,
            matchTags=False,
            matchConstraints=False,
        )
        pdu.setComponentByPosition(
            1,
            self._networkAddress,
            verifyConstraints=False,
            matchTags=False,
            matchConstraints=False,
        )
        pdu.setComponentByPosition(
            2,
            self._genericTrap,
            verifyConstraints=False,
            matchTags=False,
            matchConstraints=False,
        )
        pdu.setComponentByPosition(
            3,
            self._zeroInt,
            verifyConstraints=False,
            matchTags=False,
            matchConstraints=False,
        )
        pdu.setComponentByPosition(
            4,
            self._zeroTime,
            verifyConstraints=False,
            matchTags=False,
            matchConstraints=False,
        )
        varBindList = pdu.setComponentByPosition(5).getComponentByPosition(5)
        varBindList.clear()

    @staticmethod
    def getEnterprise(pdu):
        """Return enterprise component of SNMP trap PDU."""
        return pdu.getComponentByPosition(0)

    @staticmethod
    def setEnterprise(pdu, value):
        """Set enterprise component of SNMP trap PDU."""
        pdu.setComponentByPosition(0, value)

    @staticmethod
    def getAgentAddr(pdu):
        """Return agent address component of SNMP trap PDU."""
        return pdu.getComponentByPosition(1).getComponentByPosition(0)

    @staticmethod
    def setAgentAddr(pdu, value):
        """Set agent address component of SNMP trap PDU."""
        pdu.setComponentByPosition(1).getComponentByPosition(1).setComponentByPosition(
            0, value
        )

    @staticmethod
    def getGenericTrap(pdu):
        """Return generic trap component of SNMP trap PDU."""
        return pdu.getComponentByPosition(2)

    @staticmethod
    def setGenericTrap(pdu, value):
        """Set generic trap component of SNMP trap PDU."""
        pdu.setComponentByPosition(2, value)

    @staticmethod
    def getSpecificTrap(pdu):
        """Return specific trap component of SNMP trap PDU."""
        return pdu.getComponentByPosition(3)

    @staticmethod
    def setSpecificTrap(pdu, value):
        """Set specific trap component of SNMP trap PDU."""
        pdu.setComponentByPosition(3, value)

    @staticmethod
    def getTimeStamp(pdu):
        """Return time stamp component of SNMP trap PDU."""
        return pdu.getComponentByPosition(4)

    @staticmethod
    def setTimeStamp(pdu, value):
        """Set time stamp component of SNMP trap PDU."""
        pdu.setComponentByPosition(4, value)

    @staticmethod
    def getVarBindList(pdu):
        """Return var-bind list component of SNMP trap PDU."""
        return pdu.getComponentByPosition(5)

    @staticmethod
    def setVarBindList(pdu, varBindList):
        """Set var-bind list component of SNMP trap PDU."""
        pdu.setComponentByPosition(5, varBindList)

    @staticmethod
    def getVarBinds(pdu):
        """Return var-binds component of SNMP trap PDU."""
        varBinds = []
        for varBind in pdu.getComponentByPosition(5):
            varBinds.append(apiVarBind.getOIDVal(varBind))
        return varBinds

    @staticmethod
    def setVarBinds(pdu, varBinds):
        """Set var-binds component of SNMP trap PDU."""
        varBindList = pdu.setComponentByPosition(5).getComponentByPosition(5)
        varBindList.clear()
        idx = 0
        for varBind in varBinds:
            if isinstance(varBind, VarBind):
                varBindList.setComponentByPosition(idx, varBind)
            else:
                varBindList.setComponentByPosition(idx)
                apiVarBind.setOIDVal(varBindList.getComponentByPosition(idx), varBind)
            idx += 1


apiTrapPDU = TrapPDUAPI()  # noqa: N816


class MessageAPI:
    """SNMP message API."""

    _version = rfc1157.version.clone(0)
    _community = univ.OctetString("public")

    def setDefaults(self, msg):
        """Set default values for SNMP message."""
        msg.setComponentByPosition(
            0,
            self._version,
            verifyConstraints=False,
            matchTags=False,
            matchConstraints=False,
        )
        msg.setComponentByPosition(
            1,
            self._community,
            verifyConstraints=False,
            matchTags=False,
            matchConstraints=False,
        )
        return msg

    @staticmethod
    def getVersion(msg):
        """Return version component of SNMP message."""
        return msg.getComponentByPosition(0)

    @staticmethod
    def setVersion(msg, value):
        """Set version component of SNMP message."""
        msg.setComponentByPosition(0, value)

    @staticmethod
    def getCommunity(msg):
        """Return community component of SNMP message."""
        return msg.getComponentByPosition(1)

    @staticmethod
    def setCommunity(msg, value):
        """Set community component of SNMP message."""
        msg.setComponentByPosition(1, value)

    @staticmethod
    def getPDU(msg):
        """Return PDU component of SNMP message."""
        return msg.getComponentByPosition(2).getComponent()

    @staticmethod
    def setPDU(msg, value):
        """Set PDU component of SNMP message."""
        msg.setComponentByPosition(2).getComponentByPosition(2).setComponentByType(
            value.getTagSet(),
            value,
            verifyConstraints=False,
            matchTags=False,
            matchConstraints=False,
            innerFlag=True,
        )

    def getResponse(self, reqMsg):
        """Return a response message to a request message."""
        rspMsg = Message()
        self.setDefaults(rspMsg)
        self.setVersion(rspMsg, self.getVersion(reqMsg))
        self.setCommunity(rspMsg, self.getCommunity(reqMsg))
        self.setPDU(rspMsg, apiPDU.getResponse(self.getPDU(reqMsg)))
        return rspMsg


apiMessage = MessageAPI()  # noqa: N816
