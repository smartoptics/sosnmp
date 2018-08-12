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
            )

            assert errorIndication is None
            assert errorStatus == 0
            assert len(varBinds) == num_bulk
            assert varBinds[0][0][0].prettyPrint() == "SNMPv2-MIB::sysObjectID.0"
            if num_bulk > 1:
                assert varBinds[1][0][0].prettyPrint() == "SNMPv2-MIB::sysUpTime.0"
            if num_bulk > 2:
                assert varBinds[2][0][0].prettyPrint() == "SNMPv2-MIB::sysContact.0"
