import pytest

from pysnmp.hlapi.v3arch.asyncio import *
from tests.agent_context import AGENT_PORT, AgentContextManager


@pytest.mark.asyncio
async def test_v2c_get_table_bulk():
    async with AgentContextManager():
        snmpEngine = SnmpEngine()
        objects = bulkWalkCmd(
            snmpEngine,
            CommunityData("public"),
            UdpTransportTarget(("localhost", AGENT_PORT)),
            ContextData(),
            0,
            4,
            ObjectType(ObjectIdentity("SNMPv2-MIB", "sysDescr", 0)),
        )

        objects_list = [obj async for obj in objects]

        errorIndication, errorStatus, errorIndex, varBinds = objects_list[0]

        assert errorIndication is None
        assert errorStatus == 0
        assert len(varBinds) == 1
        assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::sysObjectID.0"

        errorIndication, errorStatus, errorIndex, varBinds = objects_list[1]

        assert errorIndication is None
        assert errorStatus == 0
        assert len(varBinds) == 1
        assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::sysUpTime.0"

        assert len(objects_list), 50

        snmpEngine.closeDispatcher()


@pytest.mark.asyncio
async def test_v2c_get_table_bulk_0_4():
    async with AgentContextManager():
        snmpEngine = SnmpEngine()
        index = 0
        async for errorIndication, errorStatus, errorIndex, varBinds in bulkWalkCmd(
            snmpEngine,
            CommunityData("public"),
            UdpTransportTarget(("localhost", AGENT_PORT)),
            ContextData(),
            0,
            4,
            ObjectType(ObjectIdentity("SNMPv2-MIB", "snmp")),
            lexicographicMode=False,
        ):
            assert errorIndication is None
            assert errorStatus == 0
            assert len(varBinds) == 1
            if index == 0:
                assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::snmpInPkts.0"

            if index == 1:
                assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::snmpOutPkts.0"

            if index == 26:
                assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::snmpSilentDrops.0"

            if index == 27:
                assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::snmpProxyDrops.0"

            index += 1

        assert index == 28

        snmpEngine.closeDispatcher()


@pytest.mark.asyncio
async def test_v2c_get_table_bulk_0_1():
    async with AgentContextManager():
        snmpEngine = SnmpEngine()
        index = 0
        async for errorIndication, errorStatus, errorIndex, varBinds in bulkWalkCmd(
            snmpEngine,
            CommunityData("public"),
            UdpTransportTarget(("localhost", AGENT_PORT)),
            ContextData(),
            0,
            1,
            ObjectType(ObjectIdentity("SNMPv2-MIB", "snmp")),
            lexicographicMode=False,
        ):
            assert errorIndication is None
            assert errorStatus == 0
            assert len(varBinds) == 1
            if index == 0:
                assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::snmpInPkts.0"

            if index == 1:
                assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::snmpOutPkts.0"

            if index == 26:
                assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::snmpSilentDrops.0"

            if index == 27:
                assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::snmpProxyDrops.0"

            index += 1

        assert index == 28

        snmpEngine.closeDispatcher()
