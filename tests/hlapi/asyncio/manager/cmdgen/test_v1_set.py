import pytest
from pysnmp.entity.engine import SnmpEngine
from pysnmp.hlapi.v3arch.asyncio.cmdgen import walkCmd
from pysnmp.hlapi.v3arch.asyncio.slim import Slim
from pysnmp.hlapi.v3arch.asyncio.transport import UdpTransportTarget
from pysnmp.hlapi.v3arch.asyncio.auth import CommunityData
from pysnmp.hlapi.v3arch.asyncio.context import ContextData
from pysnmp.proto.rfc1902 import Integer, OctetString
from pysnmp.smi.rfc1902 import ObjectIdentity, ObjectType
from tests.agent_context import AGENT_PORT, AgentContextManager


@pytest.mark.asyncio
async def test_v1_set():
    async with AgentContextManager():
        with Slim(1) as slim:
            errorIndication, errorStatus, errorIndex, varBinds = await slim.set(
                "public",
                "localhost",
                AGENT_PORT,
                ObjectType(ObjectIdentity("SNMPv2-MIB", "sysLocation", 0), "Shanghai"),
            )

            assert errorIndication is None
            assert errorStatus == 0
            assert len(varBinds) == 1
            assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::sysLocation.0"
            assert varBinds[0][1].prettyPrint() == "Shanghai"
            assert isinstance(varBinds[0][1], OctetString)


@pytest.mark.asyncio
async def test_v1_set_table_creation():
    async with AgentContextManager(enable_table_creation=True):
        with Slim(1) as slim:
            snmpEngine = SnmpEngine()

            # Perform a SNMP walk to get all object counts
            objects = walkCmd(
                snmpEngine,
                CommunityData("public", mpModel=0),
                UdpTransportTarget(("localhost", AGENT_PORT)),
                ContextData(),
                ObjectType(ObjectIdentity("1.3.6")),
            )

            objects_list = [item async for item in objects]
            assert len(objects_list) > 0

            object_counts = len(objects_list)

            errorIndication, errorStatus, errorIndex, varBinds = await slim.set(
                "public",
                "localhost",
                AGENT_PORT,
                ObjectType(
                    ObjectIdentity("1.3.6.6.1.5.2.97.98.99"), OctetString("My value")
                ),
            )

            assert errorIndication is None
            assert errorStatus == 0
            assert len(varBinds) == 1
            assert varBinds[0][0].prettyPrint() == "SNMPv2-SMI::dod.6.1.5.2.97.98.99"
            assert varBinds[0][1].prettyPrint() == "My value"
            assert isinstance(varBinds[0][1], OctetString)

            errorIndication, errorStatus, errorIndex, varBinds = await slim.set(
                "public",
                "localhost",
                AGENT_PORT,
                ObjectType(ObjectIdentity("1.3.6.6.1.5.4.97.98.99"), Integer(4)),
            )

            assert errorIndication is None
            assert errorStatus == 0
            assert len(varBinds) == 1
            assert varBinds[0][0].prettyPrint() == "SNMPv2-SMI::dod.6.1.5.4.97.98.99"
            assert varBinds[0][1].prettyPrint() == "1"
            # assert isinstance(varBinds[0][1], Integer)

            # Perform a SNMP walk to get all object counts
            objects = walkCmd(
                snmpEngine,
                CommunityData("public", mpModel=0),
                UdpTransportTarget(("localhost", AGENT_PORT)),
                ContextData(),
                ObjectType(ObjectIdentity("1.3.6")),
            )

            objects_list = [item async for item in objects]
            assert len(objects_list) > 0

            assert len(objects_list) == object_counts + 4
