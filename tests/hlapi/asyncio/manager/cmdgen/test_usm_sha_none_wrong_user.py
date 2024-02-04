import pytest
from pysnmp.hlapi.asyncio import *
from pysnmp.proto.errind import UnknownUserName

@pytest.mark.asyncio
async def test_usm_sha_none_wrong_user():
    snmpEngine = SnmpEngine()
    authData = UsmUserData(
        "usr-sha-none-not-exist",
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

    assert isinstance(errorIndication, UnknownUserName)
    assert str(errorIndication) == 'Unknown USM user'

    snmpEngine.transportDispatcher.closeDispatcher()
