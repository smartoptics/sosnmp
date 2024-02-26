import pytest
from pysnmp.hlapi.asyncio.slim import Slim
from pysnmp.smi.rfc1902 import ObjectIdentity, ObjectType
from tests.agent_context import AGENT_PORT, AgentContextManager


@pytest.mark.asyncio
async def test_v2c_bulk():
    async with AgentContextManager():
        slim = Slim()
        errorIndication, errorStatus, errorIndex, varBinds = await slim.bulk(
            "public",
            "localhost",
            AGENT_PORT,
            0,
            50,
            ObjectType(ObjectIdentity("SNMPv2-MIB", "sysDescr", 0)),
        )

        assert errorIndication is None
        assert errorStatus == 0
        assert len(varBinds) == 50

        slim.close()
