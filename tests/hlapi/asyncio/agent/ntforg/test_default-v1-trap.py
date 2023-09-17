import pytest
from pysnmp.hlapi.asyncio import *

@pytest.mark.asyncio
async def test_send_notification():
    snmpEngine = SnmpEngine()
    errorIndication, errorStatus, errorIndex, varBinds = await sendNotification(
        snmpEngine,
        CommunityData('public', mpModel=0),
        UdpTransportTarget(('demo.pysnmp.com', 162)),
        ContextData(),
        "trap",
        NotificationType(ObjectIdentity("1.3.6.1.6.3.1.1.5.2")).addVarBinds(
            ("1.3.6.1.6.3.1.1.4.3.0", "1.3.6.1.4.1.20408.4.1.1.2"),
            ("1.3.6.1.2.1.1.1.0", OctetString("my system")),
        ),
    )
    assert errorIndication is None
    assert errorStatus == 0
    assert errorIndex == 0
    assert varBinds == []
    snmpEngine.transportDispatcher.closeDispatcher()
