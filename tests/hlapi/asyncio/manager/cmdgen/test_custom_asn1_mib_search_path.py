import pytest
from pysnmp.hlapi.asyncio import *

@pytest.mark.asyncio
async def test_custom_asn1_mib_search_path():
    snmpEngine = SnmpEngine()
    errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
        snmpEngine,
        CommunityData('public'),
        UdpTransportTarget(('demo.pysnmp.com', 161)),
        ContextData(),
        ObjectType(ObjectIdentity('IF-MIB', 'ifInOctets', 1).addAsn1MibSource('file:///usr/share/snmp',
                                                                                'https://mibs.pysnmp.com/asn1/@mib@'))
    )

    assert errorIndication is None
    assert errorStatus == 0
    assert len(varBinds) == 1
    assert varBinds[0][0].prettyPrint() == 'IF-MIB::ifInOctets.1'

    snmpEngine.transportDispatcher.closeDispatcher()