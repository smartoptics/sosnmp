import asyncio
import pytest


from pysnmp.hlapi.v3arch.asyncio import *
from tests.manager_context import MANAGER_PORT, ManagerContextManager


@pytest.mark.asyncio
async def test_send_v3_trap_notification():
    async with ManagerContextManager() as (_, message_count):
        # snmptrap -v3 -l authPriv -u usr-md5-des -A authkey1 -X privkey1 -e 8000000001020304 localhost:MANAGER_PORT 0 1.3.6.1.6.3.1.1.5.1 1.3.6.1.2.1.1.1.0 s "my system"
        snmpEngine = SnmpEngine(OctetString(hexValue="8000000001020304"))
        errorIndication, errorStatus, errorIndex, varBinds = await send_notification(
            snmpEngine,
            UsmUserData("usr-md5-des", "authkey1", "privkey1"),
            await UdpTransportTarget.create(("localhost", MANAGER_PORT)),
            ContextData(),
            "trap",
            NotificationType(ObjectIdentity("IF-MIB", "linkDown")),
        )

        snmpEngine.close_dispatcher()
        await asyncio.sleep(1)
        assert message_count == [1]


@pytest.mark.asyncio
async def test_send_v3_trap_notification_none():
    async with ManagerContextManager() as (_, message_count):
        # snmptrap -v3 -l noAuthNoPriv -u usr-none-none -e 8000000001020305 localhost:MANAGER_PORT 0 1.3.6.1.6.3.1.1.5.1 1.3.6.1.2.1.1.1.0 s "my system"
        snmpEngine = SnmpEngine(OctetString(hexValue="8000000001020305"))
        errorIndication, errorStatus, errorIndex, varBinds = await send_notification(
            snmpEngine,
            UsmUserData("usr-none-none", None, None),
            await UdpTransportTarget.create(("localhost", MANAGER_PORT)),
            ContextData(),
            "trap",
            NotificationType(ObjectIdentity("IF-MIB", "linkDown")),
        )

        snmpEngine.close_dispatcher()
        await asyncio.sleep(1)
        assert message_count == [1]


@pytest.mark.asyncio
async def test_send_v3_trap_notification_invalid_user():
    async with ManagerContextManager() as (_, message_count):
        # snmptrap -v3 -l authPriv -u usr-md5-des -A authkey1 -X privkey1 -e 8000000001020304 localhost:MANAGER_PORT 0 1.3.6.1.6.3.1.1.5.1 1.3.6.1.2.1.1.1.0 s "my system"
        snmpEngine = SnmpEngine(OctetString(hexValue="8000000001020304"))
        errorIndication, errorStatus, errorIndex, varBinds = await send_notification(
            snmpEngine,
            UsmUserData("usr-md5-des1", "authkey1", "privkey1"),
            await UdpTransportTarget.create(("localhost", MANAGER_PORT)),
            ContextData(),
            "trap",
            NotificationType(ObjectIdentity("IF-MIB", "linkDown")),
        )

        snmpEngine.close_dispatcher()
        await asyncio.sleep(1)
        assert message_count == [0]
