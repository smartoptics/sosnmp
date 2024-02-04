import pytest
from pysnmp.hlapi.asyncio import *

@pytest.mark.asyncio
async def test_usm_sha_none():
    snmpEngine = SnmpEngine()
    authData = UsmUserData(
        "usr-sha-none",
        "authkey1",
        authProtocol=usmHMACSHAAuthProtocol,
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

    snmpEngine.transportDispatcher.closeDispatcher()
