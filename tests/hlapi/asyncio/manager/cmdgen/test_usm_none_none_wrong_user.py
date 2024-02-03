import pytest
from pysnmp.hlapi.asyncio import *
from pysnmp.proto.errind import DecryptionError

@pytest.mark.asyncio
async def test_usm_no_auth_no_priv_wrong_user():
    snmpEngine = SnmpEngine()
    authData = UsmUserData(
        "usr-none-none-not-exist"
    )
    errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
        snmpEngine,
        authData,
        UdpTransportTarget(("demo.pysnmp.com", 161), retries=0),
        ContextData(),
        ObjectType(ObjectIdentity("SNMPv2-MIB", "sysDescr", 0)),
    )

    assert isinstance(errorIndication, DecryptionError)
    # assert str(errorIndication) == 'Ciphering services not available or ciphertext is broken'
