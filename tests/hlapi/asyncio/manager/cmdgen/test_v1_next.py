"""
SNMPv1
++++++

Send SNMP GET request using the following options:

  * with SNMPv1, community 'public'
  * over IPv4/UDP
  * to an Agent at demo.pysnmp.com:161
  * for an instance of SNMPv2-MIB::sysDescr.0 MIB object
  * Based on asyncio I/O framework

Functionally similar to:

| $ snmpgetnext -v1 -c public demo.pysnmp.com SNMPv2-MIB::sysDescr.0

"""  #
import pytest
from pysnmp.entity.engine import SnmpEngine
from pysnmp.hlapi.asyncio.slim import Slim
from pysnmp.hlapi.asyncio.sync.cmdgen import nextCmd as nextCmdSync
from pysnmp.hlapi.asyncio.transport import UdpTransportTarget
from pysnmp.hlapi.auth import CommunityData
from pysnmp.hlapi.context import ContextData
from pysnmp.proto.rfc1902 import ObjectIdentifier
from pysnmp.smi.rfc1902 import ObjectIdentity, ObjectType
from tests.agent_context import AGENT_PORT, AgentContextManager


@pytest.mark.asyncio
async def test_v1_next():
    async with AgentContextManager():
        with Slim(1) as slim:
            errorIndication, errorStatus, errorIndex, varBinds = await slim.next(
                "public",
                "localhost",
                AGENT_PORT,
                ObjectType(ObjectIdentity("SNMPv2-MIB", "sysDescr", 0)),
            )

            assert errorIndication is None
            assert errorStatus == 0
            assert errorIndex == 0
            assert len(varBinds) == 1
            assert varBinds[0][0][0].prettyPrint() == "SNMPv2-MIB::sysObjectID.0"
            assert varBinds[0][0][1].prettyPrint() == "PYSNMP-MIB::pysnmp"
            # assert isinstance(varBinds[0][0][1], ObjectIdentifier) # TODO: fix this


def test_v1_next_sync():
    snmpEngine = SnmpEngine()
    errorIndication, errorStatus, errorIndex, varBinds = nextCmdSync(
        snmpEngine,
        CommunityData("public", mpModel=0),
        UdpTransportTarget(("demo.pysnmp.com", 161)),
        ContextData(),
        ObjectType(ObjectIdentity("SNMPv2-MIB", "sysDescr", 0)),
    )

    assert errorIndication is None
    assert errorStatus == 0
    assert len(varBinds) == 1
    assert varBinds[0][0][0].prettyPrint() == "SNMPv2-MIB::sysObjectID.0"
    assert varBinds[0][0][1].prettyPrint() == "SNMPv2-SMI::internet"
    # assert isinstance(varBinds[0][0][1], ObjectIdentifier) # TODO: fix this

    snmpEngine.transportDispatcher.closeDispatcher()
