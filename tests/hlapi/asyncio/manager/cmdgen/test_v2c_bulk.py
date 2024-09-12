import pytest

from pysnmp.hlapi.v3arch.asyncio import *
from tests.agent_context import AGENT_PORT, AgentContextManager
import pytest
from pysnmp.hlapi.v3arch.asyncio import *
from tests.agent_context import AGENT_PORT, AgentContextManager


@pytest.mark.asyncio
@pytest.mark.parametrize("num_bulk", [1, 2, 50])
async def test_v2c_bulk(num_bulk):
    async with AgentContextManager():
        with Slim() as slim:
            errorIndication, errorStatus, errorIndex, varBinds = await slim.bulk(
                "public",
                "localhost",
                AGENT_PORT,
                0,
                num_bulk,
                ObjectType(ObjectIdentity("SNMPv2-MIB", "sysDescr", 0)),
                retries=0,
            )

            assert errorIndication is None
            assert errorStatus == 0
            assert len(varBinds) == 1
            assert varBinds[0][0][0].prettyPrint() == "SNMPv2-MIB::sysObjectID.0"
            if num_bulk > 1:
                assert varBinds[0][1][0].prettyPrint() == "SNMPv2-MIB::sysUpTime.0"
            if num_bulk > 2:
                assert varBinds[0][2][0].prettyPrint() == "SNMPv2-MIB::sysContact.0"


@pytest.mark.asyncio
async def test_v2c_bulk_multiple_input():
    mib_objects = [
        ObjectType(ObjectIdentity("SNMPv2-MIB", "sysContact")),
        ObjectType(ObjectIdentity("SNMPv2-MIB", "sysORIndex")),
        ObjectType(ObjectIdentity("SNMPv2-MIB", "sysORDescr")),
    ]
    async with AgentContextManager():
        with Slim() as slim:
            errorIndication, errorStatus, errorIndex, varBinds = await slim.bulk(
                "public", "demo.pysnmp.com", 161, 1, 2, *mib_objects, retries=0
            )

            assert errorIndication is None
            assert errorStatus == 0
            assert len(varBinds) == 1
            assert len(varBinds[0]) == 5


# snmpbulkget -v2c -c public -C n1 -C r2 localhost 1.3.6.1.2.1.1.4 1.3.6.1.2.1.1.9.1.1 1.3.6.1.2.1.1.9.1.3
