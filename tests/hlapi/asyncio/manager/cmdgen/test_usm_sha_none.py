import pytest
from pysnmp.hlapi.asyncio import *
from pysnmp.proto.errind import UnknownUserName, WrongDigest

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

@pytest.mark.asyncio
async def test_usm_sha_none_wrong_auth():
    snmpEngine = SnmpEngine()
    authData = UsmUserData(
        "usr-sha-none",
        "authkey1",
        authProtocol=usmHMACMD5AuthProtocol, # wrongly use usmHMACMD5AuthProtocol
    )
    errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
        snmpEngine,
        authData,
        UdpTransportTarget(("demo.pysnmp.com", 161), retries=0),
        ContextData(),
        ObjectType(ObjectIdentity("SNMPv2-MIB", "sysDescr", 0)),
    )

    assert isinstance(errorIndication, WrongDigest)
    assert str(errorIndication) == 'Wrong SNMP PDU digest'

    snmpEngine.transportDispatcher.closeDispatcher()

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
