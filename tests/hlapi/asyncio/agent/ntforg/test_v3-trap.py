import pytest
from pysnmp.hlapi import *
from pysnmp.hlapi.asyncio.ntforg import sendNotification
from pysnmp.hlapi.asyncio.transport import UdpTransportTarget
from pysnmp.proto.api import v2c
from tests.manager_context import MANAGER_PORT, ManagerContextManager


@pytest.mark.asyncio
async def test_send_v3_trap_notification():
    async with ManagerContextManager():
        snmpEngine = SnmpEngine(OctetString(hexValue="8000000001020304"))
        errorIndication, errorStatus, errorIndex, varBinds = await sendNotification(
            snmpEngine,
            UsmUserData("usr-md5-des", "authkey1", "privkey1"),
            UdpTransportTarget(("localhost", MANAGER_PORT)),
            ContextData(),
            "trap",
            NotificationType(ObjectIdentity("IF-MIB", "linkDown")),
        )

        snmpEngine.transportDispatcher.closeDispatcher()
