import pytest
from pysnmp.hlapi.asyncio.slim import Slim
from pysnmp.smi.rfc1902 import ObjectIdentity, ObjectType

@pytest.mark.asyncio
async def test_v2c_bulk():
    slim = Slim()
    errorIndication, errorStatus, errorIndex, varBinds = await slim.bulk(
        'public',
        'demo.pysnmp.com',
        161,
        0,
        50,
        ObjectType(ObjectIdentity("SNMPv2-MIB", "sysDescr", 0)),
    )

    assert errorIndication is None
    assert errorStatus == 0
    assert len(varBinds) > 0

    slim.close()