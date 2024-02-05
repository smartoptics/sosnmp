import pytest
from pysnmp.hlapi.asyncio import *
from pysnmp.proto.errind import DecryptionError, RequestTimedOut, UnknownUserName

@pytest.mark.asyncio
async def test_usm_sha_aes128():
    snmpEngine = SnmpEngine()
    authData = UsmUserData(
        "usr-sha-aes",
        "authkey1",
        "privkey1",
        authProtocol=usmHMACSHAAuthProtocol,
        privProtocol=usmAesCfb128Protocol,
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

@pytest.mark.asyncio
async def test_usm_sha_aes128_wrong_auth():
    snmpEngine = SnmpEngine()
    authData = UsmUserData(
        "usr-sha-aes",
        "authkey1",
        "privkey1",
        authProtocol=usmHMACMD5AuthProtocol, # wrongly use usmHMACMD5AuthProtocol
        privProtocol=usmAesCfb128Protocol
    )
    errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
        snmpEngine,
        authData,
        UdpTransportTarget(("demo.pysnmp.com", 161), retries=0),
        ContextData(),
        ObjectType(ObjectIdentity("SNMPv2-MIB", "sysDescr", 0)),
    )

    assert isinstance(errorIndication, DecryptionError)
    assert str(errorIndication) == 'Ciphering services not available or ciphertext is broken'

    snmpEngine.transportDispatcher.closeDispatcher()

@pytest.mark.asyncio
async def test_usm_sha_aes128_wrong_priv():
    snmpEngine = SnmpEngine()
    authData = UsmUserData(
        "usr-sha-aes",
        "authkey1",
        "privkey1",
        authProtocol=usmHMACSHAAuthProtocol,
        privProtocol=usmDESPrivProtocol, # wrongly use usmDESPrivProtocol
    )
    errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
        snmpEngine,
        authData,
        UdpTransportTarget(("demo.pysnmp.com", 161), retries=0),
        ContextData(),
        ObjectType(ObjectIdentity("SNMPv2-MIB", "sysDescr", 0)),
    )

    assert isinstance(errorIndication, DecryptionError)
    assert str(errorIndication) == 'Ciphering services not available or ciphertext is broken'

    snmpEngine.transportDispatcher.closeDispatcher()

@pytest.mark.asyncio
async def test_usm_sha_aes128_wrong_user():
    snmpEngine = SnmpEngine()
    authData = UsmUserData(
        "usr-sha-aes-not-exist",
        "authkey1",
        "privkey1",
        authProtocol=usmHMACSHAAuthProtocol,
        privProtocol=usmAesCfb128Protocol,
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
