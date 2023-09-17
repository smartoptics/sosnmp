import pytest
from pysnmp.hlapi.asyncio.slim import Slim
from pysnmp.smi.rfc1902 import ObjectIdentity, ObjectType

@pytest.mark.asyncio
async def test_v1_set():
    slim = Slim(1)
    errorIndication, errorStatus, errorIndex, varBinds = await slim.set(
        'public',
        'demo.pysnmp.com',
        161,
        ObjectType(ObjectIdentity("SNMPv2-MIB", "sysLocation", 0), "Shanghai")
    )

    assert errorIndication is None
    assert errorStatus == 0
    assert len(varBinds) == 1
    assert varBinds[0][0].prettyPrint() == 'SNMPv2-MIB::sysLocation.0'
    assert varBinds[0][1].prettyPrint() == 'Shanghai'

    slim.close()