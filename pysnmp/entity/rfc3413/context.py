#
# This file is part of pysnmp software.
#
# Copyright (c) 2005-2020, Ilya Etingof <etingof@gmail.com>
# License: https://www.pysnmp.com/pysnmp/license.html
#
from pyasn1.type import univ
from pysnmp import debug, error
from pysnmp.entity.engine import SnmpEngine
from pysnmp.smi.instrum import MibInstrumController


class SnmpContext:
    """Create a context object."""

    def __init__(self, snmpEngine: SnmpEngine, contextEngineId=None):
        """Create a context object."""
        (
            snmpEngineId,
        ) = snmpEngine.msgAndPduDsp.mibInstrumController.mibBuilder.importSymbols(  # type: ignore
            "__SNMP-FRAMEWORK-MIB", "snmpEngineID"
        )
        if contextEngineId is None:
            # Default to local snmpEngineId
            self.contextEngineId = snmpEngineId.syntax
        else:
            self.contextEngineId = snmpEngineId.syntax.clone(contextEngineId)
        debug.logger & debug.FLAG_INS and debug.logger(
            f'SnmpContext: contextEngineId "{self.contextEngineId!r}"'
        )
        self.contextNames = {
            b"": snmpEngine.msgAndPduDsp.mibInstrumController  # Default name
        }

    def registerContextName(self, contextName, mibInstrum=None):
        """Register a context name."""
        contextName = univ.OctetString(contextName).asOctets()
        if contextName in self.contextNames:
            raise error.PySnmpError("Duplicate contextName %s" % contextName)
        debug.logger & debug.FLAG_INS and debug.logger(
            f"registerContextName: registered contextName {contextName!r}, mibInstrum {mibInstrum!r}"
        )
        if mibInstrum is None:
            self.contextNames[contextName] = self.contextNames[b""]
        else:
            self.contextNames[contextName] = mibInstrum

    def unregisterContextName(self, contextName):
        """Unregister a context name."""
        contextName = univ.OctetString(contextName).asOctets()
        if contextName in self.contextNames:
            debug.logger & debug.FLAG_INS and debug.logger(
                "unregisterContextName: unregistered contextName %r" % contextName
            )
            del self.contextNames[contextName]

    def getMibInstrum(self, contextName=b"") -> MibInstrumController:
        """Get MIB instrumentation for a context name."""
        contextName = univ.OctetString(contextName).asOctets()
        if contextName not in self.contextNames:
            debug.logger & debug.FLAG_INS and debug.logger(
                "getMibInstrum: contextName %r not registered" % contextName
            )
            raise error.PySnmpError("Missing contextName %s" % contextName)
        else:
            debug.logger & debug.FLAG_INS and debug.logger(
                f"getMibInstrum: contextName {contextName!r}, mibInstum {self.contextNames[contextName]!r}"
            )
            return self.contextNames[contextName]
