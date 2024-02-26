import pytest
from pysnmp.hlapi.asyncio.slim import Slim
from pysnmp.hlapi.asyncio import *
from tests.agent_context import AGENT_PORT, AgentContextManager


@pytest.mark.asyncio
async def test_v1_get():
    async with AgentContextManager():
        slim = Slim()
        errorIndication, errorStatus, errorIndex, varBinds = await slim.get(
            "public",
            "localhost",
            AGENT_PORT,
            ObjectType(ObjectIdentity("SNMPv2-MIB", "sysDescr", 0)),
        )

        assert errorIndication is None
        assert errorStatus == 0
        assert len(varBinds) == 1
        assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::sysDescr.0"
        assert varBinds[0][1].prettyPrint().startswith("PySNMP engine version")
        assert isinstance(varBinds[0][1], OctetString)

        slim.close()
