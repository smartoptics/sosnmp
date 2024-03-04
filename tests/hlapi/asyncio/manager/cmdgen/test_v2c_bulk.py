import pytest
from pysnmp.entity.engine import SnmpEngine
from pysnmp.hlapi.asyncio.slim import Slim
from pysnmp.hlapi.asyncio.sync.cmdgen import bulkCmd as bulkCmdSync
from pysnmp.hlapi.asyncio.transport import UdpTransportTarget
from pysnmp.hlapi.auth import CommunityData
from pysnmp.hlapi.context import ContextData
from pysnmp.proto.rfc1902 import ObjectIdentifier
from pysnmp.smi.rfc1902 import ObjectIdentity, ObjectType
from tests.agent_context import AGENT_PORT, AgentContextManager


@pytest.mark.asyncio
async def test_v2c_bulk():
    async with AgentContextManager():
        with Slim() as slim:
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
            assert varBinds[0][0][0].prettyPrint() == "SNMPv2-MIB::sysObjectID.0"
            assert varBinds[0][0][1].prettyPrint() == "PYSNMP-MIB::pysnmp"
            # assert isinstance(varBinds[0][0][1], ObjectIdentifier)


def test_v2_bulk_sync():
    snmpEngine = SnmpEngine()
    errorIndication, errorStatus, errorIndex, varBinds = bulkCmdSync(
        snmpEngine,
        CommunityData("public"),
        UdpTransportTarget(("demo.pysnmp.com", 161)),
        ContextData(),
        0,
        50,
        ObjectType(ObjectIdentity("SNMPv2-MIB", "sysDescr", 0)),
    )

    assert errorIndication is None
    assert errorStatus == 0
    assert len(varBinds) == 50
    assert varBinds[0][0][0].prettyPrint() == "SNMPv2-MIB::sysObjectID.0"
    assert varBinds[0][0][1].prettyPrint() == "SNMPv2-SMI::internet"
    # assert isinstance(varBinds[0][0][1], ObjectIdentifier)

    snmpEngine.transportDispatcher.closeDispatcher()
