import pytest
from pysnmp.hlapi.asyncio import *

@pytest.mark.asyncio
async def test_usm_no_auth_no_priv():
    snmpEngine = SnmpEngine()
    authData = UsmUserData(
        "usr-none-none"
    )
    errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
        snmpEngine,
        authData,
        UdpTransportTarget(("demo.pysnmp.com", 161), retries=0),
        ContextData(),
        ObjectType(ObjectIdentity("SNMPv2-MIB", "sysDescr", 0)),
    )

    assert errorIndication is None
    assert errorStatus == 0
    assert len(varBinds) == 1
    assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::sysDescr.0"
    isinstance(varBinds[0][1], OctetString)